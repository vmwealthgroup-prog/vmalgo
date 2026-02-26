-- database/schema.sql
-- VM Algo Research Lab - PostgreSQL Schema

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    subscription_tier VARCHAR(50) DEFAULT 'free', -- free, pro, elite
    api_limit INT DEFAULT 100,
    two_fa_enabled BOOLEAN DEFAULT false,
    two_fa_secret VARCHAR(255),
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_subscription ON users(subscription_tier);

-- API Credentials (Encrypted Storage)
CREATE TABLE api_credentials (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    broker VARCHAR(50) NOT NULL, -- zerodha, angel_one, binance
    api_key VARCHAR(500) NOT NULL, -- Encrypted
    api_secret VARCHAR(500) NOT NULL, -- Encrypted
    api_token VARCHAR(500), -- For token-based auth
    is_active BOOLEAN DEFAULT true,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, broker)
);

CREATE INDEX idx_api_credentials_user_id ON api_credentials(user_id);
CREATE INDEX idx_api_credentials_broker ON api_credentials(broker);

-- Strategies Table
CREATE TABLE strategies (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Strategy Logic (JSON format)
    entry_conditions JSONB NOT NULL, -- Array of condition objects
    exit_conditions JSONB NOT NULL,
    position_sizing JSONB, -- Position sizing rules
    
    -- Configuration
    is_active BOOLEAN DEFAULT false,
    is_approved BOOLEAN DEFAULT false,
    approval_notes TEXT,
    
    -- Metadata
    wins INT DEFAULT 0,
    losses INT DEFAULT 0,
    total_trades INT DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_strategies_user_id ON strategies(user_id);
CREATE INDEX idx_strategies_is_active ON strategies(is_active);
CREATE INDEX idx_strategies_is_approved ON strategies(is_approved);

-- Backtest Results
CREATE TABLE backtest_results (
    id SERIAL PRIMARY KEY,
    strategy_id INT NOT NULL REFERENCES strategies(id) ON DELETE CASCADE,
    
    -- Metrics
    total_return FLOAT NOT NULL,
    cagr FLOAT NOT NULL,
    max_drawdown FLOAT NOT NULL,
    sharpe_ratio FLOAT NOT NULL,
    win_rate FLOAT NOT NULL,
    profit_factor FLOAT,
    expectancy FLOAT,
    
    -- Period
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    
    -- Equity Curve (Daily values)
    equity_curve JSONB, -- Array of {date, value}
    trades_log JSONB, -- Detailed trades
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_backtest_strategy_id ON backtest_results(strategy_id);
CREATE INDEX idx_backtest_created_at ON backtest_results(created_at);

-- Scans Table
CREATE TABLE scans (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    
    name VARCHAR(255) NOT NULL,
    description TEXT,
    conditions JSONB NOT NULL, -- Array of scan conditions
    
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_scans_user_id ON scans(user_id);
CREATE INDEX idx_scans_is_public ON scans(is_public);

-- Positions Table
CREATE TABLE positions (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    strategy_id INT REFERENCES strategies(id) ON DELETE SET NULL,
    
    -- Stock Information
    symbol VARCHAR(20) NOT NULL,
    quantity INT NOT NULL,
    entry_price FLOAT NOT NULL,
    entry_time TIMESTAMP NOT NULL,
    
    -- Exit Strategy
    stop_loss FLOAT,
    target FLOAT,
    trailing_stop FLOAT,
    trailing_stop_percent FLOAT,
    
    -- Current Status
    current_price FLOAT,
    pnl FLOAT,
    pnl_percent FLOAT,
    
    -- Position Lifecycle
    status VARCHAR(20) DEFAULT 'open', -- open, closed, partially_closed
    closed_price FLOAT,
    closed_time TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_positions_user_id ON positions(user_id);
CREATE INDEX idx_positions_strategy_id ON positions(strategy_id);
CREATE INDEX idx_positions_symbol ON positions(symbol);
CREATE INDEX idx_positions_status ON positions(status);

-- Trades Table
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    position_id INT REFERENCES positions(id) ON DELETE SET NULL,
    
    -- Trade Details
    symbol VARCHAR(20) NOT NULL,
    order_id VARCHAR(100) UNIQUE,
    broker_order_id VARCHAR(100),
    
    side VARCHAR(10) NOT NULL, -- buy, sell
    quantity INT NOT NULL,
    price FLOAT NOT NULL,
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- pending, completed, rejected, cancelled
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP,
    
    -- Additional Details
    commission FLOAT,
    slippage FLOAT
);

CREATE INDEX idx_trades_user_id ON trades(user_id);
CREATE INDEX idx_trades_position_id ON trades(position_id);
CREATE INDEX idx_trades_symbol ON trades(symbol);
CREATE INDEX idx_trades_status ON trades(status);
CREATE INDEX idx_trades_created_at ON trades(created_at);

-- Alerts Table
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    alert_type VARCHAR(50) NOT NULL, -- price, indicator, news, pattern
    symbol VARCHAR(20),
    condition JSONB NOT NULL,
    
    is_active BOOLEAN DEFAULT true,
    alert_count INT DEFAULT 0,
    last_triggered TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alerts_user_id ON alerts(user_id);
CREATE INDEX idx_alerts_is_active ON alerts(is_active);

-- Audit Logs
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    action VARCHAR(255) NOT NULL, -- strategy_created, position_opened, trade_executed
    resource_type VARCHAR(50), -- strategy, position, trade
    resource_id INT,
    details JSONB,
    
    ip_address VARCHAR(50),
    user_agent TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- Market Data Cache
CREATE TABLE market_data_cache (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10), -- 1m, 5m, 15m, 1h, 1d
    
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume BIGINT,
    
    timestamp TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_market_data_symbol_timestamp ON market_data_cache(symbol, timestamp);
CREATE INDEX idx_market_data_timeframe ON market_data_cache(timeframe);

-- Portfolio Summary (Denormalized for performance)
CREATE TABLE portfolio_summary (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    
    total_capital FLOAT,
    cash_available FLOAT,
    invested_capital FLOAT,
    
    today_pnl FLOAT,
    today_pnl_percent FLOAT,
    mtd_pnl FLOAT,
    ytd_pnl FLOAT,
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_portfolio_summary_user_id ON portfolio_summary(user_id);

-- Subscriptions Table
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    
    tier VARCHAR(50) NOT NULL, -- free, pro, elite
    status VARCHAR(20) DEFAULT 'active', -- active, cancelled, suspended
    
    start_date DATE NOT NULL,
    renewal_date DATE,
    cancel_date DATE,
    
    auto_renew BOOLEAN DEFAULT true,
    amount FLOAT,
    currency VARCHAR(3) DEFAULT 'INR',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_tier ON subscriptions(tier);

-- AI Predictions Table
CREATE TABLE ai_predictions (
    id SERIAL PRIMARY KEY,
    
    symbol VARCHAR(20) NOT NULL,
    prediction_type VARCHAR(50), -- sentiment, volatility, price_direction
    
    prediction_value FLOAT,
    confidence FLOAT,
    
    generated_at TIMESTAMP NOT NULL,
    horizon_days INT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_predictions_symbol ON ai_predictions(symbol);
CREATE INDEX idx_ai_predictions_created_at ON ai_predictions(created_at);

-- Create triggers for updated_at columns
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER users_update_timestamp BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER strategies_update_timestamp BEFORE UPDATE ON strategies
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER positions_update_timestamp BEFORE UPDATE ON positions
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER scans_update_timestamp BEFORE UPDATE ON scans
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER alerts_update_timestamp BEFORE UPDATE ON alerts
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER api_credentials_update_timestamp BEFORE UPDATE ON api_credentials
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- Create important views
CREATE VIEW user_statistics AS
SELECT 
    u.id,
    u.username,
    u.subscription_tier,
    COUNT(DISTINCT s.id) as strategy_count,
    COUNT(DISTINCT p.id) as position_count,
    COUNT(DISTINCT t.id) as trade_count,
    u.created_at
FROM users u
LEFT JOIN strategies s ON u.id = s.user_id
LEFT JOIN positions p ON u.id = p.user_id
LEFT JOIN trades t ON u.id = t.user_id
GROUP BY u.id, u.username, u.subscription_tier, u.created_at;

-- Grants (Customize based on your deployment)
-- CREATE ROLE vm_algo_app WITH PASSWORD 'secure-password';
-- GRANT CONNECT ON DATABASE vm_algo_db TO vm_algo_app;
-- GRANT USAGE ON SCHEMA public TO vm_algo_app;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vm_algo_app;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vm_algo_app;
