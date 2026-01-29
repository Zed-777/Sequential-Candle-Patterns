from __future__ import annotations

import typer
from candle_patterns.ingestion import load_csv
from candle_patterns.detection import detect_patterns
import pandas as pd

app = typer.Typer()


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


if __name__ == "__main__":
    app()
