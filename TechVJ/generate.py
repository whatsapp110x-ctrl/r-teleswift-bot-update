# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import (
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from config import API_ID, API_HASH, SESSION_STRING_SIZE
from database.db import db
from TechVJ.strings import LOGIN_HELP

logger = logging.getLogger(__name__)

@Client.on_message(filters.private & filters.command(["logout"]))
async def logout(client, message):
    """Handle logout command"""
    try:
        user_id = message.from_user.id
        await db.update_last_active(user_id)
        
        user_data = await db.get_session(user_id)
        
        if user_data is None:
            return await message.reply_text("❌ **You are not logged in!**")
        
        success = await db.set_session(user_id, session=None)
        if success:
            await message.reply_text("✅ **Logout Successful!** 🔓\n\nYour session has been removed.")
            logger.info(f"User {user_id} logged out successfully")
        else:
            await message.reply_text("❌ **Logout failed!** Please try again.")
            
    except Exception as e:
        logger.error(f"Error in logout: {e}")
        await message.reply_text("❌ An error occurred during logout.")

@Client.on_message(filters.private & filters.command(["login"]))
async def login_command(client, message):
    """Handle login command"""
    try:
        user_id = message.from_user.id
        await db.update_last_active(user_id)
        
        # Check if user is already logged in
        user_data = await db.get_session(user_id)
        if user_data is not None:
            return await message.reply_text("⚠️ **You are already logged in!**\n\nFirst use `/logout` to remove your current session, then login again.")
        
        # Send login instructions
        await message.reply_text(LOGIN_HELP)
        
        # Ask for phone number
        try:
            phone_msg = await client.ask(
                chat_id=user_id,
                text="📱 **Please send your phone number**\n\nInclude country code (e.g., +1234567890)\n\nSend `/cancel` to cancel",
                timeout=120
            )
        except asyncio.TimeoutError:
            return await message.reply_text("⏰ **Timeout!** Please try `/login` again.")
        
        if phone_msg.text == '/cancel':
            return await phone_msg.reply_text('🛑 **Process cancelled!**')
        
        phone_number = phone_msg.text.strip()
        
        # Validate phone number
        if not phone_number.startswith('+') or len(phone_number) < 10:
            return await phone_msg.reply_text("❌ **Invalid format!** Please include country code (e.g., +1234567890)")
        
        # Create temp client
        temp_client = Client(":memory:", API_ID, API_HASH)
        await temp_client.connect()
        
        try:
            # Send OTP
            await phone_msg.reply_text("📤 **Sending OTP...**")
            code = await temp_client.send_code(phone_number)
            
            # Ask for OTP
            try:
                otp_msg = await client.ask(
                    user_id,
                    "🔐 **Enter the OTP**\n\nCheck your Telegram for the verification code.\nSend `/cancel` to cancel",
                    timeout=120
                )
            except asyncio.TimeoutError:
                await temp_client.disconnect()
                return await message.reply_text("⏰ **OTP timeout!** Please try again.")
            
            if otp_msg.text == '/cancel':
                await temp_client.disconnect()
                return await otp_msg.reply_text('🛑 **Process cancelled!**')
            
            phone_code = otp_msg.text.replace(" ", "").strip()
            
            # Sign in
            try:
                await temp_client.sign_in(phone_number, code.phone_code_hash, phone_code)
            except SessionPasswordNeeded:
                # Handle 2FA
                try:
                    pwd_msg = await client.ask(
                        user_id,
                        '🔐 **2FA Password Required**\n\nEnter your password:\nSend `/cancel` to cancel',
                        timeout=120
                    )
                except asyncio.TimeoutError:
                    await temp_client.disconnect()
                    return await message.reply_text("⏰ **Password timeout!**")
                
                if pwd_msg.text == '/cancel':
                    await temp_client.disconnect()
                    return await pwd_msg.reply_text('🛑 **Process cancelled!**')
                
                await temp_client.check_password(pwd_msg.text)
            
            # Export session
            session_string = await temp_client.export_session_string()
            me = await temp_client.get_me()
            await temp_client.disconnect()
            
            # Save session
            success = await db.set_session(user_id, session=session_string)
            if success:
                await message.reply_text(
                    f"✅ **Login Successful!** 🎉\n\n"
                    f"👤 **Account:** {me.first_name}\n"
                    f"📱 **Phone:** {me.phone_number}\n\n"
                    f"Now you can send me Telegram links to download!"
                )
            else:
                await message.reply_text("❌ **Failed to save session!** Please try again.")
                
        except PhoneNumberInvalid:
            await temp_client.disconnect()
            await phone_msg.reply_text('❌ **Invalid phone number!**')
        except PhoneCodeInvalid:
            await temp_client.disconnect()
            await otp_msg.reply_text('❌ **Invalid OTP!**')
        except Exception as e:
            await temp_client.disconnect()
            logger.error(f"Login error: {e}")
            await message.reply_text('❌ **Login failed!** Please try again.')
            
    except Exception as e:
        logger.error(f"Login command error: {e}")
        await message.reply_text("❌ **Error occurred!** Please try again.")
