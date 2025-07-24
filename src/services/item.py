from typing import List, Optional
from ..schemas.item import ItemCreate, ItemUpdate, ItemResponse

class ItemService:
    def __init__(self):
        # In-memory storage (replace with database in production)
        self._items: List[ItemResponse] = [
            ItemResponse(id=1, name="Sample Item 1", description="This is a sample item", price=29.99),
            ItemResponse(id=2, name="Sample Item 2", description="Another sample item", price=39.99),
        ]
        self._next_id = 3

    def get_all_items(self) -> List[ItemResponse]:
        """Get all items"""
        return self._items

    def get_item_by_id(self, item_id: int) -> Optional[ItemResponse]:
        """Get item by ID"""
        return next((item for item in self._items if item.id == item_id), None)

    def create_item(self, item_data: ItemCreate) -> ItemResponse:
        """Create a new item"""
        new_item = ItemResponse(
            id=self._next_id,
            **item_data.model_dump()
        )
        self._items.append(new_item)
        self._next_id += 1
        return new_item

    def update_item(self, item_id: int, item_data: ItemUpdate) -> Optional[ItemResponse]:
        """Update an existing item"""
        existing_item = self.get_item_by_id(item_id)
        if not existing_item:
            return None
        
        # Update the item in place
        update_data = item_data.model_dump()
        for field, value in update_data.items():
            setattr(existing_item, field, value)
        
        return existing_item

    def delete_item(self, item_id: int) -> bool:
        """Delete an item"""
        initial_length = len(self._items)
        self._items = [item for item in self._items if item.id != item_id]
        return len(self._items) < initial_length

# Create a singleton instance
item_service = ItemService()
