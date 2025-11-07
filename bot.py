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

        # Method 1: Try direct resolve
        try:
            await client.resolve_peer(user_id)
            logger.info(f"✅ {name} peer already cached")
            return True
        except:
            pass

        # Method 2: Fetch dialogs to populate cache
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
            # Try resolve again
            await asyncio.sleep(1)
            await client.resolve_peer(user_id)
            logger.info(f"✅ {name} peer cached successfully")
            return True
        else:
            logger.warning(f"⚠️  {name} not found in recent dialogs")
            logger.warning(f"   Message forwarding may fail - ensure you have an active chat")
            return False

    except Exception as e:
        logger.warning(f"⚠️  Could not cache {name}: {e}")
        return False


@app.on_message(filters.private & ~filters.me)
async def forward_message(client: Client, message: Message):
    """
    Forward messages from Contact A to Contact B
    Uses message copying as fallback for peer resolution issues
    """
    global contact_a_id, contact_b_id

    # Check if the message is from Contact A
    if message.from_user.id == contact_a_id:
        try:
            logger.info(f"📨 Received message from {message.from_user.first_name} (ID: {contact_a_id})")

            # Try standard forward first (preserves "Forwarded from" label)
            try:
                await message.forward(contact_b_id)
                logger.info(f"✅ Message forwarded to Contact B (ID: {contact_b_id})")
                return

            except Exception as forward_error:
                # If forward fails due to peer issues, try copying instead
                if "PEER_ID_INVALID" in str(forward_error) or "peer" in str(forward_error).lower():
                    logger.warning(f"⚠️  Forward failed, trying copy method: {forward_error}")

                    # Copy message based on type
                    if message.text:
                        # Text message
                        await client.send_message(
                            contact_b_id,
                            message.text,
                            parse_mode=message.parse_mode
                        )
                        logger.info(f"✅ Text message copied to Contact B")

                    elif message.photo:
                        # Photo message
                        await client.send_photo(
                            contact_b_id,
                            message.photo.file_id,
                            caption=message.caption or "",
                            parse_mode=message.parse_mode
                        )
                        logger.info(f"✅ Photo copied to Contact B")

                    elif message.video:
                        # Video message
                        await client.send_video(
                            contact_b_id,
                            message.video.file_id,
                            caption=message.caption or "",
                            parse_mode=message.parse_mode
                        )
                        logger.info(f"✅ Video copied to Contact B")

                    elif message.document:
                        # Document/file message
                        await client.send_document(
                            contact_b_id,
                            message.document.file_id,
                            caption=message.caption or "",
                            parse_mode=message.parse_mode
                        )
                        logger.info(f"✅ Document copied to Contact B")

                    elif message.voice:
                        # Voice message
                        await client.send_voice(
                            contact_b_id,
                            message.voice.file_id,
                            caption=message.caption or ""
                        )
                        logger.info(f"✅ Voice message copied to Contact B")

                    elif message.audio:
                        # Audio message
                        await client.send_audio(
                            contact_b_id,
                            message.audio.file_id,
                            caption=message.caption or "",
                            parse_mode=message.parse_mode
                        )
                        logger.info(f"✅ Audio copied to Contact B")

                    elif message.sticker:
                        # Sticker
                        await client.send_sticker(
                            contact_b_id,
                            message.sticker.file_id
                        )
                        logger.info(f"✅ Sticker copied to Contact B")

                    elif message.animation:
                        # GIF/Animation
                        await client.send_animation(
                            contact_b_id,
                            message.animation.file_id,
                            caption=message.caption or ""
                        )
                        logger.info(f"✅ Animation copied to Contact B")

                    elif message.video_note:
                        # Video note (round video)
                        await client.send_video_note(
                            contact_b_id,
                            message.video_note.file_id
                        )
                        logger.info(f"✅ Video note copied to Contact B")

                    elif message.location:
                        # Location
                        await client.send_location(
                            contact_b_id,
                            latitude=message.location.latitude,
                            longitude=message.location.longitude
                        )
                        logger.info(f"✅ Location copied to Contact B")

                    elif message.contact:
                        # Contact card
                        await client.send_contact(
                            contact_b_id,
                            phone_number=message.contact.phone_number,
                            first_name=message.contact.first_name,
                            last_name=message.contact.last_name or ""
                        )
                        logger.info(f"✅ Contact copied to Contact B")

                    elif message.poll:
                        # Poll
                        logger.warning(f"⚠️  Polls cannot be copied - skipping")

                    else:
                        # Fallback: use generic copy
                        await message.copy(contact_b_id)
                        logger.info(f"✅ Message copied to Contact B (generic)")

                else:
                    # If it's a different error, re-raise it
                    raise forward_error

        except FloodWait as e:
            # Handle rate limiting
            logger.warning(f"⏳ FloodWait: sleeping for {e.value} seconds")
            await asyncio.sleep(e.value)

            # Retry with copy method
            try:
                await message.copy(contact_b_id)
                logger.info(f"✅ Message copied to Contact B after FloodWait")
            except Exception as retry_error:
                logger.error(f"❌ Failed to send after FloodWait: {retry_error}")

        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")

            # Provide helpful troubleshooting info
            if "PEER_ID_INVALID" in str(e):
                logger.error(f"   💡 Contact B (ID: {contact_b_id}) is not accessible")
                logger.error(f"   Solutions:")
                logger.error(f"   1. Ensure you have an active chat with Contact B")
                logger.error(f"   2. Send Contact B a message manually in Telegram")
                logger.error(f"   3. Ask Contact B to send you a message")
                logger.error(f"   4. Restart the bot after establishing contact")


async def main():
    """Main function to start the bot"""
    global contact_a_id, contact_b_id

    await app.start()
    logger.info("🤖 Bot started successfully!")

    # Resolve contact identifiers to user IDs
    logger.info("🔍 Resolving contacts...")
    contact_a_id = await get_contact_id(app, Config.CONTACT_A)
    contact_b_id = await get_contact_id(app, Config.CONTACT_B)

    if not contact_a_id or not contact_b_id:
        logger.error("❌ Failed to resolve one or both contacts. Please check your configuration.")
        await app.stop()
        return

    logger.info(f"📋 Contact A ID: {contact_a_id}")
    logger.info(f"📋 Contact B ID: {contact_b_id}")

    # Attempt to cache peers
    logger.info("🔄 Attempting to cache peer information...")
    await cache_peer(app, contact_a_id, "Contact A")
    await cache_peer(app, contact_b_id, "Contact B")

    logger.info("✅ Bot is ready!")
    logger.info("👂 Listening for messages from Contact A...")
    logger.info("")
    logger.info("📝 Note: If forwarding fails, the bot will automatically")
    logger.info("   try copying the message instead (without 'Forwarded from' label)")
    logger.info("")

    # Keep the bot running
    await asyncio.Event().wait()


if __name__ == "__main__":
    app.run(main())
