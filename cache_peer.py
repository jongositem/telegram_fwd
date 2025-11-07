#!/usr/bin/env python3
"""Pre-cache Contact B peer in session"""

import asyncio
from pyrogram import Client
from config import Config

async def cache_peer():
    app = Client(
        "telegram_forwarder",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        phone_number=Config.PHONE_NUMBER
    )

    await app.start()
    print("✅ Bot connected\n")

    try:
        # Get Contact B
        contact_b = Config.CONTACT_B
        if contact_b.startswith('@'):
            contact_b = contact_b[1:]
        elif contact_b.isdigit():
            contact_b = int(contact_b)

        print(f"🔍 Getting Contact B information: {contact_b}")
        user_b = await app.get_users(contact_b)

        print(f"✅ Found: {user_b.first_name} {user_b.last_name or ''}")
        print(f"   ID: {user_b.id}")
        print()

        # Fetch dialogs to populate cache
        print("📥 Fetching recent dialogs...")
        dialog_count = 0
        found = False

        async for dialog in app.get_dialogs(limit=200):
            dialog_count += 1
            if dialog.chat.id == user_b.id:
                print(f"✅ Found Contact B in dialogs (position {dialog_count})")
                found = True

        print(f"   Fetched {dialog_count} dialogs total")
        print()

        if not found:
            print("⚠️  Contact B not found in recent dialogs")
            print("   This might cause issues. Attempting workaround...")
            print()

            # Send a dummy message to ourselves mentioning the user
            # This forces Telegram to cache the peer
            try:
                me = await app.get_me()
                await app.send_message(
                    me.id,
                    f"Bot initialization - caching peer {user_b.id}"
                )
                print("✅ Sent cache initialization message")
                await asyncio.sleep(2)
            except Exception as e:
                print(f"⚠️  Could not send initialization: {e}")

        # Try to resolve the peer directly
        print("🔍 Testing peer resolution...")
        try:
            peer = await app.resolve_peer(user_b.id)
            print(f"✅ Peer resolved successfully!")
            print(f"   Type: {type(peer).__name__}")
            print()
        except Exception as e:
            print(f"❌ Failed to resolve peer: {e}")
            print()
            print("💡 SOLUTION:")
            print("   The chat exists but peer isn't cached. Try this:")
            print()
            print("   1. From your Telegram account, send a message TO Contact B")
            print("   2. Wait for their reply (or just wait 30 seconds)")
            print("   3. Run this script again")
            print()
            await app.stop()
            return

        # Test if we can actually send to this peer
        print("🔍 Testing if we can interact with peer...")
        try:
            # Get chat history (doesn't send anything)
            async for message in app.get_chat_history(user_b.id, limit=1):
                print(f"✅ Can access chat history")
                break

            print()
            print("🎉 SUCCESS! Contact B is fully cached and accessible")
            print("   Your bot should now be able to forward messages")
            print()

        except Exception as e:
            print(f"⚠️  Cannot access chat: {e}")
            print()
            print("   Possible issues:")
            print("   - Privacy settings")
            print("   - Need to exchange messages first")
            print()

    except Exception as e:
        print(f"❌ Error: {e}")

    await app.stop()
    print("Done!")

if __name__ == "__main__":
    asyncio.run(cache_peer())
