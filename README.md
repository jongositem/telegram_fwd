# Telegram Message Forwarder Bot

A Python bot that automatically forwards messages from Contact A to Contact B using Telegram's user account API. Designed for easy deployment with Docker.

## Features

- ✅ Automatically forwards all messages from a specific contact to another contact
- ✅ Supports usernames and user IDs
- ✅ Handles rate limiting automatically
- ✅ Comprehensive logging
- ✅ Easy configuration via environment variables
- ✅ **Docker support for containerized deployment**
- ✅ Persistent session storage

## Quick Start (Docker - Recommended)

### Prerequisites

- Docker and Docker Compose installed
- Telegram account
- Telegram API credentials

### 1. Get Telegram API Credentials

1. Go to https://my.telegram.org
2. Log in with your phone number
3. Click **"API development tools"**
4. Create a new application
5. Note down your `api_id` and `api_hash`

### 2. Configure

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

Fill in your `.env`:

```env
API_ID=12345678
API_HASH=your_api_hash_here
PHONE_NUMBER=+1234567890
CONTACT_A=@source_username
CONTACT_B=@destination_username
```

### 3. Deploy with Docker

```bash
# Build and start the bot
docker-compose up -d

# First run: authenticate interactively
docker-compose up

# Enter verification code when prompted
# After authentication, press Ctrl+C and run:
docker-compose up -d
```

### 4. Manage the Bot

```bash
# View logs
docker-compose logs -f

# Stop the bot
docker-compose down

# Restart the bot
docker-compose restart

# Check status
docker-compose ps
```

That's it! The bot is now running and will automatically forward messages from Contact A to Contact B.

## Alternative: Local Installation (without Docker)

If you prefer to run without Docker, use `uv` for fast dependency management:

### Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) package manager

### Install uv

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup

```bash
# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env

# Run
python bot.py
```

## Configuration Details

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `API_ID` | Telegram API ID (numeric) | `12345678` |
| `API_HASH` | Telegram API Hash | `abc123...` |
| `PHONE_NUMBER` | Your phone number with country code | `+1234567890` |
| `CONTACT_A` | Source contact (username or user ID) | `@john_doe` or `123456789` |
| `CONTACT_B` | Destination contact (username or user ID) | `@jane_doe` or `987654321` |

### Finding Contact Information

**Option 1: Username**
- Format: `@username` (include @)
- Example: `CONTACT_A=@john_doe`

**Option 2: User ID**
- Find using @userinfobot on Telegram
- Format: Just the number
- Example: `CONTACT_A=123456789`

## How It Works

```
Contact A sends message → Bot detects → Bot forwards to Contact B
```

The bot:
1. Logs into your Telegram account using Pyrogram
2. Resolves Contact A and Contact B to their user IDs
3. Monitors incoming private messages
4. When a message from Contact A arrives, forwards it to Contact B
5. Handles Telegram rate limits automatically
6. Logs all activities

## Project Structure

```
telegram_fwd/
├── Dockerfile              # Docker container definition
├── docker-compose.yml      # Docker orchestration
├── .dockerignore          # Docker build exclusions
├── bot.py                 # Main bot script
├── config.py              # Configuration loader
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project metadata
├── .env.example           # Configuration template
├── .env                   # Your credentials (gitignored)
├── .gitignore            # Git exclusions
├── DOCKER.md             # Detailed Docker guide
├── QUICKSTART.md         # Quick start guide
└── LICENSE               # MIT License
```

## Documentation

- **[DOCKER.md](DOCKER.md)** - Complete Docker deployment guide
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start for local installation
- **README.md** - This file

## Troubleshooting

### "Missing required configuration" error

Check that all fields in `.env` are filled correctly without quotes:

```env
# ✅ Correct
API_ID=12345678

# ❌ Wrong
API_ID="12345678"
```

### "Failed to resolve contacts" error

- Verify usernames are correct (include @ symbol)
- Ensure you've chatted with both contacts at least once
- Try using numeric user IDs instead

### Docker: Container keeps restarting

```bash
# Check logs
docker-compose logs telegram-forwarder

# Common fixes:
# 1. Verify .env configuration
# 2. Re-authenticate (delete sessions/ directory)
# 3. Check contact usernames/IDs are valid
```

### Authentication issues

**Docker:**
```bash
docker-compose down
rm -rf sessions/*.session*
docker-compose up  # Run interactively
```

**Local:**
```bash
rm telegram_forwarder.session*
python bot.py
```

### FloodWait errors

The bot automatically handles rate limiting. If it happens frequently:
- Reduce message frequency
- Wait a few hours
- Check if your account is restricted

## Security Notes

⚠️ **Important:**

- **Never share your API credentials or `.env` file**
- `.env` is gitignored - keep it that way!
- Session files contain sensitive data
- This bot uses your **personal Telegram account**
- Use responsibly and ethically
- Be aware of Telegram's Terms of Service

## Docker Security Best Practices

```bash
# Set proper permissions
chmod 600 .env

# Use Docker secrets in production
# See DOCKER.md for details
```

## Production Deployment

### Running 24/7 with Docker

Docker automatically restarts the container unless explicitly stopped:

```bash
# Set restart policy in docker-compose.yml
restart: unless-stopped  # Default
restart: always         # Always restart
```

### Resource Monitoring

```bash
# Check resource usage
docker stats telegram_forwarder_bot

# View logs with timestamps
docker-compose logs -t -f
```

### Backups

```bash
# Backup session files
cp -r sessions/ sessions_backup/

# Backup .env
cp .env .env.backup
```

## Advanced Usage

### Multiple Bot Instances

```bash
# Copy the directory
cp -r telegram_fwd telegram_fwd_2

# Edit the new .env with different contacts
cd telegram_fwd_2
nano .env

# Run with different project name
docker-compose -p bot2 up -d
```

### Custom Filtering

Edit `bot.py` to add message filtering:

```python
@app.on_message(filters.private & ~filters.me)
async def forward_message(client: Client, message: Message):
    if message.from_user.id == contact_a_id:
        # Add custom logic here
        if message.text and "important" in message.text.lower():
            await message.forward(contact_b_id)
```

## Legal & Ethics

⚠️ **Important Disclaimers:**

- For **educational and personal use only**
- Get **explicit permission** before forwarding messages
- Respect **privacy** and Telegram's Terms of Service
- Unauthorized forwarding may violate privacy laws
- Authors not responsible for misuse

## Contributing

Contributions welcome! Feel free to:
- Submit bug reports
- Request features
- Improve documentation
- Submit pull requests

## Technologies Used

- **[Pyrogram](https://docs.pyrogram.org/)** - Telegram MTProto API Framework
- **[TgCrypto](https://github.com/pyrogram/tgcrypto)** - Fast encryption for Pyrogram
- **[python-dotenv](https://github.com/theskumar/python-dotenv)** - Environment management
- **[Docker](https://www.docker.com/)** - Containerization platform
- **[uv](https://github.com/astral-sh/uv)** - Fast Python package manager

## FAQ

**Q: Can I forward messages from multiple contacts?**
A: Currently supports one A→B pair. Run multiple instances for multiple pairs.

**Q: Does this work with groups/channels?**
A: Currently only private messages. Group support requires modifications.

**Q: Will contacts know their messages are forwarded?**
A: Yes, Telegram shows "Forwarded from" label on forwarded messages.

**Q: Is this a bot account or user account?**
A: **User account** - that's why it can access and forward messages between contacts.

**Q: How much does it cost to run?**
A: Free! Uses minimal resources (~50-100MB RAM, minimal CPU).

**Q: Can I run on Raspberry Pi?**
A: Yes! Docker supports ARM architecture.

**Q: What if I want to modify messages before forwarding?**
A: Edit the `forward_message()` function in `bot.py` to customize behavior.

## Support

Having issues?

1. Check troubleshooting section above
2. Review logs: `docker-compose logs -f`
3. Read [DOCKER.md](DOCKER.md) for Docker-specific help
4. Verify API credentials are valid
5. Ensure contacts exist and are accessible

## License

MIT License - See [LICENSE](LICENSE) file

## Acknowledgments

Built with ❤️ for Telegram automation enthusiasts.

Special thanks to:
- Pyrogram developers for excellent Telegram API framework
- Docker community for containerization best practices
- uv team for blazing-fast Python package management

---

**Ready to forward! 🚀**

Star ⭐ this repo if you find it useful!