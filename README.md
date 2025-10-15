# E-commerce Product Recommender

Minimal demo that combines a simple recommender with LLM-powered explanations.

## Demo video

https://drive.google.com/file/d/1AcInfxBPaBhBCGA8EL1K-g1jPQNgyj2I/view?usp=sharing


## Features
- FastAPI backend exposing recommendations API
- SQLite database (SQLModel) for products and user interactions - **PostgreSQL & MySQL supported**
- Simple tag-based recommender with popularity boost
- LLM wrapper that calls OpenAI if `OPENAI_API_KEY` is set, otherwise returns deterministic explanations
- Sample data loader and tests
- **Modern, animated dashboard** with gradient design and smooth UX

## Requirements
- Python 3.10+
- Optional: set `OPENAI_API_KEY` to enable real LLM explanations
  - Or set `LLM_BACKEND=hf` to use a local Hugging Face model (default: `google/flan-t5-small`) with caching in `app/hf_cache/`.

## Quick start (fish shell)

```fish
cd "/home/ram/projects/Product Recommender"
# Option A: use your system Python directly (no venv)
pip install -r requirements.txt

# Fetch REAL product data from public APIs (recommended - no auth needed!)
python scripts/fetch_real_products.py

# OR generate realistic synthetic data
# python scripts/generate_realistic_data.py

uvicorn app.main:app --reload --port 8000

# Option B: use a virtualenv (recommended for isolation)
# python -m venv .venv
# source .venv/bin/activate.fish
# pip install -r requirements.txt
# uvicorn app.main:app --reload --port 8000
```

Then in another terminal:

```fish
# Load sample data
curl -X POST http://localhost:8000/load-sample-data

# Get recommendations for user 1
curl -X POST http://localhost:8000/recommendations -H 'content-type: application/json' -d '{"user_id": 1, "k": 5}'

# Import realistic data from CSVs (recommended - generated via script)
curl -X POST http://localhost:8000/import-csv
```

## API
- POST `/load-sample-data` – seed a small catalog and interactions (basic demo)
- POST `/import-csv` – import realistic data from `data/products.csv`, `data/users.csv`, `data/interactions.csv`
- POST `/recommendations` – request recommendations
  - body: `{ "user_id": <int>, "k": <int?> }` or `{ "user_behavior": {"product_ids": [..], "tags": [..]}, "k": <int?> }`
  - returns: list of products with an `explanation` string per item

## Data
The project supports multiple data sources:

### Option 1: Real Product Data from APIs ⭐ (Recommended)
Fetches actual product data from public APIs:
```fish
python scripts/fetch_real_products.py
```
- **~90 real products** from DummyJSON/FakeStore APIs (electronics, fashion, furniture, etc.)
- **20 generated users** with realistic names
- **200 interactions** with smart user-product affinity (users prefer certain categories)
- No authentication required!

### Option 2: Realistic Synthetic Data
Generates believable e-commerce scenarios:
```fish
python scripts/generate_realistic_data.py
```
- **30 products** across categories: Electronics, Fitness, Home, Fashion, Books, Gaming
- **10 user personas** with distinct behaviors (Tech Enthusiast, Fitness Buff, etc.)
- **80+ interactions** spanning 90 days with realistic patterns

### Option 3: Kaggle Datasets (Advanced)
For production-scale data:
```fish
# See instructions
cat scripts/DATASET_DOWNLOAD_INSTRUCTIONS.md

# Download (requires Kaggle API key)
python scripts/download_real_data.py

# Convert to our format
python scripts/convert_dataset.py
```
Supports: Brazilian E-Commerce (100K orders), Instacart, H&M datasets


## Database options
- **SQLite (default)**: Great for development, single-file database (`recs.db`)
- **PostgreSQL**: Production-ready, set `DATABASE_URL=postgresql://user:password@localhost/dbname`
- **MySQL**: Also supported, set `DATABASE_URL=mysql://user:password@localhost/dbname`

Example PostgreSQL setup (fish):
```fish
# Install PostgreSQL driver
pip install psycopg2-binary

# Set connection string
set -x DATABASE_URL postgresql://myuser:mypass@localhost/recommender_db

# Run migrations (creates tables)
uvicorn app.main:app --reload --port 8000
```

## LLM backends
- Auto (default): uses OpenAI if `OPENAI_API_KEY` is set; otherwise returns a deterministic explanation.
- Hugging Face (local): set `LLM_BACKEND=hf` and optionally `HF_MODEL` (e.g., `google/flan-t5-small`). First run downloads the model to `app/hf_cache/` so subsequent runs are offline.

Example (fish):

```fish
set -x LLM_BACKEND hf
set -x HF_MODEL google/flan-t5-small
uvicorn app.main:app --reload --port 8000
```

Note: HF is already available by default. The first model download may take a minute. Some models may require a larger PyTorch install; the default small model should work on CPU.
