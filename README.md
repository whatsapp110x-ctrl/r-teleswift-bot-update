R-TeleSwift💖Bot

Welcome to R-TeleSwift💖Bot, a powerful and efficient Telegram bot designed to streamline the process of downloading restricted content with ease. Built with Flask and Pyrogram, this bot serves as a bridge between web-based and Telegram-based content access, providing users with an intuitive experience for downloading files and media.

💡 Features

Restricted Content Access: Seamlessly download content from Telegram using provided API credentials and bot token.

Concurrent Operations: Flask web app and Telegram bot run concurrently, ensuring smooth operation across platforms.

Logging & Monitoring: Built-in logging for monitoring activities and errors in the bot's operations.

MongoDB Integration: Handles user data and interactions securely via MongoDB.

Admin Panel: Includes admin controls for managing broadcasts and access permissions.



---

🚀 Getting Started

Prerequisites

Ensure you have the following:

Python 3.8+

MongoDB Atlas Account (for database management)

Telegram Bot Token from BotFather

Telegram API ID and API Hash from my.telegram.org


1. Clone the Repository

git clone https://github.com/whatsapp110x-ctrl/r-teleswift-bot-update

cd r-teleswift-bot-update

2. Install Dependencies

pip install -r requirements.txt

3. Set Up Environment Variables

Create a .env file in the root directory and include the following variables:

BOT_TOKEN=<your_telegram_bot_token>
API_ID=<your_telegram_api_id>
API_HASH=<your_telegram_api_hash>
ADMINS=<admin_telegram_user_id>
DB_URI=<your_mongo_database_url>
DB_NAME=<your_database_name>

4. Run the Bot

Start the bot with:

python main.py

This will start both the Flask web app and the Telegram bot concurrently.


---
