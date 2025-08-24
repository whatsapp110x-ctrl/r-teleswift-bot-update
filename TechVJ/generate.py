# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio  # ADDED - This was missing
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
from TechVJ.strings import ERROR_MESSAGES, LOGIN_HELP

logger = logging.getLogger(__name__)

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["logout"]))
async def logout(client, message):
    """Handle logout command - optimized"""
    try:
        await db.update_last_active(message.from_user.id)
        user_data = await db.get_session(message.from_user.id)  
        
        if user_data is None:
            return await message.reply_text("❌ **You are not logged in!**")
        
        success = await db.set_session(message.from_user.id, session=None)
        if success:
            await message.reply("✅ **Logout Successful!** 🔓\n\nYour session has been removed.")
            logger.info(f"User {message.from_user.id} logged out successfully")
        else:
            await message.reply_text("❌ **Logout failed!** Please try again.")
            
    except Exception as e:
        logger.error(f"Error in logout: {e}")
        await message.reply_text("❌ An error occurred during logout.")

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["login"]))
async def main(bot: Client, message: Message):
    """Handle login command - optimized version"""
    try:
        await db.update_last_active(message.from_user.id)
        
        # Check if user is already logged in
        user_data = await db.get_session(message.from_user.id)
        if user_data is not None:
            await message.reply("⚠️ **You are already logged in!**\n\nFirst `/logout` your old session, then login again.")
            return 
        
        user_id = int(message.from_user.id)
        
        # Send login instructions
        await message.reply_text(LOGIN_HELP)
        
        # Ask for phone number with reduced timeout
        try:
            phone_number_msg = await bot.ask(
                chat_id=user_id, 
                text="📱 **Please send your phone number**\n\n"
                     "Include country code (e.g., +1234567890)\n\n"
                     "Enter `/cancel` to cancel the process",
                timeout=60  # Reduced from USER_INPUT_TIMEOUT
            )
        except TimeoutError:
            return await message.reply_text("⏰ **Login timeout!** Please try `/login` again.")
        
        if phone_number_msg.text == '/cancel':
            return await phone_number_msg.reply('🛑 **Process cancelled!**')
        
        phone_number = phone_number_msg.text.strip()
        
        # Validate phone number format
        if not phone_number.startswith('+') or len(phone_number) < 10:
            return await phone_number_msg.reply("❌ **Invalid phone number format!**\n\nPlease include country code (e.g., +1234567890)")
        
        # Create client with optimized settings
        client = Client(
            ":memory:", 
            API_ID, 
            API_HASH,
            device_model="VJ Bot",
            system_version="1.0"
        )
        await client.connect()
        
        await phone_number_msg.reply("📤 **Sending OTP...**")
        
        # Send verification code
        try:
            code = await client.send_code(phone_number)
        except PhoneNumberInvalid:
            await client.disconnect()
            return await phone_number_msg.reply('❌ **Invalid phone number!**\n\nPlease check your phone number and try again.')
        except Exception as e:
            await client.disconnect()
            logger.error(f"Error sending code: {e}")
            return await phone_number_msg.reply('❌ **Failed to send OTP!** Please try again.')
        
        # Ask for OTP with reduced timeout
        try:
            phone_code_msg = await bot.ask(
                user_id, 
                "🔐 **Please enter the OTP**\n\n"
                "Check your Telegram app for the verification code.\n"
                "If OTP is `12345`, send it as `1 2 3 4 5` (with spaces)\n\n"
                "Enter `/cancel` to cancel the process", 
                filters=filters.text, 
                timeout=90  # Reduced timeout
            )
        except TimeoutError:
            await client.disconnect()
            return await message.reply_text("⏰ **OTP timeout!** Please try `/login` again.")
        
        if phone_code_msg.text == '/cancel':
            await client.disconnect()
            return await phone_code_msg.reply('🛑 **Process cancelled!**')
        
        # Sign in with OTP
        try:
            phone_code = phone_code_msg.text.replace(" ", "").strip()
            if not phone_code.isdigit():
                await client.disconnect()
                return await phone_code_msg.reply('❌ **Invalid OTP format!** Please enter only numbers.')
            
            await client.sign_in(phone_number, code.phone_code_hash, phone_code)
            
        except PhoneCodeInvalid:
            await client.disconnect()
            return await phone_code_msg.reply('❌ **Invalid OTP!** Please check and try again.')
        except PhoneCodeExpired:
            await client.disconnect()
            return await phone_code_msg.reply('❌ **OTP expired!** Please try `/login` again.')
        except SessionPasswordNeeded:
            # Handle 2FA with reduced timeout
            try:
                two_step_msg = await bot.ask(
                    user_id, 
                    '🔐 **Two-Step Verification**\n\n'
                    'Your account has 2FA enabled. Please enter your password.\n\n'
                    'Enter `/cancel` to cancel the process', 
                    filters=filters.text, 
                    timeout=60  # Reduced timeout
                )
            except TimeoutError:
                await client.disconnect()
                return await message.reply_text("⏰ **Password timeout!** Please try `/login` again.")
            
            if two_step_msg.text == '/cancel':
                await client.disconnect()
                return await two_step_msg.reply('🛑 **Process cancelled!**')
            
            try:
                password = two_step_msg.text
                await client.check_password(password=password)
            except PasswordHashInvalid:
                await client.disconnect()
                return await two_step_msg.reply('❌ **Invalid password!** Please try again.')
            except Exception as e:
                await client.disconnect()
                logger.error(f"2FA error: {e}")
                return await two_step_msg.reply('❌ **2FA authentication failed!** Please try again.')
        
        except Exception as e:
            await client.disconnect()
            logger.error(f"Sign in error: {e}")
            return await phone_code_msg.reply('❌ **Login failed!** Please try again.')
        
        # Export session string
        try:
            string_session = await client.export_session_string()
            await client.disconnect()
        except Exception as e:
            await client.disconnect()
            logger.error(f"Session export error: {e}")
            return await message.reply_text('❌ **Failed to create session!** Please try again.')
        
        # Validate session string
        if len(string_session) < SESSION_STRING_SIZE:
            return await message.reply_text('❌ **Invalid session string!** Please try again.')
        
        # Test the session quickly
        try:
            test_client = Client(":memory:", session_string=string_session, api_id=API_ID, api_hash=API_HASH)
            await test_client.connect()
            me = await test_client.get_me()
            await test_client.disconnect()
            
            # Save session to database with retry
            max_retries = 3
            success = False
            for attempt in range(max_retries):
                try:
                    success = await db.set_session(message.from_user.id, session=string_session)
                    if success:
                        break
                    logger.warning(f"Session save attempt {attempt + 1} failed")
                except Exception as save_error:
                    logger.error(f"Session save error (attempt {attempt + 1}): {save_error}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)  # Brief delay between retries
            
            if not success:
                return await message.reply_text('❌ **Failed to save session!** Database issue detected. Please try again.')
            
            await bot.send_message(
                message.from_user.id, 
                f"✅ **Login Successful!** 🎉\n\n"
                f"👤 **Account:** {me.first_name}\n"
                f"📱 **Phone:** {me.phone_number}\n\n"
                f"🔐 Your session has been saved securely.\n"
                f"Now you can download restricted content!\n\n"
                f"💡 **Tip:** If you get AUTH KEY errors, `/logout` and `/login` again."
            )
            
            logger.info(f"User {message.from_user.id} logged in successfully")
            
        except Exception as e:
            logger.error(f"Session test error: {e}")
            return await message.reply_text('❌ **Session validation failed!** Please try again.')
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        await message.reply_text("❌ **Login process failed!** Please try again later.")

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
