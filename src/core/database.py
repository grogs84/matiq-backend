# Database configuration will go here when needed
# For now, using in-memory storage

class Database:
    def __init__(self):
        self.items = []
    
    def get_connection(self):
        # Future: return database connection
        pass

database = Database()
