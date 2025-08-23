# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

HELP_TXT = """🌟 **Help Menu** 

📋 **How to use this bot:**

🔐 **First, you need to login:**
• Use `/login` command to add your Telegram session
• Follow the instructions to enter your phone number and OTP
• Once logged in, you can download restricted content

📥 **For downloading content:**

**🔒 FOR PRIVATE CHATS:**
• First send invite link of the chat (if not already member)
• Then send the post link you want to download

**🤖 FOR BOT CHATS:**
• Send link with '/b/', bot's username and message id
• Format: `https://t.me/b/botusername/4321`

**📚 MULTI POSTS:**
• Send post links with range format "from - to"
• Examples:
  - `https://t.me/channel/1001-1010`
  - `https://t.me/c/123456/101-120`
• Space between numbers doesn't matter

**⚠️ Important Notes:**
• You must `/login` first to download restricted content
• Use `/logout` to remove your session
• Use `/cancel` to stop any ongoing download
• Only admins can use `/broadcast` command

**🔧 Commands:**
• `/start` - Start the bot
• `/help` - Show this help menu
• `/login` - Login with your Telegram account
• `/logout` - Logout and remove session
• `/cancel` - Cancel ongoing operations
• `/broadcast` - Send message to all users (Admin only)

**📞 Support:**
• Developer: t.me/fightermonk110"""

START_TXT = """👋 **Hi {user_mention}!**

🤖 I am **R-TeleSwiftBot💖**

📥 I can help you download and forward restricted content from Telegram channels and groups.

🔐 **To get started:**
1. Use `/login` to authenticate with your Telegram account
2. Send me any Telegram post link to download it
3. I'll forward the content to you!

💡 **Need help?** Use `/help` command

⚡ **Powered by:** @Ashish"""

LOGIN_HELP = """🔐 **Login Instructions:**

1️⃣ **Send your phone number** (with country code)
   Example: `+1234567890`

2️⃣ **Enter OTP** when you receive it
   Format: `1 2 3 4 5` (with spaces)

3️⃣ **Enter 2FA password** if you have one enabled

✅ Once logged in, you can download restricted content!

⚠️ **Security Note:** Your session is stored securely and only used for downloading content."""

ERROR_MESSAGES = {
    'not_logged_in': "🔐 **You need to login first!**\n\nUse `/login` command to authenticate your Telegram account.",
    'session_expired': "⚠️ **Your session has expired!**\n\nPlease `/logout` and then `/login` again.",
    'invalid_link': "❌ **Invalid Telegram link!**\n\nPlease send a valid Telegram post link.",
    'download_failed': "💥 **Download failed!**\n\nThere was an error downloading the content. Please try again.",
    'upload_failed': "💥 **Upload failed!**\n\nThere was an error uploading the content. Please try again.",
    'batch_cancelled': "🛑 **Batch download cancelled!**\n\nAll pending downloads have been stopped.",
    'task_in_progress': "⏳ **Another task is in progress!**\n\nPlease wait for it to complete or use `/cancel`",
    'file_too_large': "📦 **File too large!**\n\nThe file size exceeds the maximum limit.",
    'private_chat_error': "🔒 **Private chat access error!**\n\nMake sure you're a member of the chat or channel.",
    'bot_blocked': "🚫 **Bot access blocked!**\n\nThe bot doesn't have access to this chat.",
    'invalid_session': "❌ **Invalid session!**\n\nPlease logout and login again.",
    'database_error': "💾 **Database error!**\n\nThere was an error accessing the database. Please try again later."
}

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
