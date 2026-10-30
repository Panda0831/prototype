"""
Module de vision par ordinateur pour la vanille de Madagascar (Hazo Lova Agri-AI).

Analyse fine-tunée des photos de gousses bord-champ :
- Extraction colorimétrique calibrée (HSV/RGB) : vanille verte (vivid/olive/jaune-vert),
  noire Bourbon ébène, brune chocolatée TK, rougeâtre extraction.
- Détection des anomalies critiques : cueillette prématurée / vanille verte et moisissure (mycélium).
- Intégration du modèle entraîné `VanillaVisionModel` (Ridge multi-classes) avec repli normatif ISO 5565-1.
"""

import colorsys
import hashlib
import io
import os
from typing import Any, Dict, List, Optional

from PIL import Image, ImageFilter, ImageStat

from src.ai.vision_model import (
    DEFAULT_VISION_MODEL_PATH,
    VanillaVisionModel,
    extract_features_from_image,
)

# Instance singleton du modèle de vision, chargée au démarrage
_vision_model: Optional[VanillaVisionModel] = None


def get_vision_model() -> VanillaVisionModel:
    global _vision_model
    if _vision_model is None:
        _vision_model = VanillaVisionModel(DEFAULT_VISION_MODEL_PATH)
        if not _vision_model.load():
            print(" [*] Modèle de vision entraîné absent : repli heuristique ISO actif.")
    return _vision_model


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def analyze_lot_photo(image_bytes: bytes) -> Dict[str, Any]:
    """
    Analyse approfondie et calibrée d'une photo de gousses de vanille.
    Retourne les ratios colorimétriques, le grade prédit, la maturité estimée et le risque sanitaire.
    """
    image_sha256 = hashlib.sha256(image_bytes).hexdigest()
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.load()
        image = image.convert("RGB")
    except Exception as exc:  # noqa: BLE001
        return {
            "engine": "Vision IA Hybride",
            "image_sha256": image_sha256,
            "reliable": False,
            "error": f"Photo illisible : {exc.__class__.__name__}",
            "flags": ["photo illisible"],
            "green_ratio": 0.0,
            "brown_ratio": 0.0,
            "mold_patch_ratio": 0.0,
            "estimated_maturity_pct": 50.0,
            "mold_risk_pct": 0.0,
            "confidence": 0.0,
            "predicted_grade": "Extraction_Grade_C",
        }

    width, height = image.size
    features = extract_features_from_image(image)

    green_ratio = features.get("green_ratio", 0.0)
    dark_ebony_ratio = features.get("dark_ebony_ratio", 0.0)
    cured_brown_ratio = features.get("cured_brown_ratio", 0.0)
    reddish_ratio = features.get("reddish_ratio", 0.0)
    mold_patch_ratio = features.get("mold_patch_ratio", 0.0)
    sheen_index = features.get("sheen_index", 0.0)
    subject_ratio = features.get("subject_ratio", 0.0)
    brightness = features.get("mean_brightness", 0.0)
    sharpness = features.get("edge_density", 0.0)

    # Ratio brun global pour compatibilité descendante
    brown_ratio = min(1.0, cured_brown_ratio + dark_ebony_ratio + reddish_ratio)

    # Inférence via le modèle entraîné localement
    model = get_vision_model()
    prediction = model.predict(features)

    predicted_grade = prediction.get("predicted_grade", "Extraction_Grade_C")
    estimated_maturity = prediction.get("estimated_maturity_pct", 50.0)
    mold_risk = prediction.get("mold_risk_pct", 0.0)
    model_confidence = prediction.get("confidence", 0.85)

    # Alertes qualité de prise de vue
    flags: List[str] = []
    if brightness < 30.0:
        flags.append("photo trop sombre")
    if brightness > 238.0:
        flags.append("photo surexposée")
    if subject_ratio < 0.01:
        flags.append("aucune gousse détectée")
    if sharpness < 8.0:
        flags.append("image floue ou sans contour")

    confidence = model_confidence
    if flags:
        confidence = round(confidence * 0.7, 2)

    reliable = len(flags) == 0

    engine_name = (
        "Vision IA Hybride (Ridge Classifier + ISO 5565-1)"
        if model.is_trained
        else "Vision classique (Colorimétrie ISO 5565-1)"
    )

    return {
        "engine": engine_name,
        "image_sha256": image_sha256,
        "width": width,
        "height": height,
        "brightness": round(brightness, 1),
        "subject_ratio": round(subject_ratio, 3),
        "green_ratio": round(green_ratio, 3),
        "brown_ratio": round(brown_ratio, 3),
        "dark_ebony_ratio": round(dark_ebony_ratio, 3),
        "mold_patch_ratio": round(mold_patch_ratio, 3),
        "sheen_index": round(sheen_index, 3),
        "estimated_maturity_pct": round(_clamp(estimated_maturity, 10.0, 99.0), 1),
        "mold_risk_pct": round(_clamp(mold_risk, 0.0, 100.0), 1),
        "predicted_grade": predicted_grade,
        "grade_probabilities": prediction.get("grade_probabilities", {}),
        "sharpness": round(sharpness, 1),
        "confidence": round(min(confidence, 0.99), 2),
        "reliable": reliable,
        "flags": flags,
    }
