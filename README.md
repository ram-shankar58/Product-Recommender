# E-commerce Product Recommender

This project is a minimal demo that combines a simple recommendation engine with LLM-powered explanations. It provides a FastAPI backend, a database for storing product and user interaction data, and optional LLM integration for generating human-readable explanations for recommendations.

---

## Features
- **FastAPI Backend**: Exposes endpoints for loading data, fetching metadata, and generating recommendations.
- **Database Support**: SQLite (default) for development; PostgreSQL/MySQL for production.
- **Recommendation Engine**: Tag-based scoring with a popularity boost.
- **LLM Integration**: Supports OpenAI, HuggingFace, or deterministic fallback for explanations.
- **Frontend Dashboard**: A simple static UI for testing recommendations.
- **Data Loaders**: Fetch real product data from APIs, generate synthetic data, or use Kaggle datasets.

---

## Setup Instructions

### 1. Clone the Repository
```bash
# Clone the repository to your local machine
git clone https://github.com/ram-shankar58/Product-Recommender.git
cd Product-Recommender
```

### 2. Set Up Python Environment
```bash
# Create a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Configuration
- By default, the app uses SQLite (`recs.db`).
- For PostgreSQL:
```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Set DATABASE_URL environment variable
export DATABASE_URL=postgresql://user:password@localhost/recommender_db
```
- For MySQL:
```bash
# Install MySQL driver
pip install mysql-connector-python

# Set DATABASE_URL environment variable
export DATABASE_URL=mysql://user:password@localhost/recommender_db
```

### 4. Start the Server
```bash
# Start the FastAPI server
uvicorn app.main:app --reload --port 8000
```

---

## API Endpoints

### **GET /data-info**
- **Description**: Fetch metadata about the current dataset (e.g., product/user counts).
- **Example**:
```bash
curl -sS http://127.0.0.1:8000/data-info | jq .
```

### **GET /active-users**
- **Description**: Fetch a list of users with interactions in the current dataset.
- **Example**:
```bash
curl -sS http://127.0.0.1:8000/active-users | jq .
```

### **POST /load-data-source**
- **Description**: Load a dataset into the database.
- **Parameters**:
  - `source`: `synthetic`, `api`, or `sample`.
- **Example**:
```bash
curl -sS -X POST "http://127.0.0.1:8000/load-data-source?source=synthetic" | jq .
```

### **POST /recommendations**
- **Description**: Generate product recommendations for a user.
- **Request Body**:
  - `{ "user_id": <int>, "k": <int?> }` or `{ "user_behavior": {"product_ids": [..], "tags": [..]}, "k": <int?> }`
- **Example**:
```bash
curl -sS -X POST "http://127.0.0.1:8000/recommendations" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "k": 5}' | jq .
```

---

## Data Loading Options

### **Option 1: Real Product Data from APIs**
- Fetches product data from public APIs (e.g., DummyJSON, FakeStore).
```bash
python scripts/fetch_real_products.py
```

### **Option 2: Realistic Synthetic Data**
- Generates realistic product, user, and interaction data.
```bash
python scripts/generate_realistic_data.py
```

### **Option 3: Kaggle Datasets**
- Use production-scale datasets (e.g., Brazilian E-Commerce, Instacart).
```bash
# Follow instructions in the dataset download script
cat scripts/DATASET_DOWNLOAD_INSTRUCTIONS.md

# Download and convert datasets
python scripts/download_real_data.py
python scripts/convert_dataset.py
```

---

## LLM Integration

### **Supported Backends**
- **OpenAI**: Set `OPENAI_API_KEY` to use OpenAI models.
- **HuggingFace**: Set `LLM_BACKEND=hf` to use a local HuggingFace model (default: `google/flan-t5-small`).
- **Deterministic Fallback**: Generates explanations without an LLM.

### **Example Configuration**
```bash
# Use HuggingFace backend
export LLM_BACKEND=hf
export HF_MODEL=google/flan-t5-small

# Start the server
uvicorn app.main:app --reload --port 8000
```

---

## Frontend Dashboard
- A static HTML dashboard is available at `/demo`.
- **Usage**:
  - Open `http://127.0.0.1:8000/demo` in your browser.
  - Select a user and view recommendations with explanations.

---

## Deployment

### **Docker Setup**
- Build and run the app using Docker Compose:
```bash
# Build and start the containers
docker compose up --build
```
- The app will be available at `http://127.0.0.1:8000`.

### **Environment Variables**
- `DATABASE_URL`: Database connection string (e.g., `postgresql://user:password@localhost/dbname`).
- `OPENAI_API_KEY`: OpenAI API key for LLM integration.
- `LLM_BACKEND`: Set to `hf` for HuggingFace backend.
- `HF_MODEL`: HuggingFace model ID (default: `google/flan-t5-small`).

---

## Testing
- Run the test suite:
```bash
pytest tests/
```
