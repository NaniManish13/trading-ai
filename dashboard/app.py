"""
Main Streamlit Dashboard for Trading AI Platform
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config.settings import (
    STARTING_CAPITAL, NIFTY_50_STOCKS, STREAMLIT_PAGE_CONFIG,
    STREAMLIT_THEME
)
from agents.decision_agent import DecisionAgent
from agents.technical_agent import TechnicalAgent
from agents.sentiment_agent import SentimentAgent
from agents.market_scanner import MarketScannerAgent
from paper_trading.simulator import PaperTradingSimulator
from paper_trading.journal import TradeJournal
from backtesting.backtest import Backtester
from services.market_data import MarketDataService

# Configure Streamlit
st.set_page_config(**STREAMLIT_PAGE_CONFIG)

# Initialize session state
if 'simulator' not in st.session_state:
    st.session_state.simulator = PaperTradingSimulator(STARTING_CAPITAL)

if 'journal' not in st.session_state:
    st.session_state.journal = TradeJournal()

if 'decision_agent' not in st.session_state:
    st.session_state.decision_agent = DecisionAgent()

# Sidebar
with st.sidebar:
    st.header("🤖 AI Trading Platform")
    
    page = st.radio(
        "Select Page",
        [
            "📊 Overview",
            "🔍 Market Scanner",
            "📈 Technical Analysis",
            "💬 Sentiment Analysis",
            "💼 Paper Trading",
            "📉 Backtesting",
            "📋 Trade Journal",
            "⚙️ Settings"
        ]
    )
    
    st.divider()
    st.markdown("### Quick Stats")
    summary = st.session_state.simulator.get_summary()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Portfolio Value", f"${summary.get('current_value', 0):,.0f}")
    with col2:
        st.metric("Return", f"{summary.get('return_percent', 0):.2f}%")


# Page: Overview
if page == "📊 Overview":
    st.title("Portfolio Overview")
    
    summary = st.session_state.simulator.get_summary()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Value", f"${summary.get('current_value', 0):,.0f}")
    with col2:
        st.metric("Cash Balance", f"${summary.get('cash_balance', 0):,.0f}")
    with col3:
        st.metric("Open Positions", summary.get('open_positions', 0))
    with col4:
        st.metric("Total Trades", summary.get('total_trades', 0))
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Return %", f"{summary.get('return_percent', 0):.2f}%")
    with col2:
        st.metric("Win Rate", f"{summary.get('win_rate', 0):.1f}%")
    with col3:
        st.metric("Drawdown", f"{summary.get('drawdown', 0):.2f}%")
    with col4:
        st.metric("Daily P&L", f"${summary.get('daily_pnl', 0):,.0f}")
    
    st.divider()
    st.subheader("Open Positions")
    
    positions = st.session_state.simulator.get_positions()
    if positions:
        df_positions = pd.DataFrame(positions)
        st.dataframe(df_positions, use_container_width=True)
    else:
        st.info("No open positions")
    
    st.divider()
    st.subheader("Recent Trades")
    
    trades = st.session_state.simulator.get_trades(limit=10)
    if trades:
        df_trades = pd.DataFrame(trades)
        st.dataframe(df_trades, use_container_width=True)
    else:
        st.info("No trades yet")


# Page: Market Scanner
elif page == "🔍 Market Scanner":
    st.title("Market Scanner")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("Scanning NIFTY 50 stocks for trading opportunities...")
    with col2:
        if st.button("🔄 Scan Now"):
            with st.spinner("Scanning market..."):
                opportunities = st.session_state.decision_agent.get_market_opportunities()
                st.session_state.scan_results = opportunities
    
    if 'scan_results' in st.session_state:
        results = st.session_state.scan_results
        
        st.metric("Total Opportunities", results.get('total_opportunities', 0))
        
        if results.get('top_opportunities'):
            st.subheader("Top Opportunities")
            df = pd.DataFrame(results['top_opportunities'])
            st.dataframe(df, use_container_width=True)


# Page: Technical Analysis
elif page == "📈 Technical Analysis":
    st.title("Technical Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.selectbox("Select Symbol", NIFTY_50_STOCKS[:15])
    with col2:
        period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y"])
    
    if st.button("Analyze"):
        with st.spinner(f"Analyzing {symbol}..."):
            technical_agent = TechnicalAgent()
            analysis = technical_agent.analyze(symbol, period)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Signal", analysis.get('signal', 'N/A'))
            with col2:
                st.metric("Confidence", f"{analysis.get('confidence', 0):.1%}")
            with col3:
                st.metric("RSI", f"{analysis.get('details', {}).get('rsi', 0):.1f}")
            with col4:
                st.metric("ATR", f"{analysis.get('details', {}).get('atr', 0):.2f}")
            
            st.divider()
            st.json(analysis)


# Page: Sentiment Analysis
elif page == "💬 Sentiment Analysis":
    st.title("Sentiment Analysis")
    
    sentiment_text = st.text_area("Enter financial news or text to analyze:")
    symbol = st.text_input("Symbol (optional):")
    
    if st.button("Analyze Sentiment"):
        with st.spinner("Analyzing sentiment..."):
            sentiment_agent = SentimentAgent()
            result = sentiment_agent.analyze_text(sentiment_text, symbol)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Sentiment", result.get('sentiment', 'N/A'))
            with col2:
                st.metric("Confidence", f"{result.get('confidence', 0):.1%}")
            with col3:
                st.metric("Impact", result.get('impact', 'neutral'))
            
            st.divider()
            st.write(result.get('explanation', 'No explanation'))


# Page: Paper Trading
elif page == "💼 Paper Trading":
    st.title("Paper Trading")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        action = st.radio("Action", ["BUY", "SELL"])
    
    with col2:
        symbol = st.text_input("Symbol").upper()
    
    with col3:
        price = st.number_input("Price", min_value=0.01)
    
    col1, col2 = st.columns(2)
    with col1:
        quantity = st.number_input("Quantity", min_value=1, value=1)
    with col2:
        stop_loss = st.number_input("Stop Loss", min_value=0.01)
    
    take_profit = st.number_input("Take Profit", min_value=0.01)
    reasoning = st.text_area("Trade Reasoning:")
    
    if st.button("Execute Trade"):
        if action == "BUY":
            result = st.session_state.simulator.execute_buy(
                symbol, int(quantity), price, stop_loss, take_profit, reasoning
            )
        else:
            result = st.session_state.simulator.execute_sell(symbol, price, reasoning)
        
        if result.get('success'):
            st.success(f"✓ {action} order executed!")
            st.json(result)
        else:
            st.error(f"✗ Error: {result.get('reason', 'Unknown error')}")


# Page: Backtesting
elif page == "📉 Backtesting":
    st.title("Strategy Backtesting")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        symbol = st.text_input("Symbol").upper()
    with col2:
        strategy = st.selectbox("Strategy", ["EMA Crossover", "RSI"])
    with col3:
        period = st.selectbox("Period", ["3mo", "6mo", "1y", "2y", "5y"])
    
    initial_capital = st.number_input("Initial Capital", value=100000)
    
    if st.button("Run Backtest"):
        with st.spinner("Running backtest..."):
            backtester = Backtester()
            
            if strategy == "EMA Crossover":
                results = backtester.run_backtest(
                    symbol,
                    backtester.simple_ema_strategy,
                    initial_capital,
                    period
                )
            else:
                results = backtester.run_backtest(
                    symbol,
                    backtester.rsi_strategy,
                    initial_capital,
                    period
                )
            
            if 'error' not in results:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Return", f"{results.get('total_return_percent', 0):.2f}%")
                with col2:
                    st.metric("CAGR", f"{results.get('cagr_percent', 0):.2f}%")
                with col3:
                    st.metric("Sharpe Ratio", f"{results.get('sharpe_ratio', 0):.2f}")
                with col4:
                    st.metric("Max Drawdown", f"{results.get('max_drawdown_percent', 0):.2f}%")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Trades", results.get('total_trades', 0))
                with col2:
                    st.metric("Win Rate", f"{results.get('win_rate', 0):.1f}%")
                with col3:
                    st.metric("Profit Factor", f"{results.get('profit_factor', 0):.2f}")
                with col4:
                    st.metric("Final Capital", f"${results.get('final_capital', 0):,.0f}")
            else:
                st.error(results.get('error'))


# Page: Trade Journal
elif page == "📋 Trade Journal":
    st.title("Trade Journal")
    
    tab1, tab2, tab3 = st.tabs(["All Trades", "Statistics", "Export"])
    
    with tab1:
        entries = st.session_state.journal.get_all_entries()
        if entries:
            df = pd.DataFrame(entries)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No entries in journal")
    
    with tab2:
        stats = st.session_state.journal.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Entries", stats.get('total_entries', 0))
        with col2:
            st.metric("Open Entries", stats.get('open_entries', 0))
        with col3:
            st.metric("Closed Entries", stats.get('closed_entries', 0))
        with col4:
            st.metric("Win Rate", f"{stats.get('win_rate', 0):.1f}%")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Avg Win", f"${stats.get('avg_win', 0):,.0f}")
        with col2:
            st.metric("Avg Loss", f"${stats.get('avg_loss', 0):,.0f}")
        with col3:
            st.metric("Profit Factor", f"{stats.get('profit_factor', 0):.2f}")
        with col4:
            st.metric("Total P&L", f"${stats.get('total_pnl', 0):,.0f}")
    
    with tab3:
        filepath = st.text_input("Export path:", "trade_journal.csv")
        if st.button("Export"):
            st.session_state.journal.export_csv(filepath)
            st.success(f"✓ Exported to {filepath}")


# Page: Settings
elif page == "⚙️ Settings":
    st.title("Settings")
    
    st.subheader("API Keys")
    gemini_key = st.text_input("Gemini API Key", type="password", value="")
    
    st.divider()
    st.subheader("Trading Parameters")
    
    col1, col2 = st.columns(2)
    with col1:
        risk_per_trade = st.slider("Risk per Trade %", 0.1, 5.0, 1.0, 0.1)
    with col2:
        daily_loss_limit = st.slider("Daily Loss Limit %", 1.0, 10.0, 2.0, 0.5)
    
    st.divider()
    st.subheader("System Info")
    st.info(f"**Platform Version**: 1.0.0\n**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.sidebar.markdown("---")
st.sidebar.markdown("📌 **AI Trading Platform v1.0**\n*Paper Trading Only*")
