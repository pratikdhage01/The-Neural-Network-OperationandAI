"""
Populate all collections at once.
"""

import asyncio
from populate_inventory import populate_inventory
from populate_suppliers import populate_suppliers
from populate_staff import populate_staff


async def populate_all():
    """Populate all collections."""
    print("=" * 50)
    print("POPULATING MSME DATABASE")
    print("=" * 50)
    
    print("\n📦 Populating Inventory...")
    print("-" * 50)
    await populate_inventory()
    
    print("\n🏭 Populating Suppliers...")
    print("-" * 50)
    await populate_suppliers()
    
    print("\n👥 Populating Staff...")
    print("-" * 50)
    await populate_staff()
    
    print("\n" + "=" * 50)
    print("✅ ALL DATA POPULATED SUCCESSFULLY!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(populate_all())
