import motor.motor_asyncio
import logging
import asyncio
from config import DB_NAME, DB_URI

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, uri, database_name):
        self._client = None
        self.db = None
        self.col = None
        self._initialized = False
        self._uri = uri
        self._database_name = database_name
        
        # Validate URI
        if not uri or uri.strip() == "":
            logger.error("Database URI is empty! Please set DATABASE_URL environment variable.")
            raise ValueError("Database URI cannot be empty")
        
        try:
            logger.info(f"Initializing database client for: {database_name}")
            logger.info(f"Database URI provided: {'Yes' if uri else 'No'}")
            self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
            self.db = self._client[database_name]
            self.col = self.db.users
            logger.info(f"Database client created successfully for: {database_name}")
        except Exception as e:
            logger.error(f"Database client creation error: {e}")
            raise

    async def initialize(self):
        """Initialize database connection - call this in async context"""
        try:
            if not self._client:
                logger.error("Database client is None!")
                return False
                
            # Test connection with timeout
            await asyncio.wait_for(
                self.col.find_one({}), 
                timeout=10.0
            )
            self._initialized = True
            logger.info("Database connection initialized successfully")
            return True
        except asyncio.TimeoutError:
            logger.error("Database connection timeout")
            self._initialized = False
            return False
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            self._initialized = False
            return False

    def new_user(self, id, name):
        """Create new user document structure"""
        return dict(
            id=id,
            name=name,
            session=None,
            join_date=None,
            last_active=None
        )
    
    async def add_user(self, id, name):
        """Add new user to database"""
        try:
            if not self._initialized:
                await self.initialize()
            
            if not self._initialized:
                logger.warning("Database not initialized, using in-memory fallback")
                return True  # Fallback for when DB is not available
            
            user = self.new_user(id, name)
            await self.col.insert_one(user)
            logger.info(f"New user added: {id}")
            return True
        except Exception as e:
            logger.error(f"Error adding user {id}: {e}")
            return False
    
    async def is_user_exist(self, id):
        """Check if user exists in database"""
        try:
            if not self._initialized:
                await self.initialize()
            
            if not self._initialized:
                return False  # Fallback
            
            user = await self.col.find_one({'id': int(id)})
            return bool(user)
        except Exception as e:
            logger.error(f"Error checking user existence {id}: {e}")
            return False
    
    async def total_users_count(self):
        """Get total number of users"""
        try:
            if not self._initialized:
                await self.initialize()
            
            if not self._initialized:
                return 0  # Fallback
            
            count = await self.col.count_documents({})
            return count
        except Exception as e:
            logger.error(f"Error counting users: {e}")
            return 0

    async def get_all_users(self):
        """Get all users from database"""
        try:
            if not self._initialized:
                await self.initialize()
            
            if not self._initialized:
                return []  # Fallback
            
            return self.col.find({})
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

    async def delete_user(self, user_id):
        """Delete user from database"""
        try:
            if not self._initialized:
                await self.initialize()
            
            if not self._initialized:
                return False  # Fallback
            
            result = await self.col.delete_many({'id': int(user_id)})
            logger.info(f"User deleted: {user_id}, deleted count: {result.deleted_count}")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False

    async def set_session(self, id, session):
        """Set user session string"""
        try:
            if not self._initialized:
                await self.initialize()
            
            if not self._initialized:
                logger.warning(f"Cannot store session for user {id} - database not available")
                return False  # Fallback
            
            result = await self.col.update_one(
                {'id': int(id)}, 
                {'$set': {'session': session}},
                upsert=True
            )
            logger.info(f"Session updated for user: {id}")
            return result.modified_count > 0 or result.upserted_id is not None
        except Exception as e:
            logger.error(f"Error setting session for user {id}: {e}")
            return False

    async def get_session(self, id):
        """Get user session string"""
        try:
            if not self._initialized:
                await self.initialize()
            
            if not self._initialized:
                logger.warning(f"Cannot get session for user {id} - database not available")
                return None  # Fallback
            
            user = await self.col.find_one({'id': int(id)})
            if user:
                return user.get('session')
            return None
        except Exception as e:
            logger.error(f"Error getting session for user {id}: {e}")
            return None

    async def update_last_active(self, id):
        """Update user's last active timestamp"""
        try:
            if not self._initialized:
                await self.initialize()
                
            if not self._initialized:
                return  # Fallback
                
            from datetime import datetime
            await self.col.update_one(
                {'id': int(id)}, 
                {'$set': {'last_active': datetime.utcnow()}}
            )
        except Exception as e:
            logger.error(f"Error updating last active for user {id}: {e}")

# Create database instance with error handling
try:
    db = Database(DB_URI, DB_NAME)
except Exception as e:
    logger.error(f"Failed to create database instance: {e}")
    # Create a dummy database object that will handle errors gracefully
    class DummyDatabase:
        async def initialize(self): return False
        async def add_user(self, id, name): return True
        async def is_user_exist(self, id): return False
        async def total_users_count(self): return 0
        async def get_all_users(self): return []
        async def delete_user(self, user_id): return False
        async def set_session(self, id, session): return False
        async def get_session(self, id): return None
        async def update_last_active(self, id): pass
    
    db = DummyDatabase()
