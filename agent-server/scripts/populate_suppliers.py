"""
Populate suppliers collection with sample suppliers.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
import certifi
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "msme_db")
TLS_CA_FILE = certifi.where()


SUPPLIERS = [
    # Jewelry Suppliers
    {
        "name": "Golden Touch Jewelry Suppliers",
        "contact_person": "Rajesh Mehta",
        "phone": "+91 98765 43210",
        "email": "rajesh@goldentouchjewels.com",
        "address": "Shop 15, Zaveri Bazaar, Mumbai 400002",
        "categories": ["jewelry"],
        "products_offered": [
            "Gold Plated Necklaces",
            "Silver Jewelry",
            "Kundan Sets",
            "Temple Jewelry"
        ],
        "avg_response_time_hours": 12,
        "reliability_score": 0.92
    },
    {
        "name": "Silver Palace Wholesale",
        "contact_person": "Anita Shah",
        "phone": "+91 98123 45678",
        "email": "anita@silverpalace.in",
        "address": "45, Silver Street, Jaipur 302001",
        "categories": ["jewelry"],
        "products_offered": [
            "Silver Anklets",
            "Oxidized Jewelry",
            "Brass Rings",
            "Pearl Earrings"
        ],
        "avg_response_time_hours": 8,
        "reliability_score": 0.88
    },
    
    # Kitchen Appliance Suppliers
    {
        "name": "Home Appliances Hub",
        "contact_person": "Vikram Singh",
        "phone": "+91 99876 54321",
        "email": "vikram@homeapplianceshub.com",
        "address": "Industrial Area Phase 2, Faridabad 121003",
        "categories": ["kitchen_appliances"],
        "products_offered": [
            "Mixer Grinders",
            "Toasters",
            "Electric Kettles",
            "Induction Cooktops"
        ],
        "avg_response_time_hours": 6,
        "reliability_score": 0.95
    },
    {
        "name": "Kitchen Tech Solutions",
        "contact_person": "Priya Sharma",
        "phone": "+91 98765 12345",
        "email": "priya@kitchentech.in",
        "address": "Sector 18, Noida 201301",
        "categories": ["kitchen_appliances"],
        "products_offered": [
            "Air Fryers",
            "Microwave Ovens",
            "Food Processors",
            "Coffee Makers"
        ],
        "avg_response_time_hours": 4,
        "reliability_score": 0.90
    },
    {
        "name": "Bharat Electronics Wholesale",
        "contact_person": "Suresh Kumar",
        "phone": "+91 97654 32109",
        "email": "suresh@bharatelec.com",
        "address": "Lamington Road, Mumbai 400004",
        "categories": ["kitchen_appliances"],
        "products_offered": [
            "Hand Mixers",
            "Rice Cookers",
            "Sandwich Makers",
            "Juicers"
        ],
        "avg_response_time_hours": 10,
        "reliability_score": 0.85
    },
    
    # Makeup Suppliers
    {
        "name": "Glamour Cosmetics Distributors",
        "contact_person": "Neha Kapoor",
        "phone": "+91 98111 22233",
        "email": "neha@glamourcos.com",
        "address": "Sadar Bazaar, Delhi 110006",
        "categories": ["makeup"],
        "products_offered": [
            "Lipsticks",
            "Foundations",
            "Mascaras",
            "Eyeshadow Palettes"
        ],
        "avg_response_time_hours": 8,
        "reliability_score": 0.91
    },
    {
        "name": "Beauty Essentials India",
        "contact_person": "Ritu Malhotra",
        "phone": "+91 99888 77766",
        "email": "ritu@beautyessentials.in",
        "address": "Commercial Street, Bangalore 560001",
        "categories": ["makeup"],
        "products_offered": [
            "Compact Powder",
            "Kajal",
            "Lip Gloss",
            "Blush",
            "Highlighters"
        ],
        "avg_response_time_hours": 6,
        "reliability_score": 0.88
    },
    {
        "name": "Cosmetics World Wholesale",
        "contact_person": "Aishwarya Patel",
        "phone": "+91 98222 33344",
        "email": "aishwarya@cosworld.com",
        "address": "Crawford Market, Mumbai 400001",
        "categories": ["makeup"],
        "products_offered": [
            "Setting Spray",
            "Concealer",
            "Primer",
            "Eyeliner",
            "Contour Kits"
        ],
        "avg_response_time_hours": 12,
        "reliability_score": 0.86
    },
    
    # Multi-category Supplier
    {
        "name": "Universal Trading Company",
        "contact_person": "Amit Goel",
        "phone": "+91 98765 99999",
        "email": "amit@universaltrading.in",
        "address": "Karol Bagh, Delhi 110005",
        "categories": ["jewelry", "kitchen_appliances", "makeup"],
        "products_offered": [
            "Various Jewelry Items",
            "Small Kitchen Appliances",
            "Makeup Accessories"
        ],
        "avg_response_time_hours": 24,
        "reliability_score": 0.80
    },
]


async def populate_suppliers():
    """Populate the suppliers collection with sample data."""
    print(f"Connecting to MongoDB at {MONGODB_URI}...")
    client = AsyncIOMotorClient(MONGODB_URI, tlsCAFile=TLS_CA_FILE)
    db = client[DATABASE_NAME]
    suppliers_collection = db["suppliers"]
    
    # Clear existing suppliers (optional)
    existing_count = await suppliers_collection.count_documents({})
    if existing_count > 0:
        print(f"Found {existing_count} existing suppliers. Clearing...")
        await suppliers_collection.delete_many({})
    
    # Add timestamps and active status
    suppliers_with_timestamps = []
    for supplier in SUPPLIERS:
        supplier_copy = supplier.copy()
        supplier_copy["created_at"] = datetime.utcnow()
        supplier_copy["is_active"] = True
        suppliers_with_timestamps.append(supplier_copy)
    
    # Insert suppliers
    result = await suppliers_collection.insert_many(suppliers_with_timestamps)
    
    print(f"\n✅ Successfully added {len(result.inserted_ids)} suppliers!")
    
    # Print summary by category
    print("\nSuppliers Summary:")
    print("-" * 40)
    
    for category in ["jewelry", "kitchen_appliances", "makeup"]:
        count = await suppliers_collection.count_documents({"categories": category})
        category_name = category.replace("_", " ").title()
        print(f"  {category_name}: {count} suppliers")
    
    client.close()
    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(populate_suppliers())
