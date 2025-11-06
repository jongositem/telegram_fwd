# Telegram Message Forwarder Bot

A Python bot that automatically forwards messages from Contact A to Contact B using Telegram's user account API.

## Features

- ✅ Automatically forwards all messages from a specific contact to another contact
- ✅ Supports usernames and user IDs
- ✅ Handles rate limiting automatically
- ✅ Comprehensive logging
- ✅ Easy configuration via environment variables
- ✅ Uses `uv` for fast dependency management

## Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- A Telegram account
- Telegram API credentials (API ID and API Hash)

## Installation

### 1. Install uv (if not already installed)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Get Telegram API Credentials

1. Go to https://my.telegram.org
2. Log in with your phone number
3. Click on "API development tools"
4. Create a new application (if you haven't already)
5. Note down your `api_id` and `api_hash`

### 3. Clone/Navigate to the Project

```bash
cd telegram_fwd
```

### 4. Create Virtual Environment and Install Dependencies

Using `uv`:

```bash
# Create virtual environment
uv venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

Alternatively, install dependencies directly with uv:

```bash
uv pip install pyrogram TgCrypto python-dotenv
```

### 5. Configure the Bot

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your credentials:
   ```env
   API_ID=12345678
   API_HASH=abcdef1234567890abcdef1234567890
   PHONE_NUMBER=+1234567890
   CONTACT_A=@source_username
   CONTACT_B=@destination_username
   ```

   **Configuration Details:**
   - `API_ID`: Your Telegram API ID (numeric)
   - `API_HASH`: Your Telegram API Hash (32-character string)
   - `PHONE_NUMBER`: Your Telegram phone number with country code (e.g., +1234567890)
   - `CONTACT_A`: The username (with @) or user ID of the person whose messages you want to forward
   - `CONTACT_B`: The username (with @) or user ID of the person to forward messages to

## Usage

### Start the Bot

Make sure your virtual environment is activated, then run:

```bash
python bot.py
```

### First Run Authentication

On the first run, you'll be prompted to:
1. Enter the verification code sent to your Telegram account
2. If you have 2FA enabled, enter your password

The session will be saved, so you won't need to authenticate again unless you delete the session file.

### What Happens

1. The bot logs into your Telegram account
2. It resolves Contact A and Contact B to their user IDs
3. It starts monitoring incoming messages
4. When a message arrives from Contact A, it automatically forwards it to Contact B
5. All activities are logged to the console

## How It Works

```
Contact A sends message → Bot detects message → Bot forwards to Contact B
```

The bot uses:
- **Pyrogram**: A modern, elegant and async Telegram client library
- **TgCrypto**: Fast encryption library for Pyrogram
- **python-dotenv**: Environment variable management

## Project Structure

```
telegram_fwd/
├── bot.py              # Main bot script
├── config.py           # Configuration loader
├── requirements.txt    # Python dependencies
├── pyproject.toml      # uv/pip project configuration
├── .env.example        # Environment template
├── .env                # Your credentials (not in git)
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Security Notes

⚠️ **Important Security Information:**

- **Never share your API credentials or .env file**
- The `.env` file is already in `.gitignore` - don't commit it!
- This bot uses your personal Telegram account
- Session files contain sensitive data - keep them secure
- Be aware of Telegram's rate limits and terms of service
- Use this bot responsibly and ethically

## Troubleshooting

### "Missing required configuration" error

**Solution:** Make sure all fields in `.env` are filled correctly without extra spaces or quotes.

```env
# ✅ Correct
API_ID=12345678

# ❌ Wrong
API_ID="12345678"
API_ID = 12345678 
```

### "Failed to resolve contacts" error

**Possible causes:**
- Username is incorrect or doesn't exist
- User ID is invalid
- You don't have an existing conversation with the contact

**Solution:** 
- Verify usernames include the @ symbol
- Ensure you've chatted with both contacts at least once
- Try using numeric user IDs instead of usernames

### FloodWait errors

**What it means:** Telegram is rate-limiting your requests

**Solution:** The bot automatically handles this by waiting. If it happens frequently:
- Reduce message frequency
- Wait a few hours before retrying
- Check if you're being rate-limited on your account

### "No module named 'pyrogram'" error

**Solution:** Make sure your virtual environment is activated and dependencies are installed:

```bash
source .venv/bin/activate  # On macOS/Linux
uv pip install -r requirements.txt
```

### Session file issues

If you encounter authentication problems:

1. Delete the session file:
   ```bash
   rm telegram_forwarder.session*
   ```

2. Run the bot again and re-authenticate

## Advanced Usage

### Using User IDs Instead of Usernames

If you know the user IDs, you can use them directly in `.env`:

```env
CONTACT_A=123456789
CONTACT_B=987654321
```

To find a user ID, you can use bots like @userinfobot on Telegram.

### Running as a Service

To keep the bot running 24/7, consider using:

**On Linux (systemd):**
Create a service file at `/etc/systemd/system/telegram-forwarder.service`

**Using screen/tmux:**
```bash
screen -S telegram_bot
python bot.py
# Press Ctrl+A, then D to detach
```

**Using nohup:**
```bash
nohup python bot.py > bot.log 2>&1 &
```

## Stopping the Bot

Press `Ctrl+C` to stop the bot gracefully.

## Common Use Cases

- 📱 Forward work messages to personal account
- 🔔 Create message backups
- 📊 Monitor important contacts
- 🤖 Integrate with other automation workflows

## Legal & Ethics

⚠️ **Important Disclaimers:**

- This bot is for **educational and personal use only**
- Always get **explicit permission** before forwarding someone's messages
- Respect **privacy** and Telegram's Terms of Service
- Unauthorized message forwarding may violate privacy laws in your jurisdiction
- The authors are not responsible for misuse of this software

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - See LICENSE file for details

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs for error messages
3. Ensure your Telegram API credentials are valid
4. Verify that both contacts exist and are accessible

## FAQ

**Q: Can I forward messages from multiple contacts?**
A: Currently, the bot supports one Contact A → Contact B pair. You'd need to run multiple instances for multiple pairs.

**Q: Does this work with groups/channels?**
A: The current version only supports private messages. Group/channel support would require modifications.

**Q: Will contacts know their messages are being forwarded?**
A: Forwarded messages show a "Forwarded from" label in Telegram, so yes, Contact B will see the messages are forwarded.

**Q: Can I modify messages before forwarding?**
A: Yes! Modify the `forward_message` function in `bot.py` to edit message content before forwarding.

**Q: Is this a bot account or user account?**
A: This uses your **user account**, not a bot account. That's why it can forward messages between contacts.

## Acknowledgments

Built with:
- [Pyrogram](https://docs.pyrogram.org/) - Telegram MTProto API Framework
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Environment variable management

---

**Made with ❤️ for Telegram automation enthusiasts**