# E-commerce Product Recommender

Minimal demo that combines a simple recommender with LLM-powered explanations.

## Features
- FastAPI backend exposing recommendations API
- SQLite database (SQLModel) for products and user interactions
- Simple tag-based recommender with popularity boost
- LLM wrapper that calls OpenAI if `OPENAI_API_KEY` is set, otherwise returns deterministic explanations
- Sample data loader and tests
- Optional static dashboard page to preview recommendations

## Requirements
- Python 3.10+
- Optional: set `OPENAI_API_KEY` to enable real LLM explanations

## Quick start (fish shell)

```fish
cd "/home/ram/projects/Product Recommender"
python -m venv .venv
source .venv/bin/activate.fish
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Then in another terminal:

```fish
# Load sample data
curl -X POST http://localhost:8000/load-sample-data

# Get recommendations for user 1
curl -X POST http://localhost:8000/recommendations -H 'content-type: application/json' -d '{"user_id": 1, "k": 5}'
```

## API
- POST `/load-sample-data` – seed a small catalog and interactions
- POST `/recommendations` – request recommendations
  - body: `{ "user_id": <int>, "k": <int?> }` or `{ "user_behavior": {"product_ids": [..], "tags": [..]}, "k": <int?> }`
  - returns: list of products with an `explanation` string per item

## Demo video
- Record 2–3 minutes: start server, load data, request recommendations, and show explanations.

## Notes
- This is a starting point. Replace the recommender with a learned model or extend the schema for production use.
