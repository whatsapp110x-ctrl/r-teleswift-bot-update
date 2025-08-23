import motor.motor_asyncio
import logging
from config import DB_NAME, DB_URI

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, uri, database_name):
        try:
            self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
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
            join_date=None,
            last_active=None
        )
    
    async def add_user(self, id, name):
        """Add new user to database"""
        try:
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
            user = await self.col.find_one({'id': int(id)})
            return bool(user)
        except Exception as e:
            logger.error(f"Error checking user existence {id}: {e}")
            return False
    
    async def total_users_count(self):
        """Get total number of users"""
        try:
            count = await self.col.count_documents({})
            return count
        except Exception as e:
            logger.error(f"Error counting users: {e}")
            return 0

    async def get_all_users(self):
        """Get all users from database"""
        try:
            return self.col.find({})
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

    async def delete_user(self, user_id):
        """Delete user from database"""
        try:
            result = await self.col.delete_many({'id': int(user_id)})
            logger.info(f"User deleted: {user_id}, deleted count: {result.deleted_count}")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False

    async def set_session(self, id, session):
        """Set user session string"""
        try:
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
            from datetime import datetime
            await self.col.update_one(
                {'id': int(id)}, 
                {'$set': {'last_active': datetime.utcnow()}}
            )
        except Exception as e:
            logger.error(f"Error updating last active for user {id}: {e}")

# Initialize database connection
try:
    db = Database(DB_URI, DB_NAME)
    logger.info("Database connection established")
except Exception as e:
    logger.error(f"Failed to establish database connection: {e}")
    raise
