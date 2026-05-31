"""
Configuration and settings for the trading platform
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
LOG_DIR = BASE_DIR / "logs"
DB_DIR = BASE_DIR / "database"

# Ensure directories exist
LOG_DIR.mkdir(exist_ok=True)
DB_DIR.mkdir(exist_ok=True)

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trading_ai.db")
DB_PATH = DB_DIR / "trading_ai.db"

# Trading Parameters
STARTING_CAPITAL = float(os.getenv("STARTING_CAPITAL", "100000"))
RISK_PER_TRADE = float(os.getenv("RISK_PER_TRADE", "0.01"))  # 1% max risk
DAILY_LOSS_LIMIT = float(os.getenv("DAILY_LOSS_LIMIT", "0.02"))  # 2% daily limit
MAX_DRAWDOWN = float(os.getenv("MAX_DRAWDOWN", "0.10"))  # 10% max drawdown

# Market Parameters
NIFTY_50_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HINDUNILVR.NS", "ICICIBANK.NS",
    "HDFC.NS", "MARUTI.NS", "BAJAJ-AUTO.NS", "LT.NS", "AXISBANK.NS",
    "BHARTIARTL.NS", "ITC.NS", "SBIN.NS", "WIPRO.NS", "ULTRACEMCO.NS",
    "NESTLEIND.NS", "POWERGRID.NS", "SUNPHARMA.NS", "DRREDDY.NS", "JSWSTEEL.NS",
    "M&M.NS", "BAJAJFINSV.NS", "INDUSIND.NS", "HDFCBANK.NS", "GRASIM.NS",
    "TECHM.NS", "TATASTEEL.NS", "TITAN.NS", "ANOTHERSTOCK.NS", "COALINDIA.NS",
    "BPCL.NS", "NTPC.NS", "IOC.NS", "LT.NS", "MRF.NS",
    "EICHERMOT.NS", "BRITANNIA.NS", "ADANIPORTS.NS", "ADANIGREEN.NS", "ADANITRANS.NS"
]

# Technical Indicators
EMA_FAST = int(os.getenv("EMA_FAST", "20"))
EMA_SLOW = int(os.getenv("EMA_SLOW", "50"))
RSI_PERIOD = int(os.getenv("RSI_PERIOD", "14"))
RSI_OVERBOUGHT = float(os.getenv("RSI_OVERBOUGHT", "70"))
RSI_OVERSOLD = float(os.getenv("RSI_OVERSOLD", "30"))
MACD_FAST = int(os.getenv("MACD_FAST", "12"))
MACD_SLOW = int(os.getenv("MACD_SLOW", "26"))
MACD_SIGNAL = int(os.getenv("MACD_SIGNAL", "9"))
ATR_PERIOD = int(os.getenv("ATR_PERIOD", "14"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOG_DIR / "trading_ai.log"

# Streamlit
STREAMLIT_THEME = "dark"
STREAMLIT_PAGE_CONFIG = {
    "page_title": "AI Trading Platform",
    "page_icon": "📈",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# Paper Trading
PAPER_TRADING_ENABLED = True
DEFAULT_POSITION_HOLD_DAYS = 5

print(f"✓ Configuration loaded from {BASE_DIR}")
print(f"✓ Database: {DB_PATH}")
print(f"✓ Logs: {LOG_DIR}")
