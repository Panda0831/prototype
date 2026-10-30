"""
Entraînement local du modèle de pricing vanille (Hazo Lova Agri-AI).

Usage :
    python train_vanilla_ai.py

Le script ajuste une régression ridge multi-cibles sur le dataset réel,
affiche les métriques train/test, puis sauvegarde les poids dans
`data/models/vanilla_pricing_model.json`.
"""

import sys

from src.ai.pricing_model import (
    DEFAULT_DATASET_PATH,
    DEFAULT_MODEL_PATH,
    TARGETS,
    VanillaPricingModel,
    load_dataset_rows,
)


def main() -> int:
    print("=" * 70)
    print(" ENTRAÎNEMENT LOCAL — MODÈLE DE PRICING VANILLE (Hazo Lova Agri-AI)")
    print("=" * 70)

    rows = load_dataset_rows(DEFAULT_DATASET_PATH)
    if not rows:
        print(f"[!] Dataset introuvable ou vide : {DEFAULT_DATASET_PATH}")
        return 1

    print(f"[*] Dataset        : {DEFAULT_DATASET_PATH}")
    print(f"[*] Observations   : {len(rows)}")
    print("[*] Algorithme     : régression ridge multi-cibles (pure Python)")
    print("[*] Split          : 80% train / 20% test (graine 42)")
    print()

    model = VanillaPricingModel()
    metrics = model.fit(rows, ridge_lambda=1.0, dataset_path=DEFAULT_DATASET_PATH)
    path = model.save(DEFAULT_MODEL_PATH)

    labels = {
        "fair_farmgate_price_mga": "Prix bord-champ (MGA/kg)",
        "fob_export_price_usd": "Prix FOB export (USD/kg)",
    }

    print("-" * 70)
    print(f"{'CIBLE':<34}{'MAE':>10}{'RMSE':>10}{'R2':>8}{'MAPE':>9}")
    print("-" * 70)
    for target in TARGETS:
        m = metrics["targets"][target]
        print(
            f"{labels[target]:<34}{m['mae']:>10.2f}{m['rmse']:>10.2f}"
            f"{m['r2']:>8.3f}{m['mape_pct']:>8.1f}%"
        )
    print("-" * 70)

    print("\nComparaison au prix moyen (baseline) :")
    for target in TARGETS:
        m = metrics["targets"][target]
        gain = (1 - m["mae"] / m["baseline_mae"]) * 100 if m["baseline_mae"] else 0
        print(
            f"  {labels[target]} : MAE {m['mae']:.0f} vs {m['baseline_mae']:.0f} "
            f"-> {gain:+.1f}% de réduction de l'erreur"
        )

    print(f"\n[OK] Modèle sauvegardé : {path}")
    print("[OK] L'API et l'IA vanille chargent ce modèle au démarrage.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
