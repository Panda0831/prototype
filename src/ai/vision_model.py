"""
Modèle de vision par ordinateur pour la filière vanille (Hazo Lova Agri-AI).

Implémentation pure Python combinant :
1. Segmentation robuste du sujet (séparation fond/gousse sur tables en bois, sacs en jute ou draps d'inspection).
2. Extraction précise des caractéristiques colorimétriques et texturales (HSV, RGB, brillance, contours).
3. Modèle multi-classes (Régression Ridge One-vs-Rest) pour la prédiction des 5 grades ISO 5565-1 :
   - Gourmet_Grade_A (noire ébène, grasse/luisante)
   - Standard_TK_Grade_B (brune chocolatée, souple)
   - Extraction_Grade_C (courte, fendue, rougeâtre)
   - Rejected_Immature (cueillette prématurée, vanille verte/jaune-vert)
   - Defective_Mold (contamination fongique / moisissure)
4. Modèles de régression pour l'estimation continue de la maturité (%) et du risque de moisissure (%).
"""

import colorsys
import datetime
import json
import math
import os
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, ImageFilter, ImageStat

CLASSES = [
    "Gourmet_Grade_A",
    "Standard_TK_Grade_B",
    "Extraction_Grade_C",
    "Rejected_Immature",
    "Defective_Mold",
]

FEATURE_NAMES = [
    "green_ratio",
    "dark_ebony_ratio",
    "cured_brown_ratio",
    "reddish_ratio",
    "mold_patch_ratio",
    "sheen_index",
    "mean_brightness",
    "mean_saturation",
    "mean_hue",
    "edge_density",
    "color_std",
    "subject_ratio",
]

DEFAULT_VISION_MODEL_PATH = "data/models/vanilla_vision_model.json"


def _solve_linear_system(matrix: List[List[float]], vector: List[float]) -> List[float]:
    """Résout A·x = b par élimination de Gauss-Jordan avec pivot partiel."""
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


def extract_features_from_image(image: Image.Image) -> Dict[str, float]:
    """
    Extrait un vecteur de caractéristiques physiques, colorimétriques et texturales
    avec élimination d'arrière-plan adaptative.
    """
    image = image.convert("RGB")
    thumb = image.copy()
    thumb.thumbnail((256, 256))
    width, height = thumb.size
    pixels = thumb.load()

    # 1. Échantillonnage de la bordure périphérique pour estimer la couleur du fond
    border_r, border_g, border_b = 0.0, 0.0, 0.0
    border_count = 0
    border_pixels = []
    for x in range(width):
        for y in (0, 1, height - 2, height - 1):
            r, g, b = pixels[x, y]
            border_r += r
            border_g += g
            border_b += b
            border_pixels.append((r, g, b))
            border_count += 1
    for y in range(2, height - 2):
        for x in (0, 1, width - 2, width - 1):
            r, g, b = pixels[x, y]
            border_r += r
            border_g += g
            border_b += b
            border_pixels.append((r, g, b))
            border_count += 1

    bg_r = border_r / border_count if border_count else 240.0
    bg_g = border_g / border_count if border_count else 240.0
    bg_b = border_b / border_count if border_count else 240.0

    # Test si une gousse / sujet est présent distinctement du fond
    all_px: List[Tuple[int, int, int]] = []
    dist_threshold = 28.0
    has_distinct_foreground = False

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            all_px.append((r, g, b))
            dist = math.sqrt((r - bg_r) ** 2 + (g - bg_g) ** 2 + (b - bg_b) ** 2)
            if dist > dist_threshold:
                has_distinct_foreground = True

    # 2. Détermination des pixels de gousse (sujet)
    subject_pixels: List[Tuple[int, int, int]] = []
    subject_coords: List[Tuple[int, int]] = []

    if has_distinct_foreground:
        # Masque premier plan
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                dist = math.sqrt((r - bg_r) ** 2 + (g - bg_g) ** 2 + (b - bg_b) ** 2)
                if dist > dist_threshold:
                    subject_pixels.append((r, g, b))
                    subject_coords.append((x, y))
    else:
        # Échantillon macro ou gros plan uniforme : exclut seulement les blancs / noirs extrêmes
        for r, g, b in all_px:
            bright = (r + g + b) / 3.0
            if (r > 242 and g > 242 and b > 242) or bright < 8:
                continue
            subject_pixels.append((r, g, b))

    n_subject = len(subject_pixels)
    if n_subject == 0:
        return {name: 0.0 for name in FEATURE_NAMES}

    # 3. Analyse colorimétrique et texturales sur les pixels de la gousse
    green_count = 0
    dark_ebony_count = 0
    cured_brown_count = 0
    reddish_count = 0
    sheen_count = 0
    mold_patch_count = 0

    sum_brightness = 0.0
    sum_saturation = 0.0
    sum_hue = 0.0

    for r, g, b in subject_pixels:
        bright = (r + g + b) / 3.0
        rn, gn, bn = r / 255.0, g / 255.0, b / 255.0
        h, s, v = colorsys.rgb_to_hsv(rn, gn, bn)

        sum_brightness += bright
        sum_saturation += s
        sum_hue += h

        # A. Vanille verte / cueillette prématurée (vert franc, vert olive, jaune-vert)
        is_green_vivid = (0.20 <= h <= 0.45) and (s >= 0.14) and (bright >= 36)
        is_green_olive = (0.14 <= h <= 0.35) and (g > b * 1.12) and (g >= r * 0.92) and (bright >= 36)
        is_green_yellowish = (0.11 <= h < 0.20) and (s >= 0.16) and (g >= r * 0.90) and (g > b * 1.15) and (bright >= 36)

        if is_green_vivid or is_green_olive or is_green_yellowish:
            green_count += 1
        # B. Moisissure suspecte sur gousse (spots clairs poudreux)
        elif (s < 0.22) and (115 < bright < 242) and (max(r, g, b) - min(r, g, b) < 30):
            mold_patch_count += 1
        # C. Noire Bourbon ébène (Gourmet A)
        elif bright <= 48 and abs(r - g) < 24 and abs(r - b) < 28:
            dark_ebony_count += 1
            if bright > 32:
                sheen_count += 1
        # D. Brune chocolatée (Standard TK B) — testée avant reddish pour préserver le brun ambré
        elif ((0.03 <= h < 0.15) and (s >= 0.18) and (25 < bright < 210)) or (
            r > g * 1.04 and g >= b * 0.82 and (r - b) > 16 and 25 < bright < 210
        ):
            cured_brown_count += 1
            if bright > 55 and s < 0.35:
                sheen_count += 1
        # E. Rougeâtre / sèche / fendue (Extraction C)
        elif (h < 0.03 or h >= 0.96 or r > g * 1.35) and (r - b > 28) and bright > 40:
            reddish_count += 1

    # Détection avancée de moisissure pour fonds blancs :
    if has_distinct_foreground and (bg_r + bg_g + bg_b) / 3.0 > 200 and subject_coords:
        coords_set = set(subject_coords)
        for x, y in subject_coords:
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if (nx, ny) not in coords_set and 0 <= nx < width and 0 <= ny < height:
                    nr, ng, nb = pixels[nx, ny]
                    nbright = (nr + ng + nb) / 3.0
                    nsat = colorsys.rgb_to_hsv(nr / 255.0, ng / 255.0, nb / 255.0)[1]
                    if 115 < nbright < 242 and nsat < 0.22:
                        mold_patch_count += 1
                        coords_set.add((nx, ny))

    green_ratio = green_count / n_subject
    dark_ebony_ratio = dark_ebony_count / n_subject
    cured_brown_ratio = cured_brown_count / n_subject
    reddish_ratio = reddish_count / n_subject
    mold_patch_ratio = mold_patch_count / n_subject
    sheen_index = sheen_count / n_subject
    subject_ratio = n_subject / (width * height)

    mean_brightness = sum_brightness / n_subject
    mean_saturation = sum_saturation / n_subject
    mean_hue = sum_hue / n_subject

    # Variance de couleur
    bright_var = sum(((p[0] + p[1] + p[2]) / 3.0 - mean_brightness) ** 2 for p in subject_pixels) / n_subject
    color_std = math.sqrt(bright_var)

    # Contours / netteté
    gray = thumb.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_variance = float(ImageStat.Stat(edges).var[0])

    return {
        "green_ratio": round(green_ratio, 4),
        "dark_ebony_ratio": round(dark_ebony_ratio, 4),
        "cured_brown_ratio": round(cured_brown_ratio, 4),
        "reddish_ratio": round(reddish_ratio, 4),
        "mold_patch_ratio": round(mold_patch_ratio, 4),
        "sheen_index": round(sheen_index, 4),
        "mean_brightness": round(mean_brightness, 2),
        "mean_saturation": round(mean_saturation, 4),
        "mean_hue": round(mean_hue, 4),
        "edge_density": round(edge_variance, 2),
        "color_std": round(color_std, 2),
        "subject_ratio": round(subject_ratio, 4),
    }


class VanillaVisionModel:
    """
    Modèle de classification multi-classes et régression pour l'analyse d'images de vanille.
    Entraîné localement avec régression Ridge (pure Python).
    """

    def __init__(self, model_path: str = DEFAULT_VISION_MODEL_PATH):
        self.model_path = model_path
        self.feature_names = list(FEATURE_NAMES)
        self.classes = list(CLASSES)
        self.feature_means: Dict[str, float] = {}
        self.feature_stds: Dict[str, float] = {}
        self.class_weights: Dict[str, List[float]] = {}
        self.regression_weights: Dict[str, List[float]] = {}
        self.metrics: Dict[str, Any] = {}
        self.trained_at: Optional[str] = None
        self.n_samples: int = 0

    def _normalize_features(self, features: Dict[str, float]) -> List[float]:
        vector = [1.0]  # Terme de biais
        for name in self.feature_names:
            val = features.get(name, 0.0)
            if name == "subject_ratio":
                # Écrêtage pour ne pas saturer le régresseur sur un échantillon plein écran
                val = min(val, 0.15)
            mean = self.feature_means.get(name, 0.0)
            std = self.feature_stds.get(name, 1.0)
            vector.append((val - mean) / std)
        return vector

    @staticmethod
    def _dot(w: List[float], x: List[float]) -> float:
        return sum(wi * xi for wi, xi in zip(w, x))

    @staticmethod
    def _softmax(logits: Dict[str, float]) -> Dict[str, float]:
        max_logit = max(logits.values())
        exp_vals = {cls: math.exp(v - max_logit) for cls, v in logits.items()}
        sum_exp = sum(exp_vals.values()) or 1.0
        return {cls: round(v / sum_exp, 4) for cls, v in exp_vals.items()}

    def fit(
        self,
        samples: List[Dict[str, Any]],
        ridge_lambda: float = 0.5,
        test_ratio: float = 0.2,
        seed: int = 42,
    ) -> Dict[str, Any]:
        """Entraîne le modèle sur une liste d'échantillons annotés."""
        if len(samples) < 15:
            raise ValueError("Jeu d'images insuffisant pour l'entraînement.")

        import random

        indices = list(range(len(samples)))
        random.Random(seed).shuffle(indices)
        n_test = max(1, int(len(samples) * test_ratio))
        test_indices = set(indices[:n_test])

        train_samples = [samples[i] for i in range(len(samples)) if i not in test_indices]
        test_samples = [samples[i] for i in range(len(samples)) if i in test_indices]

        # Normalisation sur train
        self.feature_means = {}
        self.feature_stds = {}
        for name in self.feature_names:
            vals = [min(s["features"][name], 0.15) if name == "subject_ratio" else s["features"][name] for s in train_samples]
            m = sum(vals) / len(vals)
            v = sum((x - m) ** 2 for x in vals) / len(vals)
            self.feature_means[name] = m
            self.feature_stds[name] = math.sqrt(v) or 1.0

        x_train = [self._normalize_features(s["features"]) for s in train_samples]
        x_test = [self._normalize_features(s["features"]) for s in test_samples]
        n_features = len(x_train[0])

        # 1. Classification One-vs-Rest par classe
        self.class_weights = {}
        for cls in self.classes:
            y_train = [1.0 if s["label"] == cls else 0.0 for s in train_samples]
            w = self._fit_ridge(x_train, y_train, ridge_lambda, n_features)
            self.class_weights[cls] = w

        # 2. Régression continue pour maturité et moisissure
        self.regression_weights = {}
        for target in ("maturity_pct", "mold_risk_pct"):
            y_train = [float(s[target]) for s in train_samples]
            w = self._fit_ridge(x_train, y_train, ridge_lambda, n_features)
            self.regression_weights[target] = w

        # 3. Évaluation sur test
        correct = 0
        mat_errors: List[float] = []
        mold_errors: List[float] = []

        for s, xt in zip(test_samples, x_test):
            scores = {cls: self._dot(self.class_weights[cls], xt) for cls in self.classes}
            pred_cls = max(scores.items(), key=lambda item: item[1])[0]
            if pred_cls == s["label"]:
                correct += 1

            pred_mat = self._dot(self.regression_weights["maturity_pct"], xt)
            mat_errors.append(abs(pred_mat - s["maturity_pct"]))

            pred_mold = self._dot(self.regression_weights["mold_risk_pct"], xt)
            mold_errors.append(abs(pred_mold - s["mold_risk_pct"]))

        accuracy = correct / len(test_samples) if test_samples else 0.0
        mat_mae = sum(mat_errors) / len(mat_errors) if mat_errors else 0.0
        mold_mae = sum(mold_errors) / len(mold_errors) if mold_errors else 0.0

        self.metrics = {
            "n_samples": len(samples),
            "n_train": len(train_samples),
            "n_test": len(test_samples),
            "accuracy": round(accuracy, 4),
            "maturity_mae": round(mat_mae, 2),
            "mold_risk_mae": round(mold_mae, 2),
        }
        self.n_samples = len(samples)
        self.trained_at = datetime.datetime.now().isoformat(timespec="seconds")
        return self.metrics

    def _fit_ridge(
        self,
        x_train: List[List[float]],
        y_train: List[float],
        ridge_lambda: float,
        n_features: int,
    ) -> List[float]:
        xtx = [[0.0] * n_features for _ in range(n_features)]
        xty = [0.0] * n_features

        for x, y in zip(x_train, y_train):
            for i in range(n_features):
                xty[i] += x[i] * y
                for j in range(n_features):
                    xtx[i][j] += x[i] * x[j]

        # Pas de pénalité sur le biais (colonne 0)
        for i in range(1, n_features):
            xtx[i][i] += ridge_lambda

        return _solve_linear_system(xtx, xty)

    def predict(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Prédit le grade ISO 5565-1, les probabilités, la maturité et le risque de moisissure."""
        green = features.get("green_ratio", 0.0)
        mold = features.get("mold_patch_ratio", 0.0)
        ebony = features.get("dark_ebony_ratio", 0.0)
        brown = features.get("cured_brown_ratio", 0.0)

        if not self.is_trained:
            return self._heuristic_predict(features)

        x = self._normalize_features(features)
        logits = {cls: self._dot(self.class_weights[cls], x) for cls in self.classes}
        probs = self._softmax(logits)
        predicted_grade = max(probs.items(), key=lambda item: item[1])[0]

        pred_mat = self._dot(self.regression_weights["maturity_pct"], x)
        pred_mold = self._dot(self.regression_weights["mold_risk_pct"], x)

        # Réalité physique & anti-fraude :
        # 1. Si aucun patch de moisissure détecté (< 2%), risque de moisissure borné
        if mold < 0.02:
            pred_mold = min(pred_mold, 5.0 * (mold / 0.02))
        elif mold >= 0.04 or pred_mold >= 35.0:
            predicted_grade = "Defective_Mold"
            pred_mold = max(pred_mold, 45.0 + 50.0 * min(mold / 0.15, 1.0))
            probs["Defective_Mold"] = 0.99

        # 2. Si gousses vertes détectées (>= 10%), rejet cueillette prématurée impératif
        if green >= 0.10:
            predicted_grade = "Rejected_Immature"
            pred_mat = min(pred_mat, 18.0 + 35.0 * (1.0 - min(green, 1.0)))
            probs["Rejected_Immature"] = max(probs.get("Rejected_Immature", 0.0), 0.98)
        elif pred_mat < 60.0 and (brown > 0.3 or ebony > 0.3):
            # Si gousses brunes/ébène sans vert, maturité élevée (au moins 85%)
            pred_mat = max(pred_mat, 85.0 + 12.0 * min(brown + ebony, 1.0))

        confidence = probs.get(predicted_grade, 0.85)

        return {
            "predicted_grade": predicted_grade,
            "grade_probabilities": probs,
            "estimated_maturity_pct": round(max(10.0, min(99.0, pred_mat)), 1),
            "mold_risk_pct": round(max(0.0, min(100.0, pred_mold)), 1),
            "confidence": round(confidence, 2),
        }

    def _heuristic_predict(self, f: Dict[str, float]) -> Dict[str, Any]:
        """Règles d'évaluation heuristiques déterministes conformes ISO 5565-1."""
        green = f.get("green_ratio", 0.0)
        mold = f.get("mold_patch_ratio", 0.0)
        ebony = f.get("dark_ebony_ratio", 0.0)
        brown = f.get("cured_brown_ratio", 0.0)

        mold_risk = min(100.0, mold * 260.0)

        if green >= 0.25:
            mat = 18.0 + 15.0 * (1.0 - min(green, 1.0))
        elif green >= 0.10:
            mat = 35.0 + 25.0 * (1.0 - green / 0.25)
        else:
            cured = brown + ebony
            mat = 60.0 + 38.0 * min(cured, 1.0)

        if mold_risk >= 35.0 or mold >= 0.04:
            grade = "Defective_Mold"
            conf = 0.98
        elif green >= 0.10 or mat < 68.0:
            grade = "Rejected_Immature"
            conf = 0.96
        elif ebony >= 0.40 and mat >= 90.0:
            grade = "Gourmet_Grade_A"
            conf = 0.94
        elif brown >= 0.35 or mat >= 78.0:
            grade = "Standard_TK_Grade_B"
            conf = 0.90
        else:
            grade = "Extraction_Grade_C"
            conf = 0.86

        return {
            "predicted_grade": grade,
            "grade_probabilities": {grade: conf},
            "estimated_maturity_pct": round(mat, 1),
            "mold_risk_pct": round(mold_risk, 1),
            "confidence": conf,
        }

    @property
    def is_trained(self) -> bool:
        return bool(self.class_weights) and bool(self.feature_means)

    def save(self, path: Optional[str] = None) -> str:
        target = path or self.model_path
        directory = os.path.dirname(target)
        if directory:
            os.makedirs(directory, exist_ok=True)

        payload = {
            "version": 1,
            "trained_at": self.trained_at,
            "n_samples": self.n_samples,
            "classes": self.classes,
            "feature_names": self.feature_names,
            "feature_means": self.feature_means,
            "feature_stds": self.feature_stds,
            "class_weights": self.class_weights,
            "regression_weights": self.regression_weights,
            "metrics": self.metrics,
        }
        with open(target, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return target

    def load(self, path: Optional[str] = None) -> bool:
        target = path or self.model_path
        if not os.path.exists(target):
            return False

        try:
            with open(target, "r", encoding="utf-8") as f:
                payload = json.load(f)
            self.classes = list(payload["classes"])
            self.feature_names = list(payload["feature_names"])
            self.feature_means = dict(payload["feature_means"])
            self.feature_stds = dict(payload["feature_stds"])
            self.class_weights = {k: list(v) for k, v in payload["class_weights"].items()}
            self.regression_weights = {k: list(v) for k, v in payload["regression_weights"].items()}
            self.metrics = dict(payload.get("metrics", {}))
            self.trained_at = payload.get("trained_at")
            self.n_samples = int(payload.get("n_samples", 0))
            return self.is_trained
        except Exception:
            return False

    def summary(self) -> Dict[str, Any]:
        return {
            "trained": self.is_trained,
            "algorithm": "Vision Classifier One-vs-Rest Ridge + Heuristique ISO 5565-1",
            "trained_at": self.trained_at,
            "n_samples": self.n_samples,
            "classes": self.classes,
            "metrics": self.metrics,
        }
