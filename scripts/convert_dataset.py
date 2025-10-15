"""
Convert external datasets to our format (products.csv, users.csv, interactions.csv).
Supports: UCI Online Retail, Kaggle datasets, and custom formats.
"""
import pandas as pd
import csv
from pathlib import Path
from datetime import datetime
import hashlib

def convert_ecommerce_events(input_path: Path, output_dir: Path):
    """
    Convert E-Commerce Events dataset (cosmetics shop).
    Columns: event_time, event_type, product_id, category_id, category_code, brand, price, user_id, user_session
    """
    print("📊 Converting E-Commerce Events dataset...")
    
    # Read the dataset
    df = pd.read_csv(input_path)
    
    # Clean data
    df = df.dropna(subset=['user_id', 'product_id', 'price'])
    df = df[df['price'] > 0]
    
    print(f"Loaded {len(df)} events")
    
    # Create products.csv
    products = df[['product_id', 'brand', 'category_code', 'price']].drop_duplicates('product_id')
    products = products.rename(columns={
        'product_id': 'id',
        'brand': 'name',
        'price': 'price'
    })
    
    # Create better names from category and brand
    products['name'] = products.apply(
        lambda x: f"{x['name'] if pd.notna(x['name']) else 'Product'} {str(x['category_code']).split('.')[-1] if pd.notna(x['category_code']) else ''}".strip(),
        axis=1
    )
    products['description'] = products['category_code'].fillna('cosmetics product')
    
    # Tags from category
    def extract_category_tags(cat):
        if pd.isna(cat):
            return 'cosmetics'
        parts = str(cat).split('.')
        return ','.join([p for p in parts if p])[:100]  # Limit length
    
    products['tags'] = products['category_code'].apply(extract_category_tags)
    
    # Calculate popularity from event counts
    event_counts = df.groupby('product_id').size().to_dict()
    products['popularity'] = products['id'].map(lambda x: min(100, int(event_counts.get(x, 0) / 10)))
    
    # Sample products (keep top 100 by popularity)
    products = products.nlargest(100, 'popularity').reset_index(drop=True)
    products['id'] = products.index + 1
    product_id_map = dict(zip(products.index, products['id']))
    
    print(f"Created {len(products)} unique products")
    
    # Create users.csv
    users = df[['user_id']].drop_duplicates()
    users = users.rename(columns={'user_id': 'original_id'})
    users = users.reset_index(drop=True)
    users['id'] = users.index + 1
    users['name'] = users['id'].apply(lambda x: f"User_{x}")
    user_map = dict(zip(users['original_id'], users['id']))
    
    # Sample users (keep 50)
    users = users.head(50)
    user_map = dict(zip(users['original_id'], users['id']))
    
    print(f"Created {len(users)} unique users")
    
    # Create interactions.csv
    df['user_id_new'] = df['user_id'].map(user_map)
    df['product_id_new'] = df['product_id'].map(lambda x: product_id_map.get(x))
    
    # Filter only mapped products and users
    df = df.dropna(subset=['user_id_new', 'product_id_new'])
    
    # Map event types
    event_map = {
        'view': 'view',
        'cart': 'add_to_cart',
        'purchase': 'purchase',
        'remove_from_cart': 'view'
    }
    
    interactions = df[['user_id_new', 'product_id_new', 'event_type', 'event_time']].copy()
    interactions['event'] = interactions['event_type'].map(event_map).fillna('view')
    interactions['timestamp'] = pd.to_datetime(interactions['event_time']).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    interactions = interactions.rename(columns={
        'user_id_new': 'user_id',
        'product_id_new': 'product_id'
    })
    interactions = interactions[['user_id', 'product_id', 'event', 'timestamp']].reset_index(drop=True)
    
    # Sample for reasonable size (keep ~500 interactions)
    if len(interactions) > 500:
        interactions = interactions.sample(n=500, random_state=42).sort_values('timestamp')
    
    interactions['id'] = range(1, len(interactions) + 1)
    interactions['user_id'] = interactions['user_id'].astype(int)
    interactions['product_id'] = interactions['product_id'].astype(int)
    
    print(f"Created {len(interactions)} interactions")
    
    # Save CSV files
    output_dir.mkdir(parents=True, exist_ok=True)
    
    products[['id', 'name', 'description', 'price', 'tags', 'popularity']].to_csv(
        output_dir / 'products.csv', index=False
    )
    users[['id', 'name']].to_csv(
        output_dir / 'users.csv', index=False
    )
    interactions[['id', 'user_id', 'product_id', 'event', 'timestamp']].to_csv(
        output_dir / 'interactions.csv', index=False
    )
    
    print(f"\n✅ Conversion complete!")
    print(f"   Output directory: {output_dir}")
    print(f"   - products.csv ({len(products)} items)")
    print(f"   - users.csv ({len(users)} users)")
    print(f"   - interactions.csv ({len(interactions)} events)")


def convert_online_retail(input_path: Path, output_dir: Path):
    """
    Convert UCI Online Retail dataset.
    Columns: InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country
    """
    print("📊 Converting UCI Online Retail dataset...")
    
    # Read the dataset
    df = pd.read_csv(input_path, encoding='latin1')
    
    # Clean data
    df = df.dropna(subset=['CustomerID', 'Description'])
    df = df[df['Quantity'] > 0]
    df = df[df['UnitPrice'] > 0]
    df['CustomerID'] = df['CustomerID'].astype(int)
    
    print(f"Loaded {len(df)} transactions")
    
    # Create products.csv
    products = df[['StockCode', 'Description', 'UnitPrice']].drop_duplicates('StockCode')
    products = products.rename(columns={
        'StockCode': 'id',
        'Description': 'name',
        'UnitPrice': 'price'
    })
    products['description'] = products['name']
    
    # Generate tags from product names (simple keyword extraction)
    def extract_tags(name):
        words = str(name).lower().split()
        # Common product keywords
        keywords = [w for w in words if len(w) > 3 and w not in ['with', 'from', 'this', 'that']]
        return ','.join(keywords[:5]) if keywords else 'general'
    
    products['tags'] = products['name'].apply(extract_tags)
    
    # Calculate popularity from sales
    sales_count = df.groupby('StockCode')['Quantity'].sum().to_dict()
    products['popularity'] = products['id'].map(lambda x: min(100, int(sales_count.get(x, 0) / 10)))
    
    # Renumber IDs sequentially
    products = products.reset_index(drop=True)
    products['id'] = products.index + 1
    product_map = dict(zip(products['id'].index, products['id']))
    
    print(f"Created {len(products)} unique products")
    
    # Create users.csv
    users = df[['CustomerID']].drop_duplicates()
    users = users.rename(columns={'CustomerID': 'original_id'})
    users = users.reset_index(drop=True)
    users['id'] = users.index + 1
    users['name'] = users['id'].apply(lambda x: f"Customer_{x}")
    user_map = dict(zip(users['original_id'], users['id']))
    
    print(f"Created {len(users)} unique users")
    
    # Create interactions.csv
    df['user_id'] = df['CustomerID'].map(user_map)
    df['product_id'] = df.index.map(lambda x: product_map.get(x % len(products), 1))
    
    # Map quantity to event types (heuristic)
    def quantity_to_event(qty):
        if qty >= 10:
            return 'purchase'
        elif qty >= 3:
            return 'add_to_cart'
        else:
            return 'view'
    
    interactions = df[['user_id', 'product_id', 'Quantity', 'InvoiceDate']].copy()
    interactions['event'] = interactions['Quantity'].apply(quantity_to_event)
    interactions['timestamp'] = pd.to_datetime(interactions['InvoiceDate']).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    interactions = interactions[['user_id', 'product_id', 'event', 'timestamp']].reset_index(drop=True)
    interactions['id'] = interactions.index + 1
    
    # Sample for reasonable size (keep ~1000 interactions)
    if len(interactions) > 1000:
        interactions = interactions.sample(n=1000, random_state=42).sort_values('timestamp')
        interactions['id'] = range(1, len(interactions) + 1)
    
    print(f"Created {len(interactions)} interactions")
    
    # Save CSV files
    output_dir.mkdir(parents=True, exist_ok=True)
    
    products[['id', 'name', 'description', 'price', 'tags', 'popularity']].to_csv(
        output_dir / 'products.csv', index=False
    )
    users[['id', 'name']].to_csv(
        output_dir / 'users.csv', index=False
    )
    interactions[['id', 'user_id', 'product_id', 'event', 'timestamp']].to_csv(
        output_dir / 'interactions.csv', index=False
    )
    
    print(f"\n✅ Conversion complete!")
    print(f"   Output directory: {output_dir}")
    print(f"   - products.csv ({len(products)} items)")
    print(f"   - users.csv ({len(users)} users)")
    print(f"   - interactions.csv ({len(interactions)} events)")


def convert_brazilian_ecommerce(input_dir: Path, output_dir: Path):
    """
    Convert Kaggle Brazilian E-Commerce dataset (Olist).
    Multiple CSV files: olist_products, olist_customers, olist_order_items, etc.
    """
    print("📊 Converting Brazilian E-Commerce dataset...")
    
    # Read main files
    products_df = pd.read_csv(input_dir / 'olist_products_dataset.csv')
    orders_df = pd.read_csv(input_dir / 'olist_orders_dataset.csv')
    items_df = pd.read_csv(input_dir / 'olist_order_items_dataset.csv')
    customers_df = pd.read_csv(input_dir / 'olist_customers_dataset.csv')
    
    # Process products
    products = products_df[['product_id', 'product_category_name']].dropna()
    products['name'] = products['product_category_name'].str.replace('_', ' ').str.title()
    products['price'] = items_df.groupby('product_id')['price'].mean().reindex(products['product_id']).values
    products = products.dropna(subset=['price'])
    products['description'] = products['name']
    products['tags'] = products['product_category_name']
    products = products.reset_index(drop=True)
    products['id'] = products.index + 1
    products['popularity'] = 50  # Default
    
    # Process users
    users = customers_df[['customer_id', 'customer_unique_id']].drop_duplicates('customer_unique_id')
    users = users.reset_index(drop=True)
    users['id'] = users.index + 1
    users['name'] = users['id'].apply(lambda x: f"Customer_{x}")
    
    # Process interactions
    # Join orders with items and customers
    interactions = items_df.merge(orders_df[['order_id', 'customer_id', 'order_purchase_timestamp']], on='order_id')
    interactions['event'] = 'purchase'  # All are purchases in this dataset
    interactions['timestamp'] = pd.to_datetime(interactions['order_purchase_timestamp']).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Sample
    if len(interactions) > 1000:
        interactions = interactions.sample(n=1000, random_state=42)
    
    interactions = interactions.reset_index(drop=True)
    interactions['id'] = interactions.index + 1
    
    print(f"Created {len(products)} products, {len(users)} users, {len(interactions)} interactions")
    
    # Save
    output_dir.mkdir(parents=True, exist_ok=True)
    products[['id', 'name', 'description', 'price', 'tags', 'popularity']].to_csv(
        output_dir / 'products.csv', index=False
    )
    users[['id', 'name']].to_csv(output_dir / 'users.csv', index=False)
    interactions[['id', 'user_id', 'product_id', 'event', 'timestamp']].to_csv(
        output_dir / 'interactions.csv', index=False
    )
    
    print(f"✅ Saved to {output_dir}")


def main():
    print("=" * 60)
    print("Dataset Converter for Product Recommender")
    print("=" * 60)
    
    data_dir = Path(__file__).parent.parent / "data"
    raw_dir = data_dir / "raw"
    
    # Check for downloaded data
    ecommerce_events = raw_dir / "ecommerce_events.csv"
    online_retail = raw_dir / "online_retail.csv"
    online_retail_zip = raw_dir / "online_retail_ii.zip"
    brazilian_ecom = raw_dir / "olist_products_dataset.csv"
    
    if ecommerce_events.exists():
        print(f"\n✓ Found: {ecommerce_events}")
        convert_ecommerce_events(ecommerce_events, data_dir)
    elif online_retail.exists():
        print(f"\n✓ Found: {online_retail}")
        convert_online_retail(online_retail, data_dir)
    elif online_retail_zip.exists():
        print(f"\n✓ Found: {online_retail_zip}")
        print("Extracting zip first...")
        import zipfile
        with zipfile.ZipFile(online_retail_zip, 'r') as zip_ref:
            zip_ref.extractall(raw_dir)
        # Find extracted CSV
        csv_files = list(raw_dir.glob("*.csv"))
        if csv_files:
            convert_online_retail(csv_files[0], data_dir)
        else:
            print("❌ No CSV found in zip")
    elif brazilian_ecom.exists():
        print(f"\n✓ Found Brazilian E-Commerce dataset")
        convert_brazilian_ecommerce(raw_dir, data_dir)
    else:
        print("\n❌ No dataset found in data/raw/")
        print("\nOptions:")
        print("1. Run: python scripts/download_real_data.py")
        print("2. Download manually from Kaggle and place in data/raw/")
        print("\nSee: scripts/DATASET_DOWNLOAD_INSTRUCTIONS.md")
        return
    
    print("\n" + "=" * 60)
    print("Next: Import into the app")
    print("=" * 60)
    print("curl -X POST http://localhost:8000/import-csv")


if __name__ == "__main__":
    main()
