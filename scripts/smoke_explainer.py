import asyncio
from app.llm import explainer

async def main():
    product = "Road Running Shoes"
    signals = (
        "User recently purchased/added to cart: Trail Running Shoes (purchase); "
        "shared tags running with Trail Running Shoes (purchase); product popularity score: 9"
    )
    out = await explainer.explain(product, signals)
    print(out)

if __name__ == '__main__':
    asyncio.run(main())
