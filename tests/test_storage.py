import pandas as pd
from candle_patterns import storage


def test_storage_save_and_list(tmp_path):
    db = tmp_path / "test.db"
    storage.init_db(db)
    df = pd.DataFrame(
        {
            "timestamp": ["2026-01-01T00:00:00"],
            "open": [100],
            "high": [101],
            "low": [99],
            "close": [100.5],
            "volume": [100],
        }
    )
    dets = [{"timestamp": "2026-01-01T00:00:00", "pattern": "doji", "index": 0}]
    uid = storage.save_upload("test.csv", df, dets)
    assert isinstance(uid, int)
    rows = storage.list_uploads()
    assert len(rows) >= 1
    rec = storage.get_upload(uid)
    assert rec is not None
    assert rec["filename"] == "test.csv"
