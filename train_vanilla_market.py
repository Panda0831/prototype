"""
Entraînement local du modèle de marché vanille sur données réelles.

Usage :
    python train_vanilla_market.py

Source : UN Comtrade (exportations Madagascar, HS 0905.10, 2015-2025) et
Banque mondiale (taux de change MGA/USD). Aucune donnée simulée.
"""

import sys

from src.ai.market_model import (
    DEFAULT_MARKET_DATASET,
    DEFAULT_MARKET_MODEL,
    VanillaMarketModel,
    load_market_rows,
)


def main() -> int:
    rows = load_market_rows(DEFAULT_MARKET_DATASET)
    if len(rows) < 6:
        print(f"[!] Série de marché introuvable ou trop courte : {DEFAULT_MARKET_DATASET}")
        print("    Lancez d'abord : python scripts/fetch_vanilla_market_data.py")
        return 1

    print("=" * 70)
    print(" ENTRAÎNEMENT LOCAL — MODÈLE DE MARCHÉ VANILLE (données ONU réelles)")
    print("=" * 70)
    print(f"[*] Dataset     : {DEFAULT_MARKET_DATASET}")
    print(f"[*] Années      : {rows[0]['year']} → {rows[-1]['year']} ({len(rows)})")
    print("[*] Cible       : prix FOB USD/kg (UN Comtrade)")
    print("[*] Validation  : leave-one-year-out")
    print()

    model = VanillaMarketModel()
    metrics = model.fit(rows, dataset_path=DEFAULT_MARKET_DATASET)
    path = model.save(DEFAULT_MARKET_MODEL)

    print(f"{'ANNÉE':<8}{'RÉEL $/kg':>12}{'AJUSTÉ $/kg':>14}")
    print("-" * 40)
    for point in model.series:
        print(f"{point['year']:<8}{point['actual_usd']:>12.2f}{point['fitted_usd']:>14.2f}")
    print("-" * 40)
    print(
        f"LOO : MAE {metrics['loo_mae_usd_per_kg']:.2f} $/kg · "
        f"R² {metrics['loo_r2']:.3f} · MAPE {metrics['loo_mape_pct']:.1f}%"
    )
    latest = model.latest() or {}
    print(
        f"Dernier point réel : {latest.get('year')} — "
        f"{latest.get('actual_usd')} $/kg"
    )
    print(f"\n[OK] Modèle sauvegardé : {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
