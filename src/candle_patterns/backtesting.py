"""
Backtesting module for evaluating pattern-based trading signals.

Calculates:
- Sharpe ratio (return vs volatility)
- Maximum drawdown
- Win rate and profit factor
- Per-pattern performance metrics
"""

import logging
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class BacktestEngine:
    """Engine for backtesting trading signals based on detected patterns."""

    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize backtest engine.
        
        Args:
            risk_free_rate: Annual risk-free rate for Sharpe ratio calculation
        """
        self.risk_free_rate = risk_free_rate

    def calculate_returns(
        self,
        df: pd.DataFrame,
        pattern_indices: List[int],
        hold_periods: int = 5
    ) -> pd.DataFrame:
        """
        Calculate returns for trades entered at pattern signals.
        
        Args:
            df: OHLC DataFrame
            pattern_indices: List of bar indices where patterns occur
            hold_periods: Number of periods to hold after signal
            
        Returns:
            DataFrame with entry price, exit price, and return
        """
        df = df.copy()
        df['return'] = df['close'].pct_change(hold_periods)
        
        trades = []
        for idx in pattern_indices:
            if idx + hold_periods < len(df):
                entry_price = df.iloc[idx]['close']
                exit_price = df.iloc[idx + hold_periods]['close']
                trade_return = (exit_price - entry_price) / entry_price
                
                trades.append({
                    'entry_idx': idx,
                    'entry_price': entry_price,
                    'exit_idx': idx + hold_periods,
                    'exit_price': exit_price,
                    'return': trade_return,
                    'profit': exit_price - entry_price,
                })
        
        return pd.DataFrame(trades)

    def calculate_sharpe_ratio(
        self,
        returns: pd.Series,
        periods_per_year: int = 252
    ) -> float:
        """
        Calculate Sharpe ratio.
        
        Sharpe = (mean_return - risk_free_rate) / std_return
        
        Args:
            returns: Series of returns
            periods_per_year: Number of trading periods per year
            
        Returns:
            Sharpe ratio
        """
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        excess_return = returns.mean() - (self.risk_free_rate / periods_per_year)
        return excess_return / returns.std() * np.sqrt(periods_per_year)

    def calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """
        Calculate maximum drawdown.
        
        Max Drawdown = (Peak - Trough) / Peak
        
        Args:
            equity_curve: Series of cumulative returns or portfolio values
            
        Returns:
            Maximum drawdown as decimal (e.g., -0.15 for 15% drawdown)
        """
        if len(equity_curve) == 0:
            return 0.0
        
        cumulative = (1 + equity_curve).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        return drawdown.min()

    def calculate_win_rate(self, trades: pd.DataFrame) -> Tuple[float, int, int]:
        """
        Calculate win rate and trade counts.
        
        Args:
            trades: DataFrame with 'return' column
            
        Returns:
            (win_rate, n_wins, n_losses)
        """
        if len(trades) == 0:
            return 0.0, 0, 0
        
        n_wins = (trades['return'] > 0).sum()
        n_losses = (trades['return'] <= 0).sum()
        win_rate = n_wins / len(trades) if len(trades) > 0 else 0.0
        
        return win_rate, n_wins, n_losses

    def calculate_profit_factor(self, trades: pd.DataFrame) -> float:
        """
        Calculate profit factor.
        
        Profit Factor = Gross Profit / Gross Loss
        
        Args:
            trades: DataFrame with 'profit' column
            
        Returns:
            Profit factor
        """
        if len(trades) == 0:
            return 0.0
        
        gross_profit = trades[trades['profit'] > 0]['profit'].sum()
        gross_loss = abs(trades[trades['profit'] <= 0]['profit'].sum())
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return gross_profit / gross_loss

    def backtest_pattern(
        self,
        df: pd.DataFrame,
        pattern_name: str,
        pattern_data: List[Dict],
        hold_periods: int = 5
    ) -> Dict:
        """
        Backtest a specific candle pattern.
        
        Args:
            df: OHLC DataFrame
            pattern_name: Name of the pattern to backtest
            pattern_data: List of pattern occurrences
            hold_periods: Number of periods to hold trades
            
        Returns:
            Dictionary with backtest results
        """
        # Filter patterns
        filtered_patterns = [p for p in pattern_data if p['pattern'] == pattern_name]
        
        if not filtered_patterns:
            logger.warning(f"No occurrences of pattern {pattern_name}")
            return {'pattern': pattern_name, 'n_trades': 0}
        
        # Find indices
        pattern_indices = []
        for p in filtered_patterns:
            matching_idx = df[df['timestamp'] == p['timestamp']].index
            if len(matching_idx) > 0:
                pattern_indices.append(matching_idx[0])
        
        if not pattern_indices:
            logger.warning(f"Could not match {pattern_name} to DataFrame indices")
            return {'pattern': pattern_name, 'n_trades': 0}
        
        # Calculate trades
        trades = self.calculate_returns(df, pattern_indices, hold_periods)
        
        if len(trades) == 0:
            return {'pattern': pattern_name, 'n_trades': 0}
        
        # Calculate metrics
        returns = trades['return']
        win_rate, n_wins, n_losses = self.calculate_win_rate(trades)
        sharpe = self.calculate_sharpe_ratio(returns)
        max_dd = self.calculate_max_drawdown(returns)
        profit_factor = self.calculate_profit_factor(trades)
        
        results = {
            'pattern': pattern_name,
            'n_trades': len(trades),
            'n_wins': n_wins,
            'n_losses': n_losses,
            'win_rate': win_rate,
            'avg_return': returns.mean(),
            'std_return': returns.std(),
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd,
            'profit_factor': profit_factor,
            'total_return': returns.sum(),
        }
        
        logger.info(f"Backtest {pattern_name}: {len(trades)} trades, {win_rate:.1%} win rate, Sharpe: {sharpe:.2f}")
        
        return results

    def backtest_all_patterns(
        self,
        df: pd.DataFrame,
        pattern_data: List[Dict],
        hold_periods: int = 5
    ) -> pd.DataFrame:
        """
        Backtest all patterns in the dataset.
        
        Args:
            df: OHLC DataFrame
            pattern_data: List of detected patterns
            hold_periods: Number of periods to hold trades
            
        Returns:
            DataFrame with results for each pattern
        """
        pattern_names = sorted(set(p['pattern'] for p in pattern_data))
        results_list = []
        
        for pattern_name in pattern_names:
            results = self.backtest_pattern(df, pattern_name, pattern_data, hold_periods)
            results_list.append(results)
        
        results_df = pd.DataFrame(results_list)
        
        logger.info(f"Backtested {len(results_df)} patterns")
        logger.info(f"Patterns with trades: {(results_df['n_trades'] > 0).sum()}")
        
        return results_df

    def calculate_equity_curve(
        self,
        trades: pd.DataFrame,
        initial_capital: float = 10000.0
    ) -> pd.Series:
        """
        Calculate equity curve from trades.
        
        Args:
            trades: DataFrame with 'profit' column
            initial_capital: Starting capital
            
        Returns:
            Series of cumulative equity
        """
        if len(trades) == 0:
            return pd.Series([initial_capital])
        
        profits = trades['profit'].values
        equity = initial_capital + np.cumsum(profits)
        
        return pd.Series(equity)


def evaluate_pattern_profitability(
    df: pd.DataFrame,
    patterns: List[Dict],
    hold_periods: int = 5
) -> Dict:
    """
    Comprehensive evaluation of pattern profitability.
    
    Args:
        df: OHLC DataFrame
        patterns: List of detected patterns
        hold_periods: Number of periods to hold trades
        
    Returns:
        Dictionary with evaluation results
    """
    engine = BacktestEngine()
    
    # Backtest all patterns
    pattern_results = engine.backtest_all_patterns(df, patterns, hold_periods)
    
    # Overall statistics
    total_trades = pattern_results['n_trades'].sum()
    profitable_patterns = (pattern_results['avg_return'] > 0).sum()
    
    evaluation = {
        'total_trades': total_trades,
        'n_patterns': len(pattern_results),
        'profitable_patterns': profitable_patterns,
        'pattern_results': pattern_results.to_dict('records'),
    }
    
    if total_trades > 0:
        all_returns = []
        for _, row in pattern_results.iterrows():
            # Reconstruct returns for overall calculation
            pass  # Would need original trades
        
        evaluation['overall_win_rate'] = (pattern_results['n_wins'].sum() / total_trades) if total_trades > 0 else 0
    
    logger.info(f"Evaluation complete: {total_trades} total trades, {profitable_patterns}/{len(pattern_results)} patterns profitable")
    
    return evaluation
