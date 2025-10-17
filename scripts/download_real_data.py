import urllib.request
import json
import csv
import zipfile
import os
from pathlib import Path
import sys


def download_amazon_electronics():
    print("Downloading Amazon Electronics dataset...")
    url = "http://snap.stanford.edu/data/amazon/productGraph/categoryFiles/reviews_Electronics_5.json.gz"
    print("Note: This is a large dataset. For demo purposes, we'll use a sample.")
    print("Alternative: Use the H&M or Instacart datasets below for easier setup.\n")
    print("Dataset options:")
    print("1. Amazon Electronics (reviews & ratings) - Large")
    print("2. UCI Online Retail Dataset - Medium, CSV format")
    print("3. Instacart Orders Dataset - Medium, multiple CSVs")
    print("\nFor now, I recommend using the UCI Online Retail dataset.")


def download_uci_online_retail():
    print("Downloading UCI Online Retail Dataset...")
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"
    print(f"Downloading from: {url}")
    print("This dataset contains ~500K real transactions from 2010-2011")
    print("\nNote: This is an Excel file. You'll need to convert it to CSV.")
    print("Alternative: Use the preprocessed version below...")


def create_kaggle_download_instructions():
    instructions = """



1. **H&M Personalized Fashion Recommendations**
   - URL: https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations
   - Size: ~30GB (use sample for testing)
   - Contains: Real customer transactions, product data, images

2. **Brazilian E-Commerce Public Dataset by Olist**
   - URL: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
   - Size: ~50MB
   - Contains: 100K orders, product info, customer reviews

3. **Instacart Market Basket Analysis**
   - URL: https://www.kaggle.com/competitions/instacart-market-basket-analysis
   - Size: ~200MB
   - Contains: 3M+ orders from 200K+ users


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
   kaggle datasets download -d olistbr/brazilian-ecommerce -p ./data
   unzip ./data/brazilian-ecommerce.zip -d ./data/brazilian_ecom

   kaggle competitions download -c instacart-market-basket-analysis -p ./data
   ```


**UCI Online Retail Dataset:**
```bash
wget -O data/online_retail.csv "https://github.com/reisanar/datasets/raw/master/OnlineRetail.csv"
```


I've created a script that uses public CSV datasets:

```bash
python scripts/download_real_data.py --source public
```

---


Run the converter script to transform any dataset into our format:
```bash
python scripts/convert_dataset.py --input data/raw --output data/
```

This will create:
- products.csv
- users.csv
- interactions.csv
"""
    instructions_path = Path(__file__).parent / "DATASET_DOWNLOAD_INSTRUCTIONS.md"
    with open(instructions_path, "w") as f:
        f.write(instructions)
    print(f"Instructions saved to: {instructions_path}")
    return instructions_path


def download_public_sample():
    print("Downloading public e-commerce sample...")
    data_dir = Path(__file__).parent.parent / "data" / "raw"
    data_dir.mkdir(parents=True, exist_ok=True)
    sources = [
        {
            "name": "E-Commerce Events Dataset",
            "url": "https://www.dropbox.com/s/4m9xzq86k2yvzqx/ecommerce-events.csv?dl=1",
            "output": "ecommerce_events.csv",
            "description": "Real cosmetics shop behavior data (Oct 2019-Feb 2020)"
        },
        {
            "name": "Online Retail II (UCI)",
            "url": "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip",
            "output": "online_retail_ii.zip",
            "description": "UK retailer transactions (2009-2011)"
        },
        {
            "name": "Sample E-commerce Dataset",
            "url": "https://github.com/datasets/awesome-data/raw/master/ecommerce-behavior-data-from-multi-category-store/2019-Oct-sample.csv",
            "output": "ecommerce_sample.csv",
            "description": "Multi-category store sample"
        }
    ]
    for source in sources:
        try:
            output_path = data_dir / source["output"]
            print(f"\nTrying: {source['name']}")
            print(f"URL: {source['url']}")
            urllib.request.urlretrieve(source["url"], output_path)
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            if size_mb < 0.01:
                print(f"Download too small ({size_mb:.2f} MB), trying next source...")
                continue
            print(f"Downloaded successfully")
            print(f"   File: {output_path}")
            print(f"   Size: {size_mb:.2f} MB")
            print(f"   Description: {source['description']}")
            if output_path.suffix == '.zip':
                print(f"Extracting zip file...")
                with zipfile.ZipFile(output_path, 'r') as zip_ref:
                    zip_ref.extractall(data_dir)
                print(f"Extracted to {data_dir}")
            return output_path
        except Exception as e:
            print(f"Failed: {e}")
            continue
    print("All download attempts failed.")
    print("Please use Kaggle datasets (see instructions)")
    return None


def try_kaggle_download(data_dir):
    try:
        import subprocess
        print("Attempting Kaggle download...")
        print("Note: This requires Kaggle API credentials (~/.kaggle/kaggle.json)")
        result = subprocess.run([
            "kaggle", "datasets", "download", "-d", "olistbr/brazilian-ecommerce", "-p", str(data_dir)
        ], capture_output=True, text=True)
        if result.returncode == 0:
            print("Kaggle download successful")
            zip_path = data_dir / "brazilian-ecommerce.zip"
            if zip_path.exists():
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(data_dir)
                return zip_path
        else:
            print(f"Kaggle CLI not configured: {result.stderr}")
            return None
    except Exception as e:
        print(f"Kaggle download failed: {e}")
        return None


def main():
    print("=" * 60)
    print("Real E-Commerce Data Downloader")
    print("=" * 60)
    print()
    instructions_file = create_kaggle_download_instructions()
    print(f"See {instructions_file} for detailed instructions\n")
    print("Attempting to download public dataset (no auth required)...")
    result = download_public_sample()
    if result:
        print("\n" + "=" * 60)
        print("SUCCESS! Dataset downloaded.")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Convert the dataset to our format:")
        print("   python scripts/convert_dataset.py")
        print("\n2. Import into the app:")
        print("   curl -X POST http://localhost:8000/import-csv")
    else:
        print("\n" + "=" * 60)
        print("Public download failed.")
        print("=" * 60)
        print(f"\nPlease follow instructions in: {instructions_file}")
        print("Recommended: Brazilian E-Commerce dataset from Kaggle (50MB)")


if __name__ == "__main__":
    main()
