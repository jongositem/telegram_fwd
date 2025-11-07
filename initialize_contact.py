#!/usr/bin/env python3
"""Initialize contact - creates chat with Contact B"""

import asyncio
from pyrogram import Client
from config import Config

async def initialize_contact():
    app = Client(
        "telegram_forwarder",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        phone_number=Config.PHONE_NUMBER
    )

    await app.start()
    print("✅ Bot connected\n")

    try:
        # Resolve Contact B
        contact_b = Config.CONTACT_B
        if contact_b.startswith('@'):
            contact_b = contact_b[1:]

        print(f"🔍 Looking up Contact B: {contact_b}")
        user_b = await app.get_users(contact_b)

        print(f"✅ Found: {user_b.first_name} {user_b.last_name or ''}")
        print(f"   Username: @{user_b.username or 'N/A'}")
        print(f"   ID: {user_b.id}")
        print()

        # Check if chat already exists
        print("🔍 Checking for existing chat...")
        try:
            chat = await app.get_chat(user_b.id)
            print(f"✅ Chat already exists with {chat.first_name}")
            print()
        except Exception:
            print("⚠️  No existing chat found")
            print()

            # Send a message to create the chat
            print(f"📤 Sending initialization message to {user_b.first_name}...")
            try:
                await app.send_message(
                    user_b.id,
                    "👋 Hi! This is an automated message from my Telegram forwarder bot. "
                    "You can safely ignore this message."
                )
                print("✅ Message sent! Chat initialized.")
                print()
            except Exception as e:
                print(f"❌ Could not send message: {e}")
                print()
                print("💡 Possible reasons:")
                print("   - User has privacy settings preventing messages from non-contacts")
                print("   - User blocked you")
                print("   - User doesn't accept messages from unknown users")
                print()
                print("🔧 Manual fix required:")
                print(f"   1. Open Telegram")
                print(f"   2. Search for: @{user_b.username or user_b.id}")
                print(f"   3. Send them a message manually")
                print()
                await app.stop()
                return

        # Verify we can now access the user
        print("🔍 Verifying bot can access contact...")
        try:
            peer = await app.resolve_peer(user_b.id)
            print(f"✅ Contact B is now accessible!")
            print(f"   Peer ID: {peer.user_id if hasattr(peer, 'user_id') else peer}")
            print()
            print("🎉 Initialization complete!")
            print("   You can now start the forwarder bot.")
        except Exception as e:
            print(f"⚠️  Still having issues: {e}")
            print()
            print("Please manually send a message to Contact B in Telegram.")

    except Exception as e:
        print(f"❌ Error: {e}")

    await app.stop()

if __name__ == "__main__":
    asyncio.run(initialize_contact())
