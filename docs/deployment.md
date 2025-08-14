# 🚀 Production Deployment Guide

## Overview

This guide covers deploying Story Agent to production environments with scalability, security, and reliability considerations.

## Deployment Architecture Options

### Option 1: Single Server Deployment (Small Scale)

```mermaid
graph TB
    subgraph "Production Server"
        LB[Nginx Load Balancer]
        WSGI[Gunicorn WSGI Server]
        Django[Django Application]
        Redis[Redis Cache/Sessions]
        PG[(PostgreSQL Database)]
        Media[Media Storage]
        Ollama[Ollama LLM Server]
        SD[Stable Diffusion GPU]
    end
    
    Internet --> LB
    LB --> WSGI
    WSGI --> Django
    Django --> Redis
    Django --> PG
    Django --> Media
    Django --> Ollama
    Django --> SD
```

### Option 2: Microservices Deployment (Large Scale)

```mermaid
graph TB
    subgraph "Load Balancing Layer"
        ALB[Application Load Balancer]
    end
    
    subgraph "Web Application Layer"
        WEB1[Django App Server 1]
        WEB2[Django App Server 2]
        WEB3[Django App Server 3]
    end
    
    subgraph "AI Service Layer"
        LLM1[Ollama Server 1]
        LLM2[Ollama Server 2]
        IMG1[Image Gen Server 1]
        IMG2[Image Gen Server 2]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL Primary)]
        PGS[(PostgreSQL Replica)]
        Redis[Redis Cluster]
        S3[S3 Media Storage]
    end
    
    subgraph "Task Queue"
        Celery[Celery Workers]
        RabbitMQ[Message Broker]
    end
    
    Internet --> ALB
    ALB --> WEB1
    ALB --> WEB2
    ALB --> WEB3
    WEB1 --> Redis
    WEB2 --> Redis
    WEB3 --> Redis
    WEB1 --> PG
    WEB2 --> PGS
    WEB3 --> PG
    WEB1 --> Celery
    WEB2 --> Celery
    WEB3 --> Celery
    Celery --> RabbitMQ
    Celery --> LLM1
    Celery --> LLM2
    Celery --> IMG1
    Celery --> IMG2
    WEB1 --> S3
    WEB2 --> S3
    WEB3 --> S3
```

## Step-by-Step Deployment

### 1. Server Preparation

**System Requirements:**
- Ubuntu 20.04+ or CentOS 8+
- 16GB+ RAM (8GB minimum)
- 4+ CPU cores
- 100GB+ SSD storage
- NVIDIA GPU with 8GB+ VRAM (for image generation)

**Initial Setup:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and system dependencies
sudo apt install python3.9 python3.9-venv python3.9-dev
sudo apt install postgresql postgresql-contrib nginx redis-server
sudo apt install git curl wget htop

# Install CUDA for GPU support
wget https://developer.download.nvidia.com/compute/cuda/12.0.1/local_installers/cuda_12.0.1_525.85.12_linux.run
sudo sh cuda_12.0.1_525.85.12_linux.run

# Install Docker (optional, for containerized deployment)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### 2. Database Setup

**PostgreSQL Configuration:**
```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE story_agent_prod;
CREATE USER story_agent WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE story_agent_prod TO story_agent;
ALTER USER story_agent CREATEDB;
\q

# Configure PostgreSQL for production
sudo nano /etc/postgresql/12/main/postgresql.conf
# Uncomment and modify:
# listen_addresses = '*'
# max_connections = 100
# shared_buffers = 256MB
# effective_cache_size = 1GB

sudo nano /etc/postgresql/12/main/pg_hba.conf
# Add line:
# host story_agent_prod story_agent 127.0.0.1/32 md5

sudo systemctl restart postgresql
```

**Redis Configuration:**
```bash
# Configure Redis for sessions
sudo nano /etc/redis/redis.conf
# Modify:
# maxmemory 256mb
# maxmemory-policy allkeys-lru
# save 60 1000

sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

### 3. Application Deployment

**Clone and Setup:**
```bash
# Create application user
sudo useradd -m -s /bin/bash storyagent
sudo su - storyagent

# Clone repository
git clone https://github.com/SriHarshitha88/story_agent.git
cd story_agent

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary redis celery
```

**Environment Configuration:**
```bash
# Create production environment file
cat > .env << EOF
DEBUG=False
SECRET_KEY=your_very_secure_secret_key_here
DATABASE_URL=postgresql://story_agent:secure_password_here@localhost/story_agent_prod
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,127.0.0.1
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Media and static files
MEDIA_ROOT=/var/www/story_agent/media
STATIC_ROOT=/var/www/story_agent/static

# Security settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
EOF

# Create media and static directories
sudo mkdir -p /var/www/story_agent/media
sudo mkdir -p /var/www/story_agent/static
sudo chown -R storyagent:storyagent /var/www/story_agent
```

**Database Migration:**
```bash
source venv/bin/activate
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createsuperuser
```

### 4. Ollama Setup

**Install and Configure Ollama:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
sudo systemctl start ollama
sudo systemctl enable ollama

# Pull required models
ollama pull llama2
ollama pull mistral  # Alternative model

# Configure Ollama for production
sudo nano /etc/systemd/system/ollama.service
# Add environment variables:
# Environment="OLLAMA_HOST=0.0.0.0"
# Environment="OLLAMA_ORIGINS=http://localhost:8000,https://yourdomain.com"

sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### 5. Web Server Configuration

**Gunicorn Setup:**
```bash
# Create Gunicorn configuration
cat > gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 300
keepalive = 2
preload_app = True
user = "storyagent"
group = "storyagent"
EOF

# Create systemd service
sudo cat > /etc/systemd/system/story-agent.service << EOF
[Unit]
Description=Story Agent Django Application
After=network.target

[Service]
User=storyagent
Group=storyagent
WorkingDirectory=/home/storyagent/story_agent
Environment=PATH=/home/storyagent/story_agent/venv/bin
EnvironmentFile=/home/storyagent/story_agent/.env
ExecStart=/home/storyagent/story_agent/venv/bin/gunicorn --config gunicorn.conf.py story_generator.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start story-agent
sudo systemctl enable story-agent
```

**Nginx Configuration:**
```bash
# Create Nginx site configuration
sudo cat > /etc/nginx/sites-available/story-agent << EOF
upstream story_agent {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Static files
    location /static/ {
        alias /var/www/story_agent/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/story_agent/media/;
        expires 1d;
        add_header Cache-Control "public";
    }

    # Application
    location / {
        proxy_pass http://story_agent;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/story-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL Certificate Setup

**Let's Encrypt SSL:**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add line:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 7. Background Task Setup (Optional)

**Celery Configuration:**
```bash
# Install message broker
sudo apt install rabbitmq-server
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server

# Create Celery configuration
cat > celery.py << EOF
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'story_generator.settings')

app = Celery('story_agent')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configure Celery
app.conf.update(
    broker_url='amqp://localhost:5672',
    result_backend='redis://localhost:6379/1',
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
)
EOF

# Create Celery systemd service
sudo cat > /etc/systemd/system/celery.service << EOF
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=storyagent
Group=storyagent
EnvironmentFile=/home/storyagent/story_agent/.env
WorkingDirectory=/home/storyagent/story_agent
ExecStart=/home/storyagent/story_agent/venv/bin/celery -A story_generator worker --loglevel=info --detach
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start celery
sudo systemctl enable celery
```

## Monitoring and Maintenance

### 1. Log Management

**Log Configuration:**
```python
# Add to settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/story-agent/django.log',
            'maxBytes': 1024*1024*10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'stories': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### 2. Performance Monitoring

**System Monitoring Script:**
```bash
#!/bin/bash
# monitoring.sh

# Check services
services=("story-agent" "nginx" "postgresql" "redis-server" "ollama")
for service in "${services[@]}"; do
    if systemctl is-active --quiet "$service"; then
        echo "✅ $service is running"
    else
        echo "❌ $service is down"
        # Send alert notification
        curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/sendMessage" \
             -d chat_id=YOUR_CHAT_ID \
             -d text="🚨 $service is down on $(hostname)"
    fi
done

# Check disk space
disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$disk_usage" -gt 80 ]; then
    echo "⚠️ Disk usage: ${disk_usage}%"
fi

# Check memory usage
memory_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
if [ "$memory_usage" -gt 85 ]; then
    echo "⚠️ Memory usage: ${memory_usage}%"
fi
```

### 3. Backup Strategy

**Database Backup:**
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/story-agent"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Database backup
pg_dump -h localhost -U story_agent story_agent_prod | gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz"

# Media files backup
tar -czf "$BACKUP_DIR/media_backup_$DATE.tar.gz" /var/www/story_agent/media/

# Clean old backups (keep last 7 days)
find "$BACKUP_DIR" -name "*.gz" -mtime +7 -delete

# Upload to cloud storage (optional)
# aws s3 sync "$BACKUP_DIR" s3://your-backup-bucket/story-agent/
```

## Security Hardening

### 1. Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 2. Fail2Ban Setup

```bash
# Install Fail2Ban
sudo apt install fail2ban

# Create Nginx jail
sudo cat > /etc/fail2ban/jail.local << EOF
[nginx-http-auth]
enabled = true
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 3
bantime = 3600

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 10
bantime = 600
EOF

sudo systemctl restart fail2ban
```

## Troubleshooting Common Issues

### 1. High Memory Usage
```bash
# Check memory usage
htop
# Optimize Ollama memory
export OLLAMA_MAX_MEMORY=4GB

# Optimize Gunicorn workers
# Reduce workers if memory constrained
```

### 2. Slow Image Generation
```bash
# Check GPU utilization
nvidia-smi
# Monitor disk I/O
iotop
# Consider SSD upgrade for faster model loading
```

### 3. Database Performance
```bash
# Monitor PostgreSQL performance
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
# Add database indexes for frequently queried fields
```

## Scaling Considerations

### Horizontal Scaling Checklist
- [ ] Load balancer configuration
- [ ] Database connection pooling
- [ ] Session store externalization (Redis)
- [ ] Shared media storage (S3/NFS)
- [ ] Background task distribution
- [ ] Monitoring and alerting setup

### Performance Optimization
- [ ] Database query optimization
- [ ] Image generation caching
- [ ] CDN integration for static files
- [ ] Model loading optimization
- [ ] Connection pooling implementation

---

*This deployment guide ensures a robust, scalable production environment for Story Agent.*