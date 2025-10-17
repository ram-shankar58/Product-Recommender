from typing import Optional
import os
import asyncio
import re

PROMPT_TEMPLATE = (
    "You are a helpful shopping assistant. Explain in 1-3 concise sentences why the product '{name}' is recommended to this user "
    "based on their past behavior and interests provided below. Be specific: cite which past items (by name) or which tags caused the match, and mention the interaction type when relevant (viewed, added to cart, purchased).\n\nContext: {signals}\n\nExplanation:"
)

BACKEND = os.getenv("LLM_BACKEND", "auto").lower()  # auto | openai | hf | none

def _want_openai() -> bool:
    if BACKEND == "openai":
        return True
    if BACKEND == "hf" or BACKEND == "none":
        return False
    # auto
    return bool(os.getenv("OPENAI_API_KEY"))


# OpenAI backend
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
        return _deterministic_explain(product_name, signals)


# Hugging Face backend (local)
_HF_PIPELINE = None

def _get_hf_pipeline():
    global _HF_PIPELINE
    if _HF_PIPELINE is not None:
        return _HF_PIPELINE
    try:
        from transformers import pipeline
        model_id = os.getenv("HF_MODEL", "google/flan-t5-small")
        cache_dir = os.getenv("HF_CACHE_DIR")
        if not cache_dir: # default to a project-local cache folder
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
    if pipe is None: # fallback deterministic
        return _deterministic_explain(product_name, signals)
    prompt = PROMPT_TEMPLATE.format(name=product_name, signals=signals)

    def _run():
        out = pipe(
            prompt,
            max_new_tokens=80,
            do_sample=True,
            temperature=0.7,
            num_return_sequences=1,
        )
    text = out[0].get("generated_text", "").strip()
    return text or _deterministic_explain(product_name, signals)

    return await asyncio.to_thread(_run)


async def explain(product_name: str, signals: str) -> str:
    if _want_openai():
        return await _openai_explain(product_name, signals)
    if BACKEND == "hf":
        return await _hf_explain(product_name, signals)
    return _deterministic_explain(product_name, signals)


def _deterministic_explain(product_name: str, signals: str) -> str:
    """Create a short deterministic explanation from the provided signal string.

    This uses simple heuristics to surface recent purchases/add_to_cart, shared tags,
    and product popularity hints so the explanation is informative even without an LLM.
    """
    if not signals:
        return f"{product_name}: Recommended because it matches your interests and past activity."

    # Try to extract recent purchased/added items
    purchase_match = re.search(r"User recently purchased/added to cart:\s*([^;]+)", signals)
    # Find shared tags mentions
    # This looks for patterns like 'shared tags tag1, tag2 with Item Name (event)'
    shared_tags_match = re.search(r"shared tags\s*([^;]+)\s*with\s*([^;]+)", signals)
    pop_match = re.search(r"product popularity score:\s*(\d+)", signals)

    parts = []
    if purchase_match:
        names = purchase_match.group(1).strip()
        short = names.split(",")[0]
        parts.append(f"You recently purchased or added to cart {short}.")

    if shared_tags_match:
        tags = shared_tags_match.group(1).strip()
        recent_name = shared_tags_match.group(2).strip()
        parts.append(f"This item shares tags {tags} with {recent_name}.")

    if not parts:
        # Fallback: include a trimmed version of the signals
        summary = signals
        if len(summary) > 200:
            summary = summary[:197] + "..."
        parts.append(f"Based on: {summary}")

    if pop_match:
        parts.append(f"It also has popularity score {pop_match.group(1)}.")

    text = " ".join(parts)
    return f"{product_name}: {text}"
