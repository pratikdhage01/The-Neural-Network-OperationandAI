"""
Populate inventory with sample products.
Categories: Jewelry, Kitchen Appliances, Makeup
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


# Sample inventory data
PRODUCTS = [
    # ============ JEWELRY ============
    {
        "name": "Gold Plated Necklace Set",
        "category": "jewelry",
        "description": "Elegant gold plated necklace with matching earrings, perfect for festive occasions",
        "price": 2499.00,
        "quantity": 15,
        "low_stock_threshold": 5
    },
    {
        "name": "Silver Anklet Pair",
        "category": "jewelry",
        "description": "Traditional silver anklets with delicate bell charms",
        "price": 899.00,
        "quantity": 25,
        "low_stock_threshold": 8
    },
    {
        "name": "Pearl Drop Earrings",
        "category": "jewelry",
        "description": "Classic freshwater pearl drop earrings with gold hooks",
        "price": 1299.00,
        "quantity": 20,
        "low_stock_threshold": 5
    },
    {
        "name": "Diamond Studded Ring",
        "category": "jewelry",
        "description": "Sterling silver ring with cubic zirconia stones",
        "price": 1899.00,
        "quantity": 12,
        "low_stock_threshold": 4
    },
    {
        "name": "Kundan Choker Set",
        "category": "jewelry",
        "description": "Traditional Kundan choker necklace with earrings for weddings",
        "price": 4999.00,
        "quantity": 8,
        "low_stock_threshold": 3
    },
    {
        "name": "Rose Gold Bracelet",
        "category": "jewelry",
        "description": "Minimalist rose gold plated bracelet with heart charm",
        "price": 699.00,
        "quantity": 30,
        "low_stock_threshold": 10
    },
    {
        "name": "Oxidized Silver Jhumkas",
        "category": "jewelry",
        "description": "Traditional oxidized silver jhumka earrings with mirror work",
        "price": 549.00,
        "quantity": 35,
        "low_stock_threshold": 10
    },
    {
        "name": "Temple Gold Necklace",
        "category": "jewelry",
        "description": "South Indian temple design gold plated necklace",
        "price": 3499.00,
        "quantity": 6,
        "low_stock_threshold": 3
    },
    {
        "name": "Crystal Tennis Bracelet",
        "category": "jewelry",
        "description": "Sparkling crystal tennis bracelet for party wear",
        "price": 1599.00,
        "quantity": 18,
        "low_stock_threshold": 5
    },
    {
        "name": "Antique Brass Ring Set",
        "category": "jewelry",
        "description": "Set of 5 stackable antique brass rings with gemstones",
        "price": 799.00,
        "quantity": 22,
        "low_stock_threshold": 7
    },

    # ============ KITCHEN APPLIANCES ============
    {
        "name": "Hand Mixer 300W",
        "category": "kitchen_appliances",
        "description": "Powerful 300W hand mixer with 5 speed settings and beaters",
        "price": 1299.00,
        "quantity": 20,
        "low_stock_threshold": 5
    },
    {
        "name": "Pop-up Toaster 2-Slice",
        "category": "kitchen_appliances",
        "description": "Stainless steel 2-slice toaster with browning control",
        "price": 1499.00,
        "quantity": 15,
        "low_stock_threshold": 4
    },
    {
        "name": "Mixer Grinder 750W",
        "category": "kitchen_appliances",
        "description": "Heavy duty mixer grinder with 3 jars for grinding and blending",
        "price": 3999.00,
        "quantity": 12,
        "low_stock_threshold": 4
    },
    {
        "name": "Digital Air Fryer 4.5L",
        "category": "kitchen_appliances",
        "description": "Large capacity digital air fryer with 8 preset cooking modes",
        "price": 5999.00,
        "quantity": 10,
        "low_stock_threshold": 3
    },
    {
        "name": "Electric Kettle 1.5L",
        "category": "kitchen_appliances",
        "description": "Fast boiling electric kettle with auto shut-off",
        "price": 799.00,
        "quantity": 30,
        "low_stock_threshold": 8
    },
    {
        "name": "Sandwich Maker",
        "category": "kitchen_appliances",
        "description": "Non-stick sandwich maker for grilled sandwiches",
        "price": 999.00,
        "quantity": 25,
        "low_stock_threshold": 6
    },
    {
        "name": "Induction Cooktop 2000W",
        "category": "kitchen_appliances",
        "description": "Energy efficient induction cooktop with touch controls",
        "price": 2499.00,
        "quantity": 18,
        "low_stock_threshold": 5
    },
    {
        "name": "Juicer Mixer Grinder",
        "category": "kitchen_appliances",
        "description": "Versatile juicer mixer grinder with 4 jars",
        "price": 4499.00,
        "quantity": 8,
        "low_stock_threshold": 3
    },
    {
        "name": "Electric Rice Cooker 1.8L",
        "category": "kitchen_appliances",
        "description": "Automatic rice cooker with keep warm function",
        "price": 1899.00,
        "quantity": 14,
        "low_stock_threshold": 4
    },
    {
        "name": "Coffee Maker 6-Cup",
        "category": "kitchen_appliances",
        "description": "Drip coffee maker with programmable timer",
        "price": 2299.00,
        "quantity": 10,
        "low_stock_threshold": 3
    },
    {
        "name": "Microwave Oven 20L",
        "category": "kitchen_appliances",
        "description": "Solo microwave oven with defrost function",
        "price": 5499.00,
        "quantity": 6,
        "low_stock_threshold": 2
    },
    {
        "name": "Food Processor 600W",
        "category": "kitchen_appliances",
        "description": "Multi-function food processor with slicing and dicing attachments",
        "price": 3299.00,
        "quantity": 9,
        "low_stock_threshold": 3
    },

    # ============ MAKEUP ============
    {
        "name": "Matte Lipstick - Red Velvet",
        "category": "makeup",
        "description": "Long-lasting matte lipstick in classic red shade",
        "price": 399.00,
        "quantity": 50,
        "low_stock_threshold": 15
    },
    {
        "name": "Liquid Foundation - Natural Beige",
        "category": "makeup",
        "description": "Full coverage liquid foundation for medium skin tone",
        "price": 699.00,
        "quantity": 35,
        "low_stock_threshold": 10
    },
    {
        "name": "Waterproof Mascara - Black",
        "category": "makeup",
        "description": "Volumizing waterproof mascara for dramatic lashes",
        "price": 449.00,
        "quantity": 40,
        "low_stock_threshold": 12
    },
    {
        "name": "Eyeshadow Palette - Nude Collection",
        "category": "makeup",
        "description": "12 shade eyeshadow palette with matte and shimmer finishes",
        "price": 899.00,
        "quantity": 25,
        "low_stock_threshold": 8
    },
    {
        "name": "Compact Powder - Fair",
        "category": "makeup",
        "description": "Oil-control compact powder for fair skin",
        "price": 349.00,
        "quantity": 45,
        "low_stock_threshold": 12
    },
    {
        "name": "Kajal Pencil - Intense Black",
        "category": "makeup",
        "description": "Smudge-proof kajal pencil for defined eyes",
        "price": 199.00,
        "quantity": 60,
        "low_stock_threshold": 20
    },
    {
        "name": "Lip Gloss - Pink Shine",
        "category": "makeup",
        "description": "High-shine lip gloss with subtle pink tint",
        "price": 299.00,
        "quantity": 40,
        "low_stock_threshold": 12
    },
    {
        "name": "Blush Palette - Rosy Cheeks",
        "category": "makeup",
        "description": "4 shade blush palette with natural and bold colors",
        "price": 549.00,
        "quantity": 30,
        "low_stock_threshold": 8
    },
    {
        "name": "Setting Spray - Long Wear",
        "category": "makeup",
        "description": "Makeup setting spray for 16-hour wear",
        "price": 499.00,
        "quantity": 28,
        "low_stock_threshold": 8
    },
    {
        "name": "Concealer - Medium",
        "category": "makeup",
        "description": "Full coverage concealer for dark circles and blemishes",
        "price": 399.00,
        "quantity": 35,
        "low_stock_threshold": 10
    },
    {
        "name": "Primer - Pore Minimizing",
        "category": "makeup",
        "description": "Silicone-based primer for smooth makeup application",
        "price": 599.00,
        "quantity": 22,
        "low_stock_threshold": 6
    },
    {
        "name": "Eyeliner - Liquid Black",
        "category": "makeup",
        "description": "Precision tip liquid eyeliner for winged looks",
        "price": 349.00,
        "quantity": 38,
        "low_stock_threshold": 10
    },
    {
        "name": "Highlighter Stick - Golden Glow",
        "category": "makeup",
        "description": "Cream highlighter stick for luminous skin",
        "price": 449.00,
        "quantity": 25,
        "low_stock_threshold": 7
    },
    {
        "name": "Contour Kit - Medium to Dark",
        "category": "makeup",
        "description": "Complete contour kit with highlight and contour shades",
        "price": 799.00,
        "quantity": 18,
        "low_stock_threshold": 5
    },
    {
        "name": "Eyebrow Pencil - Brown",
        "category": "makeup",
        "description": "Retractable eyebrow pencil with spoolie brush",
        "price": 249.00,
        "quantity": 45,
        "low_stock_threshold": 12
    },
]


async def populate_inventory():
    """Populate the inventory collection with sample products."""
    print(f"Connecting to MongoDB at {MONGODB_URI}...")
    client = AsyncIOMotorClient(MONGODB_URI, tlsCAFile=TLS_CA_FILE)
    db = client[DATABASE_NAME]
    products_collection = db["products"]
    
    # Clear existing products (optional)
    existing_count = await products_collection.count_documents({})
    if existing_count > 0:
        print(f"Found {existing_count} existing products. Clearing...")
        await products_collection.delete_many({})
    
    # Add timestamps to products
    products_with_timestamps = []
    for product in PRODUCTS:
        product_copy = product.copy()
        product_copy["created_at"] = datetime.utcnow()
        product_copy["updated_at"] = datetime.utcnow()
        products_with_timestamps.append(product_copy)
    
    # Insert products
    result = await products_collection.insert_many(products_with_timestamps)
    
    print(f"\n✅ Successfully added {len(result.inserted_ids)} products to inventory!")
    
    # Print summary by category
    print("\nInventory Summary:")
    print("-" * 40)
    
    for category in ["jewelry", "kitchen_appliances", "makeup"]:
        count = await products_collection.count_documents({"category": category})
        pipeline = [
            {"$match": {"category": category}},
            {"$group": {"_id": None, "total_value": {"$sum": {"$multiply": ["$price", "$quantity"]}}}}
        ]
        value_result = await products_collection.aggregate(pipeline).to_list(1)
        total_value = value_result[0]["total_value"] if value_result else 0
        
        category_name = category.replace("_", " ").title()
        print(f"  {category_name}: {count} products, ₹{total_value:,.2f} total value")
    
    client.close()
    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(populate_inventory())
