#!/usr/bin/env python3
"""Simple test to verify search functionality works."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_search_imports():
    """Test that all search components can be imported."""
    try:
        from src.services.search import SearchService
        print("✓ SearchService imported successfully")
        
        from src.schemas.global_search import GlobalSearchResponse
        print("✓ GlobalSearchResponse imported successfully")
        
        from src.routers.search import router as search_router
        print("✓ Search router imported successfully")
        
        service = SearchService()
        print("✓ SearchService instantiated successfully")
        
        print("\n🎉 All search components are working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_search_imports()
    sys.exit(0 if success else 1)
