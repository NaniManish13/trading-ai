"""
Database models for the trading platform
"""
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, DateTime, Integer, Boolean, 
    Text, ForeignKey, create_engine, event
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Portfolio(Base):
    """Portfolio tracking model"""
    __tablename__ = "portfolio"
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow, unique=True)
    total_value = Column(Float)
    cash_balance = Column(Float)
    open_positions_value = Column(Float)
    realized_pnl = Column(Float, default=0)
    unrealized_pnl = Column(Float, default=0)
    win_rate = Column(Float, default=0)
    total_trades = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    trades = relationship("Trade", back_populates="portfolio")
    positions = relationship("Position", back_populates="portfolio")


class Trade(Base):
    """Trade history model"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey("portfolio.id"))
    symbol = Column(String(50), nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float)
    quantity = Column(Integer, nullable=False)
    side = Column(String(10), nullable=False)  # BUY or SELL
    entry_date = Column(DateTime, default=datetime.utcnow)
    exit_date = Column(DateTime)
    pnl = Column(Float)
    pnl_percent = Column(Float)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    status = Column(String(20), default="OPEN")  # OPEN, CLOSED, CANCELLED
    technical_score = Column(Float)
    sentiment_score = Column(Float)
    risk_score = Column(Float)
    reasoning = Column(Text)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="trades")


class Position(Base):
    """Open positions model"""
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey("portfolio.id"))
    symbol = Column(String(50), nullable=False, unique=True)
    quantity = Column(Integer, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float)
    entry_date = Column(DateTime, default=datetime.utcnow)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    unrealized_pnl = Column(Float, default=0)
    unrealized_pnl_percent = Column(Float, default=0)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="positions")


class Signal(Base):
    """Trading signals from agents"""
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(50), nullable=False)
    signal_type = Column(String(20), nullable=False)  # BUY, SELL, HOLD
    technical_signal = Column(String(20))
    sentiment_signal = Column(String(20))
    risk_approved = Column(Boolean)
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    technical_details = Column(Text)
    sentiment_details = Column(Text)
    reasoning = Column(Text)


class News(Base):
    """News and sentiment data"""
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(50), nullable=False)
    title = Column(String(500))
    content = Column(Text)
    source = Column(String(100))
    sentiment = Column(String(20))  # POSITIVE, NEGATIVE, NEUTRAL
    confidence = Column(Float)
    analysis = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class BacktestResult(Base):
    """Backtest results"""
    __tablename__ = "backtest_results"
    
    id = Column(Integer, primary_key=True)
    strategy_name = Column(String(100))
    symbol = Column(String(50))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    initial_capital = Column(Float)
    final_capital = Column(Float)
    total_return = Column(Float)
    cagr = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    win_rate = Column(Float)
    total_trades = Column(Integer)
    avg_win = Column(Float)
    avg_loss = Column(Float)
    profit_factor = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
