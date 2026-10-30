import os

from src.ai.market_model import (
    DEFAULT_MARKET_DATASET,
    VanillaMarketModel,
    load_market_rows,
)


def test_market_dataset_is_real_comtrade_series():
    """La série doit contenir les exportations réelles ONU, pas des données simulées."""
    rows = load_market_rows(DEFAULT_MARKET_DATASET)

    assert len(rows) >= 10
    assert rows[0]["year"] <= 2015
    assert rows[-1]["year"] >= 2025
    assert all(r["fob_usd_per_kg"] > 0 for r in rows)
    assert all(r["qty_mkg"] > 0 for r in rows)


def test_market_model_beats_baseline_leave_one_year_out():
    """Le modèle de marché doit expliquer la série réelle mieux que la moyenne."""
    model = VanillaMarketModel()
    metrics = model.fit(load_market_rows(DEFAULT_MARKET_DATASET))

    assert metrics["loo_r2"] > 0.5
    assert metrics["loo_mape_pct"] < 40.0
    assert model.latest()["year"] == 2025


def test_market_model_save_and_load_roundtrip(tmp_path):
    model = VanillaMarketModel()
    model.fit(load_market_rows(DEFAULT_MARKET_DATASET))
    path = os.path.join(tmp_path, "market.json")
    model.save(path)

    reloaded = VanillaMarketModel()
    assert reloaded.load(path)
    assert reloaded.metrics == model.metrics
    assert reloaded.latest() == model.latest()
