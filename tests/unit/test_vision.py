import io
from PIL import Image, ImageDraw

from scripts.generate_vanilla_vision_dataset import (
    _draw_background,
    _draw_pod,
    _generate_pod_path,
)
from src.ai.vanilla_ai import vanilla_ai
from src.ai.vision import analyze_lot_photo, get_vision_model
from src.ai.vision_model import VanillaVisionModel


def _image_bytes(base_color, patch=None) -> bytes:
    image = Image.new("RGB", (120, 120), base_color)
    if patch:
        color, box = patch
        ImageDraw.Draw(image).rectangle(box, fill=color)
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=92)
    return buffer.getvalue()


def _synthetic_pod_bytes(label: str, bg: str = "wood") -> bytes:
    img = _draw_background(bg)
    points = _generate_pod_path()
    _draw_pod(img, label, points)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=90)
    return buffer.getvalue()


# ---------------------------------------------------------------------- #
# Tests de base et de régression
# ---------------------------------------------------------------------- #
def test_brown_beans_score_higher_maturity_than_green():
    brown = analyze_lot_photo(_image_bytes((110, 70, 30)))
    green = analyze_lot_photo(_image_bytes((60, 140, 60)))

    assert brown["brown_ratio"] > 0.8
    assert green["green_ratio"] > 0.8
    assert brown["estimated_maturity_pct"] > green["estimated_maturity_pct"]


def test_light_patches_raise_mold_risk():
    clean = analyze_lot_photo(_image_bytes((110, 70, 30)))
    moldy = analyze_lot_photo(
        _image_bytes((110, 70, 30), patch=((220, 220, 215), (0, 0, 60, 120)))
    )

    assert moldy["mold_patch_ratio"] > clean["mold_patch_ratio"]
    assert moldy["mold_risk_pct"] > clean["mold_risk_pct"]


def test_photo_analysis_is_deterministic_and_handles_empty_image():
    data = _image_bytes((110, 70, 30))
    assert analyze_lot_photo(data) == analyze_lot_photo(data)

    blank = analyze_lot_photo(_image_bytes((255, 255, 255)))
    assert blank["subject_ratio"] < 0.15
    assert "aucune gousse détectée" in blank["flags"]
    assert blank["reliable"] is False


def test_inspection_embeds_vision_result():
    data = _image_bytes((110, 70, 30))
    result = vanilla_ai.inspect_lot(
        district="Sambava",
        bean_length_cm=18.5,
        moisture_pct=32.0,
        vanillin_pct=2.3,
        mold_detected=False,
        maturity_pct=96.0,
        image_bytes=data,
    )

    assert result["vision"] is not None
    assert result["vision"]["brown_ratio"] > 0.8
    assert result["vision"]["image_sha256"]


def test_green_vanilla_photo_triggers_rejection_even_with_gourmet_inputs():
    """Vérifie que la détection d'une gousse verte par vision rejette le lot même si le formulaire prétend Gourmet A."""
    green_photo = _image_bytes((70, 135, 55))
    result = vanilla_ai.inspect_lot(
        district="Sambava",
        bean_length_cm=19.0,      # Prétendu Gourmet
        moisture_pct=32.0,        # Prétendu Gourmet
        vanillin_pct=2.4,         # Prétendu Gourmet
        mold_detected=False,
        maturity_pct=98.0,        # Prétendu 98% mûr
        image_bytes=green_photo,
    )

    assert result["quality_grade"] == "Rejected_Immature"
    assert result["status"] == "REJECTED"
    assert result["maturity_pct"] < 60.0
    assert result["estimated_fair_price_mga_per_kg"] <= 42000.0
    assert any("cueillette prématurée" in exp.lower() or "vanille verte" in exp.lower() for exp in result["explanations"])


# ---------------------------------------------------------------------- #
# Tests avancés de reconnaissance photo fine-tunée
# ---------------------------------------------------------------------- #
def test_all_green_shades_trigger_immature_rejection():
    """Vérifie que toutes les teintes de vanille verte (vif, olive, jaune-vert) sont détectées."""
    shades = [
        (55, 145, 55),   # Vert vif
        (80, 120, 45),   # Vert olive
        (125, 165, 50),  # Jaune-vert
    ]
    for r, g, b in shades:
        analysis = analyze_lot_photo(_image_bytes((r, g, b)))
        assert analysis["green_ratio"] > 0.6, f"Échec détection vert pour RGB({r},{g},{b})"
        assert analysis["predicted_grade"] == "Rejected_Immature"
        assert analysis["estimated_maturity_pct"] < 50.0


def test_synthetic_gourmet_pod_on_wood_background():
    """Vérifie qu'une gousse noire Gourmet sur fond de table en bois est parfaitement reconnue."""
    data = _synthetic_pod_bytes("Gourmet_Grade_A", bg="wood")
    analysis = analyze_lot_photo(data)

    assert analysis["reliable"] is True
    assert analysis["green_ratio"] < 0.05
    assert analysis["mold_risk_pct"] < 20.0
    assert analysis["predicted_grade"] == "Gourmet_Grade_A"
    assert analysis["estimated_maturity_pct"] >= 80.0


def test_synthetic_green_pod_on_fabric_background():
    """Vérifie qu'une gousse verte sur tissu blanc est classée Rejected_Immature."""
    data = _synthetic_pod_bytes("Rejected_Immature", bg="fabric")
    analysis = analyze_lot_photo(data)

    assert analysis["reliable"] is True
    assert analysis["green_ratio"] > 0.5
    assert analysis["predicted_grade"] == "Rejected_Immature"
    assert analysis["estimated_maturity_pct"] <= 50.0


def test_synthetic_moldy_pod_triggers_mold_rejection():
    """Vérifie qu'une gousse avec mycélium est classée Defective_Mold avec prix nul."""
    data = _synthetic_pod_bytes("Defective_Mold", bg="jute")
    analysis = analyze_lot_photo(data)

    assert analysis["mold_patch_ratio"] > 0.02
    assert analysis["predicted_grade"] == "Defective_Mold"

    # Vérification de l'inspection globale
    result = vanilla_ai.inspect_lot(
        district="Sambava",
        bean_length_cm=18.0,
        moisture_pct=32.0,
        vanillin_pct=2.1,
        mold_detected=False,
        maturity_pct=95.0,
        image_bytes=data,
    )
    assert result["quality_grade"] == "Defective_Mold"
    assert result["status"] == "REJECTED"
    assert result["estimated_fair_price_mga_per_kg"] == 0.0


def test_trained_vision_model_persistence():
    """Vérifie le chargement et le résumé du modèle de vision entraîné."""
    model = get_vision_model()
    assert model.is_trained is True
    summary = model.summary()
    assert summary["trained"] is True
    assert summary["n_samples"] >= 300
    assert "metrics" in summary
    assert summary["metrics"]["accuracy"] >= 0.85
