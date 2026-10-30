import os

from src.ai.pricing_model import VanillaPricingModel, load_dataset_rows
from src.ai.vanilla_ai import vanilla_ai


def test_pricing_model_beats_baseline_on_holdout():
    """Le modèle entraîné localement doit réduire l'erreur face au prix moyen."""
    rows = load_dataset_rows()
    assert len(rows) >= 100, "Dataset vanille introuvable ou trop petit"

    model = VanillaPricingModel()
    metrics = model.fit(rows)

    for target in ("fair_farmgate_price_mga", "fob_export_price_usd"):
        m = metrics["targets"][target]
        assert m["mae"] < m["baseline_mae"]
        assert m["r2"] > 0.5
        assert m["mape_pct"] < 30.0


def test_trained_model_prices_gourmet_above_immature():
    """Un lot Gourmet doit être valorisé bien au-dessus d'un lot immature."""
    model = VanillaPricingModel()
    if not model.load():
        model.fit(load_dataset_rows())

    gourmet = model.predict(
        district="Sambava",
        bean_length_cm=18.5,
        moisture_pct=32.0,
        vanillin_pct=2.3,
        maturity_pct=96.0,
        mold_detected=False,
    )
    immature = model.predict(
        district="Sambava",
        bean_length_cm=9.8,
        moisture_pct=52.0,
        vanillin_pct=0.7,
        maturity_pct=48.0,
        mold_detected=False,
    )

    assert gourmet["fair_farmgate_price_mga"] > immature["fair_farmgate_price_mga"]
    assert immature["fair_farmgate_price_mga"] >= 0


def test_model_save_and_load_roundtrip(tmp_path):
    """Les poids sauvegardés doivent reproduire les mêmes prédictions."""
    rows = load_dataset_rows()
    model = VanillaPricingModel()
    model.fit(rows)
    path = os.path.join(tmp_path, "model.json")
    model.save(path)

    reloaded = VanillaPricingModel()
    assert reloaded.load(path)
    assert reloaded.metrics["n_samples"] == model.metrics["n_samples"]

    kwargs = dict(
        district="Antalaha",
        bean_length_cm=15.2,
        moisture_pct=28.0,
        vanillin_pct=1.7,
        maturity_pct=88.0,
        mold_detected=False,
    )
    before = model.predict(**kwargs)["fair_farmgate_price_mga"]
    after = reloaded.predict(**kwargs)["fair_farmgate_price_mga"]
    assert abs(before - after) < 1.0


def test_iso_grades_and_deterministic_hash():
    """Les règles ISO 5565-1 et le hash d'inspection doivent être stables."""
    kwargs = dict(
        district="Sambava",
        bean_length_cm=18.5,
        moisture_pct=32.0,
        vanillin_pct=2.3,
        mold_detected=False,
        maturity_pct=96.0,
    )
    first = vanilla_ai.inspect_lot(**kwargs)
    second = vanilla_ai.inspect_lot(**kwargs)

    assert first["quality_grade"] == "Gourmet_Grade_A"
    assert first["inspection_hash"] == second["inspection_hash"]
    assert first["pricing_engine"].startswith("Ridge")

    moldy = vanilla_ai.inspect_lot(**{**kwargs, "mold_detected": True})
    immature = vanilla_ai.inspect_lot(**{**kwargs, "maturity_pct": 48.0, "vanillin_pct": 0.7})

    assert moldy["quality_grade"] == "Defective_Mold"
    assert moldy["status"] == "REJECTED"
    assert immature["quality_grade"] == "Rejected_Immature"
    assert immature["status"] == "REJECTED"


def test_photo_is_committed_in_inspection_hash():
    """La photo bord-champ doit changer le hash et rester reproductible."""
    kwargs = dict(
        district="Sambava",
        bean_length_cm=18.5,
        moisture_pct=32.0,
        vanillin_pct=2.3,
        mold_detected=False,
        maturity_pct=96.0,
    )
    photo = b"gousse-vanille-001"
    with_photo = vanilla_ai.inspect_lot(**kwargs, image_bytes=photo)
    same_photo = vanilla_ai.inspect_lot(**kwargs, image_bytes=photo)
    without_photo = vanilla_ai.inspect_lot(**kwargs)

    assert with_photo["inspection_hash"] == same_photo["inspection_hash"]
    assert with_photo["inspection_hash"] != without_photo["inspection_hash"]
