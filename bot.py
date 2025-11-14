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
import os
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

# Determine session file path
# Priority: 1. /app/sessions/ (Docker), 2. Current directory
SESSION_NAME = "telegram_forwarder"

def get_session_path():
    """Determine the correct session file path"""
    # Check Docker location first
    docker_session = f"/app/sessions/{SESSION_NAME}.session"
    if os.path.exists(docker_session):
        logger.info(f"✅ Found session in Docker volume: {docker_session}")
        return f"/app/sessions/{SESSION_NAME}"

    # Check if we're in Docker but session doesn't exist yet
    if os.path.exists('/app/sessions'):
        logger.info(f"📁 Using Docker session path (new session): /app/sessions/{SESSION_NAME}")
        return f"/app/sessions/{SESSION_NAME}"

    # Check local directory
    local_session = f"{SESSION_NAME}.session"
    if os.path.exists(local_session):
        logger.info(f"✅ Found local session: {local_session}")
        return SESSION_NAME

    # Default to local
    logger.info(f"📁 Using local session path (new session): {SESSION_NAME}")
    return SESSION_NAME

SESSION_PATH = get_session_path()

# Initialize the Pyrogram client (user account)
app = Client(
    SESSION_PATH,
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
            user_id = int(identifier)
            # Verify the user exists
            try:
                user = await client.get_users(user_id)
                logger.info(f"✅ Resolved user ID {user_id}: {user.first_name}")
                return user_id
            except Exception as e:
                logger.error(f"❌ User ID {user_id} is invalid: {e}")
                return None

        # If it's a username, resolve it
        if identifier.startswith('@'):
            identifier = identifier[1:]

        user = await client.get_users(identifier)
        logger.info(f"✅ Resolved @{identifier}: {user.first_name} (ID: {user.id})")
        return user.id
    except Exception as e:
        logger.error(f"❌ Error resolving contact {identifier}: {e}")
        return None


async def cache_peer(client: Client, user_id: int, name: str):
    """
    Attempt to cache peer by fetching dialogs
    """
    try:
        logger.info(f"Caching {name}...")

        # Try direct resolve
        try:
            await client.resolve_peer(user_id)
            logger.info(f"✅ {name} peer already cached")
            return True
        except:
            pass

        # Fetch dialogs to populate cache
        logger.info(f"Fetching dialogs to cache {name}...")
        dialog_count = 0
        found = False

        async for dialog in client.get_dialogs(limit=100):
            dialog_count += 1
            if dialog.chat.id == user_id:
                found = True
                logger.info(f"✅ Found {name} in dialogs (position {dialog_count})")
                break

        if found:
            await asyncio.sleep(1)
            await client.resolve_peer(user_id)
            logger.info(f"✅ {name} peer cached successfully")
            return True
        else:
            logger.warning(f"⚠️  {name} not found in recent dialogs")
            return False

    except Exception as e:
        logger.warning(f"⚠️  Could not cache {name}: {e}")
        return False


@app.on_message(filters.private & ~filters.me)
async def forward_message(client: Client, message: Message):
    """
    Forward messages from Contact A to Contact B
    """
    global contact_a_id, contact_b_id

    if message.from_user.id == contact_a_id:
        try:
            logger.info(f"📨 Received message from {message.from_user.first_name} (ID: {contact_a_id})")

            # Try forward first
            try:
                await message.forward(contact_b_id)
                logger.info(f"✅ Message forwarded to Contact B (ID: {contact_b_id})")
                return

            except Exception as forward_error:
                if "PEER_ID_INVALID" in str(forward_error) or "peer" in str(forward_error).lower():
                    logger.warning(f"⚠️  Forward failed, trying copy method")

                    # Copy based on message type
                    if message.text:
                        await client.send_message(contact_b_id, message.text)
                        logger.info(f"✅ Text message copied to Contact B")
                    elif message.photo:
                        await client.send_photo(contact_b_id, message.photo.file_id, caption=message.caption or "")
                        logger.info(f"✅ Photo copied to Contact B")
                    elif message.video:
                        await client.send_video(contact_b_id, message.video.file_id, caption=message.caption or "")
                        logger.info(f"✅ Video copied to Contact B")
                    elif message.document:
                        await client.send_document(contact_b_id, message.document.file_id, caption=message.caption or "")
                        logger.info(f"✅ Document copied to Contact B")
                    elif message.voice:
                        await client.send_voice(contact_b_id, message.voice.file_id)
                        logger.info(f"✅ Voice copied to Contact B")
                    elif message.audio:
                        await client.send_audio(contact_b_id, message.audio.file_id, caption=message.caption or "")
                        logger.info(f"✅ Audio copied to Contact B")
                    elif message.sticker:
                        await client.send_sticker(contact_b_id, message.sticker.file_id)
                        logger.info(f"✅ Sticker copied to Contact B")
                    else:
                        await message.copy(contact_b_id)
                        logger.info(f"✅ Message copied to Contact B")
                else:
                    raise forward_error

        except FloodWait as e:
            logger.warning(f"⏳ FloodWait: sleeping for {e.value} seconds")
            await asyncio.sleep(e.value)
            try:
                await message.copy(contact_b_id)
                logger.info(f"✅ Message copied after FloodWait")
            except Exception as retry_error:
                logger.error(f"❌ Failed after FloodWait: {retry_error}")

        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")


async def main():
    """Main function to start the bot"""
    global contact_a_id, contact_b_id

    # Check for session file
    session_file = f"{SESSION_PATH}.session"
    if os.path.exists(session_file):
        logger.info(f"✅ Session file exists: {session_file}")
    else:
        logger.error(f"❌ Session file NOT found: {session_file}")
        logger.error(f"   Expected location: {session_file}")
        logger.error(f"   Current directory: {os.getcwd()}")
        logger.error(f"   Files in current directory:")
        for f in os.listdir(os.getcwd()):
            logger.error(f"     - {f}")

        if os.path.exists('/app/sessions'):
            logger.error(f"   Files in /app/sessions:")
            for f in os.listdir('/app/sessions'):
                logger.error(f"     - {f}")

        logger.error("")
        logger.error("🔧 To fix this:")
        logger.error("   1. Stop the container: docker-compose down")
        logger.error("   2. Authenticate locally: python3 bot.py")
        logger.error("   3. Copy session: cp telegram_forwarder.session* sessions/")
        logger.error("   4. Restart Docker: docker-compose up -d")
        logger.error("")

        # Exit to prevent interactive prompt in Docker
        exit(1)

    try:
        await app.start()
        logger.info("🤖 Bot started successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        logger.error("   Session file may be corrupted or invalid")
        logger.error("   Delete sessions and re-authenticate")
        exit(1)

    # Resolve contacts
    logger.info("🔍 Resolving contacts...")
    contact_a_id = await get_contact_id(app, Config.CONTACT_A)
    contact_b_id = await get_contact_id(app, Config.CONTACT_B)

    if not contact_a_id or not contact_b_id:
        logger.error("❌ Failed to resolve contacts")
        await app.stop()
        return

    logger.info(f"📋 Contact A ID: {contact_a_id}")
    logger.info(f"📋 Contact B ID: {contact_b_id}")

    # Cache peers
    logger.info("🔄 Caching peer information...")
    await cache_peer(app, contact_a_id, "Contact A")
    await cache_peer(app, contact_b_id, "Contact B")

    logger.info("✅ Bot is ready!")
    logger.info("👂 Listening for messages from Contact A...")

    # Keep running
    await asyncio.Event().wait()


if __name__ == "__main__":
    app.run(main())
