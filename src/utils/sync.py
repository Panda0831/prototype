from src.blockchain.transaction import SecteurActivite
from src.utils.crypto import Crypto
from src.api.instances import parcel_owner_map

def synchronize_state(block, instances):
    """
    Met à jour l'état de l'application en fonction des transactions d'un nouveau bloc.
    Centralise la logique métier déclenchée par la blockchain.
    """
    agriculture_manager = instances.get("agriculture_manager")
    foncier_uf = instances.get("foncier_uf")
    pending_land_requests = instances.get("pending_land_requests")
    diploma_manager = instances.get("diploma_manager")
    pending_diploma_requests = instances.get("pending_diploma_requests")
    microfinance_manager = instances.get("microfinance_manager")

    print(f" [SYNC] Synchronisation de l'état pour le bloc #{block.index}")

    for tx in block.transactions:
        secteur = tx.secteur
        donnees = tx.donnees
        
        # ... (Agriculture logic unchanged)
        # 1. AGRICULTURE
        if secteur == SecteurActivite.PRODUITS_AGRICOLES:
            if isinstance(donnees, dict):
                # Cas 1: Enregistrement Récolte (contient 'product_type')
                if "product_type" in donnees and "id" in donnees:
                    from src.use_cases.produitsAgricoles import AgriculturalLot
                    lot = AgriculturalLot(**donnees)
                    agriculture_manager.lots[lot.id] = lot
                    print(f" [SYNC] Lot agricole enregistré: {lot.id}")
                
                # Cas 2: Vente Lot
                elif donnees.get("action") == "SALE":
                    lot_id = donnees.get("lot_id")
                    if lot_id in agriculture_manager.lots:
                        lot = agriculture_manager.lots[lot_id]
                        
                        # Fix: Ensure owner_id is a normalized string
                        dest = tx.destinataire
                        if isinstance(dest, tuple):
                             normalized_owner = "".join([Crypto.normalize_key(part) for part in dest])
                        else:
                             normalized_owner = Crypto.normalize_key(dest)
                             
                        lot.owner_id = normalized_owner
                        lot.status = "VENDU"
                        lot.traceability.append({
                            "action": "VENDU",
                            "acheteur": normalized_owner,
                            "prix": donnees.get("price"),
                            "timestamp": tx.horodatage
                        })
                        print(f" [SYNC] Lot {lot_id} vendu à {normalized_owner}")

                # Cas 3: Transport
                elif donnees.get("action") == "TRANSPORT":
                    lot_id = donnees.get("lot_id")
                    if lot_id in agriculture_manager.lots:
                        lot = agriculture_manager.lots[lot_id]
                        lot.status = "EN_TRANSIT"
                        lot.traceability.append({
                            "action": "TRANSPORT_OPTIMISE",
                            "destination": tx.destinataire.replace("CENTRE_COLLECTE_", ""),
                            "chemin": donnees.get("chemin"),
                            "timestamp": tx.horodatage
                        })
                        print(f" [SYNC] Lot {lot_id} en cours de transport")

        # 2. FONCIER
        elif secteur == SecteurActivite.FONCIER:
            if not isinstance(donnees, dict):
                continue
            parcel_id = donnees.get("parcel_id")
            action = donnees.get("action")
            
            # Normalise la clé
            dest = tx.destinataire
            if isinstance(dest, tuple):
                normalized_owner = "".join([Crypto.normalize_key(part) for part in dest])
            else:
                normalized_owner = Crypto.normalize_key(dest)
            
            if action == "REGISTRATION_APPROVED":
                foncier_uf.bind(normalized_owner, parcel_id)
                parcel_owner_map[parcel_id] = normalized_owner
                
                # Mise à jour du statut des demandes locales
                if pending_land_requests:
                    for req in pending_land_requests:
                        # Le parcel_id généré contient le request_id à la fin
                        req_id_str = str(req.get("id"))
                        if parcel_id.endswith(f"-{req_id_str}"):
                             req["status"] = "APPROVED"
                             req["generated_parcel_id"] = parcel_id
                print(f" [SYNC] Titre foncier validé: {parcel_id} lié à {normalized_owner}")

            elif action == "TRANSFER":
                parcel_owner_map[parcel_id] = normalized_owner
                print(f" [SYNC] Mutation foncière: {parcel_id} transféré à {normalized_owner}")

        # 3. ÉDUCATION
        elif secteur == SecteurActivite.DIPLOME:
            if not isinstance(donnees, dict):
                continue
            student_id = tx.destinataire
            # Recréation de l'ID diplôme
            year = donnees.get('year')
            diploma_id = f"DIP-{student_id}-{year}"
            diploma_manager.diplomas[diploma_id] = donnees
            
            # Mise à jour du statut des demandes locales
            if pending_diploma_requests is not None:
                for req in pending_diploma_requests:
                    if req.get("student_id") == student_id and req.get("year") == year:
                        req["status"] = "APPROVED"
                        req["diploma_id"] = diploma_id
            
            print(f" [SYNC] Diplôme certifié pour {student_id}")

        # 4. MICROFINANCE
        elif secteur == SecteurActivite.MICROFINANCE:
            if isinstance(donnees, dict):
                # Cas 1: Demande de transfert (Send)
                if donnees.get("type") == "MICRO_TRANSFER_REQUEST":
                    transfer_id = donnees.get("transfer_id")
                    # On ajoute à la liste des attentes si pas déjà présent
                    if not any(t["id"] == transfer_id for t in microfinance_manager.pending_transfers):
                        microfinance_manager.pending_transfers.append({
                            "id": transfer_id,
                            "sender_id": tx.expediteur,
                            "receiver_id": tx.destinataire,
                            "amount": donnees.get("amount"),
                            "description": donnees.get("description"),
                            "status": "PENDING",
                            "timestamp": tx.horodatage
                        })
                        print(f" [SYNC] Nouvelle demande de transfert {transfer_id} pour {tx.destinataire}")

                # Cas 2: Confirmation de transfert (Accept)
                elif donnees.get("type") == "MICRO_TRANSFER":
                    transfer_id = donnees.get("transfer_id")
                    # On retire de la liste des transferts en attente
                    original_len = len(microfinance_manager.pending_transfers)
                    microfinance_manager.pending_transfers = [
                        t for t in microfinance_manager.pending_transfers if t["id"] != transfer_id
                    ]
                    if len(microfinance_manager.pending_transfers) < original_len:
                        print(f" [SYNC] Micro-transfert {transfer_id} confirmé et retiré des attentes")

def sync_all(blockchain, instances):
    """
    Réinitialise et resynchronise tout l'état de l'application depuis le début de la blockchain.
    """
    # Réinitialisation Agriculture
    instances.get("agriculture_manager").lots = {}
    
    # Réinitialisation Foncier
    instances.get("foncier_uf").parent = {}
    instances.get("foncier_uf").rang = {}
    pending_land_requests = instances.get("pending_land_requests")
    if pending_land_requests:
        for req in pending_land_requests:
            req["status"] = "PENDING"
            
    # Réinitialisation Éducation
    instances.get("diploma_manager").diplomas = {}
    pending_diploma_requests = instances.get("pending_diploma_requests")
    if pending_diploma_requests:
        for req in pending_diploma_requests:
            req["status"] = "PENDING"
            
    # Réinitialisation Microfinance
    instances.get("microfinance_manager").pending_transfers = []

    # Synchronisation bloc par bloc
    for block in blockchain.chaine:
        synchronize_state(block, instances)
