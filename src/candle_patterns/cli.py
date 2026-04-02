from __future__ import annotations

"""
Command-line interface for candlestick pattern analysis.

This module provides Typer-based CLI commands for:
- run: Execute full pipeline (load CSV → detect patterns → save report)
- cleanup: Remove old artifacts and database references
- train: Train ML baseline models on detected patterns
- backtest: Run strategy backtests with various hold periods
- scan: Scan real-time data from Yahoo Finance

Each command includes full help text (--help) and parameter validation.

Example:
    $ python -m candle_patterns.cli run data.csv --out report.csv
    $ python -m candle_patterns.cli train --file data.csv --model-out model.pkl
"""

import typer
from candle_patterns.ingestion import load_csv
from candle_patterns.detection import detect_patterns
import pandas as pd

app = typer.Typer(help="Candle Patterns CLI — detection, backtesting & ML pipeline")


@app.command()
def run(file: str, out: str = "report.csv") -> None:
    """Run full pipeline on a CSV file and produce a report CSV"""
    df = load_csv(file)
    patterns = detect_patterns(df)
    if patterns:
        pd.DataFrame(patterns).to_csv(out, index=False)
        typer.echo(f"Report written to {out}")
    else:
        typer.echo("No patterns detected")


@app.command()
def cleanup(days: int = 30) -> None:
    """Remove stored artifacts older than `days` and delete DB references."""
    from candle_patterns.storage import cleanup_old_uploads

    removed = cleanup_old_uploads(retention_days=days)
    typer.echo(f"Removed {removed} old uploads/detections")


@app.command()
def train(
    file: str = typer.Argument(..., help="Path to OHLC CSV file"),
    model_out: str = typer.Option("artifacts/model.pkl", "--model-out", "-m", help="Path to save trained model"),
) -> None:
    """Train an ML baseline model on detected patterns from an OHLC CSV."""
    from pathlib import Path
    from candle_patterns.ml_baseline import PatternMLModel

    df = load_csv(file)
    patterns = detect_patterns(df)
    typer.echo(f"Loaded {len(df)} candles, detected {len(patterns)} pattern occurrences")

    model = PatternMLModel()
    X, y = model.engineer_features(df, patterns)

    if len(X) < 10:
        typer.echo("ERROR: Insufficient data for training (need >= 10 samples)")
        raise typer.Exit(code=1)

    metrics = model.train(X, y)
    typer.echo(f"Training complete — accuracy: {metrics.get('accuracy', 0):.4f}, "
               f"f1: {metrics.get('f1_score', 0):.4f}")

    cv = model.cross_validate(X, y, n_splits=min(5, max(2, len(X) // 10)))
    typer.echo(f"Cross-validation — mean accuracy: {cv.get('mean_accuracy', 0):.4f} "
               f"(+/- {cv.get('std_accuracy', 0):.4f})")

    out_path = Path(model_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(out_path)
    typer.echo(f"Model saved to {out_path}")


@app.command()
def predict(
    file: str = typer.Argument(..., help="Path to OHLC CSV file"),
    model_path: str = typer.Option("artifacts/model.pkl", "--model", "-m", help="Path to trained model"),
    out: str = typer.Option("predictions.csv", "--out", "-o", help="Output CSV path"),
) -> None:
    """Generate predictions using a trained model on new OHLC data."""
    from pathlib import Path
    from candle_patterns.ml_baseline import PatternMLModel

    mp = Path(model_path)
    if not mp.exists():
        typer.echo(f"ERROR: Model file not found at {mp}. Run 'train' first.")
        raise typer.Exit(code=1)

    model = PatternMLModel()
    model.load(mp)
    typer.echo(f"Loaded model from {mp}")

    df = load_csv(file)
    patterns = detect_patterns(df)
    typer.echo(f"Loaded {len(df)} candles, detected {len(patterns)} pattern occurrences")

    X, _ = model.engineer_features(df, patterns)
    if len(X) == 0:
        typer.echo("No valid samples to predict on")
        raise typer.Exit(code=1)

    preds, probs = model.predict(X)
    result = X.copy()
    result["prediction"] = preds
    result["probability"] = probs
    result.to_csv(out, index=False)
    typer.echo(f"Predictions written to {out} ({len(result)} rows)")


@app.command()
def backtest(
    file: str = typer.Argument(..., help="Path to OHLC CSV file"),
    hold: int = typer.Option(5, "--hold", "-h", help="Number of periods to hold after signal"),
    out: str = typer.Option("backtest_report.csv", "--out", "-o", help="Output CSV path"),
) -> None:
    """Backtest detected patterns and report profitability metrics."""
    from candle_patterns.backtesting import evaluate_pattern_profitability

    df = load_csv(file)
    patterns = detect_patterns(df)
    typer.echo(f"Loaded {len(df)} candles, detected {len(patterns)} pattern occurrences")

    evaluation = evaluate_pattern_profitability(df, patterns, hold_periods=hold)

    typer.echo(f"\n--- Backtest Results (hold={hold} periods) ---")
    typer.echo(f"  Total patterns tested: {evaluation.get('n_patterns', 0)}")
    typer.echo(f"  Total trades: {evaluation.get('total_trades', 0)}")
    typer.echo(f"  Profitable patterns: {evaluation.get('profitable_patterns', 0)}")
    typer.echo(f"  Overall win rate: {evaluation.get('overall_win_rate', 0):.2%}")

    pattern_results = evaluation.get("pattern_results", [])
    if pattern_results:
        pd.DataFrame(pattern_results).to_csv(out, index=False)
        typer.echo(f"\nDetailed results written to {out}")
    else:
        typer.echo("No pattern results to export")


if __name__ == "__main__":
    app()
