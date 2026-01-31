"""
Database connection module using Motor for async MongoDB operations.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config import settings
import certifi


class Database:
    """MongoDB database connection manager."""
    
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None
    
    async def connect(self) -> None:
        """Establish connection to MongoDB."""
        self.client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            tlsCAFile=certifi.where()
        )
        self.db = self.client[settings.DATABASE_NAME]
        print(f"Connected to MongoDB database: {settings.DATABASE_NAME}")
    
    async def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")
    
    def get_collection(self, name: str):
        """Get a collection from the database."""
        if self.db is None:
            raise RuntimeError("Database not connected")
        return self.db[name]


# Global database instance
database = Database()


async def get_database() -> Database:
    """Dependency for getting database instance."""
    return database
