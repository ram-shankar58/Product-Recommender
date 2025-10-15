import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

PRODUCTS = [
    {"id": 1, "name": "iPhone 15 Pro", "description": "Latest Apple smartphone with A17 chip", "price": 999, "tags": "electronics,phone,apple", "popularity": 95},
    {"id": 2, "name": "Samsung Galaxy S24", "description": "Flagship Android phone", "price": 899, "tags": "electronics,phone,samsung,android", "popularity": 90},
    {"id": 3, "name": "Sony WH-1000XM5", "description": "Premium noise-cancelling headphones", "price": 399, "tags": "electronics,audio,headphones,sony", "popularity": 88},
    {"id": 4, "name": "MacBook Pro 14", "description": "M3 chip, 16GB RAM, professional laptop", "price": 1999, "tags": "electronics,laptop,apple,computer", "popularity": 92},
    {"id": 5, "name": "iPad Air", "description": "10.9-inch tablet for work and play", "price": 599, "tags": "electronics,tablet,apple", "popularity": 85},
    {"id": 6, "name": "AirPods Pro 2", "description": "Active noise cancellation earbuds", "price": 249, "tags": "electronics,audio,earbuds,apple", "popularity": 93},
    {"id": 7, "name": "Dell XPS 15", "description": "High-performance Windows laptop", "price": 1799, "tags": "electronics,laptop,dell,computer,windows", "popularity": 82},
    {"id": 8, "name": "LG OLED TV 55\"", "description": "4K OLED smart television", "price": 1499, "tags": "electronics,tv,lg,oled", "popularity": 87},
    {"id": 9, "name": "Nike Air Max Running Shoes", "description": "Comfortable running shoes", "price": 140, "tags": "fitness,running,shoes,nike", "popularity": 89},
    {"id": 10, "name": "Lululemon Yoga Mat", "description": "Premium non-slip yoga mat", "price": 78, "tags": "fitness,yoga,mat,lululemon", "popularity": 84},
    {"id": 11, "name": "Bowflex Adjustable Dumbbells", "description": "5-52.5 lbs per dumbbell", "price": 349, "tags": "fitness,strength,weights,bowflex", "popularity": 86},
    {"id": 12, "name": "Fitbit Charge 6", "description": "Advanced fitness tracker", "price": 159, "tags": "fitness,tracker,wearable,fitbit", "popularity": 81},
    {"id": 13, "name": "Adidas Ultraboost", "description": "Energy-returning running shoes", "price": 180, "tags": "fitness,running,shoes,adidas", "popularity": 88},
    {"id": 14, "name": "Hydro Flask 32oz", "description": "Insulated water bottle", "price": 45, "tags": "fitness,hydration,bottle", "popularity": 79},
    {"id": 15, "name": "Ninja Air Fryer", "description": "6-quart air fryer with multiple functions", "price": 119, "tags": "home,kitchen,appliance,ninja", "popularity": 91},
    {"id": 16, "name": "Vitamix Blender", "description": "Professional-grade blender", "price": 449, "tags": "home,kitchen,appliance,vitamix", "popularity": 85},
    {"id": 17, "name": "Instant Pot Duo", "description": "7-in-1 electric pressure cooker", "price": 89, "tags": "home,kitchen,appliance,instantpot", "popularity": 90},
    {"id": 18, "name": "Dyson V15 Vacuum", "description": "Cordless stick vacuum cleaner", "price": 649, "tags": "home,cleaning,appliance,dyson", "popularity": 87},
    {"id": 19, "name": "Nespresso Machine", "description": "Original espresso coffee maker", "price": 199, "tags": "home,kitchen,coffee,nespresso", "popularity": 86},
    {"id": 20, "name": "Ray-Ban Aviator Sunglasses", "description": "Classic aviator style", "price": 154, "tags": "fashion,sunglasses,rayban,accessories", "popularity": 83},
    {"id": 21, "name": "Fossil Smartwatch", "description": "Hybrid smartwatch with classic design", "price": 195, "tags": "fashion,watch,fossil,wearable", "popularity": 78},
    {"id": 22, "name": "North Face Backpack", "description": "30L outdoor daypack", "price": 89, "tags": "fashion,backpack,northface,outdoor", "popularity": 84},
    {"id": 23, "name": "Levi's 511 Jeans", "description": "Slim fit denim jeans", "price": 69, "tags": "fashion,clothing,jeans,levis", "popularity": 80},
    {"id": 24, "name": "Patagonia Fleece Jacket", "description": "Warm outdoor fleece", "price": 129, "tags": "fashion,clothing,jacket,patagonia,outdoor", "popularity": 86},
    {"id": 25, "name": "Kindle Paperwhite", "description": "Waterproof e-reader with backlight", "price": 139, "tags": "books,ereader,amazon,kindle", "popularity": 88},
    {"id": 26, "name": "Atomic Habits Book", "description": "Bestselling self-improvement book", "price": 16, "tags": "books,selfhelp,reading", "popularity": 92},
    {"id": 27, "name": "Udemy Pro Subscription", "description": "Annual learning platform access", "price": 199, "tags": "learning,online,courses,udemy", "popularity": 76},
    {"id": 28, "name": "PlayStation 5", "description": "Next-gen gaming console", "price": 499, "tags": "gaming,console,playstation,sony", "popularity": 94},
    {"id": 29, "name": "Xbox Series X", "description": "4K gaming console", "price": 499, "tags": "gaming,console,xbox,microsoft", "popularity": 91},
    {"id": 30, "name": "Nintendo Switch OLED", "description": "Portable gaming console", "price": 349, "tags": "gaming,console,nintendo,portable", "popularity": 89},
]

USER_PERSONAS = [
    {"id": 1, "name": "Sarah Chen", "type": "tech_enthusiast", "budget": "high", "interests": ["electronics", "apple", "audio"]},
    {"id": 2, "name": "Mike Johnson", "type": "fitness_buff", "budget": "medium", "interests": ["fitness", "running", "health"]},
    {"id": 3, "name": "Emma Rodriguez", "type": "home_chef", "budget": "medium", "interests": ["kitchen", "cooking", "appliance"]},
    {"id": 4, "name": "David Kim", "type": "gamer", "budget": "high", "interests": ["gaming", "console", "electronics"]},
    {"id": 5, "name": "Lisa Anderson", "type": "wellness_seeker", "budget": "high", "interests": ["fitness", "yoga", "wellness"]},
    {"id": 6, "name": "James Taylor", "type": "outdoor_adventurer", "budget": "medium", "interests": ["outdoor", "hiking", "adventure"]},
    {"id": 7, "name": "Priya Patel", "type": "bookworm", "budget": "low", "interests": ["books", "learning", "reading"]},
    {"id": 8, "name": "Alex Martinez", "type": "fashion_conscious", "budget": "medium", "interests": ["fashion", "clothing", "style"]},
    {"id": 9, "name": "Rachel Green", "type": "smart_home_enthusiast", "budget": "high", "interests": ["home", "electronics", "smart"]},
    {"id": 10, "name": "Tom Wilson", "type": "budget_shopper", "budget": "low", "interests": ["deals", "value", "practical"]},
]


def generate_interactions():
    interactions = []
    interaction_id = 1
    base_date = datetime.now() - timedelta(days=90)
    for user in USER_PERSONAS:
        user_id = user["id"]
        interests = user["interests"]
        budget = user["budget"]
        matching_products = []
        for product in PRODUCTS:
            product_tags = product["tags"].lower().split(",")
            if any(interest.lower() in product_tags for interest in interests):
                matching_products.append(product)
        all_products = matching_products + random.sample([p for p in PRODUCTS if p not in matching_products], min(5, len(PRODUCTS) - len(matching_products)))
        num_interactions = random.randint(5, 15)
        user_timeline = sorted([base_date + timedelta(days=random.randint(0, 90)) for _ in range(num_interactions)])
        for timestamp in user_timeline:
            if matching_products and random.random() < 0.7:
                product = random.choice(matching_products)
            else:
                product = random.choice(all_products)
            if budget == "low" and product["price"] > 200:
                if random.random() < 0.7:
                    continue
            rand = random.random()
            if rand < 0.5:
                event = "view"
            elif rand < 0.8:
                event = "add_to_cart"
            else:
                event = "purchase"
            interactions.append({"id": interaction_id, "user_id": user_id, "product_id": product["id"], "event": event, "timestamp": timestamp.isoformat() + "Z"})
            interaction_id += 1
    return interactions


def save_data():
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    with open(data_dir / "products.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "description", "price", "tags", "popularity"])
        writer.writeheader()
        writer.writerows(PRODUCTS)
    with open(data_dir / "users.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name"])
        writer.writeheader()
        writer.writerows([{"id": u["id"], "name": u["name"]} for u in USER_PERSONAS])
    interactions = generate_interactions()
    with open(data_dir / "interactions.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "user_id", "product_id", "event", "timestamp"])
        writer.writeheader()
        writer.writerows(interactions)
    print(f"Generated realistic data:")
    print(f"   - {len(PRODUCTS)} products")
    print(f"   - {len(USER_PERSONAS)} users with personas")
    print(f"   - {len(interactions)} interactions")
    print(f"Data saved to: {data_dir}")


if __name__ == "__main__":
    save_data()
