from typing import Optional
import os

USE_OPENAI = bool(os.getenv("OPENAI_API_KEY"))

PROMPT_TEMPLATE = (
    "Explain briefly and helpfully why the product '{name}' is recommended to this user "
    "based on their behavior and interests: {signals}. Be specific but concise."
)

async def explain(product_name: str, signals: str) -> str:
    if not USE_OPENAI:
        return f"Recommended because it matches your interests: {signals}."

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
