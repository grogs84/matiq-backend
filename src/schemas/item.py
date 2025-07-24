from pydantic import BaseModel
from typing import Optional

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

class ItemCreate(ItemBase):
    """Schema for creating an item"""
    pass

class ItemUpdate(ItemBase):
    """Schema for updating an item"""
    pass

class ItemResponse(ItemBase):
    """Schema for item responses"""
    id: int
    
    class Config:
        from_attributes = True
