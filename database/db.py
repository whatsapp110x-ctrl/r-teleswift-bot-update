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
        if not uri or uri.strip() == "" or uri == "mongodb://localhost:27017":
            logger.warning("Database URI not properly configured - running in fallback mode")
            self._fallback_mode = True
            self._memory_store = {}
            return
        
        self._fallback_mode = False
        try:
            logger.info(f"Setting up database client for: {database_name}")
            # Optimized MongoDB connection with proper settings
            self._client = motor.motor_asyncio.AsyncIOMotorClient(
                uri,
                maxPoolSize=10,
                minPoolSize=1,
                maxIdleTimeMS=30000,
                waitQueueTimeoutMS=5000,
                connectTimeoutMS=20000,
                serverSelectionTimeoutMS=15000,
                socketTimeoutMS=20000,
                retryWrites=True
            )
            self.db = self._client[database_name]
            self.col = self.db.users
            logger.info(f"Database client configured successfully")
        except Exception as e:
            logger.error(f"Database client setup error: {e}")
            self._fallback_mode = True
            self._memory_store = {}

    async def initialize(self):
        """Initialize database connection - optimized version"""
        if self._fallback_mode:
            logger.info("Using fallback in-memory storage")
            self._initialized = True
            return True
            
        try:
            if not self._client:
                logger.error("Database client is None!")
                return False
                
            # Quick connection test with shorter timeout
            await asyncio.wait_for(
                self._client.admin.command('ping'), 
                timeout=5.0
            )
            self._initialized = True
            logger.info("Database connection initialized successfully")
            return True
        except asyncio.TimeoutError:
            logger.warning("Database connection timeout - switching to fallback mode")
            self._fallback_mode = True
            self._memory_store = {}
            self._initialized = True
            return True
        except Exception as e:
            logger.warning(f"Database initialization failed, using fallback: {e}")
            self._fallback_mode = True
            self._memory_store = {}
            self._initialized = True
            return True

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
        """Add new user to database with fallback"""
        try:
            if not self._initialized:
                await self.initialize()
            
            if self._fallback_mode:
                self._memory_store[int(id)] = self.new_user(id, name)
                logger.info(f"New user added to memory: {id}")
                return True
            
            user = self.new_user(id, name)
            await asyncio.wait_for(
                self.col.insert_one(user), 
                timeout=10.0
            )
            logger.info(f"New user added to database: {id}")
            return True
        except Exception as e:
            logger.error(f"Error adding user {id}: {e}")
            # Fallback to memory store
            if not hasattr(self, '_memory_store'):
                self._memory_store = {}
            self._memory_store[int(id)] = self.new_user(id, name)
            return True
    
    async def is_user_exist(self, id):
        """Check if user exists with fallback"""
        try:
            if not self._initialized:
                await self.initialize()
            
            if self._fallback_mode:
                return int(id) in self._memory_store
            
            user = await asyncio.wait_for(
                self.col.find_one({'id': int(id)}), 
                timeout=5.0
            )
            return bool(user)
        except Exception:
            if hasattr(self, '_memory_store'):
                return int(id) in self._memory_store
            return False
    
    async def total_users_count(self):
        """Get total number of users with fallback"""
        try:
            if not self._initialized:
                await self.initialize()
            
            if self._fallback_mode:
                return len(getattr(self, '_memory_store', {}))
            
            count = await asyncio.wait_for(
                self.col.count_documents({}), 
                timeout=5.0
            )
            return count
        except Exception:
            return len(getattr(self, '_memory_store', {}))

    async def get_all_users(self):
        """Get all users with fallback"""
        try:
            if not self._initialized:
                await self.initialize()
            
            if self._fallback_mode:
                for user_id, user_data in getattr(self, '_memory_store', {}).items():
                    yield user_data
                return
            
            async for user in self.col.find({}):
                yield user
        except Exception:
            if hasattr(self, '_memory_store'):
                for user_id, user_data in self._memory_store.items():
                    yield user_data

    async def delete_user(self, user_id):
        """Delete user with fallback"""
        try:
            if not self._initialized:
                await self.initialize()
            
            if self._fallback_mode:
                if hasattr(self, '_memory_store') and int(user_id) in self._memory_store:
                    del self._memory_store[int(user_id)]
                    return True
                return False
            
            result = await asyncio.wait_for(
                self.col.delete_many({'id': int(user_id)}), 
                timeout=10.0
            )
            logger.info(f"User deleted: {user_id}")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False

    async def set_session(self, id, session):
        """Set user session with fallback - CRITICAL FIX"""
        try:
            if not self._initialized:
                await self.initialize()
            
            if self._fallback_mode:
                if not hasattr(self, '_memory_store'):
                    self._memory_store = {}
                if int(id) not in self._memory_store:
                    self._memory_store[int(id)] = self.new_user(id, "Unknown")
                self._memory_store[int(id)]['session'] = session
                logger.info(f"Session saved to memory for user: {id}")
                return True
            
            result = await asyncio.wait_for(
                self.col.update_one(
                    {'id': int(id)}, 
                    {'$set': {'session': session}},
                    upsert=True
                ),
                timeout=10.0
            )
            logger.info(f"Session saved to database for user: {id}")
            return True
        except Exception as e:
            logger.error(f"Error setting session for user {id}: {e}")
            # Emergency fallback to memory
            if not hasattr(self, '_memory_store'):
                self._memory_store = {}
            if int(id) not in self._memory_store:
                self._memory_store[int(id)] = self.new_user(id, "Unknown")
            self._memory_store[int(id)]['session'] = session
            logger.info(f"Session saved to emergency fallback for user: {id}")
            return True

    async def get_session(self, id):
        """Get user session with fallback"""
        try:
            if not self._initialized:
                await self.initialize()
            
            if self._fallback_mode:
                user_data = getattr(self, '_memory_store', {}).get(int(id))
                return user_data.get('session') if user_data else None
            
            user = await asyncio.wait_for(
                self.col.find_one({'id': int(id)}), 
                timeout=5.0
            )
            if user:
                return user.get('session')
            return None
        except Exception as e:
            logger.error(f"Error getting session for user {id}: {e}")
            # Fallback to memory
            user_data = getattr(self, '_memory_store', {}).get(int(id))
            return user_data.get('session') if user_data else None

    async def update_last_active(self, id):
        """Update user's last active with fallback"""
        try:
            if not self._initialized:
                await self.initialize()
                
            if self._fallback_mode:
                if hasattr(self, '_memory_store') and int(id) in self._memory_store:
                    from datetime import datetime
                    self._memory_store[int(id)]['last_active'] = datetime.utcnow()
                return
                
            from datetime import datetime
            await asyncio.wait_for(
                self.col.update_one(
                    {'id': int(id)}, 
                    {'$set': {'last_active': datetime.utcnow()}}
                ),
                timeout=5.0
            )
        except Exception:
            pass  # Non-critical operation

# Create database instance with improved error handling
try:
    db = Database(DB_URI, DB_NAME)
    logger.info("Database instance created successfully")
except Exception as e:
    logger.error(f"Failed to create database instance: {e}")
    # Create emergency fallback
    class EmergencyDatabase:
        def __init__(self):
            self._memory_store = {}
            self._initialized = True
            
        async def initialize(self): return True
        async def add_user(self, id, name): 
            self._memory_store[int(id)] = {'id': id, 'name': name, 'session': None}
            return True
        async def is_user_exist(self, id): return int(id) in self._memory_store
        async def total_users_count(self): return len(self._memory_store)
        async def get_all_users(self): 
            for user in self._memory_store.values():
                yield user
        async def delete_user(self, user_id): 
            if int(user_id) in self._memory_store:
                del self._memory_store[int(user_id)]
                return True
            return False
        async def set_session(self, id, session): 
            if int(id) not in self._memory_store:
                self._memory_store[int(id)] = {'id': id, 'name': 'Unknown', 'session': None}
            self._memory_store[int(id)]['session'] = session
            return True
        async def get_session(self, id): 
            user = self._memory_store.get(int(id))
            return user.get('session') if user else None
        async def update_last_active(self, id): pass
    
    db = EmergencyDatabase()
    logger.info("Emergency database fallback activated")
