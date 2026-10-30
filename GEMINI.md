# 🧠 Mémoire Technique : Projet Hazo Lova

Ce document sert de "cache" et de guide de référence pour maintenir la continuité du développement de l'infrastructure blockchain Hazo Lova (Madagascar 2035).

## 🚀 État Actuel du Projet (~75%)
L'infrastructure est totalement opérationnelle. Le module **Foncier** est le plus abouti et sert de modèle pour les autres cas d'usage.

## 🛠 Architecture & Tech Stack
- **Backend** : FastAPI (Python 3.13), SQLAlchemy (SQLite).
- **Mobile** : React Native (Expo).
- **Blockchain** : Custom implementation (PoW, Merkle Trees).
- **Cryptographie** : ECDSA (secp256k1) pour les signatures, Bcrypt pour les mots de passe.
- **Persistence** : Fichiers Pickle et JSON dans `data/persistence/` (géré par `src/utils/persistence.py`).

## 📐 Algorithmes Clés
1. **Module Agriculture (Traçabilité Multi-Produits)** : 
   - Localisation : `src/use_cases/produitsAgricoles.py`.
   - **Logique** : Enregistrement de récoltes (Vanille, Girofle, Café, etc.) sur la blockchain avec calcul de trajet optimal via A*.
   - **Routes** : `/api/agriculture/harvest`, `/api/agriculture/transport`.
2. **A* (Réseau & Logistique)** : Routage entre les 119 districts. Utilisé pour optimiser le transport des produits agricoles.

## 📜 Workflow Foncier (Le Standard)
1. **Soumission** : Le citoyen envoie une demande via `/api/land/request`.
2. **Approbation** : L'admin valide via `/api/land/approve/{id}`.
3. **Génération d'ID** : Le système génère un ID unique : `HZL-LND-[TIMESTAMP]-[ID]`.
4. **Blockchain** : Inscription automatique et **Auto-Mining** immédiat pour la visibilité.
5. **Mutation** : Transfert via `/api/land/transfer` avec vérification de propriété par Union-Find.

## 🔑 Règles de Sécurité & Comparaison
- **Clés Publiques** : Toujours utiliser `normalize_key()` (dans `land_routes.py`) pour comparer les clés. Cela supprime parenthèses, guillemets et espaces pour éviter les erreurs de formatage mobile/backend.
- **Signatures** : Dans cette phase, `SIG_MOBILE_DEMO` est acceptée pour fluidifier les tests mobiles.

## 📅 Prochaines Étapes (Sprint Final)
1. **Module Agriculture** : Traçabilité de la vanille (Lier A* et Blockchain).
2. **Module Éducation** : Certification des diplômes (Merkle Proofs).
3. **Optimisation** : Benchmarks comparatifs Baseline vs IA.

---
*Note à mon futur moi : Toujours vérifier que l'état est chargé au démarrage via `src/api/instances.py`. Ne pas oublier que les données en RAM sont volatiles, la persistence disque est la source de vérité.*
