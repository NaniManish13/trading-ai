"""
Trade Journal - Records and analysis of trades
"""
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)

JOURNAL_FILE = Path(__file__).parent.parent / "logs" / "trade_journal.json"


class TradeJournal:
    """Manage trade journal"""
    
    def __init__(self):
        """Initialize journal"""
        self.journal_file = JOURNAL_FILE
        self.load_journal()
    
    def load_journal(self):
        """Load journal from file"""
        try:
            if self.journal_file.exists():
                with open(self.journal_file, 'r') as f:
                    self.entries = json.load(f)
                logger.info(f"✓ Loaded {len(self.entries)} journal entries")
            else:
                self.entries = []
        except Exception as e:
            logger.warning(f"Error loading journal: {e}")
            self.entries = []
    
    def save_journal(self):
        """Save journal to file"""
        try:
            with open(self.journal_file, 'w') as f:
                json.dump(self.entries, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving journal: {e}")
    
    def add_entry(
        self,
        symbol: str,
        side: str,
        quantity: int,
        price: float,
        stop_loss: float,
        take_profit: float,
        technical_score: float,
        sentiment_score: float,
        risk_score: float,
        reasoning: str = "",
    ) -> Dict:
        """
        Add entry to journal
        
        Args:
            symbol: Stock symbol
            side: BUY or SELL
            quantity: Number of shares
            price: Price per share
            stop_loss: Stop loss price
            take_profit: Take profit price
            technical_score: Technical analysis score
            sentiment_score: Sentiment analysis score
            risk_score: Risk score
            reasoning: Trade reasoning
        
        Returns:
            Created entry
        """
        try:
            entry = {
                'id': len(self.entries) + 1,
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': price,
                'value': quantity * price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'technical_score': technical_score,
                'sentiment_score': sentiment_score,
                'risk_score': risk_score,
                'reasoning': reasoning,
                'status': 'OPEN',
            }
            
            self.entries.append(entry)
            self.save_journal()
            
            return entry
        except Exception as e:
            logger.error(f"Error adding journal entry: {e}")
            return {}
    
    def update_entry(
        self,
        entry_id: int,
        exit_price: float,
        exit_date: str = None,
        pnl: float = 0,
        pnl_percent: float = 0,
        notes: str = "",
    ) -> Dict:
        """
        Update entry with exit info
        
        Args:
            entry_id: Journal entry ID
            exit_price: Exit price
            exit_date: Exit date
            pnl: Profit/loss
            pnl_percent: Profit/loss percentage
            notes: Exit notes
        
        Returns:
            Updated entry
        """
        try:
            for entry in self.entries:
                if entry['id'] == entry_id:
                    entry['exit_price'] = exit_price
                    entry['exit_date'] = exit_date or datetime.now().isoformat()
                    entry['pnl'] = pnl
                    entry['pnl_percent'] = pnl_percent
                    entry['exit_notes'] = notes
                    entry['status'] = 'CLOSED'
                    self.save_journal()
                    return entry
            
            return {}
        except Exception as e:
            logger.error(f"Error updating entry: {e}")
            return {}
    
    def get_entry(self, entry_id: int) -> Dict:
        """Get entry by ID"""
        for entry in self.entries:
            if entry['id'] == entry_id:
                return entry
        return {}
    
    def get_all_entries(self) -> List[Dict]:
        """Get all entries"""
        return self.entries
    
    def get_open_entries(self) -> List[Dict]:
        """Get open entries"""
        return [e for e in self.entries if e.get('status') == 'OPEN']
    
    def get_closed_entries(self) -> List[Dict]:
        """Get closed entries"""
        return [e for e in self.entries if e.get('status') == 'CLOSED']
    
    def get_entries_by_symbol(self, symbol: str) -> List[Dict]:
        """Get entries for a symbol"""
        return [e for e in self.entries if e.get('symbol') == symbol]
    
    def get_statistics(self) -> Dict:
        """Get journal statistics"""
        try:
            closed_entries = self.get_closed_entries()
            
            if not closed_entries:
                return {
                    'total_entries': len(self.entries),
                    'open_entries': len(self.get_open_entries()),
                    'closed_entries': 0,
                    'win_rate': 0,
                    'avg_win': 0,
                    'avg_loss': 0,
                    'total_pnl': 0,
                }
            
            winners = [e for e in closed_entries if e.get('pnl', 0) > 0]
            losers = [e for e in closed_entries if e.get('pnl', 0) < 0]
            
            total_wins = sum(e.get('pnl', 0) for e in winners)
            total_losses = sum(abs(e.get('pnl', 0)) for e in losers)
            
            return {
                'total_entries': len(self.entries),
                'open_entries': len(self.get_open_entries()),
                'closed_entries': len(closed_entries),
                'win_rate': (len(winners) / len(closed_entries) * 100) if closed_entries else 0,
                'avg_win': (total_wins / len(winners)) if winners else 0,
                'avg_loss': (total_losses / len(losers)) if losers else 0,
                'total_pnl': total_wins - total_losses,
                'winners': len(winners),
                'losers': len(losers),
                'profit_factor': (total_wins / total_losses) if total_losses > 0 else 0,
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def export_csv(self, filepath: str):
        """Export journal to CSV"""
        try:
            import csv
            
            if not self.entries:
                logger.warning("No entries to export")
                return
            
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.entries[0].keys())
                writer.writeheader()
                writer.writerows(self.entries)
            
            logger.info(f"✓ Exported journal to {filepath}")
        except Exception as e:
            logger.error(f"Error exporting journal: {e}")
