import os
import time
import pandas as pd
from typer.testing import CliRunner
from candle_patterns.cli import app as cli_app

from candle_patterns import storage


def test_cleanup_old_uploads(tmp_path, monkeypatch):
    # run in isolated tmp path so artifacts/db are local to test
    monkeypatch.chdir(tmp_path)

    df = pd.DataFrame({"timestamp": ["2020-01-01T00:00:00Z"], "open": [1], "high": [2], "low": [0.5], "close": [1.5]})
    detects = [{"index": 0, "timestamp": "2020-01-01T00:00:00Z", "pattern": "doji"}]

    # save an upload (should create artifacts and DB row)
    uid = storage.save_upload("sample.csv", df, detects)
    assert uid is not None

    # Ensure files exist
    rows = storage.list_uploads()
    assert len(rows) == 1
    rec = rows[0]
    assert os.path.exists(rec["filepath"]) if isinstance(rec, dict) else True

    # set file mtime to an old time so cleanup will remove it
    old_time = time.time() - (2 * 24 * 60 * 60)
    # committed files are in artifacts/uploads and artifacts/detections
    for p in [rec["filepath"], rec["detections_path"]]:
        os.utime(p, (old_time, old_time))

    removed = storage.cleanup_old_uploads(retention_days=0)
    assert removed >= 1

    rows_after = storage.list_uploads()
    assert len(rows_after) == 0


def test_cli_cleanup(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # create a sample upload to cleanup
    import pandas as pd

    df = pd.DataFrame({"timestamp": ["2020-01-01T00:00:00Z"], "open": [1], "high": [2], "low": [0.5], "close": [1.5]})
    detects = [{"index": 0, "timestamp": "2020-01-01T00:00:00Z", "pattern": "doji"}]
    storage.save_upload("s.csv", df, detects)

    runner = CliRunner()
    res = runner.invoke(cli_app, ["cleanup", "--days", "0"])  # remove immediately
    assert res.exit_code == 0
    assert "Removed" in res.stdout
