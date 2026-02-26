# DEPLOYMENT.md - Complete Deployment Guide for VM Algo Research Lab

## 📋 Table of Contents
1. Prerequisites
2. Local Development Setup
3. Docker Deployment
4. AWS EC2 Deployment
5. Production Configuration
6. Monitoring & Maintenance
7. Scaling Strategy
8. Troubleshooting

---

## 1️⃣ Prerequisites

### Required Software
- Docker & Docker Compose (v20.10+)
- Git
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
- PostgreSQL 14+ client tools
- Redis CLI

### System Requirements
- Minimum 4GB RAM
- 2 CPU cores
- 20GB storage
- Ubuntu 20.04 LTS or higher (for production)

---

## 2️⃣ Local Development Setup

### Clone Repository
\`\`\`bash
git clone https://github.com/yourusername/vm-algo-research-lab.git
cd vm-algo-research-lab
\`\`\`

### Setup Environment Variables
\`\`\`bash
# Copy example files
cp .env.example .env
cp frontend/.env.local.example frontend/.env.local

# Edit .env with your configuration
nano .env
\`\`\`

### Start Local Environment with Docker Compose
\`\`\`bash
docker-compose up -d
\`\`\`

### Initialize Database
\`\`\`bash
# The database initializes automatically via init.sql in docker-entrypoint-initdb.d
# If needed, manually init:
docker exec vm_algo_postgres psql -U vm_user -d vm_algo_db -f /docker-entrypoint-initdb.d/init.sql
\`\`\`

### Verify Services
\`\`\`bash
# Check containers
docker-compose ps

# Test API health
curl http://localhost:8000/api/v1/health

# Access services
Frontend: http://localhost:3000
Backend: http://localhost:8000
API Docs: http://localhost:8000/docs
\`\`\`

---

## 3️⃣ Docker Deployment

### Build Images
\`\`\`bash
docker-compose build --no-cache
\`\`\`

### Deploy
\`\`\`bash
docker-compose up -d
\`\`\`

### Monitor Logs
\`\`\`bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
\`\`\`

### Scale Services
\`\`\`bash
# Scale backend to 3 instances (requires load balancer)
docker-compose up -d --scale backend=3
\`\`\`

---

## 4️⃣ AWS EC2 Deployment

### Step 1: Launch EC2 Instance
\`\`\`bash
# Instance Details
- AMI: Ubuntu 22.04 LTS (ami-xxxxxxxx)
- Instance Type: t3.medium (2 vCPU, 4 GB RAM)
- Storage: 20 GB gp3
- Security Group: Allow SSH (22), HTTP (80), HTTPS (443)
\`\`\`

### Step 2: Connect and Setup
\`\`\`bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Run setup script
curl -fsSL https://raw.githubusercontent.com/yourusername/vm-algo/main/deployment/aws/ec2-setup.sh | bash
\`\`\`

### Step 3: Configure Domain
\`\`\`bash
# Update Route53 A record
- Type: A
- Value: your-ec2-elastic-ip
- TTL: 300
\`\`\`

### Step 4: Enable SSL
\`\`\`bash
sudo certbot certonly --standalone -d vm-algo.com -d www.vm-algo.com

# Auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
\`\`\`

### Step 5: Deploy Application
\`\`\`bash
cd /opt/vm-algo

# Pull latest code
git pull origin main

# Start services
docker-compose -f docker-compose.prod.yml up -d
\`\`\`

---

## 5️⃣ Production Configuration

### Environment Variables
\`\`\`bash
# .env (Production)
DEBUG=False
ENVIRONMENT=production

# Database (Use RDS)
DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/vm_algo_db

# Redis (Use ElastiCache)
REDIS_URL=redis://elasticache-endpoint:6379/0

# Security
SECRET_KEY=<strong-32-char-random-key>
ALLOWED_ORIGINS=https://vm-algo.com,https://www.vm-algo.com

# AWS
AWS_ACCESS_KEY_ID=xxxxx
AWS_SECRET_ACCESS_KEY=xxxxx
AWS_REGION=ap-south-1
\`\`\`

### Database Optimization
\`\`\`bash
# Connection pooling (in backend)
SQLALCHEMY_POOL_SIZE=20
SQLALCHEMY_MAX_OVERFLOW=40

# Query optimization
ENABLE_QUERY_CACHE=True
CACHE_TTL=300
\`\`\`

### Redis Configuration
\`\`\`bash
# Persistence
appendonly yes
appendfsync everysec

# Memory policy
maxmemory-policy allkeys-lru
maxmemory 2gb
\`\`\`

---

## 6️⃣ Monitoring & Maintenance

### Health Checks
\`\`\`bash
# API Health
curl https://vm-algo.com/api/v1/health

# Database Connection
psql postgresql://user:pass@rds-endpoint/vm_algo_db -c "SELECT version();"

# Redis Connection
redis-cli -h elasticache-endpoint ping
\`\`\`

### Logging
\`\`\`bash
# Centralized logging with ELK Stack
- Elasticsearch for storage
- Logstash for processing
- Kibana for visualization

# Backend logs
/var/log/vm-algo/backend.log

# Frontend logs
/var/log/vm-algo/frontend.log

# Nginx logs
/var/log/nginx/access.log
/var/log/nginx/error.log
\`\`\`

### Monitoring Stack
\`\`\`bash
# Prometheus metrics
curl http://localhost:9090/

# Grafana dashboards
http://localhost:3000/ (admin/admin)

# Key metrics to monitor
- API response time (< 200ms)
- Error rate (< 0.1%)
- Database connections
- Redis memory usage
- CPU utilization
- Disk space
\`\`\`

### Backup Strategy
\`\`\`bash
# Database backups (daily)
aws s3 cp /backups/db-backup.sql s3://vm-algo-backups/

# Automated backup (daily at 2 AM)
0 2 * * * /scripts/backup-database.sh
\`\`\`

---

## 7️⃣ Scaling Strategy

### Horizontal Scaling
\`\`\`
Load Balancer (AWS ALB)
    ↓
├── Backend Instance 1 (API + WebSocket)
├── Backend Instance 2 (API + WebSocket)
└── Backend Instance 3 (API + WebSocket)

Shared Resources:
├── RDS PostgreSQL (Master + Read Replica)
├── ElastiCache Redis Cluster
└── S3 for file storage
\`\`\`

### Auto Scaling Configuration
\`\`\`bash
# AWS Auto Scaling Group
- Min Instances: 2
- Desired: 3
- Max: 10

# Scale Up Trigger
- CPU > 70%
- Memory > 80%
- Request Count > 1000/min

# Scale Down Trigger
- CPU < 20% for 10 min
- Memory < 40% for 10 min
\`\`\`

### Database Scaling
\`\`\`bash
# Read Replicas for scaling queries
- Write operations → Master (RDS Multi-AZ)
- Read operations → Replicas

# Connection pooling
- PgBouncer for PostgreSQL
- Max connections: 100 per app instance
\`\`\`

### WebSocket Scaling
\`\`\`bash
# Redis Pub/Sub for distributed WebSocket
- Single server: Direct connection
- Multiple servers: Via Redis channels

# Load Balancing
- Sticky sessions (IP-based)
- Or: Use Socket.io with Redis adapter
\`\`\`

---

## 8️⃣ Troubleshooting

### Common Issues

#### Database Connection Failed
\`\`\`bash
# Check PostgreSQL service
docker ps | grep postgres

# Check connection string
echo $DATABASE_URL

# Test connection
psql postgresql://user:pass@host:5432/vm_algo_db

# View logs
docker logs vm_algo_postgres
\`\`\`

#### High API Response Time
\`\`\`bash
# Check slow queries
docker exec vm_algo_postgres psql -U vm_user -d vm_algo_db -c "SELECT query, calls, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Add indexes
psql postgresql://user:pass@host/vm_algo_db -f indexes.sql

# Clear Redis cache
redis-cli FLUSHALL
\`\`\`

#### WebSocket Connection Issues
\`\`\`bash
# Check WebSocket logs
docker logs vm_algo_backend | grep websocket

# Test WebSocket
wscat -c ws://localhost:8000/ws

# Verify Nginx WebSocket config
cat /etc/nginx/sites-available/vm-algo | grep -A5 "location /ws"
\`\`\`

#### Out of Memory
\`\`\`bash
# Check memory usage
free -h
docker stats

# Reduce container limits
docker-compose.yml → memory: 2g

# Clear old data
docker exec vm_algo_postgres vacuumdb -U vm_user vm_algo_db
\`\`\`

---

## 🔐 Security Checklist

- [ ] Change all default passwords
- [ ] Enable 2FA for admin accounts
- [ ] Configure firewall rules
- [ ] Enable HTTPS/SSL
- [ ] Setup API rate limiting
- [ ] Enable request logging
- [ ] Regular security updates
- [ ] Database encryption at rest
- [ ] Secrets management (AWS Secrets Manager)
- [ ] Regular backups and recovery testing

---

## 📊 Performance Targets

| Metric | Target |
|--------|--------|
| API Response Time | < 200ms |
| Backend Uptime | > 99.5% |
| Database Query Time | < 100ms |
| Page Load Time | < 2s |
| Error Rate | < 0.1% |
| Concurrent Users | 10,000+ |

---

## 📞 Support & Maintenance

- **Monitoring Dashboard**: https://monitoring.vm-algo.com
- **Logs**: AWS CloudWatch
- **Alerts**: Email + Slack + PagerDuty
- **Incident Response**: 15-minute SLA for P1

---

# API.md - Complete API Documentation

## Base URL
\`\`\`
Development: http://localhost:8000/api/v1
Production: https://vm-algo.com/api/v1
\`\`\`

## Authentication
All requests require JWT token in header:
\`\`\`
Authorization: Bearer <your_access_token>
\`\`\`

### Endpoints

#### POST /auth/register
Register new user
\`\`\`json
Request:
{
  "email": "user@example.com",
  "username": "trader123",
  "full_name": "John Trader",
  "password": "secure_password"
}

Response:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "trader123"
  }
}
\`\`\`

#### POST /auth/login
Login user
\`\`\`json
Request:
{
  "email": "user@example.com",
  "password": "secure_password"
}

Response: (same as register)
\`\`\`

#### GET /dashboard/market-overview
Get real-time market data
\`\`\`json
Response:
{
  "nifty": {
    "symbol": "NIFTY",
    "price": 19500.50,
    "change": 145.75,
    "change_percent": 0.75
  },
  "bank_nifty": {...},
  "sensex": {...}
}
\`\`\`

#### GET /scanner/scans
List available scans
\`\`\`json
Response:
{
  "count": 15,
  "scans": [
    {
      "id": 1,
      "name": "RSI Oversold",
      "description": "Find stocks with RSI < 30",
      "conditions_count": 2,
      "is_public": true
    }
  ]
}
\`\`\`

#### POST /scanner/run-scan/{scan_id}
Execute a scan
\`\`\`json
Response:
{
  "scan_id": 1,
  "scan_name": "RSI Oversold",
  "result_count": 4,
  "results": [
    {
      "symbol": "RELIANCE",
      "score": 85,
      "match_count": 4
    }
  ]
}
\`\`\`

#### POST /strategy/create-strategy
Create algorithmic strategy
\`\`\`json
Request:
{
  "name": "Breakout Strategy",
  "description": "Long on NIFTY breakouts",
  "entry_conditions": [
    {
      "type": "indicator",
      "params": {"indicator": "RSI", "threshold": 70}
    }
  ],
  "exit_conditions": [...],
  "position_sizing": {"type": "fixed", "size": 1}
}

Response:
{
  "strategy_id": 42,
  "message": "Strategy created successfully"
}
\`\`\`

#### POST /backtest/backtest-strategy
Run backtest on strategy
\`\`\`json
Request:
{
  "strategy_id": 42,
  "start_date": "2020-01-01T00:00:00Z",
  "end_date": "2025-01-01T00:00:00Z",
  "initial_capital": 100000
}

Response:
{
  "backtest_id": 123,
  "metrics": {
    "total_return": 25.5,
    "cagr": 7.2,
    "max_drawdown": -12.3,
    "sharpe_ratio": 1.85,
    "win_rate": 58.5
  }
}
\`\`\`

#### GET /portfolio/summary/{user_id}
Get portfolio overview
\`\`\`json
Response:
{
  "total_capital": 500000,
  "cash_available": 250000,
  "invested_capital": 250000,
  "today_pnl": 5500,
  "today_pnl_percent": 1.1,
  "mtd_pnl": 25000,
  "ytd_pnl": 75000
}
\`\`\`

---

## Error Responses

\`\`\`json
400 Bad Request:
{
  "detail": "Invalid request parameters"
}

401 Unauthorized:
{
  "detail": "Invalid or expired token"
}

403 Forbidden:
{
  "detail": "Insufficient permissions"
}

429 Rate Limited:
{
  "detail": "Rate limit exceeded. Try again in 60 seconds"
}

500 Server Error:
{
  "detail": "Internal server error"
}
\`\`\`

---

## Rate Limits

- Free Tier: 100 requests/min
- Pro Tier: 500 requests/min
- Elite Tier: Unlimited

---
