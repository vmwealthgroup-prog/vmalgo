# VM Algo Research Lab - Complete Project Structure

## 📁 Folder Architecture

```
vm-algo-research-lab/
│
├── frontend/                          # Next.js 14 + React + TailwindCSS
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx            # Root layout with theme provider
│   │   │   ├── page.tsx              # Landing page
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx          # Main dashboard
│   │   │   ├── scanner/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [scanId]/page.tsx
│   │   │   ├── strategy-builder/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [strategyId]/page.tsx
│   │   │   ├── backtest/
│   │   │   │   └── page.tsx
│   │   │   ├── portfolio/
│   │   │   │   └── page.tsx
│   │   │   ├── ai-research/
│   │   │   │   └── page.tsx
│   │   │   ├── auth/
│   │   │   │   ├── login/page.tsx
│   │   │   │   ├── register/page.tsx
│   │   │   │   └── callback/page.tsx
│   │   │   ├── admin/
│   │   │   │   ├── users/page.tsx
│   │   │   │   ├── strategies/page.tsx
│   │   │   │   ├── revenue/page.tsx
│   │   │   │   └── monitoring/page.tsx
│   │   │   └── api/
│   │   │       └── auth/[...auth0]/route.ts
│   │   │
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Navbar.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Footer.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── MarketOverview.tsx
│   │   │   │   ├── PositionsList.tsx
│   │   │   │   ├── PerformanceMetrics.tsx
│   │   │   │   ├── RiskHeatmap.tsx
│   │   │   │   └── PnLChart.tsx
│   │   │   ├── scanner/
│   │   │   │   ├── ScannerTable.tsx
│   │   │   │   ├── ScanBuilder.tsx
│   │   │   │   └── FilterPanel.tsx
│   │   │   ├── strategy/
│   │   │   │   ├── DragDropBuilder.tsx
│   │   │   │   ├── ConditionBlock.tsx
│   │   │   │   ├── BacktestResults.tsx
│   │   │   │   └── StrategyCard.tsx
│   │   │   ├── common/
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   ├── Toast.tsx
│   │   │   │   ├── LoadingSpinner.tsx
│   │   │   │   └── Chart.tsx
│   │   │   └── ai-research/
│   │   │       ├── MarketOutlook.tsx
│   │   │       ├── SentimentAnalysis.tsx
│   │   │       └── VolatilityForecast.tsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useMarketData.ts
│   │   │   ├── useStrategy.ts
│   │   │   ├── useBacktest.ts
│   │   │   └── useFetch.ts
│   │   │
│   │   ├── services/
│   │   │   ├── api.ts              # Axios instance with interceptors
│   │   │   ├── auth.service.ts
│   │   │   ├── dashboard.service.ts
│   │   │   ├── scanner.service.ts
│   │   │   ├── strategy.service.ts
│   │   │   ├── backtest.service.ts
│   │   │   └── trading.service.ts
│   │   │
│   │   ├── context/
│   │   │   ├── AuthContext.tsx
│   │   │   ├── MarketContext.tsx
│   │   │   └── ThemeContext.tsx
│   │   │
│   │   ├── utils/
│   │   │   ├── helpers.ts
│   │   │   ├── validators.ts
│   │   │   ├── formatters.ts
│   │   │   └── constants.ts
│   │   │
│   │   ├── types/
│   │   │   └── index.ts
│   │   │
│   │   └── styles/
│   │       ├── globals.css
│   │       └── variables.css
│   │
│   ├── public/
│   │   ├── icons/
│   │   └── images/
│   │
│   ├── .env.local.example
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── package.json
│
├── backend/                           # FastAPI + Python
│   ├── app/
│   │   ├── main.py                  # FastAPI app entry
│   │   ├── config.py                # Configuration
│   │   ├── security.py              # JWT, encryption
│   │   │
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── auth.py          # Auth endpoints
│   │   │   │   ├── dashboard.py     # Dashboard data
│   │   │   │   ├── scanner.py       # Scanner engine
│   │   │   │   ├── strategy.py      # Strategy management
│   │   │   │   ├── backtest.py      # Backtesting
│   │   │   │   ├── trading.py       # Order execution
│   │   │   │   ├── portfolio.py     # Portfolio management
│   │   │   │   ├── ai_research.py   # AI features
│   │   │   │   └── admin.py         # Admin endpoints
│   │   │   └── __init__.py
│   │   │
│   │   ├── models/
│   │   │   ├── user.py              # User model
│   │   │   ├── strategy.py          # Strategy model
│   │   │   ├── trade.py             # Trade model
│   │   │   ├── position.py          # Position model
│   │   │   ├── scan.py              # Scan model
│   │   │   ├── backtest.py          # Backtest result model
│   │   │   └── __init__.py
│   │   │
│   │   ├── services/
│   │   │   ├── broker_service.py    # Broker API integration
│   │   │   ├── scanner_service.py   # Scanner logic
│   │   │   ├── strategy_service.py  # Strategy execution
│   │   │   ├── backtest_service.py  # Backtest engine
│   │   │   ├── market_data.py       # Real-time data
│   │   │   ├── ai_service.py        # AI/ML features
│   │   │   └── alert_service.py     # Alerts
│   │   │
│   │   ├── database/
│   │   │   ├── session.py           # SQLAlchemy session
│   │   │   ├── models.py            # ORM models
│   │   │   └── migrations/          # Alembic migrations
│   │   │
│   │   ├── cache/
│   │   │   └── redis_client.py      # Redis cache
│   │   │
│   │   ├── utils/
│   │   │   ├── logger.py
│   │   │   ├── validators.py
│   │   │   └── helpers.py
│   │   │
│   │   └── websocket/
│   │       ├── manager.py           # WebSocket connection manager
│   │       └── handlers.py          # WebSocket handlers
│   │
│   ├── tests/
│   │   ├── test_auth.py
│   │   ├── test_scanner.py
│   │   ├── test_strategy.py
│   │   └── test_backtest.py
│   │
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   └── main.py
│
├── database/
│   ├── schema.sql                  # PostgreSQL schema
│   ├── migrations/                 # Alembic migrations
│   ├── seeds/                      # Seed data
│   └── indexes.sql                 # Important indexes
│
├── deployment/
│   ├── docker-compose.yml
│   ├── nginx/
│   │   ├── nginx.conf
│   │   └── ssl/
│   ├── aws/
│   │   ├── ec2-setup.sh
│   │   ├── terraform/
│   │   └── security-groups.json
│   ├── monitoring/
│   │   ├── prometheus.yml
│   │   └── grafana-dashboards/
│   └── ci-cd/
│       └── github-actions.yml
│
└── docs/
    ├── API.md                      # API documentation
    ├── DEPLOYMENT.md               # Deployment guide
    ├── ARCHITECTURE.md             # Architecture overview
    ├── SECURITY.md                 # Security protocols
    ├── SCALABILITY.md              # Scaling strategy
    └── DEV_SETUP.md               # Development setup
```

## 🚀 Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, React 18, TailwindCSS, Framer Motion |
| State Management | Context API + Zustand |
| UI Components | Custom + shadcn/ui |
| Backend | FastAPI, Python 3.11+ |
| Database | PostgreSQL 14+ |
| Cache | Redis 7+ |
| Auth | JWT + OAuth2 + 2FA |
| WebSocket | Socket.io / Native WS |
| Broker APIs | Zerodha Kite, Angel One |
| Deployment | AWS EC2, Docker, Nginx |
| Monitoring | Prometheus, Grafana, ELK Stack |
| CI/CD | GitHub Actions |

## 📊 Database Tables Overview

```sql
-- Core Tables
- users
- subscriptions
- api_credentials
- strategies
- strategy_conditions
- strategy_backtest_results
- scans
- scan_conditions
- positions
- trades
- alerts
- portfolios
- portfolio_allocations
- market_data_cache
- ai_predictions
- audit_logs
```

## 🔄 API Endpoints Structure

```
/api/v1/
├── /auth
│   ├── POST /register
│   ├── POST /login
│   ├── POST /refresh-token
│   └── POST /2fa-verify
├── /dashboard
│   ├── GET /market-overview
│   ├── GET /positions
│   ├── GET /performance-metrics
│   └── GET /pnl-analytics
├── /scanner
│   ├── GET /scans
│   ├── POST /create-scan
│   ├── GET /scan-results/{scanId}
│   └── POST /run-scan
├── /strategy
│   ├── GET /strategies
│   ├── POST /create-strategy
│   ├── PUT /update-strategy/{id}
│   ├── POST /backtest-strategy
│   └── POST /deploy-strategy
├── /trading
│   ├── POST /place-order
│   ├── GET /active-trades
│   ├── POST /close-position
│   └── GET /trade-history
├── /portfolio
│   ├── GET /summary
│   ├── GET /allocation
│   └── GET /equity-curve
└── /admin
    ├── GET /users
    ├── POST /create-user
    ├── GET /revenue-dashboard
    └── GET /monitoring
```

## 🔐 Security Features

- JWT token-based authentication
- Refresh token rotation
- 2FA (TOTP/SMS)
- Encrypted API credentials (AES-256)
- Rate limiting (100 req/min per user)
- CORS protection
- SQL injection prevention (ORM)
- Audit logging (all trades & strategy changes)
- IP whitelisting option
- Trade confirmation confirmation

## 📈 Scalability Architecture

- Horizontal scaling with load balancer
- Database read replicas
- Redis cluster for caching
- Microservices-ready design
- Async task queue (Celery)
- WebSocket for real-time updates
- CDN for static assets
- Database connection pooling

---

**Next Steps**: Review individual files in the comprehensive build below
