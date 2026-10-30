# Hazo Lova - Blockchain Madagascar 2035

Infrastructure blockchain décentralisée optimisée pour les enjeux critiques de Madagascar.

## 🛠 Stack Technique
- **Backend :** FastAPI (Python 3.13), SQLAlchemy (SQLite) - Logique métier, Blockchain et Algorithmes.
- **Frontend Web :** React / Vite (TypeScript) - Interface web moderne.
- **Frontend Mobile :** React Native (Expo) - Application mobile native.
- **Cryptographie :** ECDSA (secp256k1) et Bcrypt.
- **Persistence :** Fichiers Pickle et JSON dans `data/persistence/`.
- **Algorithmes :**
  - **A* :** Optimisation des flux logistiques (traçabilité multi-produits).
  - **Q-Learning :** Sélection intelligente des validateurs (économie d'énergie).
  - **Union-Find :** Gestion de l'intégrité foncière.

## 🧠 Entraînement local de l'IA Vanille

Le modèle de pricing (régression ridge multi-cibles) est entraîné localement
sur `data/madagascar_vanilla_quality_pricing.csv` :

```bash
python train_vanilla_ai.py
```

Le script affiche les métriques train/test (MAE, RMSE, R², MAPE) et sauvegarde
les poids dans `data/models/vanilla_pricing_model.json`. L'API expose ces
métriques via `GET /api/agriculture/vanilla/model-info`.

## 🌍 Modèle de marché vanille (données ONU réelles)

La série de prix n'est plus simulée : elle vient des exportations réelles de
vanille malgache (UN Comtrade, HS 0905.10) et du taux de change officiel
(Banque mondiale, `PA.NUS.FCRF`).

```bash
# 1. Télécharger / rafraîchir la source (écrit data/sources/)
python scripts/fetch_vanilla_market_data.py

# 2. Entraîner le modèle de marché local
python train_vanilla_market.py
```

Résultat (2015-2025, validation leave-one-year-out) : **R² = 0,763**,
**MAE = 57,8 $/kg**, **MAPE = 28,4 %**. Dernier point réel : **2025 = 44,84 $/kg FOB**.
L'API l'expose via `GET /api/agriculture/vanilla/market-info`.

> **Limite importante** : ce modèle donne le **niveau de marché** (FOB), pas la
> prime de qualité d'un lot. Aucun dataset public ne fournit des mesures
> physiques par lot (calibre, humidité, vanilline) avec leur prix. Le modèle
> qualité-par-lot (`pricing_model.py`) reste donc entraîné sur le jeu local de
> 1000 lots, lui-même calibré sur le marché de 2021-2022. Le recalibrer sur le
> prix 2025 diviserait les prix affichés par ~5.

## 📸 Fil rouge du prototype

`photo bord-champ → inspection ISO 5565-1 + juste prix → passeport blockchain → routage A* → dashboard Data Science`

- `POST /api/agriculture/vanilla/inspect` : accepte `image_base64` (data URL ou base64, max 5 Mo). La photo entre dans le hash d'inspection et passe par `src/ai/vision.py` : ratios brun/vert, patches clairs suspects, netteté, maturité estimée et risque de moisissure. C'est de la **vision classique (colorimétrie + texture)**, pas un réseau de neurones : les indices sont des contrôles, jamais un remplacement des mesures ISO.
- `POST /api/agriculture/vanilla/seal` : mine immédiatement le passeport dans un bloc.
- `GET /api/agriculture/vanilla/passport/{hash}` : vérification publique (exportateur, sans compte).
- `GET /api/agriculture/vanilla/dashboard-data` : agrégats réels du dataset (1000 lots) + série de marché ONU, sans données codées en dur.

Côté web, l'onglet **Agri-AI / Data Science** regroupe le diagnostic, le scellage, la vérification de passeport et la Figure Data Science (prix, grades, volumes, A* Sambava → Toamasina, certification).

## 📂 Structure du Projet
- `src/blockchain/` : Cœur du protocole blockchain (PoW, Merkle Trees).
- `src/api/` : API REST FastAPI (Point d'entrée unique).
- `interfaces/web/` : Application Web React + Vite.
- `interfaces/mobile/` : Application Mobile React Native (Expo).

## 🚀 Installation & Lancement

### 1. Backend (FastAPI)
Il est recommandé d'utiliser **Conda** pour gérer l'environnement virtuel avec Python 3.13.

```bash
# 1.1 Créer l'environnement virtuel Conda
conda create -n hazolova python=3.13 -y

# 1.2 Activer l'environnement
conda activate hazolova

# 1.3 Installer les dépendances Python
pip install -r requirements.txt

# 1.4 Lancer le serveur backend
uvicorn src.api.main:app --reload
```

### 2. Frontend Web (Vite)
```bash
# 2.1 Aller dans le répertoire web
cd interfaces/web

# 2.2 Installer les dépendances Node.js
npm install

# 2.3 Lancer le serveur de développement
npm run dev
```

### 3. Frontend Mobile (Expo)
```bash
cd interfaces/mobile
npm install
npm start
```
# prototype
