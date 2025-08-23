# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
import datetime
import time
import logging
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from database.db import db
from pyrogram.client import Client
from pyrogram import filters
from config import ADMINS

logger = logging.getLogger(__name__)

async def broadcast_messages(user_id, message):
    """Send broadcast message to a single user"""
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        logger.warning(f"FloodWait {e.value}s for user {user_id}")
        await asyncio.sleep(float(e.value))
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        logger.info(f"User {user_id} deactivated, removing from database")
        await db.delete_user(int(user_id))
        return False, "Deleted"
    except UserIsBlocked:
        logger.info(f"User {user_id} blocked bot, removing from database")
        await db.delete_user(int(user_id))
        return False, "Blocked"
    except PeerIdInvalid:
        logger.warning(f"Invalid peer ID {user_id}, removing from database")
        await db.delete_user(int(user_id))
        return False, "Error"
    except Exception as e:
        logger.error(f"Broadcast error for user {user_id}: {e}")
        return False, "Error"

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_handler(bot, message):
    """Handle broadcast command (Admin only) - FIXED"""
    try:
        # Fix admin check - ADMINS is a list
        if message.from_user.id not in ADMINS:
            return await message.reply_text("❌ **Unauthorized!** Only admins can use this command.")
        
        # Get broadcast message
        b_msg = message.reply_to_message
        if not b_msg:
            return await message.reply_text(
                "❌ **Reply Required!**\n\n"
                "Please reply to the message you want to broadcast."
            )
        
        # Get all users
        try:
            total_users = await db.total_users_count()
            if total_users == 0:
                return await message.reply_text("❌ **No users found!** The bot has no users to broadcast to.")
        except Exception as e:
            logger.error(f"Database error in broadcast: {e}")
            return await message.reply_text("❌ **Database error!** Please try again later.")
        
        # Start broadcast
        sts = await message.reply_text(
            f"📡 **Starting Broadcast...**\n\n"
            f"👥 **Total Users:** {total_users}\n"
            f"⏳ **Status:** Preparing..."
        )
        
        start_time = time.time()
        done = 0
        success = 0
        blocked = 0
        deleted = 0
        failed = 0
        
        # Broadcast to all users
        try:
            async for user in await db.get_all_users():
                try:
                    if 'id' not in user:
                        done += 1
                        failed += 1
                        continue
                    
                    user_id = int(user['id'])
                    pti, sh = await broadcast_messages(user_id, b_msg)
                    
                    if pti:
                        success += 1
                    elif pti == False:
                        if sh == "Blocked":
                            blocked += 1
                        elif sh == "Deleted":
                            deleted += 1
                        elif sh == "Error":
                            failed += 1
                    
                    done += 1
                    
                    # Update status every 10 users
                    if done % 10 == 0:
                        try:
                            await sts.edit(
                                f"📡 **Broadcasting in Progress...**\n\n"
                                f"👥 **Total Users:** {total_users}\n"
                                f"✅ **Completed:** {done}/{total_users}\n"
                                f"🎯 **Success:** {success}\n"
                                f"🚫 **Blocked:** {blocked}\n"
                                f"🗑️ **Deleted:** {deleted}\n"
                                f"❌ **Failed:** {failed}\n\n"
                                f"⏱️ **Progress:** {(done/total_users)*100:.1f}%"
                            )
                        except Exception:
                            pass
                    
                    # Small delay to prevent rate limiting
                    await asyncio.sleep(0.05)
                    
                except Exception as e:
                    logger.error(f"Error processing user in broadcast: {e}")
                    done += 1
                    failed += 1
                    continue
        
        except Exception as e:
            logger.error(f"Broadcast loop error: {e}")
            return await sts.edit("❌ **Broadcast failed!** An error occurred during the process.")
        
        # Calculate completion time
        time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
        
        # Send final summary
        final_text = (
            f"✅ **Broadcast Completed!**\n\n"
            f"⏱️ **Time Taken:** {time_taken}\n\n"
            f"📊 **Summary:**\n"
            f"👥 **Total Users:** {total_users}\n"
            f"✅ **Completed:** {done}/{total_users}\n"
            f"🎯 **Success:** {success}\n"
            f"🚫 **Blocked:** {blocked}\n"
            f"🗑️ **Deleted:** {deleted}\n"
            f"❌ **Failed:** {failed}\n\n"
            f"📈 **Success Rate:** {(success/total_users)*100:.1f}%"
        )
        
        await sts.edit(final_text)
        
        # Log broadcast completion
        logger.info(
            f"Broadcast completed by admin {message.from_user.id}: "
            f"{success}/{total_users} successful, took {time_taken}"
        )
        
    except Exception as e:
        logger.error(f"Broadcast handler error: {e}")
        await message.reply_text("❌ **Broadcast failed!** An unexpected error occurred.")

@Client.on_message(filters.command("broadcast") & ~filters.user(ADMINS))
async def broadcast_unauthorized(bot, message):
    """Handle unauthorized broadcast attempts - FIXED"""
    await message.reply_text(
        "❌ **Unauthorized Access!**\n\n"
        "🔐 Only bot admins can use the broadcast feature.\n"
        "📞 Contact the bot owner if you think this is a mistake."
    )

@Client.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats_handler(bot, message):
    """Handle stats command (Admin only) - FIXED"""
    try:
        if message.from_user.id not in ADMINS:  # Fixed admin check
            return await message.reply_text("❌ **Unauthorized!** Only admins can use this command.")
        
        total_users = await db.total_users_count()
        
        # Get active sessions count
        active_sessions = 0
        try:
            async for user in await db.get_all_users():
                if user.get('session'):
                    active_sessions += 1
        except:
            active_sessions = "Error"
        
        stats_text = (
            f"📊 **Bot Statistics**\n\n"
            f"👥 **Total Users:** {total_users}\n"
            f"🔑 **Active Sessions:** {active_sessions}\n"
            f"🤖 **Bot Status:** Online\n"
            f"💾 **Database:** Connected"
        )
        
        await message.reply_text(stats_text)
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        await message.reply_text("❌ **Stats error!** Please try again later.")

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
