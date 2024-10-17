from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Optional
from utils.auth import get_current_user
from schema.clock_in import ClockInRecord, UpdateClockInRecord
from datetime import datetime
from config.constant import CLOCK_IN_COLLECTION
from config.database import insert_one, is_valid_object_id, find_one, find_all,\
                            aggregate, delete, update
from bson import ObjectId
# Initialize router for item routes
router = APIRouter()



@router.post("/clock-in")
async def clock_in(clock_in_record: ClockInRecord, current_user: dict = Depends(get_current_user)):
    
    clock_in_data = clock_in_record.model_dump()
    clock_in_data["insert_date"] = datetime.utcnow()
    
    try:
        inserted_id = await insert_one(clock_in_data, CLOCK_IN_COLLECTION)
        return {"detail": "Clock-in recorded successfully.", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create clock-in record: {str(e)}")
    
    
@router.get("/clock-in/filter")
async def filter_clock_ins(
    email: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    after: Optional[str] = Query(None),  # Expected format: YYYY-MM-DDTHH:MM:SS
    current_user: dict = Depends(get_current_user)
):
    filter_criteria = {}
    
    if email:
        filter_criteria["email"] = email

    if location:
        filter_criteria["location"] = location

    if after:
        try:
            after_date = datetime.fromisoformat(after) 
            filter_criteria["insert_datetime"] = {"$gt": after_date}
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DDTHH:MM:SS")

    clock_ins = await find_all(filter_criteria, CLOCK_IN_COLLECTION)  

    return {"clock_ins": clock_ins}


@router.get("/clock-in/{id}")
async def get_clock_in_record(id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid clock-in record ID")

    clock_in_record = await find_one({"_id": ObjectId(id)}, CLOCK_IN_COLLECTION)

    if not clock_in_record:
        raise HTTPException(status_code=404, detail="Clock-in record not found")

    return clock_in_record


@router.put("/clock-in/{id}")
async def update_clock_in_record(id: str, clock_in_record: UpdateClockInRecord, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid clock-in record ID")

    update_data = clock_in_record.model_dump(exclude_unset=True)  

    existing_record = await find_one({"_id": ObjectId(id)}, CLOCK_IN_COLLECTION)
    if not existing_record:
        raise HTTPException(status_code=404, detail="Clock-in record not found")

    result = await update({"_id": ObjectId(id)}, update_data, CLOCK_IN_COLLECTION)
    if result["matched_count"] == 0:
        raise HTTPException(status_code=404, detail="Failed to update clock-in record")

    return {"detail": "Clock-in record updated successfully"}


@router.delete("/clock-in/{id}")
async def delete_clock_in_record(id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid clock-in record ID")

    result = await delete({"_id": ObjectId(id)}, CLOCK_IN_COLLECTION)

    if result["deleted_count"] == 0:
        raise HTTPException(status_code=404, detail="Clock-in record not found")

    return {"detail": "Clock-in record deleted successfully"}
