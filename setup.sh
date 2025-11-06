#!/bin/bash

# Telegram Forwarder Bot - Setup Script
# This script automates the initial setup process

set -e

echo "🚀 Telegram Forwarder Bot - Setup Script"
echo "=========================================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed!"
    echo ""
    echo "Please install uv first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    exit 1
fi

echo "✅ uv is installed"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
uv venv

echo "✅ Virtual environment created"
echo ""

# Activate virtual environment and install dependencies
echo "📥 Installing dependencies..."
source .venv/bin/activate
uv pip install -r requirements.txt

echo "✅ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit the .env file with your credentials!"
    echo ""
    echo "You need to:"
    echo "  1. Get API credentials from https://my.telegram.org"
    echo "  2. Edit .env and fill in:"
    echo "     - API_ID"
    echo "     - API_HASH"
    echo "     - PHONE_NUMBER"
    echo "     - CONTACT_A"
    echo "     - CONTACT_B"
    echo ""
    echo "Run: nano .env  (or use your preferred editor)"
else
    echo "ℹ️  .env file already exists, skipping..."
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env file: nano .env"
echo "  2. Activate venv: source .venv/bin/activate"
echo "  3. Run the bot: python bot.py"
echo ""
