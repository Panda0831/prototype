"""
Entraînement local du modèle de vision par ordinateur pour la vanille (Hazo Lova Agri-AI).

Usage :
    python train_vanilla_vision.py

Le script :
1. Charge ou génère le dataset de photos étiquetées selon les 5 grades ISO 5565-1.
2. Extrait le vecteur de caractéristiques colorimétriques et texturales (HSV, RGB, brillance, contours).
3. Entraîne le modèle multi-classes One-vs-Rest Ridge et les régressions continues de maturité et risque de moisissure.
4. Sauvegarde les poids dans `data/models/vanilla_vision_model.json`.
"""

import csv
import os
import sys
from typing import Any, Dict, List

from PIL import Image

from scripts.generate_vanilla_vision_dataset import (
    MANIFEST_PATH,
    OUTPUT_DIR,
    generate_dataset,
)
from src.ai.vision_model import (
    CLASSES,
    DEFAULT_VISION_MODEL_PATH,
    VanillaVisionModel,
    extract_features_from_image,
)


def load_or_create_dataset() -> List[Dict[str, Any]]:
    """Charge le manifest ou génère le dataset si absent."""
    if not os.path.exists(MANIFEST_PATH):
        print(f"[*] Manifest {MANIFEST_PATH} introuvable : génération automatique du dataset...")
        generate_dataset()

    samples: List[Dict[str, Any]] = []
    print(f"[*] Extraction des caractéristiques visuelles depuis {MANIFEST_PATH}...")

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            img_rel_path = row["image_path"]
            img_path = os.path.join(OUTPUT_DIR, img_rel_path)
            if not os.path.exists(img_path):
                continue

            try:
                img = Image.open(img_path)
                features = extract_features_from_image(img)
                samples.append({
                    "features": features,
                    "label": row["label"],
                    "maturity_pct": float(row["maturity_pct"]),
                    "mold_risk_pct": float(row["mold_risk_pct"]),
                })
            except Exception as e:
                print(f" [!] Erreur sur {img_path}: {e}")
                continue

    return samples


def main() -> int:
    print("=" * 72)
    print(" ENTRAÎNEMENT LOCAL — MODÈLE DE VISION VANILLE (Hazo Lova Agri-AI)")
    print("=" * 72)

    samples = load_or_create_dataset()
    if len(samples) < 15:
        print(f"[!] Échantillons insuffisants ({len(samples)}). Échec de l'entraînement.")
        return 1

    print(f"[*] Échantillons chargés   : {len(samples)}")
    print(f"[*] Classes cibles (5)     : {', '.join(CLASSES)}")
    print("[*] Algorithme             : One-vs-Rest Ridge Classifier + Dual Ridge Regressor (pure Python)")
    print("[*] Split                  : 80% train / 20% test (graine 42)")
    print()

    model = VanillaVisionModel(DEFAULT_VISION_MODEL_PATH)
    metrics = model.fit(samples, ridge_lambda=0.8, test_ratio=0.2, seed=42)
    path = model.save(DEFAULT_VISION_MODEL_PATH)

    print("-" * 72)
    print(f"{'MÉTRIQUE DE VALIDATION':<45}{'VALEUR':>25}")
    print("-" * 72)
    print(f"{'Précision classification globale (Accuracy)':<45}{metrics['accuracy'] * 100:>24.1f}%")
    print(f"{'Erreur absolue moyenne maturité (MAE)':<45}{metrics['maturity_mae']:>23.2f}%")
    print(f"{'Erreur absolue moyenne risque moisissure (MAE)':<45}{metrics['mold_risk_mae']:>23.2f}%")
    print("-" * 72)

    print(f"\n[OK] Modèle de vision sauvegardé : {path}")
    print("[OK] L'API et l'IA de vision chargeront ce modèle pour les inspections d'images.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
