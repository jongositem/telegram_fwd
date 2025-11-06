#!/usr/bin/env python3
"""
Telegram Message Forwarding Bot
Forwards messages from Contact A to Contact B automatically
"""

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
import asyncio
import logging
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate configuration
try:
    Config.validate()
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    exit(1)

# Initialize the Pyrogram client (user account)
app = Client(
    "telegram_forwarder",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    phone_number=Config.PHONE_NUMBER
)

# Store contact IDs (will be populated on startup)
contact_a_id = None
contact_b_id = None


async def get_contact_id(client: Client, identifier: str):
    """
    Get user ID from username or return the ID if already numeric
    """
    try:
        # If it's already a numeric ID
        if identifier.isdigit() or (identifier.startswith('-') and identifier[1:].isdigit()):
            return int(identifier)

        # If it's a username, resolve it
        if identifier.startswith('@'):
            identifier = identifier[1:]

        user = await client.get_users(identifier)
        return user.id
    except Exception as e:
        logger.error(f"Error resolving contact {identifier}: {e}")
        return None


@app.on_message(filters.private & ~filters.me)
async def forward_message(client: Client, message: Message):
    """
    Forward messages from Contact A to Contact B
    """
    global contact_a_id, contact_b_id

    # Check if the message is from Contact A
    if message.from_user.id == contact_a_id:
        try:
            logger.info(f"Forwarding message from {message.from_user.first_name} (ID: {contact_a_id})")

            # Forward the message to Contact B
            await message.forward(contact_b_id)

            logger.info(f"Message successfully forwarded to Contact B (ID: {contact_b_id})")

        except FloodWait as e:
            # Handle rate limiting
            logger.warning(f"FloodWait: sleeping for {e.value} seconds")
            await asyncio.sleep(e.value)
            await message.forward(contact_b_id)

        except Exception as e:
            logger.error(f"Error forwarding message: {e}")


async def main():
    """Main function to start the bot"""
    global contact_a_id, contact_b_id

    await app.start()
    logger.info("Bot started successfully!")

    # Resolve contact identifiers to user IDs
    logger.info("Resolving contacts...")
    contact_a_id = await get_contact_id(app, Config.CONTACT_A)
    contact_b_id = await get_contact_id(app, Config.CONTACT_B)

    if not contact_a_id or not contact_b_id:
        logger.error("Failed to resolve one or both contacts. Please check your configuration.")
        await app.stop()
        return

    logger.info(f"Contact A ID: {contact_a_id}")
    logger.info(f"Contact B ID: {contact_b_id}")
    logger.info("Listening for messages from Contact A...")

    # Keep the bot running
    await asyncio.Event().wait()


if __name__ == "__main__":
    app.run(main())
