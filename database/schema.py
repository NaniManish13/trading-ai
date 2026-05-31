"""
Database schema documentation
"""

SCHEMA_DOC = """
TRADING AI DATABASE SCHEMA
===========================

1. PORTFOLIO
   - id (PK)
   - date (UNIQUE) - Portfolio snapshot date
   - total_value - Total portfolio value
   - cash_balance - Available cash
   - open_positions_value - Value of open positions
   - realized_pnl - Closed positions profit/loss
   - unrealized_pnl - Open positions profit/loss
   - win_rate - Percentage of winning trades
   - total_trades - Total trades executed
   - created_at

2. TRADES
   - id (PK)
   - portfolio_id (FK)
   - symbol - Stock ticker
   - entry_price - Entry price
   - exit_price - Exit price (null if open)
   - quantity - Number of shares
   - side - BUY or SELL
   - entry_date
   - exit_date
   - pnl - Profit/Loss in currency
   - pnl_percent - Profit/Loss percentage
   - stop_loss
   - take_profit
   - status - OPEN, CLOSED, CANCELLED
   - technical_score - Score from technical agent
   - sentiment_score - Score from sentiment agent
   - risk_score - Score from risk agent
   - reasoning - Why the trade was made

3. POSITIONS
   - id (PK)
   - portfolio_id (FK)
   - symbol (UNIQUE) - Stock ticker
   - quantity - Current quantity held
   - entry_price - Average entry price
   - current_price - Latest price
   - entry_date
   - stop_loss
   - take_profit
   - unrealized_pnl
   - unrealized_pnl_percent

4. SIGNALS
   - id (PK)
   - symbol
   - signal_type - BUY, SELL, HOLD
   - technical_signal - From technical agent
   - sentiment_signal - From sentiment agent
   - risk_approved - From risk agent
   - confidence - 0-1 confidence score
   - timestamp
   - technical_details (JSON)
   - sentiment_details (JSON)
   - reasoning

5. NEWS
   - id (PK)
   - symbol
   - title
   - content
   - source
   - sentiment - POSITIVE, NEGATIVE, NEUTRAL
   - confidence
   - analysis (Gemini analysis)
   - created_at

6. BACKTEST_RESULTS
   - id (PK)
   - strategy_name
   - symbol
   - start_date
   - end_date
   - initial_capital
   - final_capital
   - total_return
   - cagr - Compound Annual Growth Rate
   - sharpe_ratio
   - max_drawdown
   - win_rate
   - total_trades
   - avg_win
   - avg_loss
   - profit_factor
   - created_at
"""

if __name__ == "__main__":
    print(SCHEMA_DOC)
