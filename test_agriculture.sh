#!/bin/bash

# Script de test pour le module AGRICULTURE
# Assurez-vous que le serveur est lancé : uvicorn src.api.main:app --reload

BASE_URL="http://localhost:8000"

echo "=== 1. TEST RÉCOLTE (Harvest) ==="
HARVEST_RESPONSE=$(curl -s -X POST "$BASE_URL/api/agriculture/harvest" \
     -H "Content-Type: application/json" \
     -d '{
           "owner_id": "PUB_KEY_JEAN_SAMBAVA",
           "product_type": "Vanille",
           "district": "Sambava",
           "weight": 50.5,
           "quality": "Premium"
         }')
echo $HARVEST_RESPONSE | jq .
LOT_ID=$(echo $HARVEST_RESPONSE | jq -r .lot.id)

echo -e "\n=== 2. TEST TRANSPORT OPTIMISÉ (A*) ==="
if [ "$LOT_ID" != "null" ]; then
    echo "Calcul du trajet optimal pour le lot $LOT_ID vers Antananarivo..."
    curl -s -X POST "$BASE_URL/api/agriculture/transport" \
         -H "Content-Type: application/json" \
         -d "{
               \"lot_id\": \"$LOT_ID\",
               \"destination\": \"Antananarivo\"
             }" | jq .
else
    echo "Erreur: LOT_ID est nul, impossible de tester le transport."
fi

echo -e "\n=== 3. CONSULTATION DU LOT ==="
curl -s -X GET "$BASE_URL/api/agriculture/lot/$LOT_ID" | jq .

echo -e "\n=== 4. LISTE DE TOUS LES LOTS ==="
curl -s -X GET "$BASE_URL/api/agriculture/all" | jq .

echo -e "\n=== 5. VÉRIFICATION BLOCKCHAIN (Dernier Bloc) ==="
curl -s -X GET "$BASE_URL/api/blockchain/blocks" | jq '.[-1]'

echo -e "\nTests Agriculture terminés !"
