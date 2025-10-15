import requests
import csv
import random
from pathlib import Path
from datetime import datetime, timedelta
import time


def fetch_fakestore_products():
    print("Fetching products from Fake Store API...")
    url = "https://fakestoreapi.com/products"
    response = requests.get(url)
    products_data = response.json()
    products = []
    for idx, item in enumerate(products_data, 1):
        category = item.get('category', 'general').replace(' ', ',').replace("'", '')
        products.append({
            'id': idx,
            'name': item['title'][:100],
            'description': item['description'][:200],
            'price': round(item['price'], 2),
            'tags': category,
            'popularity': random.randint(60, 95)
        })
    print(f"Fetched {len(products)} products")
    return products


def fetch_dummyjson_products():
    print("Fetching products from DummyJSON API...")
    products = []
    for skip in [0, 30, 60]:
        url = f"https://dummyjson.com/products?limit=30&skip={skip}"
        response = requests.get(url)
        data = response.json()
        for item in data.get('products', []):
            products.append({
                'id': item['id'],
                'name': item['title'],
                'description': item['description'][:200],
                'price': round(item['price'], 2),
                'tags': f"{item.get('category', 'general')},{item.get('brand', '')}".strip(','),
                'popularity': int(item.get('rating', 4) * 20)
            })
        time.sleep(0.5)
    print(f"Fetched {len(products)} products")
    return products


def generate_realistic_users(count=20):
    first_names = ['Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'Ethan', 'Sophia', 'Mason', 'Isabella', 'William',
                   'Mia', 'James', 'Charlotte', 'Benjamin', 'Amelia', 'Lucas', 'Harper', 'Henry', 'Evelyn', 'Alexander']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
                  'Anderson', 'Taylor', 'Thomas', 'Moore', 'Jackson', 'Martin', 'Lee', 'Thompson', 'White', 'Harris']
    users = []
    for i in range(1, count + 1):
        first = random.choice(first_names)
        last = random.choice(last_names)
        users.append({'id': i, 'name': f"{first} {last}"})
    return users


def generate_interactions(products, users, count=200):
    interactions = []
    base_date = datetime.now() - timedelta(days=60)
    user_preferences = {}
    for user in users:
        categories = set()
        for _ in range(random.randint(1, 3)):
            product = random.choice(products)
            categories.add(product['tags'].split(',')[0])
        user_preferences[user['id']] = list(categories)
    for i in range(1, count + 1):
        user = random.choice(users)
        if random.random() < 0.6 and user_preferences.get(user['id']):
            preferred_cat = random.choice(user_preferences[user['id']])
            matching = [p for p in products if preferred_cat in p['tags']]
            product = random.choice(matching) if matching else random.choice(products)
        else:
            product = random.choice(products)
        rand = random.random()
        if rand < 0.6:
            event = 'view'
        elif rand < 0.85:
            event = 'add_to_cart'
        else:
            event = 'purchase'
        timestamp = base_date + timedelta(days=random.randint(0, 60), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        interactions.append({
            'id': i,
            'user_id': user['id'],
            'product_id': product['id'],
            'event': event,
            'timestamp': timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
        })
    return interactions


def save_datasets():
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    print("Real Data Fetcher (Public APIs)")
    try:
        products = fetch_dummyjson_products()
    except Exception as e:
        print(f"DummyJSON failed: {e}")
        print("Trying Fake Store API...")
        products = fetch_fakestore_products()
    users = generate_realistic_users(20)
    interactions = generate_interactions(products, users, 200)
    print(f"Generated {len(users)} users")
    print(f"Generated {len(interactions)} interactions")
    with open(data_dir / 'products.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'name', 'description', 'price', 'tags', 'popularity'])
        writer.writeheader()
        writer.writerows(products)
    with open(data_dir / 'users.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'name'])
        writer.writeheader()
        writer.writerows(users)
    with open(data_dir / 'interactions.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'user_id', 'product_id', 'event', 'timestamp'])
        writer.writeheader()
        writer.writerows(interactions)
    print("Real data saved successfully")
    print(f"Location: {data_dir}")
    print(f"- products.csv ({len(products)} real products)")
    print(f"- users.csv ({len(users)} users)")
    print(f"- interactions.csv ({len(interactions)} interactions)")
    print("Next: Import into app")
    print("  curl -X POST http://localhost:8000/import-csv")


if __name__ == "__main__":
    save_datasets()
