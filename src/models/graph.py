import csv
import math


class District:
    def __init__(self, id, nom, region, lat, lon):
        self.id = id
        self.nom = nom
        self.region = region
        self.lat = float(lat)
        self.lon = float(lon)

    def __repr__(self):
        return f"{self.nom} ({self.region})"


class DistrictsGraph:
    """
    Représente la carte de Madagascar comme un graphe de districts.
    Utilisé par l'algorithme A* pour optimiser la logistique.
    """

    def __init__(self):
        self.districts = {}  # id -> objet District
        self.adjacence = {}  # id -> liste de (id_voisin, distance_km)

    def charger_depuis_csv(self, csv_path):
        """Charge les districts et leurs coordonnées depuis le fichier CSV."""
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                d_id = int(row["id"])
                d = District(
                    d_id,
                    row["district"],
                    row["region"],
                    row["latitude"],
                    row["longitude"],
                )
                self.districts[d_id] = d
                self.adjacence[d_id] = []

    @staticmethod
    def calculer_distance_haversine(lat1, lon1, lat2, lon2):
        """
        Calcule la distance en kilomètres entre deux points (Haversine).
        Utile comme heuristique pour A*.
        """
        R = 6371  # Rayon de la Terre en km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def ajouter_connexion(self, id1, id2):
        """Ajoute une route entre deux districts avec calcul auto de la distance."""
        if id1 in self.districts and id2 in self.districts:
            d1 = self.districts[id1]
            d2 = self.districts[id2]
            dist = self.calculer_distance_haversine(d1.lat, d1.lon, d2.lat, d2.lon)

            # On évite les doublons
            if not any(v == id2 for v, d in self.adjacence[id1]):
                self.adjacence[id1].append((id2, dist))
                self.adjacence[id2].append((id1, dist))

    def generer_reseau_automatique(self, k=3):
        """
        Connecte chaque district à ses k voisins les plus proches.
        Crée un graphe connexe pour simuler le réseau routier.
        """
        ids = list(self.districts.keys())
        for i, id1 in enumerate(ids):
            distances = []
            for id2 in ids:
                if id1 == id2:
                    continue  # si la distance est 0, on passe
                d1 = self.districts[id1]  # récupère les coordonnées du district 1
                d2 = self.districts[id2]  # récupère les coordonnées du district 2
                dist = self.calculer_distance_haversine(d1.lat, d1.lon, d2.lat, d2.lon)
                distances.append((dist, id2))

            # Trier par distance et prendre les k plus proches
            distances.sort()
            for dist, id2 in distances[:k]:  # pour chaque voisin le plus proche
                self.ajouter_connexion(id1, id2)

    def obtenir_voisins(self, d_id):
        return self.adjacence.get(d_id, [])

    def __len__(self):
        return len(self.districts)
