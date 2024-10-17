from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict
from utils.auth import get_current_user
from schema.items import ItemCreate, ItemUpdate
from datetime import datetime
from config.constant import ITEMS_COLLECTION
from config.database import insert_one, is_valid_object_id, find_one, find_all,\
                            aggregate, delete, update
from bson import ObjectId
router = APIRouter()

@router.post("/items")
async def create_item(item: ItemCreate, current_user: dict = Depends(get_current_user) ):
    item_data = item.model_dump()
    item_data["insert_date"] = datetime.utcnow() 
    item_data["expiry_date"] = datetime.combine(item.expiry_date, datetime.min.time())
    try:
        item_id = await insert_one(item_data, ITEMS_COLLECTION)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create item: {e}")

    return {"item_id": item_id, "message": "Item created successfully"}


@router.get("/items/filter")
async def filter_items(
    email: str = Query(None),
    expiry_date: str = Query(None),
    insert_date: str = Query(None),
    quantity: int = Query(None),
    current_user: dict = Depends(get_current_user)  
):
    filter_criteria = {}

    if email:
        filter_criteria["email"] = email
    
    if expiry_date:
        try:
            expiry_datetime = datetime.fromisoformat(expiry_date)
            filter_criteria["expiry_date"] = {"$gt": expiry_datetime}
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid expiry date format. Use YYYY-MM-DD.")

    if insert_date:
        try:
            insert_datetime = datetime.fromisoformat(insert_date)
            filter_criteria["insert_date"] = {"$gt": insert_datetime}
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid insert date format. Use YYYY-MM-DD.")

    if quantity is not None:
        filter_criteria["quantity"] = {"$gte": quantity}

    items = await find_all(filter_criteria, ITEMS_COLLECTION)
    
    return items


@router.get("/items/email-count")
async def get_item_count_by_email(current_user: dict = Depends(get_current_user)):
    pipeline = [
        {
            "$group": {
                "_id": "$email",
                "count": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "email": "$_id",
                "count": 1
            }
        }
    ]
    
    try:
        results = await aggregate(pipeline, ITEMS_COLLECTION)
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while aggregating data: {e}")
    
    
@router.get("/items/{item_id}")
async def get_item(item_id: str, current_user: dict = Depends(get_current_user)):
    if not is_valid_object_id(item_id):
        raise HTTPException(status_code=400, detail="Invalid item ID")

    item = await find_one({"_id": ObjectId(item_id)}, ITEMS_COLLECTION)
    
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item


@router.put("/items/{item_id}")
async def update_item(item_id: str, item_update: ItemUpdate, current_user: dict = Depends(get_current_user)):
    update_data = item_update.model_dump(exclude_unset=True)  
    
    if not is_valid_object_id(item_id):
        raise HTTPException(status_code=400, detail="Invalid item ID")

    if 'expiry_date' in update_data:
        try:
            update_data['expiry_date'] = datetime.fromisoformat(update_data['expiry_date'])
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid expiry date format. Use YYYY-MM-DD.")

    result = await update({"_id": ObjectId(item_id)}, update_data, ITEMS_COLLECTION)

    if result['matched_count'] == 0:
        raise HTTPException(status_code=404, detail="Item not found.")

    return {"detail": "Item updated successfully."}


@router.delete("/items/{item_id}")
async def delete_item(item_id: str, current_user: dict = Depends(get_current_user)):
    if not is_valid_object_id(item_id):
        raise HTTPException(status_code=400, detail="Invalid item ID")
    
    result = await delete({"_id": ObjectId(item_id)}, ITEMS_COLLECTION)
    
    if result['deleted_count'] == 0:
        raise HTTPException(status_code=404, detail="Item not found.")

    return {"detail": "Item deleted successfully."}