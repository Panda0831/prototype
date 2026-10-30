class TasBinaire:
    """
    Implémentation d'un Tas Binaire (Min-Heap).
    Utilisé pour gérer les priorités dans l'algorithme A* et la sélection des validateurs.
    """

    def __init__(self):
        """Initialise un tas vide."""
        self.tas = []

    def est_vide(self):
        """Vérifie si le tas est vide."""
        return len(self.tas) == 0

    def inserer(self, element, priorite):
        """
        Insère un élément avec une priorité donnée.

        :param element: L'objet à stocker (ex: nom d'un district).
        :param priorite: Valeur numérique (plus elle est petite, plus l'élément est prioritaire).
        """
        self.tas.append((priorite, element))
        self._remonter(len(self.tas) - 1)

    def extraire_min(self):
        """
        Extrait et retourne l'élément ayant la plus petite priorité.

        :return: Tuple (priorite, element) ou None si vide.
        """
        if self.est_vide():
            return None
            # si le tas contient un seul élément, on le retourne directement
        if len(self.tas) == 1:
            return self.tas.pop()
        # sinon, on extrait l'élément de la racine et on le remonte
        racine = self.tas[0]
        self.tas[0] = self.tas.pop()
        self._descendre(0)

        return racine

    def _remonter(self, index):
        """Maintient la propriété du tas en faisant remonter l'élément."""
        parent = (index - 1) // 2
        if index > 0 and self.tas[index][0] < self.tas[parent][0]:
            self.tas[index], self.tas[parent] = self.tas[parent], self.tas[index]
            self._remonter(parent)

    def _descendre(self, index):
        """Maintient la propriété du tas en faisant descendre l'élément."""
        plus_petit = index
        gauche = 2 * index + 1
        droite = 2 * index + 2

        if gauche < len(self.tas) and self.tas[gauche][0] < self.tas[plus_petit][0]:
            plus_petit = gauche

        if droite < len(self.tas) and self.tas[droite][0] < self.tas[plus_petit][0]:
            plus_petit = droite

        if plus_petit != index:
            self.tas[index], self.tas[plus_petit] = (
                self.tas[plus_petit],
                self.tas[index],
            )
            self._descendre(plus_petit)

    def __len__(self):
        return len(self.tas)

    def __repr__(self):
        return f"TasBinaire(taille={len(self.tas)})"
