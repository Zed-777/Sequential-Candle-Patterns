from candle_patterns.ingestion import load_csv
from candle_patterns.detection import detect_patterns


def test_end_to_end_bullish_engulfing(tmp_path):
    # Create small synthetic CSV with a bullish engulfing pattern
    csv = tmp_path / "synth.csv"
    csv.write_text(
        "timestamp,open,high,low,close\n"
        "2026-01-01T00:00:00Z,10,11,9,9.5\n"  # bearish
        "2026-01-01T01:00:00Z,9,12,8,12\n"    # bullish engulfing (close>open and larger body)
    )

    df = load_csv(str(csv))
    patterns = detect_patterns(df, window_size=2)
    found = [p["pattern"] for p in patterns]
    assert "bullish_engulfing" in found
