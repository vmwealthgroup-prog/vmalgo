# ARCHITECTURE.md - System Architecture & Design

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT LAYER                            │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │  Web Browser     │  │  Mobile App      │                 │
│  │  (React/Next.js) │  │  (React Native)  │                 │
│  └────────┬─────────┘  └────────┬─────────┘                 │
└───────────┼──────────────────────┼─────────────────────────┘
            │                      │
┌───────────▼──────────────────────▼─────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Nginx (Load Balancing, SSL/TLS, Rate Limiting)     │   │
│  └────────────────────┬────────────────────────────────┘   │
└───────────────────────┼─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│               APPLICATION LAYER (FastAPI)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Auth API    │  │  Trading API │  │  Scanner API │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Strategy API │  │ Backtest API │  │ Alert API    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                    ↓                                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  WebSocket Layer (Real-time Market Data/Updates)   │   │
│  └────────────────────┬────────────────────────────────┘   │
└───────────────────────┼─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌─────▼──────┐ ┌────▼──────────┐
│  PostgreSQL  │ │    Redis   │ │  Broker APIs  │
│  (Database)  │ │  (Cache)   │ │ (Zerodha/etc) │
└──────────────┘ └────────────┘ └───────────────┘
```

## 📊 Detailed Component Architecture

### 1. Frontend Architecture (Next.js 14)
```
components/
├── layout/
│   ├── Navbar (Persistent header with auth)
│   ├── Sidebar (Navigation menu)
│   └── RootLayout (Theme provider, context setup)
├── dashboard/
│   ├── MarketOverview (Live market data)
│   ├── PositionsList (Open positions)
│   ├── PerformanceMetrics (User stats)
│   ├── RiskHeatmap (Visual risk analysis)
│   └── PnLChart (Profit/Loss analytics)
├── scanner/
│   ├── ScannerTable (Results display)
│   ├── ScanBuilder (No-code builder)
│   └── FilterPanel (Advanced filters)
├── strategy/
│   ├── DragDropBuilder (Visual strategy builder)
│   ├── BacktestResults (Detailed metrics)
│   └── StrategyCard (Strategy preview)
└── common/
    ├── Card (Glassmorphism container)
    ├── Button (Styled button variants)
    ├── Modal (Dialog component)
    ├── Toast (Notifications)
    └── Chart (Chart.js wrapper)
```

### 2. Backend Architecture (FastAPI)
```
app/
├── api/
│   ├── v1/
│   │   ├── auth.py (JWT, 2FA, OAuth2)
│   │   ├── dashboard.py (Market data, positions)
│   │   ├── scanner.py (Scan engine)
│   │   ├── strategy.py (CRUD + validation)
│   │   ├── backtest.py (Historical testing)
│   │   ├── trading.py (Order execution)
│   │   ├── portfolio.py (Holdings management)
│   │   ├── ai_research.py (ML models)
│   │   └── admin.py (User/system management)
├── services/
│   ├── broker_service.py (Zerodha/Angel integration)
│   ├── scanner_service.py (Technical analysis)
│   ├── strategy_service.py (Execution logic)
│   ├── backtest_service.py (Backtesting engine)
│   ├── market_data.py (Real-time feeds)
│   ├── ai_service.py (ML predictions)
│   └── alert_service.py (Notifications)
├── models/
│   ├── user.py (User authentication)
│   ├── strategy.py (Strategy definitions)
│   ├── trade.py (Trade records)
│   ├── position.py (Open positions)
│   └── scan.py (Scan definitions)
├── database/
│   ├── models.py (SQLAlchemy ORM)
│   └── session.py (Connection management)
├── cache/
│   └── redis_client.py (Caching layer)
├── websocket/
│   ├── manager.py (Connection management)
│   └── handlers.py (Message routing)
└── security/
    ├── jwt_handler.py (Token generation)
    ├── encryption.py (API key encryption)
    └── validators.py (Input validation)
```

### 3. Database Architecture (PostgreSQL)
```
users ─┬─→ api_credentials
       ├─→ strategies ─→ backtest_results
       ├─→ positions ─→ trades
       ├─→ scans
       └─→ alerts
       
subscriptions
portfolio_summary
audit_logs
market_data_cache
ai_predictions
```

## 🔄 Data Flow

### User Authentication Flow
```
User Input
    ↓
Frontend Form Validation
    ↓
POST /auth/login
    ↓
Backend Hash Verification
    ↓
JWT Token Generation
    ↓
Store in Redis (session tracking)
    ↓
Return Access + Refresh Tokens
    ↓
Frontend stores in httpOnly cookie
```

### Strategy Execution Flow
```
Strategy Deploy
    ↓
Real-time Market Data (WebSocket)
    ↓
Condition Evaluation (In-memory or DB)
    ↓
Entry Signal Generated
    ↓
Risk Validation (SL, Position Size, Margin)
    ↓
Order Placement via Broker API
    ↓
Order Confirmation
    ↓
Position Record Created
    ↓
WebSocket Update to User
    ↓
P&L Tracking (Real-time)
```

### Backtest Execution Flow
```
Strategy Selection
    ↓
Download Historical Data (5 years)
    ↓
Initialize Virtual Account
    ↓
Loop through each date:
├─ Generate signals
├─ Place virtual orders
├─ Update positions
├─ Calculate P&L
└─ Track metrics
    ↓
Generate Report
├─ CAGR, Max Drawdown
├─ Sharpe Ratio, Win Rate
├─ Equity Curve
└─ Trade-by-trade log
    ↓
Store in Database
    ↓
Display Results
```

## 🎯 Key Design Patterns

### 1. Async/Await Pattern
```python
# Real-time data processing
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process market data
            await manager.broadcast(processed_data)
    finally:
        manager.disconnect(websocket)
```

### 2. Repository Pattern
```python
# Service abstraction
class StrategyService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_strategy(self, strategy_id: int):
        # Returns strategy with eager-loaded relations
        return self.db.query(Strategy).filter(...).first()
```

### 3. Middleware Pattern
```python
# Request logging + error handling
@app.middleware("http")
async def log_middleware(request, call_next):
    request_id = str(uuid4())
    logger.info(f"Request {request_id}: {request.method} {request.url}")
    
    response = await call_next(request)
    
    logger.info(f"Response {request_id}: {response.status_code}")
    return response
```

---

# SCALABILITY.md - Scaling & Performance Strategy

## 📈 Current Capacity

| Metric | Single Instance |
|--------|-----------------|
| Concurrent Users | 500 |
| API Requests/sec | 100 |
| Positions Tracked | 10,000 |
| Strategy Backtests/day | 1,000 |

## 🚀 Scaling Strategy (Target: 100,000 users)

### Phase 1: Vertical Scaling (Months 1-3)
```
Current: t3.medium (2vCPU, 4GB RAM)
         ↓
Target:  t3.xlarge (4vCPU, 16GB RAM)

Cost Impact: 3x
Improvement: 2x throughput
```

### Phase 2: Horizontal Scaling (Months 4-6)
```
Load Balancer (ALB)
    ↓
├── Backend Pod 1 (containerized)
├── Backend Pod 2
└── Backend Pod 3

Database: RDS Read Replicas
Cache: Redis Cluster (3-node)
```

### Phase 3: Microservices (Months 7-12)
```
API Gateway
    ↓
├── Auth Service (JWT, 2FA)
├── Trading Service (Order execution)
├── Strategy Service (Backtest, execution)
├── Scanner Service (Technical analysis)
├── AI Service (ML models)
└── Alert Service (Notifications)

Message Queue: RabbitMQ/Kafka
Background Jobs: Celery
```

## 💾 Database Scaling

### Current (Single PostgreSQL)
- Max connections: 100
- Query time: < 100ms

### Scaling Path

```
Phase 1: Connection Pooling (PgBouncer)
├── Max connections: 500
└── Query caching: 30%

Phase 2: Read Replicas
├── Write → Master
├── Read → Replica 1, 2, 3
└── Load balanced reads

Phase 3: Sharding (if needed at 1M users)
├── Shard by user_id
├── 10 shards
└── Distributed queries
```

## 🔌 Cache Strategy

### Redis Caching Layers
```
Level 1: API Response Cache
├── Duration: 30 seconds
├── Keys: /api/v1/dashboard/{user_id}
└── Hit rate: 90%+

Level 2: Market Data Cache
├── Duration: 1 second
├── Keys: NIFTY:price, RELIANCE:ohlcv
└── Updated real-time

Level 3: Session Store
├── Duration: 7 days
├── Keys: session:{user_id}
└── Distributed sessions

Level 4: User Preferences
├── Duration: 30 days
├── Keys: user:{user_id}:prefs
└── Lazy loaded
```

## 🌐 Content Delivery

### CDN Strategy (CloudFront)
```
├── Static Assets (JS, CSS, Images)
│   └── Cache: 1 year (versioned)
├── API Responses (selected endpoints)
│   └── Cache: 30 seconds
└── HTML (index.html)
    └── Cache: 1 hour
```

## 📊 Query Optimization

### Slow Query Analysis
```sql
-- Before optimization
SELECT * FROM positions 
WHERE user_id = 1 AND status = 'open'
-- Query time: 500ms

-- After optimization
CREATE INDEX idx_positions_user_status 
  ON positions(user_id, status);
-- Query time: 5ms (100x faster)
```

### N+1 Query Prevention
```python
# Bad
strategies = db.query(Strategy).all()
for s in strategies:
    print(s.user.name)  # N queries!

# Good
strategies = db.query(Strategy).options(
    joinedload(Strategy.user)
).all()
```

## 🔄 Rate Limiting Strategy

```
Tier-based approach:
├── Free: 100 req/min, 1 strategy
├── Pro: 500 req/min, 10 strategies
└── Elite: Unlimited, 100 strategies

Implementation: Redis-based token bucket
```

## 📡 WebSocket Scaling

### Single Server
```
Client 1 ─┐
Client 2 ─┼─→ WebSocket Server
Client 3 ─┘
```

### Distributed
```
Client 1 ─┐      Server 1
Client 2 ─┼─→ ┌──────────┐
          │   │          │ Redis
Client 3 ─┤   │ Pub/Sub  │◄──────┐
Client 4 ─┼─→ │          │        │
          │   └──────────┘        │
Client 5 ─┤   ┌──────────┐        │
Client 6 ─┼─→ │ Server 2 │───────┤
          │   │          │        │
Client 7 ─┘   └──────────┘        │
                                  ├─ All servers subscribe
              ┌──────────┐        │  to same channels
              │ Server 3 │───────┘
              │          │
              └──────────┘
```

## 🎯 Performance Targets After Scaling

| Metric | Target | Current |
|--------|--------|---------|
| API Response | < 100ms | 200ms |
| Page Load | < 1s | 2s |
| WebSocket Latency | < 50ms | 100ms |
| Concurrent Users | 100,000 | 500 |
| Backtest Speed | 5 years/sec | 1 year/sec |
| Database QPS | 10,000+ | 1,000 |

---

# SECURITY.md - Security Implementation

## 🔐 Authentication & Authorization

### JWT Implementation
```python
# Token payload
{
  "sub": "user_id",
  "iat": 1234567890,
  "exp": 1234571490,  # 60 min expiry
  "permissions": ["trade", "backtest"],
  "tier": "pro"
}

# Refresh token (7 days)
{
  "sub": "user_id",
  "type": "refresh",
  "exp": 1235172690
}
```

### 2FA Implementation
```
TOTP (Time-based One-Time Password)
├── Library: pyotp
├── QR Code Generation: pyqrcode
└── Backup codes: 10 single-use codes
```

### Role-Based Access Control
```python
@require_permission("trade")
def place_order(strategy_id: int):
    # Only users with 'trade' permission
    pass

ROLES = {
    "free_user": ["view_dashboard", "backtest"],
    "pro_user": ["trade", "scanner", "alerts"],
    "admin": ["*"]  # All permissions
}
```

## 🔒 Data Security

### Encryption at Rest
```
Database fields encrypted:
├── api_credentials.api_key (AES-256)
├── api_credentials.api_secret (AES-256)
├── users.phone_number (masked)
└── trades.slippage (raw data not needed)
```

### Encryption in Transit
```
├── HTTPS/TLS 1.3 (All APIs)
├── WSS (Secure WebSocket)
├── Database SSL connection
└── Redis TLS (optional)
```

### Secure Password Hashing
```python
# Using Argon2 (more secure than bcrypt)
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

# Hash with salt + multiple iterations
hashed = pwd_context.hash(password)
```

## 🛡️ API Security

### Input Validation
```python
# Pydantic models enforce types
class CreateStrategyRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., max_length=1000)
    
    @validator('name')
    def name_alphanumeric(cls, v):
        assert v.replace(' ', '').isalnum()
        return v
```

### CORS Protection
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://vm-algo.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### Rate Limiting
```python
@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    rate_limit = await redis.get(f"rate:{user_id}")
    if rate_limit and rate_limit > 100:
        return JSONResponse(status_code=429)
    await redis.incr(f"rate:{user_id}")
    return await call_next(request)
```

## 📋 Audit Logging

### What to Log
```python
audit_logger.info({
    "action": "trade_executed",
    "user_id": 123,
    "symbol": "RELIANCE",
    "quantity": 100,
    "price": 2500,
    "timestamp": datetime.utcnow(),
    "ip_address": request.client.host,
    "result": "success"
})
```

### Immutable Logs
```
├── Stored in database with hash chain
├── Cannot be deleted (only marked as reviewed)
├── Indexed by timestamp + user_id
└── Encrypted before storage
```

## 🔑 API Key Management

### Key Generation
```python
api_key = secrets.token_urlsafe(32)  # 256-bit entropy
encrypted_key = encrypt_aes(api_key, master_key)
db.store(encrypted_key)  # Never store raw
```

### Key Rotation
```
├── Rotate every 90 days
├── Keep previous key for 7 days (backward compat)
├── Alert user of change
└── Automatic disable if compromised
```

## 🚨 DDoS & Rate Limiting

### Multi-layer Protection
```
Layer 1: Nginx (IP-based)
├── Max 1000 req/min per IP
└── Blacklist after 10 violations

Layer 2: FastAPI (User-based)
├── Max 100 req/min per user
└── Backoff strategy

Layer 3: Database
├── Connection pooling (prevent exhaustion)
└── Query timeout (prevent runaway queries)
```

## 🔍 Security Headers

```nginx
add_header Strict-Transport-Security 
  "max-age=31536000; includeSubDomains" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin";
add_header Content-Security-Policy 
  "default-src 'self'; script-src 'self' 'unsafe-inline'";
```

## 🧪 Security Testing

### Regular Audits
```bash
# Dependency check
pip-audit

# SAST (Static Application Security Testing)
bandit -r app/

# DAST (Dynamic Testing)
owasp-zap scan -t https://vm-algo.com

# Penetration testing (quarterly)
```

## 📱 User Privacy

- GDPR compliant data storage
- Right to be forgotten (account deletion)
- Data export functionality
- Privacy policy + ToS
- Encrypted personal information

---

**Last Updated**: January 2024
**Version**: 1.0.0
**Maintainer**: DevOps Team
