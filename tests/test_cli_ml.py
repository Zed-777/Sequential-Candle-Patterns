"""Tests for the ML-CLI commands: train, predict, backtest."""
from __future__ import annotations

import pytest
from pathlib import Path
from typer.testing import CliRunner

from candle_patterns.cli import app

runner = CliRunner()

SAMPLE_CSV = "data/samples/sample_synthetic.csv"


class TestCLITrain:
    """Tests for the `train` CLI command."""

    def test_train_produces_model(self, tmp_path):
        model_out = tmp_path / "model.pkl"
        result = runner.invoke(app, ["train", SAMPLE_CSV, "--model-out", str(model_out)])
        assert result.exit_code == 0, result.output
        assert model_out.exists(), "Model file should be created"
        assert "Training complete" in result.output

    def test_train_shows_metrics(self):
        result = runner.invoke(app, ["train", SAMPLE_CSV, "--model-out", "artifacts/_test_model.pkl"])
        assert result.exit_code == 0, result.output
        assert "accuracy" in result.output
        assert "Cross-validation" in result.output
        # cleanup
        Path("artifacts/_test_model.pkl").unlink(missing_ok=True)


class TestCLIPredict:
    """Tests for the `predict` CLI command."""

    @pytest.fixture(autouse=True)
    def _train_model(self, tmp_path):
        """Train a model before predict tests."""
        self.model_path = tmp_path / "model.pkl"
        result = runner.invoke(app, ["train", SAMPLE_CSV, "--model-out", str(self.model_path)])
        assert result.exit_code == 0

    def test_predict_writes_csv(self, tmp_path):
        out = tmp_path / "preds.csv"
        result = runner.invoke(app, ["predict", SAMPLE_CSV, "--model", str(self.model_path), "--out", str(out)])
        assert result.exit_code == 0, result.output
        assert out.exists(), "Predictions CSV should be created"
        assert "Predictions written" in result.output

    def test_predict_missing_model(self, tmp_path):
        result = runner.invoke(app, ["predict", SAMPLE_CSV, "--model", str(tmp_path / "nope.pkl")])
        assert result.exit_code != 0


class TestCLIBacktest:
    """Tests for the `backtest` CLI command."""

    def test_backtest_produces_report(self, tmp_path):
        out = tmp_path / "bt.csv"
        result = runner.invoke(app, ["backtest", SAMPLE_CSV, "--out", str(out)])
        assert result.exit_code == 0, result.output
        assert "Backtest Results" in result.output
        assert out.exists(), "Backtest report should be created"

    def test_backtest_custom_hold(self, tmp_path):
        out = tmp_path / "bt2.csv"
        result = runner.invoke(app, ["backtest", SAMPLE_CSV, "--hold", "3", "--out", str(out)])
        assert result.exit_code == 0, result.output
        assert "hold=3" in result.output
