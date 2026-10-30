# 📝 TODO — Hazo Lova Agri-AI (IndabaX Madagascar 2026)

Feuille de route du prototype présenté dans `Dossier_Candidature_HazoLova_IndabaX_2026.pdf`.
Objectif : démontrer la chaîne complète **Photo → Analyse IA ISO 5565 → Passeport blockchain → Routage A\* → Export**.

Légende : `[x]` fait, `[ ]` à faire.

---

## ✅ 0. Socle déjà en place

- [x] **Données réelles** : `data/madagascar_vanilla_quality_pricing.csv` (1000 lots, SAVA / Analanjirofo / Diana).
- [x] **Données PAM/WFP** : `data/wfp_food_prices_mdg.csv` importé (prix réels en MGA).
- [x] **IA Vanille** (`src/ai/vanilla_ai.py`) : classification ISO 5565-1 (Gourmet A / TK B / Extraction C / Immature / Moisi) + pricing + hash d'inspection.
- [x] **Modèle de pricing entraîné localement** (`src/ai/pricing_model.py`, `train_vanilla_ai.py`) : régression ridge multi-cibles, split 80/20, R² = 0,883, MAE = 18 002 MGA/kg (**−68 % d'erreur** vs prix moyen), poids persistés dans `data/models/vanilla_pricing_model.json`.
- [x] **API Agriculture** : `harvest`, `transport` (A\*), `sell`, `accept-sale`, `lot`, `all`.
- [x] **API Agri-AI** : `POST /vanilla/inspect`, `POST /vanilla/seal` (minage immédiat du passeport), `GET /vanilla/dashboard-data`.
- [x] **Mobile** : onglet Scanner IA (presets Gourmet / Standard / Immature), suivi des lots, transport A\*, récolte, vente.
- [x] **Web** : module Agriculture (récolte, suivi, logistique A\*, notifications) + carte « Modèle IA entraîné localement » (MAE, R², MAPE, date) alimentée par `GET /vanilla/model-info`.
- [x] **Tests** : `tests/unit/test_vanilla_ai.py` (métriques holdout, cohérence des prix, sauvegarde/rechargement, règles ISO + hash) — suite complète 39/39.
- [x] **Graphe 119 districts** opérationnel pour A\*.
- [x] **Recentrage vanilla** : routes Foncier et Éducation supprimées de l'API ; écrans web/mobile de ces modules, du Mineur, du Registre et d'Algo supprimés ; navigation réduite à **Tableau + Vanille** ; services API nettoyés ; scripts debug/obsolètes (9 fichiers) supprimés.
- [x] **Données factices retirées** du dashboard (réputation, nombre de nodes) au profit de métriques réelles : blocs, lots, volume, R²/MAE du modèle local.

---

## 🌍 1 bis. Données réelles internet — modèle de marché

- [x] **Source ONU téléchargée** : `scripts/fetch_vanilla_market_data.py` récupère UN Comtrade (HS 0905.10, exportations Madagascar 2015-2025) et le taux de change Banque mondiale. Sortie : `data/sources/un_comtrade_vanilla_madagascar.csv` (457 lignes, 11 années).
- [x] **Modèle de marché local** (`src/ai/market_model.py` + `train_vanilla_market.py`) : ridge sur log(prix FOB), features année/volume/FX, validation leave-one-year-out — **R² 0,763, MAE 57,8 $/kg, MAPE 28,4 %**.
- [x] **API & dashboard** : `GET /vanilla/market-info` + bloc `market` dans `dashboard-data`, carte « Marché réel » dans l'onglet Data Science (série 2015-2025, dernier prix 44,84 $/kg en 2025).
- [ ] **Calibration du prix par lot sur 2025** : décision à prendre — diviserait les prix actuels par ~5 (Gourmet ~250 000 → ~50 000 MGA/kg), donc à valider avant de changer la démo.
- [x] **Analyse d'existence de datasets publics ouverts** :
  - Macro/marché : ✅ UN Comtrade + WFP disponibles et intégrés.
  - Micro physico-chimie & photos de gousses étiquetées : ❌ Aucune base publique mondiale existante.
  - Décision : construction d'un double dataset propriétaire (tabulaire enrichi + images synthétiques/augmentées).

---

## 🔬 1 ter. Construction de Datasets & Entraînement IA (Double Axe)

- [ ] **Axe A — Dataset Tabulaire Multi-Districts Enrichi** (`scripts/build_vanilla_dataset.py`) :
  - Générer un jeu de données étendu (3 000 à 5 000 lots) couvrant les bassins clés (SAVA, Analanjirofo, Diana) et les 119 districts malgaches.
  - Respect strict des distributions physico-chimiques ISO 5565-1 (calibre, humidité 30-38%, vanilline $\ge 1.8\%$, maturité).
  - Corrélation avec les cours réels UN Comtrade et décote de transport A\* par district.
  - Entraînement multi-modèles (`train_vanilla_ai.py`) : classification de grade ISO et pricing équitable (Ridge/k-NN).
- [x] **Axe B — Dataset d'Images & Vision par Ordinateur Entraînée** (`scripts/generate_vanilla_vision_dataset.py`) :
  - Générer par script Pillow des représentations d'échantillons de gousses pour chaque classe :
    - Gourmet Grade A (noire/brun profond luisante)
    - Standard TK Grade B (brune, plus fine)
    - Extraction Grade C (courte, fendue, rougeâtre)
    - Cueillette Immature (vert clair/jaune, cueillette prématurée)
    - Moisi (taches blanchâtres/grises de mycélium)
  - Variabilité réelle : conditions de lumière bord-champ, bruit capteur smartphone, orientations, fonds multiples (bois, jute, tissu blanc).
  - Entraîner un modèle de classification de vision léger (`train_vanilla_vision.py`) : **98,8% d'accuracy, MAE maturité 6,19%, MAE moisissure 10,16%**, persisté dans `data/models/vanilla_vision_model.json`.

## 🚨 Priorité Immédiate : Calibrage IA Vision & Détection de Vanille Verte (Anti-fraude)

- [x] **Détection colorimétrique élargie du vert** (`src/ai/vision.py`) :
  - Modèle HSV/RGB prenant en compte toutes les teintes de vanille verte récoltée bord-champ (vert vif, vert olive, vert-jaune).
  - Recalibrage de la courbe de maturité : gousses vertes $\rightarrow$ maturité $15\text{--}35\%$, ratio vert prédominant.
- [x] **Priorité absolue de la vision sur le formulaire déclaratif** (`src/ai/vanilla_ai.py`) :
  - Si l'analyse d'image détecte de la vanille verte (`green_ratio \ge 0.10` ou maturité visuelle $< 65\%$ ou `predicted_grade == Rejected_Immature`), **overrider la saisie manuelle** :
    - Classification immédiate en **`Rejected_Immature`** (statut `REJECTED`).
    - Décote du prix au tarif bord-champ vanille verte immature (~25 000 à 42 000 MGA/kg) au lieu du tarif Gourmet.
    - Explication d'alerte explicite : *"🚨 Détection IA Vision : Gousses vertes / cueillette prématurée détectée..."*
- [x] **Détection des gousses moisies par vision** :
  - Si `mold_risk_pct \ge 35\%` ou `predicted_grade == Defective_Mold`, surclasser en `Defective_Mold` (statut `REJECTED`, prix = 0 MGA).
- [x] **Synchronisation UI Mobile & Web** :
  - Actualiser les indicateurs AR et les paramètres saisis dès que la vision détecte une anomalie (HUD AR mobile et panneau d'inspection web).
- [x] **Tests unitaires de robustesse** (`tests/unit/test_vision.py`) :
  - Suite enrichie à 10/10 tests unitaires validant toutes les nuances de vert, fonds réalistes, moisissure et certification de brillance.

## 🔴 1. Backend / IA — Fonctionnalités Photo & Passeport

- [x] **Prix réels** : `dashboard-data` agrège désormais le CSV vanille (1000 lots) — courbe bord-champ par tranches de 100 lots, prix/volumes par région, distribution des grades.
- [x] **Photo dans le passeport** : `POST /vanilla/inspect` et `/vanilla/seal` acceptent `image_base64` (data URL ou base64 brut, max 5 Mo), la photo entre dans `inspection_hash` et son empreinte SHA-256 est retournée (`image_sha256`).
- [x] **Analyse d'image locale** (`src/ai/vision.py`) : ratios brun/vert, patches clairs suspects, netteté, maturité estimée, risque de moisissure, alertes photo (sombre/floue/gousse absente). 100% fonctionnel sans dépendance externe.
- [x] **Vérification publique du passeport** : `GET /vanilla/passport/{hash}` renvoie le lot, le grade, le prix et le bloc de certification avec photo, sans authentification.
- [x] **Tests unitaires validés** : `tests/unit/test_vanilla_ai.py`, `test_vision.py`, `test_market_model.py` (12/12 passés).
- [ ] **Ré-entraînement documenté** : noter dans le README/mémoire la commande `python train_vanilla_ai.py` et les métriques obtenues.
- [ ] **Script de démo** : mettre à jour `test_agriculture.sh` avec le parcours inspect (photo) → seal → passport → dashboard-data → transport.

## 🟠 2. Web — Dashboard Data Science (moitié droite de la Figure)

- [x] **Nouvel onglet « Agri-AI / Data Science »** (composant `interfaces/web/src/VanillaLab.tsx`) :
  - [x] courbe des prix bord-champ (MGA) via `SimpleChart`, agrégée du dataset réel,
  - [x] distribution des grades qualité (5 catégories),
  - [x] volumes et prix moyens par région (SAVA / Analanjirofo / Diana),
  - [x] chemin A\* **Sambava → Port de Toamasina** + distance km (472,5 km mesurés),
  - [x] bloc de certification : hash transaction, index bloc, validateur.
- [x] **Capture & Upload Photo Web** : téléversement direct de photos bord-champ avec aperçu, diagnostic IA instantané et bouton « Sceller sur la blockchain ».
- [x] **Vérification publique d'un passeport** par hash depuis le web (grade, prix, photo scellée, bloc).
- [ ] Afficher le **passeport numérique** d'un lot (hash, grade, prix, bloc) directement dans la carte de suivi.

## 🟡 3. Mobile — Capture Caméra & Réalité Augmentée (Figure 2 gauche)

- [x] **Installation dépendance caméra** : `expo-image-picker` installé dans `interfaces/mobile/package.json`.
- [x] **Raccordement déclencheur photo réel** : branché `launchCameraAsync` / `launchImageLibraryAsync` sur le bouton de capture dans `AgriScreen.tsx`.
- [x] **Envoi de la photo réelle à l'API** : passage de la photo capturée en `image_base64` à `inspectVanilla`, prévisualisation en arrière-plan du viseur et diagnostic de vision en direct.
- [x] **Affichage AR Live HUD** : Réticule vert, indicateurs ISO 5565-1, maturité %, Grade Gourmet, Prix équitable (250 000 MGA) fidèle au dossier.
- [x] **Presets Échantillons Réels** : appels dynamiques à `POST /vanilla/inspect` (Gourmet, TK, Immature).
- [ ] **QR code du passeport** partageable (exportateur / contrôleur).

## 🔵 4. Benchmarks & crédibilité (Phase 4 du projet)

- [ ] **Benchmark pricing** : ridge entraîné vs k-NN pondéré vs prix moyen collecteur (écart en % sur le dataset).
- [ ] **Benchmark Q-Learning vs sélection aléatoire** : énergie/validations économisées (graphique).
- [ ] **Benchmark A\*** : distance/temps SAVA → Toamasina vs itinéraire naïf.
- [ ] Générer les figures dans `docs/diagrams/` pour le mémoire et la présentation.

## 🟣 5. Présentation & livrables

- [ ] Mettre à jour `docs/ETAT_AVANCEMENT_PROJET.txt` (date, modules Agri-AI terminés).
- [ ] Scénario de démo bout-en-bout écrit : récolte → scan → scellement → transport → vente.
- [ ] Captures d'écran finales mobile + web pour la Figure du dossier.
- [ ] Vérifier la cohérence du PDF de candidature avec le prototype réellement livré.

---

## ⏭️ Prochaine étape recommandée

1. Raccorder `expo-image-picker` dans `AgriScreen.tsx` pour permettre la prise de photo en direct sur le smartphone.
2. Créer le script de construction du dataset étendu et d'images synthétiques pour l'entraînement.

---

_Dernière mise à jour : Vendredi 30 Octobre 2026_
