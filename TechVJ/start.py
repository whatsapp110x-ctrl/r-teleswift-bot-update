# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio 
import logging
import pyrogram
from pyrogram.client import Client
from pyrogram import filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied, MessageNotModified
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message 
from config import (
    API_ID, API_HASH, ERROR_MESSAGE, MAX_BATCH_SIZE, PROGRESS_UPDATE_INTERVAL, 
    MAX_FILE_SIZE, DOWNLOAD_CHUNK_SIZE, MAX_CONCURRENT_DOWNLOADS, CONNECTION_TIMEOUT,
    MAX_RETRIES, RETRY_DELAY, THUMBNAIL_QUALITY, THUMBNAIL_MAX_SIZE, CONNECTION_POOL_SIZE,
    MINIMAL_DELAY, UPLOAD_CHUNK_SIZE, PROGRESS_THROTTLE
)
from database.db import db
from TechVJ.strings import HELP_TXT, START_TXT, ERROR_MESSAGES
from datetime import datetime
import gc  # For garbage collection

logger = logging.getLogger(__name__)

def is_valid_telegram_post_link(text):
    """Validate if text is a valid Telegram post link"""
    try:
        text = text.strip()
        if not text.startswith('https://t.me/'):
            return False
        
        parts = text.split('/')
        if len(parts) < 5:
            return False
        
        if parts[3] == 'c' and len(parts) >= 6:
            try:
                int(parts[4])
                int(parts[5].split('-')[0])
                return True
            except (ValueError, IndexError):
                return False
        elif parts[3] == 'b' and len(parts) >= 6:
            try:
                int(parts[5].split('-')[0])
                return True
            except (ValueError, IndexError):
                return False
        else:
            try:
                int(parts[4].split('-')[0])
                return True
            except (ValueError, IndexError):
                return False
    except Exception:
        return False

class BatchTemp:
    """Class to manage batch operations state"""
    IS_BATCH = {}
    USER_CONNECTIONS = {}
    
    @classmethod
    def set_batch_state(cls, user_id, state):
        cls.IS_BATCH[user_id] = state
        if not state:  # If stopping batch, clean up connections
            if user_id in cls.USER_CONNECTIONS:
                del cls.USER_CONNECTIONS[user_id]
    
    @classmethod
    def get_batch_state(cls, user_id):
        return cls.IS_BATCH.get(user_id, True)

async def safe_delete_file(file_path):
    """Safely delete a file with retry mechanism"""
    if not file_path or not os.path.exists(file_path):
        return
        
    for attempt in range(3):
        try:
            os.remove(file_path)
            logger.debug(f"Deleted file: {file_path}")
            return
        except Exception as e:
            if attempt == 2:
                logger.error(f"Failed to delete file {file_path}: {e}")
            await asyncio.sleep(0.5)

async def ultra_fast_download(acc, msg, message, max_retries=3):
    """Ultra-fast download with better error handling"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Download attempt {attempt + 1}")
            file = await acc.download_media(msg, progress=progress, progress_args=[message, "down"])
            return file
        except FloodWait as e:
            logger.warning(f"FloodWait: waiting {e.value} seconds")
            await asyncio.sleep(e.value)
        except Exception as e:
            logger.warning(f"Download attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
            else:
                raise e

async def get_ultra_hd_thumbnail(acc, media_obj):
    """Get the highest quality thumbnail available with timeout"""
    try:
        # Add timeout to prevent hanging
        return await asyncio.wait_for(_get_thumbnail_internal(acc, media_obj), timeout=30)
    except asyncio.TimeoutError:
        logger.warning("Thumbnail download timed out")
        return None
    except Exception as e:
        logger.error(f"Error getting thumbnail: {e}")
        return None

async def _get_thumbnail_internal(acc, media_obj):
    """Internal thumbnail extraction logic"""
    if hasattr(media_obj, 'photo') and media_obj.photo:
        if hasattr(media_obj.photo, 'sizes') and media_obj.photo.sizes:
            largest = max(media_obj.photo.sizes, key=lambda x: x.width * x.height)
            return await acc.download_media(largest.file_id)
    
    elif hasattr(media_obj, 'video') and media_obj.video:
        if hasattr(media_obj.video, 'thumbs') and media_obj.video.thumbs:
            best_thumb = max(media_obj.video.thumbs, 
                           key=lambda x: getattr(x, 'width', 0) * getattr(x, 'height', 0))
            if best_thumb and hasattr(best_thumb, 'file_id'):
                return await acc.download_media(best_thumb.file_id)
    
    elif hasattr(media_obj, 'document') and media_obj.document:
        if hasattr(media_obj.document, 'thumbs') and media_obj.document.thumbs:
            best_thumb = max(media_obj.document.thumbs,
                           key=lambda x: getattr(x, 'width', 0) * getattr(x, 'height', 0))
            if best_thumb and hasattr(best_thumb, 'file_id'):
                return await acc.download_media(best_thumb.file_id)
    
    return None

async def create_client_with_retry(user_data, user_id):
    """Create and connect client with retry and connection tracking"""
    # Check if user already has a connection
    if user_id in BatchTemp.USER_CONNECTIONS:
        try:
            existing_client = BatchTemp.USER_CONNECTIONS[user_id]
            await existing_client.get_me()  # Test connection
            return existing_client
        except:
            # Connection is dead, remove it
            try:
                await existing_client.disconnect()
            except:
                pass
            del BatchTemp.USER_CONNECTIONS[user_id]
    
    # Create new connection
    for attempt in range(3):
        try:
            acc = Client(
                ":memory:", 
                session_string=user_data, 
                api_hash=API_HASH, 
                api_id=API_ID
            )
            await acc.connect()
            BatchTemp.USER_CONNECTIONS[user_id] = acc
            return acc
        except Exception as e:
            logger.warning(f"Client connection attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                await asyncio.sleep(3)
            else:
                raise e

def progress(current, total, message, type):
    """Improved progress with better error handling"""
    try:
        if total <= 0:
            return
            
        percentage = current * 100 / total
        progress_key = f"{message.id}_{type}"
        
        #
