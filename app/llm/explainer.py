from typing import Optional
import os
import asyncio

PROMPT_TEMPLATE = (
    "Explain briefly and helpfully why the product '{name}' is recommended to this user "
    "based on their behavior and interests: {signals}. Be specific but concise."
)

BACKEND = os.getenv("LLM_BACKEND", "auto").lower()  # auto | openai | hf | none

def _want_openai() -> bool:
    if BACKEND == "openai":
        return True
    if BACKEND == "hf" or BACKEND == "none":
        return False
    # auto
    return bool(os.getenv("OPENAI_API_KEY"))


# ----- OpenAI backend -----
async def _openai_explain(product_name: str, signals: str) -> str:
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI()
        prompt = PROMPT_TEMPLATE.format(name=product_name, signals=signals)
        resp = await client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You are a concise shopping assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=120,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return f"Recommended because it matches your interests: {signals}."


# ----- Hugging Face backend (local) -----
_HF_PIPELINE = None

def _get_hf_pipeline():
    global _HF_PIPELINE
    if _HF_PIPELINE is not None:
        return _HF_PIPELINE
    try:
        from transformers import pipeline
        model_id = os.getenv("HF_MODEL", "google/flan-t5-small")
        cache_dir = os.getenv("HF_CACHE_DIR")
        if not cache_dir:
            # default to a project-local cache folder
            here = os.path.dirname(__file__)
            cache_dir = os.path.abspath(os.path.join(here, "..", "..", "hf_cache"))
        os.makedirs(cache_dir, exist_ok=True)
        _HF_PIPELINE = pipeline(
            task="text2text-generation",
            model=model_id,
            cache_dir=cache_dir,
        )
        return _HF_PIPELINE
    except Exception:
        return None


async def _hf_explain(product_name: str, signals: str) -> str:
    pipe = _get_hf_pipeline()
    if pipe is None:
        # fallback deterministic
        return f"Recommended because it matches your interests: {signals}."
    prompt = PROMPT_TEMPLATE.format(name=product_name, signals=signals)

    def _run():
        out = pipe(
            prompt,
            max_new_tokens=80,
            do_sample=True,
            temperature=0.7,
            num_return_sequences=1,
        )
        # flan-t5-small returns a list of dicts with 'generated_text'
        text = out[0].get("generated_text", "").strip()
        return text or f"Recommended because it matches your interests: {signals}."

    return await asyncio.to_thread(_run)


# ----- Public API -----
async def explain(product_name: str, signals: str) -> str:
    # Choose backend
    if _want_openai():
        return await _openai_explain(product_name, signals)
    if BACKEND == "hf":
        return await _hf_explain(product_name, signals)
    # auto/none fallback -> deterministic string
    return f"Recommended because it matches your interests: {signals}."
