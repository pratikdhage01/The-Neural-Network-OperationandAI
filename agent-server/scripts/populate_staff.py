"""
Populate staff collection with sample team members.
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


STAFF = [
    {
        "name": "Arjun Sharma",
        "role": "Order Manager",
        "phone": "+91 98765 11111",
        "email": "arjun@msme.com",
        "max_workload": 12,
        "skills": ["order_processing", "customer_service", "inventory_management"]
    },
    {
        "name": "Priya Patel",
        "role": "Inventory Specialist",
        "phone": "+91 98765 22222",
        "email": "priya@msme.com",
        "max_workload": 10,
        "skills": ["inventory_management", "stock_counting", "supplier_coordination"]
    },
    {
        "name": "Rahul Verma",
        "role": "Packaging & Shipping",
        "phone": "+91 98765 33333",
        "email": "rahul@msme.com",
        "max_workload": 15,
        "skills": ["packaging", "shipping", "quality_check"]
    },
    {
        "name": "Sneha Gupta",
        "role": "Customer Representative",
        "phone": "+91 98765 44444",
        "email": "sneha@msme.com",
        "max_workload": 8,
        "skills": ["customer_service", "complaint_handling", "order_tracking"]
    },
    {
        "name": "Vikram Singh",
        "role": "Supplier Coordinator",
        "phone": "+91 98765 55555",
        "email": "vikram@msme.com",
        "max_workload": 10,
        "skills": ["supplier_coordination", "procurement", "negotiation"]
    },
    {
        "name": "Meera Joshi",
        "role": "Quality Control",
        "phone": "+91 98765 66666",
        "email": "meera@msme.com",
        "max_workload": 12,
        "skills": ["quality_check", "product_inspection", "returns_handling"]
    },
    {
        "name": "Amit Kumar",
        "role": "Warehouse Assistant",
        "phone": "+91 98765 77777",
        "email": "amit@msme.com",
        "max_workload": 15,
        "skills": ["warehousing", "stock_organization", "inventory_management"]
    },
    {
        "name": "Kavita Reddy",
        "role": "Accounts & Billing",
        "phone": "+91 98765 88888",
        "email": "kavita@msme.com",
        "max_workload": 10,
        "skills": ["billing", "invoicing", "payment_tracking"]
    },
]


async def populate_staff():
    """Populate the staff collection with sample team members."""
    print(f"Connecting to MongoDB at {MONGODB_URI}...")
    client = AsyncIOMotorClient(MONGODB_URI, tlsCAFile=TLS_CA_FILE)
    db = client[DATABASE_NAME]
    staff_collection = db["staff"]
    
    # Clear existing staff (optional)
    existing_count = await staff_collection.count_documents({})
    if existing_count > 0:
        print(f"Found {existing_count} existing staff members. Clearing...")
        await staff_collection.delete_many({})
    
    # Add timestamps and defaults
    staff_with_defaults = []
    for staff in STAFF:
        staff_copy = staff.copy()
        staff_copy["created_at"] = datetime.utcnow()
        staff_copy["is_available"] = True
        staff_copy["current_workload"] = 0
        staff_copy["assigned_tasks"] = []
        staff_with_defaults.append(staff_copy)
    
    # Insert staff
    result = await staff_collection.insert_many(staff_with_defaults)
    
    print(f"\n✅ Successfully added {len(result.inserted_ids)} staff members!")
    
    # Print summary by role
    print("\nStaff Summary:")
    print("-" * 40)
    
    for staff in STAFF:
        print(f"  {staff['name']} - {staff['role']} (Max: {staff['max_workload']} tasks)")
    
    # Calculate total capacity
    total_capacity = sum(s["max_workload"] for s in STAFF)
    print(f"\nTotal Team Capacity: {total_capacity} tasks")
    
    client.close()
    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(populate_staff())
