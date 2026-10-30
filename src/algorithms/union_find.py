class UnionFind:
    """
    Implémentation de l'algorithme Union-Find (Disjoint Set Union)
    utilisée pour la gestion foncière et la détection de double vente.
    """

    def __init__(self):
        self.parent = {}
        self.rang = {}

    def exists(self, item):
        """Vérifie si un élément existe déjà dans le set."""
        return item in self.parent

    def add(self, item):
        """Ajoute un nouvel élément (ex: une nouvelle parcelle ou un nouveau propriétaire)."""
        if item not in self.parent:
            self.parent[item] = item
            self.rang[item] = 0

    def find(self, item):
        """
        Trouve la racine de l'élément (itératif pour éviter RecursionError).
        """
        if item not in self.parent:
            return None

        # On remonte jusqu'à la racine
        path = []
        curr = item
        # tant que l'élément n'est pas la racine on remonte
        while self.parent[curr] != curr:
            path.append(curr)
            curr = self.parent[curr]
            # Sécurité anti-boucle infinie (au cas où les données seraient corrompues)
            if len(path) > 1000:
                print(
                    f" [!] Boucle infinie détectée dans UnionFind pour {item}. Réinitialisation."
                )
                self.parent[curr] = curr
                return curr

        # on le compresse pour éviter les boucles infinies
        for node in path:
            self.parent[node] = curr

        return curr

    def bind(self, parent_item, child_item):
        """
        Force une relation parent-enfant (ex: Propriétaire -> Terre).
        Garantit que le parent reste la racine.
        """
        self.add(parent_item)
        self.add(child_item)

        # On trouve les racines actuelles
        root_p = self.find(parent_item)
        root_c = self.find(child_item)

        # On attache la racine de l'enfant à la racine du parent
        if root_p != root_c:
            self.parent[root_c] = root_p
            # On augmente le rang du parent pour qu'il reste dominant
            self.rang[root_p] = max(
                self.rang.get(root_p, 0), self.rang.get(root_c, 0) + 1
            )

        # Force re-assignment to ensure root is indeed the parent_item
        self.parent[root_c] = root_p

        return True

    def union(self, item1, item2):
        """
        Fusionne deux ensembles (ex: vente d'une parcelle à un propriétaire).
        Retourne True si la fusion a réussi, False si ils étaient déjà liés.
        """
        root1 = self.find(item1)
        root2 = self.find(item2)

        if root1 is None or root2 is None:
            return False

        if root1 != root2:
            # Union by rang : on attache le plus petit arbre sous le plus grand
            if self.rang[root1] > self.rang[root2]:
                self.parent[root2] = root1
            elif self.rang[root1] < self.rang[root2]:
                self.parent[root1] = root2
            else:
                self.parent[root2] = root1
                self.rang[root1] += 1
            return True

        return False

    def is_connected(self, item1, item2):
        """Vérifie si deux éléments appartiennent au même ensemble."""
        return self.find(item1) == self.find(item2)
