"""
Modèle de marché vanille entraîné localement sur des données réelles.

Source : UN Comtrade (HS 0905.10, exportations de Madagascar) + taux de change
officiel Banque mondiale. Le modèle estime le prix FOB ($/kg) à partir de
l'année, du volume exporté et du taux de change, en régression ridge sur le
logarithme du prix. Évaluation par validation croisée « leave-one-year-out ».

Ce modèle est distinct du modèle qualité-par-lot (`pricing_model.py`) : il donne
le niveau de marché, pas la prime de qualité d'un lot.
"""

import csv
import datetime
import json
import math
import os
from typing import Any, Dict, List, Optional

from src.ai.pricing_model import _solve_linear_system

DEFAULT_MARKET_DATASET = "data/sources/un_comtrade_vanilla_madagascar.csv"
DEFAULT_MARKET_MODEL = "data/models/vanilla_market_model.json"
WORLD_PARTNER_CODE = "0"


def load_market_rows(path: str = DEFAULT_MARKET_DATASET) -> List[Dict[str, Any]]:
    """Charge la série annuelle mondiale (partenaire 0 = total Madagascar)."""
    rows: List[Dict[str, Any]] = []
    if not os.path.exists(path):
        return rows
    with open(path, "r", encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            if str(raw.get("partner_code")) != WORLD_PARTNER_CODE:
                continue
            try:
                rows.append(
                    {
                        "year": int(raw["year"]),
                        "qty_mkg": float(raw["export_qty_kg"]) / 1_000_000.0,
                        "fx_mga_per_usd": float(raw["mga_per_usd"]),
                        "fob_usd_per_kg": float(raw["unit_value_usd_per_kg"]),
                    }
                )
            except (KeyError, TypeError, ValueError):
                continue
    rows.sort(key=lambda r: r["year"])
    return rows


class VanillaMarketModel:
    """Ridge locale sur le prix FOB réel de la vanille malgache."""

    def __init__(self, model_path: str = DEFAULT_MARKET_MODEL):
        self.model_path = model_path
        self.weights: List[float] = []
        self.metrics: Dict[str, Any] = {}
        self.series: List[Dict[str, Any]] = []
        self.trained_at: Optional[str] = None
        self.dataset_path: Optional[str] = None

    @staticmethod
    def _features(row: Dict[str, Any]) -> List[float]:
        t = row["year"] - 2020
        return [
            1.0,
            t,
            t * t / 4.0,
            math.log(row["qty_mkg"]),
            math.log(row["fx_mga_per_usd"] / 4000.0),
        ]

    def _fit(self, rows: List[Dict[str, Any]], ridge_lambda: float = 1e-3) -> List[float]:
        n = 5
        x = [self._features(r) for r in rows]
        y = [math.log(r["fob_usd_per_kg"]) for r in rows]
        xtx = [[sum(row[i] * row[j] for row in x) for j in range(n)] for i in range(n)]
        xty = [sum(row[i] * target for row, target in zip(x, y)) for i in range(n)]
        for i in range(1, n):
            xtx[i][i] += ridge_lambda
        return _solve_linear_system(xtx, xty)

    def _predict(self, weights: List[float], row: Dict[str, Any]) -> float:
        return math.exp(sum(w * f for w, f in zip(weights, self._features(row))))

    def fit(self, rows: List[Dict[str, Any]], dataset_path: Optional[str] = None) -> Dict[str, Any]:
        if len(rows) < 6:
            raise ValueError("Série de marché trop courte pour entraîner le modèle.")

        self.weights = self._fit(rows)
        fitted = [self._predict(self.weights, r) for r in rows]

        loo_errors: List[float] = []
        for i in range(len(rows)):
            weights = self._fit(rows[:i] + rows[i + 1:])
            loo_errors.append(self._predict(weights, rows[i]) - rows[i]["fob_usd_per_kg"])

        actual = [r["fob_usd_per_kg"] for r in rows]
        n = len(actual)
        mae = sum(abs(e) for e in loo_errors) / n
        mean = sum(actual) / n
        ss_tot = sum((v - mean) ** 2 for v in actual)
        ss_res = sum(e * e for e in loo_errors)
        mape = sum(abs(e / v) * 100 for e, v in zip(loo_errors, actual) if v) / n

        self.metrics = {
            "n_years": n,
            "validation": "leave-one-year-out",
            "loo_mae_usd_per_kg": round(mae, 2),
            "loo_rmse_usd_per_kg": round(math.sqrt(ss_res / n), 2),
            "loo_r2": round(1 - ss_res / ss_tot, 4) if ss_tot else 0.0,
            "loo_mape_pct": round(mape, 1),
        }
        self.series = [
            {
                "year": r["year"],
                "actual_usd": round(r["fob_usd_per_kg"], 2),
                "fitted_usd": round(f, 2),
                "mga_per_usd": round(r["fx_mga_per_usd"], 2),
                "actual_mga": round(r["fob_usd_per_kg"] * r["fx_mga_per_usd"], 0),
            }
            for r, f in zip(rows, fitted)
        ]
        self.trained_at = datetime.datetime.now().isoformat(timespec="seconds")
        self.dataset_path = dataset_path
        return self.metrics

    @property
    def is_trained(self) -> bool:
        return bool(self.weights) and bool(self.series)

    def latest(self) -> Optional[Dict[str, Any]]:
        return self.series[-1] if self.series else None

    def save(self, path: Optional[str] = None) -> str:
        target = path or self.model_path
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "version": 1,
                    "trained_at": self.trained_at,
                    "dataset": self.dataset_path,
                    "weights": self.weights,
                    "metrics": self.metrics,
                    "series": self.series,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        return target

    def load(self, path: Optional[str] = None) -> bool:
        target = path or self.model_path
        if not os.path.exists(target):
            return False
        with open(target, "r", encoding="utf-8") as f:
            payload = json.load(f)
        try:
            self.weights = list(payload["weights"])
            self.metrics = dict(payload.get("metrics", {}))
            self.series = list(payload.get("series", []))
            self.trained_at = payload.get("trained_at")
            self.dataset_path = payload.get("dataset")
        except (KeyError, TypeError, ValueError):
            return False
        return self.is_trained

    def summary(self) -> Dict[str, Any]:
        latest = self.latest() or {}
        return {
            "trained": self.is_trained,
            "algorithm": "Ridge locale sur log(prix FOB)",
            "source": "UN Comtrade HS 0905.10 + Banque mondiale PA.NUS.FCRF",
            "trained_at": self.trained_at,
            "dataset": self.dataset_path,
            "metrics": self.metrics,
            "latest": latest,
            "series": self.series,
        }


vanilla_market = VanillaMarketModel()
vanilla_market.load()
