
# 🎯 How to Download Real E-commerce Datasets

## Option 1: Kaggle Datasets (Recommended)

### Best Datasets for Product Recommendations:

1. **H&M Personalized Fashion Recommendations**
   - URL: https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations
   - Size: ~30GB (use sample for testing)
   - Contains: Real customer transactions, product data, images
   
2. **Brazilian E-Commerce Public Dataset by Olist**
   - URL: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
   - Size: ~50MB
   - Contains: 100K orders, product info, customer reviews
   - ✅ Perfect size for this project!

3. **Instacart Market Basket Analysis**
   - URL: https://www.kaggle.com/competitions/instacart-market-basket-analysis
   - Size: ~200MB
   - Contains: 3M+ orders from 200K+ users

### Steps to Download from Kaggle:

1. **Install Kaggle CLI:**
   ```bash
   pip install kaggle
   ```

2. **Get API credentials:**
   - Go to https://www.kaggle.com/settings
   - Click "Create New API Token"
   - Save kaggle.json to ~/.kaggle/

3. **Download dataset:**
   ```bash
   # Brazilian E-Commerce (Recommended - smallest & complete)
   kaggle datasets download -d olistbr/brazilian-ecommerce -p ./data
   unzip ./data/brazilian-ecommerce.zip -d ./data/brazilian_ecom
   
   # OR Instacart
   kaggle competitions download -c instacart-market-basket-analysis -p ./data
   ```

## Option 2: UCI Repository (No Auth Required)

**UCI Online Retail Dataset:**
```bash
# Download CSV version
wget -O data/online_retail.csv "https://github.com/reisanar/datasets/raw/master/OnlineRetail.csv"
```

## Option 3: Direct CSV Downloads (Easiest)

I've created a script that uses public CSV datasets:

```bash
python scripts/download_real_data.py --source public
```

---

## After Download:

Run the converter script to transform any dataset into our format:
```bash
python scripts/convert_dataset.py --input data/raw --output data/
```

This will create:
- products.csv
- users.csv  
- interactions.csv
