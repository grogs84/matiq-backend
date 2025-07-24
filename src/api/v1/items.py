from fastapi import APIRouter, HTTPException
from typing import List

from ...schemas import ItemCreate, ItemUpdate, ItemResponse
from ...services import item_service

router = APIRouter()

@router.get("/", response_model=List[ItemResponse])
def get_items():
    """Get all items"""
    return item_service.get_all_items()

@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    """Get item by ID"""
    item = item_service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/", response_model=ItemResponse)
def create_item(item: ItemCreate):
    """Create a new item"""
    return item_service.create_item(item)

@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemUpdate):
    """Update an existing item"""
    updated_item = item_service.update_item(item_id, item)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated_item

@router.delete("/{item_id}")
def delete_item(item_id: int):
    """Delete an item"""
    success = item_service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}
