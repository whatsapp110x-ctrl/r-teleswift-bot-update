# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
import traceback
import logging
from pyrogram.types import Message
from pyrogram.client import Client
from pyrogram import filters
from asyncio.exceptions import TimeoutError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from config import API_ID, API_HASH, SESSION_STRING_SIZE, USER_INPUT_TIMEOUT
from database.db import db
from TechVJ.strings import LOGIN_HELP  # ← This is the fixed import line

logger = logging.getLogger(__name__)

# Rest of your code stays the same...
