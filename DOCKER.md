# Docker Deployment Guide

Deploy the Telegram Message Forwarder Bot using Docker for easy, containerized deployment.

## Prerequisites

- Docker installed (version 20.10 or higher)
- Docker Compose installed (version 2.0 or higher)
- Telegram API credentials
- 5 minutes ⏱️

## Quick Start

### 1. Get Telegram API Credentials

1. Go to https://my.telegram.org
2. Log in with your phone number
3. Click **"API development tools"**
4. Create a new application
5. Copy your `api_id` and `api_hash`

### 2. Configure Environment

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
API_ID=12345678
API_HASH=your_api_hash_here
PHONE_NUMBER=+1234567890
CONTACT_A=@source_username
CONTACT_B=@destination_username
```

### 3. Build and Run

```bash
# Build the Docker image
docker-compose build

# Start the container
docker-compose up -d
```

### 4. First Time Authentication

On first run, you need to authenticate:

```bash
# View logs and enter verification code
docker-compose logs -f telegram-forwarder
```

When prompted, the container will ask for:
1. Verification code (sent to your Telegram)
2. Password (if 2FA is enabled)

**Note:** You need to interact with the container during first authentication:

```bash
# Attach to the container for interactive authentication
docker-compose up
```

After authentication, the session is saved in the `sessions/` directory and persists across container restarts.

## Docker Commands

### Start the bot
```bash
docker-compose up -d
```

### Stop the bot
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f telegram-forwarder
```

### Restart the bot
```bash
docker-compose restart
```

### Rebuild after code changes
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Check status
```bash
docker-compose ps
```

### Remove everything (including volumes)
```bash
docker-compose down -v
```

## Directory Structure

```
telegram_fwd/
├── Dockerfile              # Container definition
├── docker-compose.yml      # Orchestration config
├── .dockerignore          # Files to exclude from image
├── .env                   # Your credentials (not in git)
├── .env.example           # Template
├── bot.py                 # Main bot script
├── config.py              # Configuration loader
├── requirements.txt       # Python dependencies
└── sessions/              # Persistent session data (created automatically)
```

## Advanced Configuration

### Custom Docker Compose

Edit `docker-compose.yml` to customize:

**Change resource limits:**
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'      # Increase CPU
      memory: 1024M    # Increase memory
```

**Change restart policy:**
```yaml
restart: always         # Always restart
restart: on-failure    # Restart only on failure
restart: unless-stopped # Default
```

**Add additional environment variables:**
```yaml
environment:
  - TZ=America/New_York
  - LOG_LEVEL=DEBUG
```

### Building Without Docker Compose

```bash
# Build image
docker build -t telegram-forwarder .

# Run container
docker run -d \
  --name telegram_forwarder \
  --env-file .env \
  -v $(pwd)/sessions:/app/sessions \
  --restart unless-stopped \
  telegram-forwarder
```

### Running on Different Platforms

**ARM Architecture (Raspberry Pi, Apple Silicon):**
```bash
docker-compose build --build-arg ARCH=arm64
docker-compose up -d
```

**Multi-platform build:**
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t telegram-forwarder .
```

## Troubleshooting

### Container keeps restarting

Check logs:
```bash
docker-compose logs telegram-forwarder
```

Common causes:
- Missing or invalid `.env` configuration
- Failed authentication (delete `sessions/` and re-authenticate)
- Invalid contact usernames/IDs

### Authentication issues

Re-authenticate:
```bash
# Stop container
docker-compose down

# Remove old sessions
rm -rf sessions/*.session*

# Start interactively to enter verification code
docker-compose up
```

### Can't see logs

```bash
# Follow logs in real-time
docker-compose logs -f

# Show last 100 lines
docker-compose logs --tail=100

# Show logs with timestamps
docker-compose logs -t
```

### Session not persisting

Make sure `sessions/` directory exists and has correct permissions:
```bash
mkdir -p sessions
chmod 755 sessions
```

### Permission denied errors

```bash
# Fix permissions
sudo chown -R $USER:$USER sessions/
```

### Out of memory errors

Increase memory limits in `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 1024M
```

## Production Deployment

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml telegram-forwarder

# Check status
docker stack services telegram-forwarder
```

### Using Kubernetes

Create a deployment:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: telegram-forwarder
spec:
  replicas: 1
  selector:
    matchLabels:
      app: telegram-forwarder
  template:
    metadata:
      labels:
        app: telegram-forwarder
    spec:
      containers:
      - name: bot
        image: telegram-forwarder:latest
        envFrom:
        - secretRef:
            name: telegram-secrets
        volumeMounts:
        - name: sessions
          mountPath: /app/sessions
      volumes:
      - name: sessions
        persistentVolumeClaim:
          claimName: telegram-sessions
```

### Health Checks

Add to `Dockerfile`:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"
```

### Automated Backups

Backup session files:
```bash
#!/bin/bash
# backup-sessions.sh
docker-compose exec telegram-forwarder tar czf /app/sessions/backup.tar.gz *.session
docker cp telegram_forwarder_bot:/app/sessions/backup.tar.gz ./backups/
```

## Security Best Practices

### 1. Protect Environment Variables

```bash
# Set proper permissions on .env
chmod 600 .env
```

### 2. Use Docker Secrets (Swarm/Compose v3.1+)

```yaml
services:
  telegram-forwarder:
    secrets:
      - api_credentials
    environment:
      API_ID_FILE: /run/secrets/api_credentials

secrets:
  api_credentials:
    file: ./secrets/api_credentials.txt
```

### 3. Run as Non-Root User

Add to `Dockerfile`:
```dockerfile
RUN useradd -m -u 1000 botuser
USER botuser
```

### 4. Network Isolation

```yaml
services:
  telegram-forwarder:
    networks:
      - bot-network

networks:
  bot-network:
    driver: bridge
```

## Monitoring

### Docker Stats

```bash
docker stats telegram_forwarder_bot
```

### Log Aggregation

Use logging drivers:
```yaml
logging:
  driver: "syslog"
  options:
    syslog-address: "tcp://logserver:514"
```

### Prometheus Metrics

Add metrics endpoint to bot and expose:
```yaml
ports:
  - "9090:9090"  # Metrics port
```

## Updates and Maintenance

### Updating the Bot

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Cleaning Up

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Full cleanup
docker system prune -a --volumes
```

## FAQ

**Q: Can I run multiple bots?**
A: Yes, copy the directory and use different container names:
```bash
docker-compose -p bot1 up -d
docker-compose -p bot2 up -d
```

**Q: How do I backup my bot?**
A: Backup the `sessions/` directory and `.env` file regularly.

**Q: Can I run this on a VPS?**
A: Yes! This works perfectly on any Linux VPS with Docker installed.

**Q: Does this work on ARM (Raspberry Pi)?**
A: Yes, the Python base image supports ARM architecture.

**Q: How much resources does it need?**
A: Very minimal - 128MB RAM and minimal CPU when idle.

## Support

For issues:
1. Check logs: `docker-compose logs`
2. Verify `.env` configuration
3. Ensure Docker/Docker Compose are up to date
4. Check the main [README.md](README.md) for general troubleshooting

---

**Ready to deploy! 🐳**