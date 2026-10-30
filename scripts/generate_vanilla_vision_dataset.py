"""
Générateur de dataset d'images synthétiques & augmentées de gousses de vanille.
Filière Vanille de Madagascar — Hazo Lova Agri-AI (IndabaX 2026).

Génère des représentations visuelles des 5 classes ISO 5565-1 :
1. Gourmet_Grade_A (noire Bourbon ébène luisante, reflet d'huile)
2. Standard_TK_Grade_B (brune chocolatée, souple)
3. Extraction_Grade_C (courte, fendue, rougeâtre)
4. Rejected_Immature (vanille verte récoltée prématurément bord-champ)
5. Defective_Mold (contamination fongique / mycélium poudreux)

Simule des conditions réelles bord-champ :
- Fonds d'inspection : tissu clair, table en bois de séchage, sac en toile de jute.
- Variations d'éclairage : plein soleil, ombre, lumière diffuse, reflets d'angle.
- Bruit de capteur smartphone et courbures naturelles des gousses.
"""

import csv
import math
import os
import random
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFilter

OUTPUT_DIR = "data/vision_dataset"
MANIFEST_PATH = os.path.join(OUTPUT_DIR, "manifest.csv")
SAMPLES_PER_CLASS = 80  # 80 x 5 = 400 images annotées


def _draw_background(bg_type: str, width: int = 256, height: int = 256) -> Image.Image:
    """Génère une surface d'arrière-plan texturée réaliste."""
    if bg_type == "fabric":
        # Fond tissu ou papier blanc d'inspection (légère variation)
        base = random.randint(236, 246)
        img = Image.new("RGB", (width, height), (base, base, base - random.randint(0, 4)))
    elif bg_type == "wood":
        # Table en bois de préparation / étuvage
        base_r = random.randint(155, 175)
        base_g = random.randint(115, 135)
        base_b = random.randint(75, 95)
        img = Image.new("RGB", (width, height), (base_r, base_g, base_b))
        draw = ImageDraw.Draw(img)
        # Veines du bois
        for _ in range(12):
            y = random.randint(0, height)
            color = (base_r - 18, base_g - 15, base_b - 12)
            draw.line([(0, y), (width, y + random.randint(-5, 5))], fill=color, width=random.randint(1, 3))
    else:  # "jute"
        # Sac en toile de jute / fibre naturelle
        base_r = random.randint(175, 195)
        base_g = random.randint(150, 170)
        base_b = random.randint(110, 130)
        img = Image.new("RGB", (width, height), (base_r, base_g, base_b))
        draw = ImageDraw.Draw(img)
        # Trame de tissage
        for x in range(0, width, 14):
            draw.line([(x, 0), (x, height)], fill=(base_r - 12, base_g - 12, base_b - 10), width=1)
        for y in range(0, height, 14):
            draw.line([(0, y), (width, y)], fill=(base_r - 12, base_g - 12, base_b - 10), width=1)

    return img


def _generate_pod_path(width: int = 256, height: int = 256, length_scale: float = 1.0) -> List[Tuple[float, float]]:
    """Génère les points de contrôle d'une gousse courbée naturelle."""
    start_x = random.randint(30, 60)
    start_y = random.randint(80, 170)
    total_len = random.randint(150, 190) * length_scale
    curve_amp = random.randint(-35, 35)

    points = []
    steps = 14
    for i in range(steps + 1):
        t = i / steps
        x = start_x + t * total_len
        # Courbure parabolique avec léger bruit
        y = start_y + curve_amp * math.sin(t * math.pi) + random.uniform(-2, 2)
        points.append((x, y))
    return points


def _draw_pod(
    img: Image.Image,
    label: str,
    points: List[Tuple[float, float]],
    pod_width: int = 16,
) -> None:
    """Dessine une gousse de vanille selon les spécifications physico-chimiques de son grade."""
    draw = ImageDraw.Draw(img)

    if label == "Gourmet_Grade_A":
        # Noire Bourbon profonde, ébène avec éclat
        r = random.randint(24, 38)
        g = random.randint(18, 30)
        b = random.randint(12, 22)
        color = (r, g, b)
    elif label == "Standard_TK_Grade_B":
        # Brune chocolatée / ambrée
        r = random.randint(85, 115)
        g = random.randint(55, 78)
        b = random.randint(28, 45)
        color = (r, g, b)
    elif label == "Extraction_Grade_C":
        # Rougeâtre / plus sèche / fendue
        r = random.randint(125, 155)
        g = random.randint(62, 85)
        b = random.randint(30, 50)
        color = (r, g, b)
    elif label == "Rejected_Immature":
        # Vanille verte récoltée avant étuvage (vert vif, olive, jaune-vert)
        sub_type = random.choice(["vivid", "olive", "yellow_green"])
        if sub_type == "vivid":
            color = (random.randint(50, 75), random.randint(135, 165), random.randint(45, 70))
        elif sub_type == "olive":
            color = (random.randint(70, 95), random.randint(110, 138), random.randint(35, 55))
        else:
            color = (random.randint(115, 140), random.randint(155, 180), random.randint(45, 68))
    else:  # Defective_Mold
        # Gousse brune ou noire porteuse de moisissure
        color = (random.randint(40, 75), random.randint(30, 55), random.randint(20, 40))

    # Corps de la gousse
    for i in range(len(points) - 1):
        draw.line([points[i], points[i + 1]], fill=color, width=pod_width)

    # Extrémités arrondies (pédoncule et pointe)
    r_cap = pod_width / 2.0
    p0 = points[0]
    p_end = points[-1]
    draw.ellipse([p0[0] - r_cap, p0[1] - r_cap, p0[0] + r_cap, p0[1] + r_cap], fill=color)
    draw.ellipse([p_end[0] - r_cap, p_end[1] - r_cap, p_end[0] + r_cap, p_end[1] + r_cap], fill=color)

    # Spécificités par grade :
    # 1. Gourmet A : Reflet spéculaire gras le long de la nervure (huiles essentielles)
    if label == "Gourmet_Grade_A":
        sheen_color = (r + 45, g + 40, b + 32)
        sheen_points = [(px, py - pod_width * 0.22) for px, py in points[2:-2]]
        for i in range(len(sheen_points) - 1):
            draw.line([sheen_points[i], sheen_points[i + 1]], fill=sheen_color, width=max(2, pod_width // 4))

    # 2. Extraction C : Gousse fendue longitudinalement (fente pâle)
    if label == "Extraction_Grade_C" and random.random() > 0.35:
        split_color = (r + 35, g + 25, b + 15)
        for i in range(3, len(points) - 3):
            draw.line([points[i], points[i + 1]], fill=split_color, width=2)

    # 3. Defective_Mold : Mycélium / plaques blanches et grises poudreuses
    if label == "Defective_Mold":
        n_patches = random.randint(4, 9)
        for _ in range(n_patches):
            idx = random.randint(2, len(points) - 3)
            cx, cy = points[idx]
            cx += random.uniform(-pod_width * 0.35, pod_width * 0.35)
            cy += random.uniform(-pod_width * 0.35, pod_width * 0.35)
            rx = random.randint(4, 9)
            ry = random.randint(3, 7)
            mold_color = (random.randint(215, 240), random.randint(215, 240), random.randint(210, 235))
            draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=mold_color)


def generate_dataset() -> None:
    """Génère l'ensemble du dataset d'entraînement synthétique avec manifest CSV."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    manifest_rows: List[Dict[str, Any]] = []

    classes = [
        ("Gourmet_Grade_A", 94.0, 98.0, 0.0, 5.0),
        ("Standard_TK_Grade_B", 82.0, 90.0, 0.0, 8.0),
        ("Extraction_Grade_C", 68.0, 76.0, 5.0, 15.0),
        ("Rejected_Immature", 18.0, 35.0, 0.0, 5.0),
        ("Defective_Mold", 42.0, 72.0, 45.0, 95.0),
    ]

    total_images = len(classes) * SAMPLES_PER_CLASS
    print(f"[*] Génération de {total_images} photos synthétiques dans {OUTPUT_DIR}...")

    img_counter = 0
    for label, min_mat, max_mat, min_mold, max_mold in classes:
        class_dir = os.path.join(OUTPUT_DIR, label)
        os.makedirs(class_dir, exist_ok=True)

        for i in range(SAMPLES_PER_CLASS):
            img_counter += 1
            bg_type = random.choice(["fabric", "wood", "jute"])
            img = _draw_background(bg_type)

            # Échelle de taille et épaisseur
            len_scale = 1.1 if label == "Gourmet_Grade_A" else (0.85 if label == "Extraction_Grade_C" else 1.0)
            pod_w = random.randint(14, 18) if label != "Extraction_Grade_C" else random.randint(10, 14)

            # Dessin de 1 à 2 gousses
            n_pods = 1 if random.random() > 0.35 else 2
            for _ in range(n_pods):
                points = _generate_pod_path(length_scale=len_scale)
                _draw_pod(img, label, points, pod_width=pod_w)

            # Flou très léger pour adoucir le tracé vectoriel
            img = img.filter(ImageFilter.GaussianBlur(radius=0.4))

            # Métriques cibles
            maturity = round(random.uniform(min_mat, max_mat), 1)
            mold_risk = round(random.uniform(min_mold, max_mold), 1)

            filename = f"{label.lower()}_{i+1:03d}.jpg"
            rel_path = os.path.join(label, filename)
            abs_path = os.path.join(class_dir, filename)

            img.save(abs_path, format="JPEG", quality=90)

            manifest_rows.append({
                "image_path": rel_path,
                "label": label,
                "maturity_pct": maturity,
                "mold_risk_pct": mold_risk,
                "background": bg_type,
            })

    # Écriture du manifest CSV
    with open(MANIFEST_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["image_path", "label", "maturity_pct", "mold_risk_pct", "background"])
        writer.writeheader()
        writer.writerows(manifest_rows)

    print(f"[OK] {total_images} images générées.")
    print(f"[OK] Manifest enregistré : {MANIFEST_PATH}")


if __name__ == "__main__":
    generate_dataset()
