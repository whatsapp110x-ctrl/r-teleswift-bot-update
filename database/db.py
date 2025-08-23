import motor.motor_asyncio
import logging
from config import DB_NAME, DB_URI
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, uri, database_name):
        try:
            self._client = motor.motor_asyncio.AsyncIOMotorClient(
                uri,
                serverSelectionTimeoutMS=30000,
                connectTimeoutMS=30000,
                socketTimeoutMS=30000,
                maxPoolSize=10,
                retryWrites=True
            )
            self.db = self._client[database_name]
            self.col = self.db.users
            logger.info(f"Database initialized: {database_name}")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def new_user(self, id, name):
        """Create new user document structure"""
        return dict(
            id=id,
            name=name,
            session=None,
            join_date=datetime.utcnow(),
            last_active=datetime.utcnow()
        )
    
    async def add_user(self, id, name):
        """Add new user to database with retry"""
        try:
            user = self.new_user(id, name)
            result = await self.col.insert_one(user)
            logger.info(f"New user added: {id}")
            return bool(result.inserted_id)
        except Exception as e:
            logger.error(f"Error adding user {id}: {e}")
            # Retry once
            try:
                await asyncio.sleep(1)
                result = await self.col.insert_one(user)
                return bool(result.inserted_id)
            except:
                return False
    
    async def is_user_exist(self, id):
        """Check if user exists in database with retry"""
        try:
            user = await self.col.find_one({'id': int(id)})
            return bool(user)
        except Exception as e:
            logger.error(f"Error checking user existence {id}: {e}")
            # Retry once
            try:
                await asyncio.sleep(1)
                user = await self.col.find_one({'id': int(id)})
                return bool(user)
            except:
                return False
    
    async def total_users_count(self):
        """Get total number of users with retry"""
        try:
            count = await self.col.count_documents({})
            return count
        except Exception as e:
            logger.error(f"Error counting users: {e}")
            try:
                await asyncio.sleep(1)
                count = await self.col.count_documents({})
                return count
            except:
                return 0

    async def get_all_users(self):
        """Get all users from database"""
        try:
            return self.col.find({})
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return self.col.find({})

    async def delete_user(self, user_id):
        """Delete user from database with retry"""
        try:
            result = await self.col.delete_many({'id': int(user_id)})
            logger.info(f"User deleted: {user_id}, deleted count: {result.deleted_count}")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            try:
                await asyncio.sleep(1)
                result = await self.col.delete_many({'id': int(user_id)})
                return result.deleted_count > 0
            except:
                return False

    async def set_session(self, id, session):
        """Set user session string with retry and timestamp"""
        try:
            update_data = {
                'session': session,
                'last_active': datetime.utcnow()
            }
            if session:
                update_data['session_created'] = datetime.utcnow()
            
            result = await self.col.update_one(
                {'id': int(id)}, 
                {'$set': update_data},
                upsert=True
            )
            logger.info(f"Session updated for user: {id}")
            return result.modified_count > 0 or result.upserted_id is not None
        except Exception as e:
            logger.error(f"Error setting session for user {id}: {e}")
            try:
                await asyncio.sleep(1)
                result = await self.col.update_one(
                    {'id': int(id)}, 
                    {'$set': update_data},
                    upsert=True
                )
                return result.modified_count > 0 or result.upserted_id is not None
            except:
                return False

    async def get_session(self, id):
        """Get user session string with expiry check"""
        try:
            user = await self.col.find_one({'id': int(id)})
            if user and user.get('session'):
                # Check session age (optional expiry)
                session_created = user.get('session_created')
                if session_created:
                    session_age = datetime.utcnow() - session_created
                    if session_age > timedelta(days=7):  # 7 day expiry
                        logger.warning(f"Session expired for user {id}")
                        await self.set_session(id, None)
                        return None
                return user.get('session')
            return None
        except Exception as e:
            logger.error(f"Error getting session for user {id}: {e}")
            try:
                await asyncio.sleep(1)
                user = await self.col.find_one({'id': int(id)})
                if user:
                    return user.get('session')
                return None
            except:
                return None

    async def update_last_active(self, id):
        """Update user's last active timestamp with retry"""
        try:
            await self.col.update_one(
                {'id': int(id)}, 
                {'$set': {'last_active': datetime.utcnow()}}
            )
        except Exception as e:
            logger.error(f"Error updating last active for user {id}: {e}")
            try:
                await asyncio.sleep(0.5)
                await self.col.update_one(
                    {'id': int(id)}, 
                    {'$set': {'last_active': datetime.utcnow()}}
                )
            except:
                pass

    async def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            result = await self.col.update_many(
                {
                    'session_created': {'$lt': cutoff_date},
                    'session': {'$ne': None}
                },
                {'$unset': {'session': '', 'session_created': ''}}
            )
            if result.modified_count > 0:
                logger.info(f"Cleaned up {result.modified_count} expired sessions")
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")

# Initialize database connection with retry
import asyncio
async def init_database():
    """Initialize database with retry mechanism"""
    for attempt in range(3):
        try:
            db = Database(DB_URI, DB_NAME)
            # Test connection
            await db.col.find_one({})
            logger.info("Database connection established successfully")
            return db
        except Exception as e:
            logger.error(f"Database connection attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)
            else:
                raise

# Create database instance
try:
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    db = loop.run_until_complete(init_database())
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    # Fallback to simple initialization
    db = Database(DB_URI, DB_NAME)
