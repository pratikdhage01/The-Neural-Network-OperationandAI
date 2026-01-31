"""
Inventory API routes - Product and inventory management.
"""

from fastapi import APIRouter, HTTPException
from database.connection import database
from database.models import ProductCreate, ProductCategory
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])


@router.get("")
async def list_inventory(
    category: str = None,
    low_stock_only: bool = False,
    limit: int = 100
):
    """List all inventory items."""
    products_collection = database.get_collection("products")
    
    query = {}
    if category:
        query["category"] = category
    
    if low_stock_only:
        query["$expr"] = {"$lte": ["$quantity", "$low_stock_threshold"]}
    
    products = await products_collection.find(query).sort("category", 1).to_list(limit)
    
    # Convert ObjectId to string
    for product in products:
        product["_id"] = str(product["_id"])
    
    return products


@router.get("/stats")
async def get_inventory_stats():
    """Get inventory statistics."""
    products_collection = database.get_collection("products")
    
    total = await products_collection.count_documents({})
    out_of_stock = await products_collection.count_documents({"quantity": 0})
    low_stock = await products_collection.count_documents({
        "$expr": {"$lte": ["$quantity", "$low_stock_threshold"]},
        "quantity": {"$gt": 0}
    })
    
    # By category
    pipeline = [
        {"$group": {
            "_id": "$category",
            "count": {"$sum": 1},
            "total_value": {"$sum": {"$multiply": ["$price", "$quantity"]}}
        }}
    ]
    category_stats = await products_collection.aggregate(pipeline).to_list(10)
    
    # Total inventory value
    value_pipeline = [
        {"$group": {"_id": None, "total": {"$sum": {"$multiply": ["$price", "$quantity"]}}}}
    ]
    value_result = await products_collection.aggregate(value_pipeline).to_list(1)
    total_value = value_result[0]["total"] if value_result else 0
    
    return {
        "total_products": total,
        "out_of_stock": out_of_stock,
        "low_stock": low_stock,
        "total_value": total_value,
        "by_category": {stat["_id"]: stat for stat in category_stats}
    }


@router.get("/low-stock")
async def get_low_stock():
    """Get items that are low or out of stock."""
    products_collection = database.get_collection("products")
    
    products = await products_collection.find({
        "$expr": {"$lte": ["$quantity", "$low_stock_threshold"]}
    }).sort("quantity", 1).to_list(50)
    
    for product in products:
        product["_id"] = str(product["_id"])
    
    return products


@router.get("/categories")
async def get_categories():
    """Get list of product categories with counts."""
    products_collection = database.get_collection("products")
    
    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}}
    ]
    
    categories = await products_collection.aggregate(pipeline).to_list(10)
    
    return [{"category": c["_id"], "count": c["count"]} for c in categories]


@router.get("/{product_id}")
async def get_product(product_id: str):
    """Get product details."""
    products_collection = database.get_collection("products")
    
    try:
        product = await products_collection.find_one({"_id": ObjectId(product_id)})
    except Exception:
        product = None
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product["_id"] = str(product["_id"])
    return product


@router.post("")
async def add_product(product: ProductCreate):
    """Add a new product."""
    products_collection = database.get_collection("products")
    
    product_doc = product.model_dump()
    product_doc["created_at"] = datetime.utcnow()
    product_doc["updated_at"] = datetime.utcnow()
    product_doc["category"] = product.category.value
    
    result = await products_collection.insert_one(product_doc)
    
    return {"id": str(result.inserted_id), "message": "Product added successfully"}


@router.put("/{product_id}")
async def update_product(product_id: str, updates: dict):
    """Update product details."""
    products_collection = database.get_collection("products")
    
    updates["updated_at"] = datetime.utcnow()
    
    # Convert category enum if present
    if "category" in updates and isinstance(updates["category"], ProductCategory):
        updates["category"] = updates["category"].value
    
    try:
        result = await products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": updates}
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": "Product updated successfully"}


@router.put("/{product_id}/stock")
async def update_stock(product_id: str, quantity_change: int):
    """Update product stock level."""
    products_collection = database.get_collection("products")
    
    try:
        result = await products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {
                "$inc": {"quantity": quantity_change},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check for low stock bottleneck
    from agents.inventory_agent import check_low_stock_bottlenecks
    await check_low_stock_bottlenecks()
    
    return {"message": f"Stock updated by {quantity_change}"}


@router.delete("/{product_id}")
async def delete_product(product_id: str):
    """Delete a product."""
    products_collection = database.get_collection("products")
    
    try:
        result = await products_collection.delete_one({"_id": ObjectId(product_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": "Product deleted successfully"}
