# backend/app/api/v1/auth.py
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
import jwt

from app.config import settings
from app.database.session import get_db
from app.database.models import User
from app.security import hash_password, verify_password, create_access_token

router = APIRouter()

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: dict

@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # Check if user exists
    existing = db.query(User).filter(
        (User.email == request.email) | (User.username == request.username)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create new user
    user = User(
        email=request.email,
        username=request.username,
        full_name=request.full_name,
        hashed_password=hash_password(request.password),
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_access_token(
        {"sub": str(user.id)},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user={
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
        },
    )

@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_access_token(
        {"sub": str(user.id)},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user={
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
        },
    )

---

# backend/app/api/v1/dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database.session import get_db
from app.database.models import User, Position, Trade

router = APIRouter()

@router.get("/market-overview")
async def get_market_overview(db: Session = Depends(get_db)):
    """Get current market overview with Nifty, Bank Nifty, Sensex"""
    # In production, integrate with broker APIs for live data
    return {
        "nifty": {
            "symbol": "NIFTY",
            "price": 19500.50,
            "change": 145.75,
            "change_percent": 0.75,
            "timestamp": datetime.utcnow().isoformat(),
        },
        "bank_nifty": {
            "symbol": "BANKNIFTY",
            "price": 45200.25,
            "change": -125.50,
            "change_percent": -0.28,
            "timestamp": datetime.utcnow().isoformat(),
        },
        "sensex": {
            "symbol": "SENSEX",
            "price": 64500.75,
            "change": 200.25,
            "change_percent": 0.31,
            "timestamp": datetime.utcnow().isoformat(),
        },
    }

@router.get("/positions/{user_id}")
async def get_positions(user_id: int, db: Session = Depends(get_db)):
    """Get all open positions for a user"""
    positions = db.query(Position).filter(
        (Position.user_id == user_id) & (Position.status == "open")
    ).all()
    
    return {
        "count": len(positions),
        "total_pnl": sum(p.pnl for p in positions),
        "total_pnl_percent": sum(p.pnl_percent for p in positions) / len(positions) if positions else 0,
        "positions": [
            {
                "id": p.id,
                "symbol": p.symbol,
                "quantity": p.quantity,
                "entry_price": p.entry_price,
                "current_price": p.current_price,
                "pnl": p.pnl,
                "pnl_percent": p.pnl_percent,
                "stop_loss": p.stop_loss,
                "target": p.target,
            }
            for p in positions
        ],
    }

@router.get("/performance-metrics/{user_id}")
async def get_performance_metrics(user_id: int, db: Session = Depends(get_db)):
    """Get performance metrics for user"""
    trades = db.query(Trade).filter(Trade.user_id == user_id).all()
    
    winning_trades = [t for t in trades if t.status == "completed"]
    wins = len([t for t in winning_trades if t.side == "sell"])  # Simplified
    
    return {
        "win_rate": (wins / len(winning_trades) * 100) if winning_trades else 0,
        "total_trades": len(trades),
        "completed_trades": len(winning_trades),
        "avg_trade_value": sum(t.price * t.quantity for t in winning_trades) / len(winning_trades) if winning_trades else 0,
        "pnl_ytd": 0,  # Calculate from actual trades
        "pnl_mtd": 0,
    }

@router.get("/pnl-analytics/{user_id}")
async def get_pnl_analytics(user_id: int, days: int = 30, db: Session = Depends(get_db)):
    """Get daily P&L analytics"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Mock data - in production, aggregate from trades
    return {
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "daily_pnl": [
            {
                "date": (end_date - timedelta(days=i)).strftime("%Y-%m-%d"),
                "pnl": -500 + i * 100,
                "cumulative": i * 1000,
            }
            for i in range(days)
        ],
    }

---

# backend/app/api/v1/scanner.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any

from app.database.session import get_db
from app.database.models import Scan

router = APIRouter()

class ScanCondition(BaseModel):
    indicator: str
    operator: str
    value: float

class CreateScanRequest(BaseModel):
    name: str
    description: str
    conditions: List[ScanCondition]

@router.get("/scans")
async def list_scans(user_id: int = Query(None), db: Session = Depends(get_db)):
    """List available scans"""
    query = db.query(Scan)
    
    if user_id:
        query = query.filter((Scan.user_id == user_id) | (Scan.is_public == True))
    else:
        query = query.filter(Scan.is_public == True)
    
    scans = query.all()
    
    return {
        "count": len(scans),
        "scans": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "conditions_count": len(s.conditions) if s.conditions else 0,
                "is_public": s.is_public,
                "created_at": s.created_at.isoformat(),
            }
            for s in scans
        ],
    }

@router.post("/create-scan")
async def create_scan(
    request: CreateScanRequest,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Create a new scan"""
    scan = Scan(
        user_id=user_id,
        name=request.name,
        description=request.description,
        conditions=[c.dict() for c in request.conditions],
        is_public=False,
    )
    
    db.add(scan)
    db.commit()
    db.refresh(scan)
    
    return {"scan_id": scan.id, "message": "Scan created successfully"}

@router.post("/run-scan/{scan_id}")
async def run_scan(scan_id: int, db: Session = Depends(get_db)):
    """Execute a scan and return results"""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    
    if not scan:
        return {"error": "Scan not found"}
    
    # In production, integrate with market data service
    results = [
        {"symbol": "RELIANCE", "score": 85, "match_count": 4},
        {"symbol": "TCS", "score": 78, "match_count": 3},
        {"symbol": "INFY", "score": 72, "match_count": 3},
        {"symbol": "WIPRO", "score": 65, "match_count": 2},
    ]
    
    return {
        "scan_id": scan_id,
        "scan_name": scan.name,
        "result_count": len(results),
        "results": results,
    }

---

# backend/app/api/v1/strategy.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any

from app.database.session import get_db
from app.database.models import Strategy

router = APIRouter()

class StrategyCondition(BaseModel):
    type: str  # indicator, price_action, custom
    params: Dict[str, Any]

class CreateStrategyRequest(BaseModel):
    name: str
    description: str
    entry_conditions: List[StrategyCondition]
    exit_conditions: List[StrategyCondition]
    position_sizing: Dict[str, Any]

@router.get("/strategies/{user_id}")
async def get_user_strategies(user_id: int, db: Session = Depends(get_db)):
    """Get all strategies for a user"""
    strategies = db.query(Strategy).filter(Strategy.user_id == user_id).all()
    
    return {
        "count": len(strategies),
        "strategies": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "is_active": s.is_active,
                "is_approved": s.is_approved,
                "created_at": s.created_at.isoformat(),
            }
            for s in strategies
        ],
    }

@router.post("/create-strategy")
async def create_strategy(
    request: CreateStrategyRequest,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Create a new strategy"""
    strategy = Strategy(
        user_id=user_id,
        name=request.name,
        description=request.description,
        entry_conditions=[c.dict() for c in request.entry_conditions],
        exit_conditions=[c.dict() for c in request.exit_conditions],
        position_sizing=request.position_sizing,
        is_active=False,
        is_approved=False,
    )
    
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    
    return {
        "strategy_id": strategy.id,
        "message": "Strategy created successfully. Awaiting approval.",
    }

---

# backend/app/api/v1/backtest.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.database.session import get_db
from app.database.models import Strategy, BacktestResult

router = APIRouter()

class BacktestRequest(BaseModel):
    strategy_id: int
    start_date: datetime
    end_date: datetime
    initial_capital: float = 100000

@router.post("/backtest-strategy")
async def backtest_strategy(
    request: BacktestRequest,
    db: Session = Depends(get_db)
):
    """Run backtest on a strategy"""
    strategy = db.query(Strategy).filter(Strategy.id == request.strategy_id).first()
    
    if not strategy:
        return {"error": "Strategy not found"}
    
    # Mock backtest results
    result = BacktestResult(
        strategy_id=request.strategy_id,
        total_return=25.5,
        cagr=7.2,
        max_drawdown=-12.3,
        sharpe_ratio=1.85,
        win_rate=58.5,
        profit_factor=2.1,
        expectancy=150.75,
        start_date=request.start_date,
        end_date=request.end_date,
    )
    
    db.add(result)
    db.commit()
    db.refresh(result)
    
    return {
        "backtest_id": result.id,
        "strategy_id": request.strategy_id,
        "metrics": {
            "total_return": result.total_return,
            "cagr": result.cagr,
            "max_drawdown": result.max_drawdown,
            "sharpe_ratio": result.sharpe_ratio,
            "win_rate": result.win_rate,
            "profit_factor": result.profit_factor,
            "expectancy": result.expectancy,
        },
    }

@router.get("/backtest-results/{backtest_id}")
async def get_backtest_results(backtest_id: int, db: Session = Depends(get_db)):
    """Get detailed backtest results"""
    result = db.query(BacktestResult).filter(BacktestResult.id == backtest_id).first()
    
    if not result:
        return {"error": "Backtest not found"}
    
    return {
        "id": result.id,
        "strategy_id": result.strategy_id,
        "period": {
            "start": result.start_date.isoformat(),
            "end": result.end_date.isoformat(),
        },
        "metrics": {
            "total_return": result.total_return,
            "cagr": result.cagr,
            "max_drawdown": result.max_drawdown,
            "sharpe_ratio": result.sharpe_ratio,
            "win_rate": result.win_rate,
            "profit_factor": result.profit_factor,
            "expectancy": result.expectancy,
        },
        "equity_curve": [
            {
                "date": (result.start_date + timedelta(days=i)).strftime("%Y-%m-%d"),
                "value": 100000 + i * 500,
            }
            for i in range(int((result.end_date - result.start_date).days))
        ],
    }
