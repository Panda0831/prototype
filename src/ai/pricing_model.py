"""
Modèle de pricing équitable de la vanille, entraîné localement.

Implémentation pure Python (aucune dépendance externe) d'une régression
ridge multi-cibles sur les caractéristiques physiques ISO 5565-1 et le
district d'origine. Le modèle est ajusté sur le jeu de données réel
`data/madagascar_vanilla_quality_pricing.csv`, évalué sur un split
train/test déterministe, puis persisté en JSON.
"""

import csv
import datetime
import json
import math
import os
import random
from typing import Any, Dict, List, Optional, Tuple

NUMERIC_FEATURES = [
    "bean_length_cm",
    "moisture_pct",
    "vanillin_pct",
    "maturity_pct",
    "mold_detected",
]
TARGETS = ["fair_farmgate_price_mga", "fob_export_price_usd"]
DEFAULT_DATASET_PATH = "data/madagascar_vanilla_quality_pricing.csv"
DEFAULT_MODEL_PATH = "data/models/vanilla_pricing_model.json"


def load_dataset_rows(path: str = DEFAULT_DATASET_PATH) -> List[Dict[str, Any]]:
    """Charge et type les lignes du dataset qualité/prix vanille."""
    rows: List[Dict[str, Any]] = []
    if not os.path.exists(path):
        return rows

    with open(path, "r", encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            try:
                row: Dict[str, Any] = {"district": raw["district"]}
                for feature in NUMERIC_FEATURES:
                    row[feature] = float(raw[feature])
                for target in TARGETS:
                    row[target] = float(raw[target])
                rows.append(row)
            except (KeyError, ValueError):
                continue
    return rows


def _solve_linear_system(matrix: List[List[float]], vector: List[float]) -> List[float]:
    """Résout A·x = b par élimination de Gauss-Jordan (pivot partiel)."""
    n = len(matrix)
    augmented = [row[:] + [vector[i]] for i, row in enumerate(matrix)]

    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(augmented[r][col]))
        if abs(augmented[pivot][col]) < 1e-12:
            continue
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]

        pivot_value = augmented[col][col]
        for j in range(col, n + 1):
            augmented[col][j] /= pivot_value

        for r in range(n):
            if r == col:
                continue
            factor = augmented[r][col]
            if abs(factor) < 1e-15:
                continue
            for j in range(col, n + 1):
                augmented[r][j] -= factor * augmented[col][j]

    return [augmented[i][n] for i in range(n)]


class VanillaPricingModel:
    """Régression ridge entraînée localement pour le juste prix bord-champ."""

    def __init__(self, model_path: str = DEFAULT_MODEL_PATH):
        self.model_path = model_path
        self.districts: List[str] = []
        self.feature_means: Dict[str, float] = {}
        self.feature_stds: Dict[str, float] = {}
        self.weights: Dict[str, List[float]] = {}
        self.metrics: Dict[str, Any] = {}
        self.trained_at: Optional[str] = None
        self.dataset_path: Optional[str] = None
        self.n_samples: int = 0

    # ------------------------------------------------------------------ #
    # Entraînement
    # ------------------------------------------------------------------ #
    def fit(
        self,
        rows: List[Dict[str, Any]],
        ridge_lambda: float = 1.0,
        test_ratio: float = 0.2,
        seed: int = 42,
        dataset_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Entraîne le modèle sur `rows` et calcule les métriques de test."""
        if len(rows) < 10:
            raise ValueError("Dataset trop petit pour entraîner le modèle de pricing.")

        self.districts = sorted({str(row["district"]) for row in rows})
        indices = list(range(len(rows)))
        random.Random(seed).shuffle(indices)
        n_test = max(1, int(len(rows) * test_ratio))
        test_indices = set(indices[:n_test])
        train_rows = [rows[i] for i in range(len(rows)) if i not in test_indices]
        test_rows = [rows[i] for i in range(len(rows)) if i in test_indices]

        # Normalisation calculée uniquement sur le train (pas de fuite de données).
        self.feature_means = {}
        self.feature_stds = {}
        for feature in NUMERIC_FEATURES:
            values = [row[feature] for row in train_rows]
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            self.feature_means[feature] = mean
            self.feature_stds[feature] = math.sqrt(variance) or 1.0
        self.feature_means["mold_detected"] = 0.0
        self.feature_stds["mold_detected"] = 1.0

        x_train = [self._features(row) for row in train_rows]
        x_test = [self._features(row) for row in test_rows]
        n_features = len(x_train[0])

        self.weights = {}
        metrics_targets: Dict[str, Any] = {}
        for target in TARGETS:
            y_train = [row[target] for row in train_rows]
            weights = self._fit_ridge(x_train, y_train, ridge_lambda)

            y_pred_test = [self._dot(weights, x) for x in x_test]
            y_true_test = [row[target] for row in test_rows]
            test_metrics = self._regression_metrics(y_true_test, y_pred_test)

            mean_baseline = sum(y_train) / len(y_train)
            baseline_pred = [mean_baseline] * len(y_true_test)
            test_metrics["baseline_mae"] = self._regression_metrics(
                y_true_test, baseline_pred
            )["mae"]

            self.weights[target] = weights
            metrics_targets[target] = test_metrics

        self.metrics = {
            "n_samples": len(rows),
            "n_train": len(train_rows),
            "n_test": len(test_rows),
            "n_features": n_features,
            "ridge_lambda": ridge_lambda,
            "targets": metrics_targets,
        }
        self.n_samples = len(rows)
        self.trained_at = datetime.datetime.now().isoformat(timespec="seconds")
        self.dataset_path = dataset_path
        return self.metrics

    def _fit_ridge(
        self, x_train: List[List[float]], y_train: List[float], ridge_lambda: float
    ) -> List[float]:
        n_features = len(x_train[0])
        xtx = [[0.0] * n_features for _ in range(n_features)]
        xty = [0.0] * n_features

        for x, y in zip(x_train, y_train):
            for i in range(n_features):
                xty[i] += x[i] * y
                for j in range(n_features):
                    xtx[i][j] += x[i] * x[j]

        # Le biais (colonne 0) n'est pas pénalisé.
        for i in range(1, n_features):
            xtx[i][i] += ridge_lambda

        return _solve_linear_system(xtx, xty)

    # ------------------------------------------------------------------ #
    # Prédiction
    # ------------------------------------------------------------------ #
    def _features(self, row: Dict[str, Any]) -> List[float]:
        vector = [1.0]
        for feature in NUMERIC_FEATURES:
            value = float(row[feature])
            if feature in ("mold_detected",):
                vector.append(value)
            else:
                vector.append(
                    (value - self.feature_means[feature]) / self.feature_stds[feature]
                )
        district = str(row["district"])
        for candidate in self.districts:
            vector.append(1.0 if candidate == district else 0.0)
        return vector

    @staticmethod
    def _dot(weights: List[float], features: List[float]) -> float:
        return sum(w * f for w, f in zip(weights, features))

    def predict(
        self,
        district: str,
        bean_length_cm: float,
        moisture_pct: float,
        vanillin_pct: float,
        maturity_pct: float,
        mold_detected: bool,
    ) -> Dict[str, float]:
        """Prédit le prix bord-champ (MGA/kg) et le prix FOB (USD/kg)."""
        if not self.is_trained:
            raise RuntimeError("Le modèle de pricing n'est pas entraîné.")

        row = {
            "district": district if district in self.districts else self.districts[0],
            "bean_length_cm": bean_length_cm,
            "moisture_pct": moisture_pct,
            "vanillin_pct": vanillin_pct,
            "maturity_pct": maturity_pct,
            "mold_detected": 1.0 if mold_detected else 0.0,
        }
        features = self._features(row)
        return {
            "fair_farmgate_price_mga": max(0.0, self._dot(self.weights[TARGETS[0]], features)),
            "fob_export_price_usd": max(0.0, self._dot(self.weights[TARGETS[1]], features)),
        }

    # ------------------------------------------------------------------ #
    # Évaluation / persistance
    # ------------------------------------------------------------------ #
    @staticmethod
    def _regression_metrics(y_true: List[float], y_pred: List[float]) -> Dict[str, float]:
        n = len(y_true)
        if n == 0:
            return {"mae": 0.0, "rmse": 0.0, "r2": 0.0, "mape_pct": 0.0}

        errors = [p - t for t, p in zip(y_true, y_pred)]
        mae = sum(abs(e) for e in errors) / n
        rmse = math.sqrt(sum(e * e for e in errors) / n)
        mean_true = sum(y_true) / n
        ss_tot = sum((t - mean_true) ** 2 for t in y_true)
        ss_res = sum(e * e for e in errors)
        r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        mape_values = [
            abs((p - t) / t) * 100.0 for t, p in zip(y_true, y_pred) if t != 0
        ]
        mape = sum(mape_values) / len(mape_values) if mape_values else 0.0
        return {
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "r2": round(r2, 4),
            "mape_pct": round(mape, 2),
        }

    @property
    def is_trained(self) -> bool:
        return bool(self.weights) and bool(self.districts)

    def save(self, path: Optional[str] = None) -> str:
        target = path or self.model_path
        directory = os.path.dirname(target)
        if directory:
            os.makedirs(directory, exist_ok=True)

        payload = {
            "version": 1,
            "trained_at": self.trained_at,
            "dataset": self.dataset_path,
            "n_samples": self.n_samples,
            "districts": self.districts,
            "feature_means": self.feature_means,
            "feature_stds": self.feature_stds,
            "weights": self.weights,
            "metrics": self.metrics,
        }
        with open(target, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return target

    def load(self, path: Optional[str] = None) -> bool:
        target = path or self.model_path
        if not os.path.exists(target):
            return False

        with open(target, "r", encoding="utf-8") as f:
            payload = json.load(f)

        try:
            self.districts = list(payload["districts"])
            self.feature_means = dict(payload["feature_means"])
            self.feature_stds = dict(payload["feature_stds"])
            self.weights = {
                target_name: list(values)
                for target_name, values in payload["weights"].items()
            }
            self.metrics = dict(payload.get("metrics", {}))
            self.trained_at = payload.get("trained_at")
            self.dataset_path = payload.get("dataset")
            self.n_samples = int(payload.get("n_samples", 0))
        except (KeyError, TypeError, ValueError):
            return False

        return self.is_trained

    def summary(self) -> Dict[str, Any]:
        """Résumé exposé à l'API et au dashboard."""
        return {
            "trained": self.is_trained,
            "algorithm": "Régression Ridge multi-cibles (entraînée localement)",
            "trained_at": self.trained_at,
            "dataset": self.dataset_path,
            "n_samples": self.n_samples,
            "districts": len(self.districts),
            "metrics": self.metrics,
        }
