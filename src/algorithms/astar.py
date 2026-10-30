from src.models.heap import TasBinaire


class AStar:
    def __init__(self, graphe):
        """
        :param graphe: Instance de DistrictsGraph.
        """
        self.graphe = graphe
        # chercher
        # cherhcher

    def chercher(self, id_depart, id_arrivee):
        """
        Trouve le chemin optimal entre deux districts.

        :return: Tuple (chemin_ids, distance_totale) ou (None, 0) si aucun chemin.
        """
        if (
            id_depart not in self.graphe.districts
            or id_arrivee not in self.graphe.districts
        ):
            return None, 0

        # Initialisation
        frontiere = TasBinaire()
        frontiere.inserer(id_depart, 0)

        provenance = {id_depart: None}
        cout_actuel = {id_depart: 0}

        while not frontiere.est_vide():
            # Extraire le district avec le plus petit score f = g + h
            res = frontiere.extraire_min()
            if not res:
                break
            priorite, actuel_id = res

            # Si on est arrivé
            if actuel_id == id_arrivee:
                return self._reconstruire_chemin(provenance, id_arrivee), cout_actuel[
                    id_arrivee
                ]

            # Explorer les voisins
            for voisin_id, distance_segment in self.graphe.obtenir_voisins(actuel_id):
                nouveau_cout = cout_actuel[actuel_id] + distance_segment

                if (
                    voisin_id not in cout_actuel
                    or nouveau_cout < cout_actuel[voisin_id]
                ):
                    cout_actuel[voisin_id] = nouveau_cout
                    # f(n) c'est la priorité de la frontière
                    # f(n) = g(n) + h(n) calculée comme la somme du coût actuel et de l'heuristique
                    # g(n) = nouveau_cout : coût actuel pour atteindre le voisin
                    # h(n) = distance à vol d'oiseau jusqu'à l'arrivée : heuristique
                    # h(n) = l'heuristique sert à estimer le coût restant pour atteindre l'arrivée
                    d_voisin = self.graphe.districts[voisin_id]
                    d_arrivee = self.graphe.districts[id_arrivee]

                    heuristique = self.graphe.calculer_distance_haversine(
                        d_voisin.lat, d_voisin.lon, d_arrivee.lat, d_arrivee.lon
                    )

                    priorite_f = nouveau_cout + heuristique
                    frontiere.inserer(voisin_id, priorite_f)
                    provenance[voisin_id] = actuel_id

        return None, 0

    def _reconstruire_chemin(self, provenance, actuel_id):
        """Remonte la trace du chemin depuis l'arrivée vers le départ."""
        chemin = []
        while actuel_id is not None:
            chemin.append(actuel_id)
            actuel_id = provenance[actuel_id]
        return chemin[::-1]  # Inverser pour avoir Départ -> Arrivée
