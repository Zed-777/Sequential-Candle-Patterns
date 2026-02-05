"""
Tests for the backtesting module.
"""
import pytest
import pandas as pd
import numpy as np
from candle_patterns.backtesting import BacktestEngine, evaluate_pattern_profitability


@pytest.fixture
def sample_ohlc_data():
    """Create sample OHLC data for testing."""
    dates = pd.date_range('2024-01-01', periods=100, freq='1h', tz='UTC')
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(100) * 0.5)
    
    return pd.DataFrame({
        'timestamp': dates,
        'open': close + np.random.randn(100) * 0.2,
        'high': close + np.abs(np.random.randn(100) * 0.5),
        'low': close - np.abs(np.random.randn(100) * 0.5),
        'close': close,
        'volume': np.random.randint(1000, 10000, 100),
    })


@pytest.fixture
def sample_patterns(sample_ohlc_data):
    """Create sample detected patterns."""
    return [
        {'timestamp': sample_ohlc_data.iloc[5]['timestamp'], 'pattern': 'Doji'},
        {'timestamp': sample_ohlc_data.iloc[15]['timestamp'], 'pattern': 'Hammer'},
        {'timestamp': sample_ohlc_data.iloc[25]['timestamp'], 'pattern': 'Doji'},
        {'timestamp': sample_ohlc_data.iloc[35]['timestamp'], 'pattern': 'Engulfing'},
    ]


def test_backtest_engine_initialization():
    """Test BacktestEngine initialization."""
    engine = BacktestEngine()
    assert engine.risk_free_rate == 0.02


def test_calculate_returns(sample_ohlc_data):
    """Test return calculation for trades."""
    engine = BacktestEngine()
    pattern_indices = [5, 15, 25]
    
    trades = engine.calculate_returns(sample_ohlc_data, pattern_indices, hold_periods=5)
    
    assert isinstance(trades, pd.DataFrame)
    assert len(trades) == 3
    assert 'entry_price' in trades.columns
    assert 'exit_price' in trades.columns
    assert 'return' in trades.columns


def test_sharpe_ratio():
    """Test Sharpe ratio calculation."""
    engine = BacktestEngine(risk_free_rate=0.02)
    
    # Positive returns
    returns = pd.Series([0.01, 0.02, 0.01, 0.03, 0.00])
    sharpe = engine.calculate_sharpe_ratio(returns)
    assert isinstance(sharpe, float)
    assert sharpe > 0  # Should be positive for positive returns
    
    # Empty returns
    empty_returns = pd.Series([])
    assert engine.calculate_sharpe_ratio(empty_returns) == 0.0
    
    # Zero volatility
    flat_returns = pd.Series([0.01, 0.01, 0.01])
    assert engine.calculate_sharpe_ratio(flat_returns) == 0.0


def test_max_drawdown():
    """Test maximum drawdown calculation."""
    engine = BacktestEngine()
    
    # Declining then recovering
    returns = pd.Series([0.05, -0.10, -0.05, 0.08, 0.03])
    max_dd = engine.calculate_max_drawdown(returns)
    
    assert isinstance(max_dd, float)
    assert max_dd <= 0  # Drawdown should be negative or zero
    
    # Empty series
    empty = pd.Series([])
    assert engine.calculate_max_drawdown(empty) == 0.0


def test_win_rate(sample_ohlc_data):
    """Test win rate calculation."""
    engine = BacktestEngine()
    trades = engine.calculate_returns(sample_ohlc_data, [5, 15, 25], hold_periods=5)
    
    win_rate, n_wins, n_losses = engine.calculate_win_rate(trades)
    
    assert 0 <= win_rate <= 1
    assert n_wins + n_losses == len(trades)
    assert isinstance(n_wins, (int, np.integer))
    assert isinstance(n_losses, (int, np.integer))


def test_profit_factor(sample_ohlc_data):
    """Test profit factor calculation."""
    engine = BacktestEngine()
    trades = engine.calculate_returns(sample_ohlc_data, [5, 15, 25], hold_periods=5)
    trades['profit'] = trades['return'] * 100  # Simple profit proxy
    
    pf = engine.calculate_profit_factor(trades)
    
    assert isinstance(pf, (float, int))
    assert pf >= 0


def test_backtest_pattern(sample_ohlc_data, sample_patterns):
    """Test backtesting a single pattern."""
    engine = BacktestEngine()
    results = engine.backtest_pattern(
        sample_ohlc_data,
        'Doji',
        sample_patterns,
        hold_periods=5
    )
    
    assert results['pattern'] == 'Doji'
    assert results['n_trades'] >= 0
    if results['n_trades'] > 0:
        assert 'sharpe_ratio' in results
        assert 'win_rate' in results
        assert 'max_drawdown' in results


def test_backtest_all_patterns(sample_ohlc_data, sample_patterns):
    """Test backtesting all patterns."""
    engine = BacktestEngine()
    results_df = engine.backtest_all_patterns(
        sample_ohlc_data,
        sample_patterns,
        hold_periods=5
    )
    
    assert isinstance(results_df, pd.DataFrame)
    assert 'pattern' in results_df.columns
    assert 'n_trades' in results_df.columns
    assert len(results_df) > 0


def test_equity_curve():
    """Test equity curve calculation."""
    engine = BacktestEngine()
    
    # Create sample trades
    trades = pd.DataFrame({
        'profit': [100, -50, 200, -75, 150]
    })
    
    equity = engine.calculate_equity_curve(trades, initial_capital=10000)
    
    assert len(equity) == len(trades)
    assert equity.iloc[0] == 10100  # First trade profit
    assert equity.iloc[-1] == 10325  # Final equity
    
    # Empty trades
    empty_equity = engine.calculate_equity_curve(pd.DataFrame(), initial_capital=10000)
    assert len(empty_equity) == 1
    assert empty_equity.iloc[0] == 10000


def test_evaluate_pattern_profitability(sample_ohlc_data, sample_patterns):
    """Test comprehensive profitability evaluation."""
    results = evaluate_pattern_profitability(
        sample_ohlc_data,
        sample_patterns,
        hold_periods=5
    )
    
    assert 'total_trades' in results
    assert 'n_patterns' in results
    assert 'profitable_patterns' in results
    assert 'pattern_results' in results
    assert isinstance(results['pattern_results'], list)
