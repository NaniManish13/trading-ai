# 🚀 AI-Powered Swing Trading Platform

A complete, production-ready swing trading platform with multi-agent AI, paper trading simulation, backtesting, and technical analysis.

## 📋 Features

### 🤖 Multi-Agent System
- **Market Scanner Agent**: Identifies trading opportunities in NIFTY 50 stocks
- **Technical Agent**: Evaluates technical indicators (RSI, EMA, MACD, ATR)
- **Sentiment Agent**: Analyzes financial news using Google Gemini API
- **Risk Agent**: Manages position sizing and portfolio risk
- **Decision Agent**: Aggregates all signals for final trading decisions

### 💼 Paper Trading Engine
- Simulated buy/sell execution
- Position tracking and P&L calculation
- Stop loss and take profit management
- Real-time portfolio valuation
- Daily P&L and performance metrics

### 📊 Analytics & Backtesting
- Historical strategy testing
- CAGR, Sharpe Ratio, Max Drawdown calculations
- Win rate and profit factor analysis
- EMA Crossover and RSI strategies
- Customizable testing parameters

### 📈 Streamlit Dashboard
- Real-time portfolio overview
- Market scanner with opportunity ranking
- Technical analysis charts
- Sentiment analysis interface
- Trade execution and management
- Trade journal with statistics
- Settings and configuration

## 🛠️ Tech Stack

- **Python 3.12+**
- **Streamlit** - Interactive web dashboard
- **FastAPI** - REST API (extensible)
- **SQLAlchemy** - ORM with SQLite/PostgreSQL support
- **Pandas & NumPy** - Data processing
- **yfinance** - Market data
- **ta** - Technical indicators
- **Google Gemini API** - Sentiment analysis
- **Docker** - Containerization

## 📁 Project Structure

```
trading-ai/
├── agents/                 # AI agent modules
│   ├── market_scanner.py  # Market opportunity scanner
│   ├── technical_agent.py # Technical analysis
│   ├── sentiment_agent.py # Sentiment analysis
│   ├── risk_agent.py      # Risk management
│   └── decision_agent.py  # Signal aggregation
│
├── dashboard/
│   └── app.py             # Streamlit UI
│
├── database/
│   ├── models.py          # SQLAlchemy models
│   ├── connection.py      # DB connection
│   └── schema.py          # Schema documentation
│
├── services/
│   ├── market_data.py     # Data fetching
│   ├── indicators.py      # Indicator calculations
│   ├── sentiment.py       # Sentiment analysis
│   └── portfolio.py       # Portfolio management
│
├── paper_trading/
│   ├── simulator.py       # Trading simulator
│   └── journal.py         # Trade journal
│
├── backtesting/
│   └── backtest.py        # Backtesting engine
│
├── config/
│   └── settings.py        # Configuration
│
├── logs/                  # Application logs
├── tests/                 # Unit tests
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🚀 Quick Start

### 1. Clone & Setup

```bash
cd "c:\Users\ADMIN\Downloads\trading ai"
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

### 4. Initialize Database

```bash
python -c "from database.connection import init_db; init_db()"
```

### 5. Run Application

```bash
streamlit run dashboard/app.py
```

The dashboard will open at `http://localhost:8501`

## 🐳 Docker Deployment

### Build & Run

```bash
docker-compose up --build
```

Access at `http://localhost:8501`

### Stop

```bash
docker-compose down
```

## 📊 Dashboard Pages

### 1. 📊 Overview
- Portfolio value and cash balance
- Open positions summary
- Recent trades
- Performance metrics (return %, win rate, drawdown)

### 2. 🔍 Market Scanner
- Scan NIFTY 50 stocks
- Identify trading opportunities
- View technical scores
- Volume breakout detection

### 3. 📈 Technical Analysis
- Select symbol and timeframe
- RSI, EMA, MACD analysis
- Support/resistance levels
- Trend identification

### 4. 💬 Sentiment Analysis
- Input financial news text
- Get Gemini AI analysis
- Sentiment score and confidence
- Trading implications

### 5. 💼 Paper Trading
- Execute BUY/SELL trades
- Set stop loss and take profit
- View execution results
- Track position management

### 6. 📉 Backtesting
- Test strategies on historical data
- EMA Crossover strategy
- RSI strategy
- View CAGR, Sharpe Ratio, drawdown

### 7. 📋 Trade Journal
- View all trades
- Statistics and performance
- Export to CSV
- Win rate analysis

### 8. ⚙️ Settings
- API key configuration
- Trading parameters
- Risk management settings

## 🔑 API Configuration

### Google Gemini API

1. Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set in `.env`:
   ```
   GEMINI_API_KEY=your_key_here
   ```

### Optional: Alpha Vantage

For additional market data:
```
ALPHA_VANTAGE_KEY=your_key_here
```

## 📊 Risk Management

### Default Settings

- **Risk per Trade**: 1% of portfolio
- **Daily Loss Limit**: 2% of portfolio
- **Max Drawdown**: 10% of portfolio
- **Starting Capital**: $100,000 (configurable)

### Position Sizing

```
Position Size = (Portfolio Risk Amount) / Stop Loss Distance
Position Risk = 1% of portfolio value
```

### Stop Loss & Take Profit

- Stop Loss: 2× ATR below entry
- Take Profit: Risk/Reward ratio of 2:1

## 🧪 Testing

### Run Tests

```bash
pytest tests/ -v
```

### Manual Testing

```bash
python -c "
from services.market_data import MarketDataService
from services.indicators import IndicatorsService

# Test market data
service = MarketDataService()
data = service.get_ohlcv('TCS.NS', period='1mo')
print('Data shape:', data.shape)

# Test indicators
indicators = IndicatorsService.get_signal_analysis(data)
print('Signal:', indicators)
"
```

## 📈 Supported Indicators

- **RSI** (Relative Strength Index)
- **EMA** (Exponential Moving Average) - 20, 50
- **MACD** (Moving Average Convergence Divergence)
- **ATR** (Average True Range)
- **Volume Analysis**
- **Support/Resistance Levels**

## 🎯 Trading Signals

### Buy Signal Criteria
- EMA 20 > EMA 50 (bullish trend)
- RSI < 30 (oversold)
- MACD > Signal Line
- Volume breakout confirmed
- Risk approval from Risk Agent

### Sell Signal Criteria
- EMA 20 < EMA 50 (bearish trend)
- RSI > 70 (overbought)
- MACD < Signal Line
- Daily loss limit approaching
- Stop loss hit

### Hold Signal
- Mixed signals
- Insufficient data
- Risk parameters not met

## 📝 Trade Journal Features

- **Entry Recording**: Price, quantity, stop loss, take profit
- **AI Scoring**: Technical, sentiment, risk scores
- **Exit Tracking**: Exit date, price, P&L
- **Statistics**: Win rate, profit factor, average win/loss
- **CSV Export**: Full trade history

## 🔄 Workflow Example

```
1. Market Scanner runs → Identifies opportunities
2. Technical Agent analyzes → Generates buy/sell signals
3. Sentiment Agent evaluates → News impact analysis
4. Risk Agent validates → Position sizing approved
5. Decision Agent aggregates → Final BUY/SELL decision
6. Paper Trading executes → Order placed
7. Trade Journal records → Trade logged
8. Monitoring continues → Check SL/TP every candle
```

## 🐛 Troubleshooting

### "Insufficient data" Error
- Use longer period (6mo instead of 1mo)
- Ensure internet connection for yfinance

### Streamlit not loading
```bash
pip install --upgrade streamlit
streamlit run dashboard/app.py --logger.level=debug
```

### Database errors
```bash
python -c "from database.connection import init_db; init_db()"
```

### API Rate Limits
- Gemini API has rate limits
- Implement caching for frequently analyzed stocks

## 🚀 Performance Optimization

- Cache market data (5 min intervals)
- Batch process multiple symbols
- Use async calls for API
- Optimize database queries

## 📚 Documentation

### Database Models
See `database/models.py` for complete schema

### Configuration
See `config/settings.py` for all parameters

### Agent Documentation
Each agent module has detailed docstrings

## 🔐 Security

- Store API keys in `.env` (never commit)
- Use environment variables for sensitive data
- Validate all user inputs
- Sanitize database queries with SQLAlchemy

## 🎓 Learning Resources

- [yfinance Documentation](https://github.com/ranaroussi/yfinance)
- [ta-lib Technical Indicators](https://github.com/bukosabino/ta)
- [Streamlit Documentation](https://docs.streamlit.io)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org)

## 📄 License

This project is for educational and research purposes only. Not financial advice.

## ⚠️ Disclaimer

**Paper trading only** - no real money transactions. This platform simulates trading for:
- Strategy testing
- Risk management practice
- Algorithm development
- Educational purposes

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional technical indicators
- Machine learning predictions
- Real-time news feeds
- Real broker integration (with caution)
- Advanced charting
- More backtesting strategies

## 📞 Support

For issues or questions:
1. Check documentation in code comments
2. Review example trades in dashboard
3. Check logs in `logs/trading_ai.log`
4. Run diagnostic tests

## 🎉 Features Coming Soon

- [ ] Real-time WebSocket feeds
- [ ] Machine learning predictions
- [ ] Advanced charting with TradingView
- [ ] Email/SMS notifications
- [ ] Mobile app
- [ ] Real broker integration (paper account only)
- [ ] Multi-timeframe analysis
- [ ] Portfolio correlation analysis

---

**Last Updated**: 2026-05-31
**Version**: 1.0.0
**Status**: ✅ Ready for Paper Trading
