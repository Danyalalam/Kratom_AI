from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

MONGODB_URL = "mongodb://localhost:27017"
database_name = "kratom_ai"

class LocationData(BaseModel):
    ip: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None

class UserData(BaseModel):
    age: int
    height: dict
    weight: dict
    body_type: str
    blood_type: str
    pain_level: int
    email: str
    newsletter: bool
    location: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    last_modified: Optional[datetime] = None

    def convert_location_data(self, location: Optional[LocationData] = None):
        """Convert LocationData to dictionary if needed"""
        if location and isinstance(location, LocationData):
            self.location = location.model_dump()
        elif location and isinstance(location, dict):
            self.location = location

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db = None
    is_connected: bool = False

    @classmethod
    async def connect_db(cls):
        try:
            if cls.client is None:
                cls.client = AsyncIOMotorClient(MONGODB_URL)
                cls.db = cls.client[database_name]
                # Create a unique index on email field
                await cls.db.users.create_index("email", unique=True)
                cls.is_connected = True
                logger.info("Connected to MongoDB and created unique email index")
        except Exception as e:
            cls.is_connected = False
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise e

    @classmethod
    async def close_db(cls):
        if cls.client is not None:
            cls.client.close()
            cls.client = None
            cls.db = None
            cls.is_connected = False
            logger.info("Closed MongoDB connection")

    @classmethod
    async def save_user_data(cls, user_data: UserData):
        if not cls.is_connected:
            await cls.connect_db()
        try:
            # Handle location data conversion
            user_data.convert_location_data(user_data.location)
            
            # Convert user_data to dict and update last_modified
            data_dict = user_data.model_dump()
            data_dict['last_modified'] = datetime.utcnow()
            
            # Use upsert operation with email as the key
            result = await cls.db.users.update_one(
                {"email": user_data.email},
                {"$set": data_dict},
                upsert=True
            )
            
            if result.upserted_id:
                logger.info(f"Created new user data for email: {user_data.email}")
                return result.upserted_id
            else:
                logger.info(f"Updated existing user data for email: {user_data.email}")
                return result.modified_count
                
        except Exception as e:
            logger.error(f"Error saving user data: {e}")
            raise e
            
    @classmethod
    async def get_user_by_email(cls, email: str) -> Optional[Dict[str, Any]]:
        """Retrieve user data by email"""
        if not cls.is_connected:
            await cls.connect_db()
        try:
            user_data = await cls.db.users.find_one({"email": email})
            return user_data
        except Exception as e:
            logger.error(f"Error retrieving user data for email {email}: {e}")
            return None