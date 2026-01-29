from candle_patterns.storage import init_db, save_upload, list_uploads
import pandas as pd

def test_history_roundtrip(tmp_path):
    db = tmp_path / "test2.db"
    init_db(db)
    df = pd.DataFrame({"timestamp":["2026-01-01T00:00:00"], "open":[100], "high":[101], "low":[99], "close":[100.5], "volume":[100]})
    dets = [{"timestamp":"2026-01-01T00:00:00", "pattern":"doji", "index":0}]
    uid = save_upload("test2.csv", df, dets)
    rows = list_uploads()
    assert any(r['id']==uid for r in rows)
