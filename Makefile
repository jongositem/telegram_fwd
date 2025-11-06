.PHONY: help build up down restart logs status clean setup auth rebuild

# Default target
help:
	@echo "Telegram Forwarder Bot - Docker Commands"
	@echo "========================================"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup      - Initial setup (copy .env.example)"
	@echo "  make build      - Build Docker image"
	@echo "  make up         - Start bot in background"
	@echo "  make auth       - Start bot interactively for authentication"
	@echo "  make down       - Stop bot"
	@echo "  make restart    - Restart bot"
	@echo "  make logs       - View logs (follow mode)"
	@echo "  make status     - Check bot status"
	@echo "  make rebuild    - Rebuild and restart bot"
	@echo "  make clean      - Stop bot and remove volumes"
	@echo "  make reset      - Delete session and re-authenticate"
	@echo ""

# Initial setup
setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ .env file created"; \
		echo "⚠️  Edit .env with your credentials!"; \
		echo "   nano .env"; \
	else \
		echo "ℹ️  .env already exists"; \
	fi
	@mkdir -p sessions
	@echo "✅ Setup complete"

# Build Docker image
build:
	@echo "🔨 Building Docker image..."
	docker-compose build

# Start bot in background
up:
	@echo "🚀 Starting bot..."
	docker-compose up -d
	@echo "✅ Bot started in background"
	@echo "   View logs: make logs"

# Start bot interactively (for first authentication)
auth:
	@echo "🔐 Starting bot for authentication..."
	@echo "   Enter verification code when prompted"
	@echo "   Press Ctrl+C after authentication completes"
	docker-compose up

# Stop bot
down:
	@echo "🛑 Stopping bot..."
	docker-compose down
	@echo "✅ Bot stopped"

# Restart bot
restart:
	@echo "🔄 Restarting bot..."
	docker-compose restart
	@echo "✅ Bot restarted"

# View logs
logs:
	@echo "📋 Viewing logs (Ctrl+C to exit)..."
	docker-compose logs -f telegram-forwarder

# Check status
status:
	@echo "📊 Bot status:"
	@docker-compose ps
	@echo ""
	@echo "💾 Resource usage:"
	@docker stats telegram_forwarder_bot --no-stream || echo "Bot not running"

# Rebuild and restart
rebuild:
	@echo "🔨 Rebuilding bot..."
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d
	@echo "✅ Bot rebuilt and started"

# Clean up everything
clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	@echo "✅ Cleanup complete"

# Reset authentication
reset:
	@echo "🔄 Resetting authentication..."
	@read -p "Delete session files? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down; \
		rm -rf sessions/*.session*; \
		echo "✅ Session deleted"; \
		echo "   Run 'make auth' to re-authenticate"; \
	else \
		echo "❌ Cancelled"; \
	fi

# Quick start (for first-time users)
quickstart: setup
	@echo ""
	@echo "📝 Next steps:"
	@echo "   1. Edit .env with your credentials: nano .env"
	@echo "   2. Authenticate: make auth"
	@echo "   3. After auth, start in background: make up"
	@echo ""
