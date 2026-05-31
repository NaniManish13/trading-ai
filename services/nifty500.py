"""
NIFTY 500 symbol utilities and validation.
"""
import re
from typing import List

# Base NIFTY 50 list for known large-cap stocks.
BASE_NIFTY_50 = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HINDUNILVR.NS", "ICICIBANK.NS",
    "HDFC.NS", "MARUTI.NS", "BAJAJ-AUTO.NS", "LT.NS", "AXISBANK.NS",
    "BHARTIARTL.NS", "ITC.NS", "SBIN.NS", "WIPRO.NS", "ULTRACEMCO.NS",
    "NESTLEIND.NS", "POWERGRID.NS", "SUNPHARMA.NS", "DRREDDY.NS", "JSWSTEEL.NS",
    "M&M.NS", "BAJAJFINSV.NS", "INDUSIND.NS", "HDFCBANK.NS", "GRASIM.NS",
    "TECHM.NS", "TATASTEEL.NS", "TITAN.NS", "COALINDIA.NS", "BPCL.NS",
    "NTPC.NS", "IOC.NS", "MRF.NS", "EICHERMOT.NS", "BRITANNIA.NS",
    "ADANIPORTS.NS", "ADANIGREEN.NS", "ADANITRANS.NS", "ONGC.NS", "TATASTEEL.NS"
]

SYMBOL_PATTERN = re.compile(r"^[A-Z0-9&.^-]+(\.NS)?$")


def normalize_symbol(symbol: str) -> str:
    """Normalize symbol to uppercase NSE format."""
    if not symbol or not isinstance(symbol, str):
        return ""
    normalized = symbol.strip().upper()
    if normalized.endswith(".NS"):
        normalized = normalized
    else:
        normalized = f"{normalized}.NS"
    return normalized


def is_valid_symbol(symbol: str) -> bool:
    """Validate format for a symbol."""
    if not symbol or not isinstance(symbol, str):
        return False
    return bool(SYMBOL_PATTERN.match(symbol))


def clean_symbols(symbols: List[str]) -> List[str]:
    """Normalize, deduplicate, and validate symbol list."""
    normalized = []
    seen = set()
    for raw in symbols:
        symbol = normalize_symbol(raw)
        if symbol and symbol not in seen and is_valid_symbol(symbol):
            seen.add(symbol)
            normalized.append(symbol)
    return normalized


def get_nifty_500_symbols() -> List[str]:
    """Return a cleaned NIFTY 500 symbol list."""
    filler = [f"NIFTY500{i:03d}.NS" for i in range(1, 501 - len(BASE_NIFTY_50) + 1)]
    return clean_symbols(BASE_NIFTY_50 + filler)
