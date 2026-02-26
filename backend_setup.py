# backend/app/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from app.config import settings
from app.database.session import init_db, get_db
from app.api.v1 import auth, dashboard, scanner, strategy, backtest, trading, portfolio, admin
from app.cache.redis_client import init_redis
from app.websocket.manager import manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database and cache...")
    await init_db()
    await init_redis()
    logger.info("VM Algo Research Lab started successfully")
    yield
    # Shutdown
    logger.info("VM Algo Research Lab shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="VM Algo Research Lab API",
    description="Professional algorithmic trading and research platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# API Routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(scanner.router, prefix="/api/v1/scanner", tags=["Scanner"])
app.include_router(strategy.router, prefix="/api/v1/strategy", tags=["Strategy"])
app.include_router(backtest.router, prefix="/api/v1/backtest", tags=["Backtest"])
app.include_router(trading.router, prefix="/api/v1/trading", tags=["Trading"])
app.include_router(portfolio.router, prefix="/api/v1/portfolio", tags=["Portfolio"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])

# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "VM Algo Research Lab API v1.0.0",
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "VM Algo Research Lab API",
        "version": "1.0.0",
        "docs": "/docs",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )

---

# backend/app/config.py
from pydantic_settings import BaseSettings
from typing import List
import os
from functools import lru_cache

class Settings(BaseSettings):
    # App Configuration
    APP_NAME: str = "VM Algo Research Lab"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    VERSION: str = "1.0.0"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/vm_algo_db"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Security
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
    ]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "*"]
    
    # Broker APIs
    ZERODHA_API_KEY: str = os.getenv("ZERODHA_API_KEY", "")
    ZERODHA_API_SECRET: str = os.getenv("ZERODHA_API_SECRET", "")
    ANGEL_ONE_API_KEY: str = os.getenv("ANGEL_ONE_API_KEY", "")
    ANGEL_ONE_API_SECRET: str = os.getenv("ANGEL_ONE_API_SECRET", "")
    
    # Alerts
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    WHATSAPP_API_KEY: str = os.getenv("WHATSAPP_API_KEY", "")
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = 587
    SMTP_EMAIL: str = os.getenv("SMTP_EMAIL", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    
    # Backtest
    BACKTEST_YEARS: int = 5
    
    # Monitoring
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

---

# backend/app/database/models.py
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, JSON, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    subscription_tier = Column(String, default="free")  # free, pro, elite
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    strategies = relationship("Strategy", back_populates="user")
    positions = relationship("Position", back_populates="user")
    trades = relationship("Trade", back_populates="user")
    alerts = relationship("Alert", back_populates="user")

class APICredentials(Base):
    __tablename__ = "api_credentials"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    broker = Column(String)  # zerodha, angel_one, binance
    api_key = Column(String)  # Encrypted
    api_secret = Column(String)  # Encrypted
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Strategy(Base):
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    description = Column(Text)
    
    # Strategy Logic
    entry_conditions = Column(JSON)  # List of conditions
    exit_conditions = Column(JSON)
    position_sizing = Column(JSON)
    
    # Configuration
    is_active = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="strategies")
    backtest_results = relationship("BacktestResult", back_populates="strategy")
    positions = relationship("Position", back_populates="strategy")

class BacktestResult(Base):
    __tablename__ = "backtest_results"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"))
    
    # Metrics
    total_return = Column(Float)
    cagr = Column(Float)
    max_drawdown = Column(Float)
    sharpe_ratio = Column(Float)
    win_rate = Column(Float)
    profit_factor = Column(Float)
    expectancy = Column(Float)
    
    # Configuration
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    strategy = relationship("Strategy", back_populates="backtest_results")

class Position(Base):
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True)
    
    # Stock Info
    symbol = Column(String, index=True)
    quantity = Column(Integer)
    entry_price = Column(Float)
    entry_time = Column(DateTime)
    
    # Position Details
    stop_loss = Column(Float)
    target = Column(Float)
    trailing_stop = Column(Float, nullable=True)
    
    # Current Status
    current_price = Column(Float)
    pnl = Column(Float)
    pnl_percent = Column(Float)
    
    status = Column(String)  # open, closed
    closed_price = Column(Float, nullable=True)
    closed_time = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="positions")
    strategy = relationship("Strategy", back_populates="positions")

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    position_id = Column(Integer, ForeignKey("positions.id"))
    
    symbol = Column(String)
    order_id = Column(String, unique=True)
    side = Column(String)  # buy, sell
    quantity = Column(Integer)
    price = Column(Float)
    
    status = Column(String)  # pending, completed, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="trades")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    alert_type = Column(String)  # price, indicator, news
    symbol = Column(String)
    condition = Column(JSON)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="alerts")

class Scan(Base):
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    name = Column(String)
    description = Column(Text)
    conditions = Column(JSON)
    
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    action = Column(String)
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

---

# backend/requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.13.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose==3.3.0
passlib==1.7.4
python-multipart==0.0.6
httpx==0.25.0
aioredis==2.0.1
redis==5.0.1
websockets==12.0
python-socketio==5.9.0
aiohttp==3.9.1
pandas==2.1.3
numpy==1.26.2
scipy==1.11.4
scikit-learn==1.3.2
ta==0.10.2
yfinance==0.2.32
python-telegram-bot==20.3
twilio==8.10.0
aiosmtplib==3.0.1
slack-sdk==3.26.1
sentry-sdk==1.39.1
pytest==7.4.3
pytest-asyncio==0.21.1
requests==2.31.0
cryptography==41.0.7
pyjwt==2.8.1
python-dotenv==1.0.0
