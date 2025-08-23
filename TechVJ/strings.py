# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ

START_TXT = """<b>ʜᴇʏ {user_mention} 👋,

ɪ'ᴍ ᴀ ᴘᴏᴡᴇʀғᴜʟ ʙᴏᴛ ᴛʜᴀᴛ ᴄᴀɴ sᴀᴠᴇ ʀᴇsᴛʀɪᴄᴛᴇᴅ ᴄᴏɴᴛᴇɴᴛ ғʀᴏᴍ ᴛᴇʟᴇɢʀᴀᴍ ᴄʜᴀɴɴᴇʟs & ɢʀᴏᴜᴘs!

🔥 ғᴇᴀᴛᴜʀᴇs:
• sɪɴɢʟᴇ ᴘᴏsᴛ ᴅᴏᴡɴʟᴏᴀᴅ
• ʙᴜʟᴋ/ʙᴀᴛᴄʜ ᴅᴏᴡɴʟᴏᴀᴅ 
• ʜɪɢʜ ǫᴜᴀʟɪᴛʏ ᴍᴇᴅɪᴀ
• ғᴀsᴛ & ʀᴇʟɪᴀʙʟᴇ

📝 ʜᴏᴡ ᴛᴏ ᴜsᴇ:
1. First login with /login command
2. Send me any Telegram post link
3. I'll download and forward it to you!

💡 ғᴏʀ ʙᴀᴛᴄʜ ᴅᴏᴡɴʟᴏᴀᴅ, ᴜsᴇ ʀᴀɴɢᴇ: 
`https://t.me/channel/100-150`

ᴅᴇᴠᴇʟᴏᴘᴇʀ: @VJ_Botz</b>"""

HELP_TXT = """<b>📖 ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅs

🤖 ᴄᴏᴍᴍᴀɴᴅs:
• /start - sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ
• /help - sʜᴏᴡ ᴛʜɪs ʜᴇʟᴘ
• /login - ʟᴏɢɪɴ ᴡɪᴛʜ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ
• /logout - ʟᴏɢᴏᴜᴛ ғʀᴏᴍ ᴀᴄᴄᴏᴜɴᴛ
• /cancel - ᴄᴀɴᴄᴇʟ ᴄᴜʀʀᴇɴᴛ ᴏᴘᴇʀᴀᴛɪᴏɴ

📖 ʜᴏᴡ ᴛᴏ ᴜsᴇ:
1. ʟᴏɢɪɴ ᴡɪᴛʜ /login ᴄᴏᴍᴍᴀɴᴅ ғɪʀsᴛ
2. sᴇɴᴅ ᴀɴʏ ᴛᴇʟᴇɢʀᴀᴍ ᴘᴏsᴛ ʟɪɴᴋ
3. ғᴏʀ sɪɴɢʟᴇ: `https://t.me/channel/123`
4. ғᴏʀ ʙᴀᴛᴄʜ: `https://t.me/channel/100-150`

🔗 ʟɪɴᴋ ғᴏʀᴍᴀᴛs sᴜᴘᴘᴏʀᴛᴇᴅ:
• `https://t.me/username/123`
• `https://t.me/c/123456789/123`  
• `https://t.me/b/123456789_123/123`

📦 ʙᴀᴛᴄʜ ᴅᴏᴡɴʟᴏᴀᴅ:
• ᴜsᴇ ғᴏʀᴍᴀᴛ: `link/start-end`
• ᴍᴀx ʙᴀᴛᴄʜ sɪᴢᴇ: 50 ᴍᴇssᴀɢᴇs
• ᴇxᴀᴍᴘʟᴇ: `https://t.me/channel/100-150`

ɴᴇᴇᴅ ʜᴇʟᴘ? ᴄᴏɴᴛᴀᴄᴛ: @VJ_Botz</b>"""

# Error messages dictionary
ERROR_MESSAGES = {
    'not_logged_in': """❌ **You're not logged in!**
    
Please use /login command first to authenticate with your Telegram account.

After logging in, you can send me any Telegram link to download content.""",

    'session_expired': """❌ **Your session has expired!**
    
Your login session is no longer valid. Please use /login command to authenticate again.

This can happen due to:
• Account security changes
• Long period of inactivity
• Session being revoked""",

    'invalid_link': """❌ **Invalid Telegram link!**
    
Please send a valid Telegram post link in one of these formats:
• `https://t.me/username/123`
• `https://t.me/c/123456789/123`
• `https://t.me/b/123456789_123/123`

For batch download, use range format:
• `https://t.me/username/100-150`""",

    'access_denied': """❌ **Access denied!**
    
Cannot access this channel or group because:
• Channel/group is private and you're not a member
• Content is restricted
• Channel/group doesn't exist

Make sure you're a member of the channel/group first.""",

    'file_too_large': """❌ **File too large!**
    
The file size exceeds the maximum limit. 

Please try:
• Smaller files
• Compress the file
• Split large files into smaller parts""",

    'download_failed': """❌ **Download failed!**
    
Failed to download the content due to:
• Network issues
• Server limitations
• File corruption
• Temporary restrictions

Please try again later.""",

    'rate_limited': """⏳ **Rate limited!**
    
Too many requests. Please wait before sending more links.

This helps prevent spam and ensures stable service for all users.""",

    'maintenance': """🔧 **Under maintenance!**
    
The bot is currently under maintenance. Please try again later.

Follow @Tech_VJ for updates.""",
    
    'unknown_error': """❌ **Unknown error occurred!**
    
An unexpected error happened. Please try again.

If the issue persists, contact: @VJ_Botz"""
}

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
