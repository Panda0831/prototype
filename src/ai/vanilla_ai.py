import csv
import math
import os
import hashlib
from typing import Dict, Any, List, Optional

from src.ai.pricing_model import DEFAULT_MODEL_PATH, VanillaPricingModel
from src.ai.vision import analyze_lot_photo

class VanillaAIModel:
    """
    Modèle d\x27Intelligence Artificielle pour la filière Vanille de Madagascar (Hazo Lova AI).
    Combinaison d\x27évaluation normative (ISO 5565-1) et de Machine Learning (k-NN Pondéré)
    pour la prédiction de grade de qualité et l\x27estimation de prix équitable bord-champ.
    """
    def __init__(self, dataset_path: str = "data/madagascar_vanilla_quality_pricing.csv"):
        self.dataset_path = dataset_path
        self.data: List[Dict[str, Any]] = []
        self.pricing_model = VanillaPricingModel(DEFAULT_MODEL_PATH)
        if not self.pricing_model.load():
            print(
                " [!] Modèle de pricing local absent ou invalide : "
                "lancez `python train_vanilla_ai.py` (repli k-NN actif)."
            )
        elif self.pricing_model.is_trained:
            trained_at = self.pricing_model.trained_at or "date inconnue"
            print(
                f" [*] IA Vanille : modèle ridge local chargé "
                f"({self.pricing_model.n_samples} échantillons, entraîné le {trained_at})."
            )
        self.load_dataset()

    def load_dataset(self) -> None:
        """Charge le jeu de données officiel des marchés et récoltes de vanille."""
        if not os.path.exists(self.dataset_path):
            print(f" [!] Attention : Dataset {self.dataset_path} introuvable.")
            return

        with open(self.dataset_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    self.data.append({
                        "lot_id": row["lot_id"],
                        "region": row["region"],
                        "district": row["district"],
                        "bean_length_cm": float(row["bean_length_cm"]),
                        "moisture_pct": float(row["moisture_pct"]),
                        "vanillin_pct": float(row["vanillin_pct"]),
                        "mold_detected": int(row["mold_detected"]),
                        "maturity_pct": float(row["maturity_pct"]),
                        "quality_grade": row["quality_grade"],
                        "fair_farmgate_price_mga": float(row["fair_farmgate_price_mga"]),
                        "fob_export_price_usd": float(row["fob_export_price_usd"])
                    })
                except (ValueError, KeyError):
                    continue
        print(f" [*] IA Vanille : {len(self.data)} enregistrements réels chargés en mémoire.")

    def inspect_lot(
        self,
        district: str,
        bean_length_cm: float,
        moisture_pct: float,
        vanillin_pct: float,
        mold_detected: bool,
        maturity_pct: float,
        image_bytes: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        Analyse multidimensionnelle d\x27un lot de vanille.
        Retourne la classification du grade, le juste prix calculé par IA et l\x27explication.
        """
        hasher = hashlib.sha256()
        hasher.update(f"{district}:{bean_length_cm}:{moisture_pct}:{vanillin_pct}:{mold_detected}:{maturity_pct}".encode())
        if image_bytes:
            hasher.update(image_bytes)
        inspection_hash = hasher.hexdigest()

        vision = analyze_lot_photo(image_bytes) if image_bytes else None

        explanations = []
        is_green_crop = False
        is_vision_mold = False

        # Si une photo est fournie et exploitable, l'analyse d'image prime sur la déclaration
        if vision and vision.get("reliable"):
            vision_maturity = vision.get("estimated_maturity_pct")
            vision_green_ratio = vision.get("green_ratio", 0.0)
            vision_mold_risk = vision.get("mold_risk_pct", 0.0)
            vision_grade = vision.get("predicted_grade")

            # 1. Détection de vanille verte / cueillette prématurée
            if (
                vision_green_ratio >= 0.10
                or (vision_maturity is not None and vision_maturity < 68.0)
                or vision_grade == "Rejected_Immature"
            ):
                is_green_crop = True
                if vision_maturity is not None:
                    maturity_pct = min(maturity_pct, vision_maturity)
                explanations.append(
                    f"🚨 Détection IA Vision : Gousses vertes / cueillette prématurée détectée "
                    f"(ratio vert {vision_green_ratio*100:.1f}%, maturité mesurée {maturity_pct:.1f}%). "
                    f"Non conforme au standard d'exportation ISO 5565-1."
                )

            # 2. Détection de moisissure
            if vision_mold_risk >= 35.0 or vision_grade == "Defective_Mold":
                is_vision_mold = True
                explanations.append(
                    f"🚨 Détection IA Vision : Risque critique de moisissure ({vision_mold_risk:.1f}%). "
                    f"Lot exclu de la chaîne d'exportation."
                )

            # 3. Confirmation visuelle d'authenticité et brillance
            if not is_green_crop and not is_vision_mold:
                ebony = vision.get("dark_ebony_ratio", 0.0)
                sheen = vision.get("sheen_index", 0.0)
                if ebony >= 0.35 and sheen >= 0.04:
                    explanations.append(
                        f"✨ Contrôle IA Vision : Gousses Bourbon ébène ({ebony*100:.1f}%) "
                        f"avec reflet spéculaire d'huile optimal (sheen {sheen*100:.1f}%)."
                    )
        elif vision and not vision.get("reliable"):
            explanations.append(
                "Photo non exploitable pour l'analyse d'image : " + ", ".join(vision.get("flags", []))
            )

        # Classification du grade selon ISO 5565-1 et la vision
        if mold_detected or is_vision_mold:
            grade = "Defective_Mold"
            confidence = 0.99
            explanations.append("Présence critique de moisissure détectée : lot non conforme pour export.")
        elif is_green_crop or maturity_pct < 70.0 or moisture_pct > 40.0:
            grade = "Rejected_Immature"
            confidence = 0.98 if is_green_crop else 0.96
            if not is_green_crop:
                explanations.append("Vanille verte récoltée prématurément (maturité < 70% ou humidité > 40%).")
        elif bean_length_cm >= 16.0 and moisture_pct >= 30.0 and vanillin_pct >= 1.8:
            grade = "Gourmet_Grade_A"
            confidence = 0.95
            explanations.append("Gousses longues (>=16cm), taux de vanilline supérieur à 1.8% et humidité optimale.")
        elif bean_length_cm >= 14.0 and vanillin_pct >= 1.5:
            grade = "Standard_TK_Grade_B"
            confidence = 0.92
            explanations.append("Qualité standard TK (14-16cm) conforme aux standards d'exportation européens.")
        else:
            grade = "Extraction_Grade_C"
            confidence = 0.89
            explanations.append("Courtes gousses ou gousses fendues réservées à l'extraction industrielle.")

        if self.pricing_model.is_trained:
            prediction = self.pricing_model.predict(
                district=district,
                bean_length_cm=bean_length_cm,
                moisture_pct=moisture_pct,
                vanillin_pct=vanillin_pct,
                maturity_pct=maturity_pct,
                mold_detected=bool(mold_detected or is_vision_mold),
            )
            estimated_price_mga = prediction["fair_farmgate_price_mga"]
            estimated_fob_usd = prediction["fob_export_price_usd"]
            pricing_engine = "Ridge Regression (entraînée localement)"
        else:
            estimated_price_mga, estimated_fob_usd = self._predict_prices(
                bean_length_cm, moisture_pct, vanillin_pct, maturity_pct, int(mold_detected or is_vision_mold), district
            )
            pricing_engine = "k-NN pondéré (repli)"

        # Ajustement des prix en cas de rejet (prix bord-champ vanille verte ou lot moisi)
        if grade == "Rejected_Immature":
            estimated_price_mga = min(estimated_price_mga, 42000.0)
            estimated_fob_usd = min(estimated_fob_usd, 38.0)
        elif grade == "Defective_Mold":
            estimated_price_mga = 0.0
            estimated_fob_usd = 0.0

        return {
            "inspection_hash": inspection_hash,
            "district": district,
            "quality_grade": grade,
            "confidence_score": confidence,
            "maturity_pct": maturity_pct,
            "estimated_fair_price_mga_per_kg": round(estimated_price_mga, -2),
            "estimated_fob_export_usd_per_kg": round(estimated_fob_usd, 1),
            "pricing_engine": pricing_engine,
            "iso_compliance": "ISO 5565-1 (Vanilla Planifolia)",
            "explanations": explanations,
            "vision": vision,
            "status": "APPROVED_FOR_BLOCKCHAIN" if grade in ["Gourmet_Grade_A", "Standard_TK_Grade_B", "Extraction_Grade_C"] else "REJECTED"
        }

    def _predict_prices(
        self,
        length: float,
        moisture: float,
        vanillin: float,
        maturity: float,
        mold: int,
        target_district: str,
        k: int = 5
    ) -> tuple[float, float]:
        if not self.data:
            return (150000.0, 150.0)

        scored_neighbors = []
        for row in self.data:
            district_penalty = 0.0 if row["district"].lower() == target_district.lower() else 0.5
            d_len = (row["bean_length_cm"] - length) / 10.0
            d_moist = (row["moisture_pct"] - moisture) / 20.0
            d_van = (row["vanillin_pct"] - vanillin) / 1.0
            d_mat = (row["maturity_pct"] - maturity) / 30.0
            d_mold = abs(row["mold_detected"] - mold) * 2.0

            dist = math.sqrt(d_len**2 + d_moist**2 + d_van**2 + d_mat**2 + d_mold**2 + district_penalty**2)
            scored_neighbors.append((dist, row["fair_farmgate_price_mga"], row["fob_export_price_usd"]))

        scored_neighbors.sort(key=lambda x: x[0])
        top_k = scored_neighbors[:k]

        weights = [1.0 / (d + 1e-5) for d, _, _ in top_k]
        sum_w = sum(weights)

        avg_price_mga = sum(w * p for w, (_, p, _) in zip(weights, top_k)) / sum_w
        avg_fob_usd = sum(w * f for w, (_, _, f) in zip(weights, top_k)) / sum_w

        return avg_price_mga, avg_fob_usd

vanilla_ai = VanillaAIModel()
