# 🎯 Data Sources Summary

Your Product Recommender now supports **real e-commerce data** from multiple sources!

## ⭐ Recommended: Real Products from Public APIs

**Easiest & Best for demos!**

```bash
python scripts/fetch_real_products.py
```

**What you get:**
- ✅ 90+ **real products** (iPhones, laptops, fashion items, furniture, etc.)
- ✅ Real names, descriptions, prices from DummyJSON & FakeStore APIs
- ✅ 20 users with realistic names
- ✅ 200 smart interactions (users have category preferences)
- ✅ **No authentication needed!**
- ✅ **No downloads needed!** (fetches via API)

**Example products:**
- iPhone 13 Pro - $899
- Mens Cotton Jacket - $55.99
- Samsung Universe 9 - $1249
- Essence Mascara Lash Princess - $9.99

## 📦 Alternative 1: Synthetic Data Generator

```bash
python scripts/generate_realistic_data.py
```

**What you get:**
- 30 curated products across 6 categories
- 10 user personas (Tech Enthusiast, Fitness Buff, Home Chef, etc.)
- 80+ interactions with behavioral patterns
- Good for testing specific scenarios

## 🔥 Alternative 2: Kaggle Datasets (Production Scale)

**For serious projects with huge datasets:**

### Option A: Brazilian E-Commerce (50MB - Recommended)
```bash
# 1. Get Kaggle API credentials from kaggle.com/settings
# 2. Save to ~/.kaggle/kaggle.json

# 3. Download
kaggle datasets download -d olistbr/brazilian-ecommerce -p ./data/raw
unzip ./data/raw/brazilian-ecommerce.zip -d ./data/raw

# 4. Convert
python scripts/convert_dataset.py
```

**Contains:** 100K real orders, customer reviews, product data from Brazilian retailer

### Option B: Other Kaggle Datasets
- **H&M Fashion Recommendations**: 30GB, fashion items with images
- **Instacart Market Basket**: 200MB, 3M+ orders, 200K users

See `scripts/DATASET_DOWNLOAD_INSTRUCTIONS.md` for full guide.

## 📊 Data Format

All sources convert to the same format:

**products.csv:**
```csv
id,name,description,price,tags,popularity
1,iPhone 13 Pro,Latest Apple smartphone,899,electronics,phone,apple,95
```

**users.csv:**
```csv
id,name
1,Emma Smith
```

**interactions.csv:**
```csv
id,user_id,product_id,event,timestamp
1,1,5,view,2025-01-15T10:30:00Z
2,1,5,add_to_cart,2025-01-15T10:32:00Z
3,1,5,purchase,2025-01-15T10:35:00Z
```

## 🚀 Quick Start

1. **Fetch real data:**
   ```bash
   python scripts/fetch_real_products.py
   ```

2. **Start server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

3. **Import data:**
   ```bash
   curl -X POST http://localhost:8000/import-csv
   ```

4. **Get recommendations:**
   ```bash
   curl -X POST http://localhost:8000/recommendations \
     -H 'content-type: application/json' \
     -d '{"user_id": 1, "k": 5}'
   ```

5. **Or use the beautiful dashboard:**
   - Open http://localhost:8000/demo
   - Click "Load Sample Data" button
   - Click "Recommend for Alice" or "Recommend for Bob"

## 🎨 What Makes the Data Realistic?

**API-fetched products (fetch_real_products.py):**
- Real product names from actual e-commerce sites
- Accurate pricing
- Proper categories (electronics, fashion, beauty, etc.)
- User-category affinity (tech users browse electronics more)
- Realistic conversion funnel (60% views, 25% cart-adds, 15% purchases)

**Generated interactions:**
- Time-based spread (60 days)
- Budget-aware behavior
- Interest-based browsing
- Purchase patterns

---

**Bottom line:** Use `fetch_real_products.py` for the best demo experience with zero setup! 🚀
