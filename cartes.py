import random
from collections.abc import Set
from typing import Literal

VALEURS = ("7", "8", "9", "10", "V", "D", "R", "1")

ORDRE_NON_ATOUT = VALEURS
ORDRE_ATOUT = ("7", "8", "10", "D", "R", "1", "9", "V")


class Couleur:
    def __init__(
        self,
        forme: Literal["♥", "♠", "♦", "♣"],
        nom: str,
        couleur: Literal["ROUGE", "NOIRE"],
    ):
        self.forme = forme
        self.nom = nom
        self.couleur = couleur


COEUR = Couleur(forme="♥", nom="COEUR", couleur="ROUGE")
CARREAUX = Couleur(forme="♦", nom="CARREAUX", couleur="ROUGE")
PIQUE = Couleur(forme="♠", nom="PIQUE", couleur="NOIRE")
TREFLE = Couleur(forme="♣", nom="TREFLE", couleur="NOIRE")

COULEURS = [COEUR, CARREAUX, PIQUE, TREFLE]

ORDRE_COULEURS_DEFAUT = [COEUR, PIQUE, CARREAUX, TREFLE]


class CarteBelote:
    def __init__(self, valeur: str, couleur: Couleur):
        if valeur not in VALEURS:
            raise ValueError("La valeur de la carte est non valide")
        if couleur not in COULEURS:
            raise ValueError("La couleur de la carte est non valide")

        self.valeur = valeur
        self.couleur: Couleur = couleur
        self.joueur = None

        self.atout: bool = False

    # @property
    # def score(self):
    #     if self.atout:
    #         if self.valeur == "V":
    #             return 20
    #         if self.valeur == "9":
    #             return 14

    #     if self.valeur == "1":
    #         return 11
    #     elif self.valeur == "V":
    #         return 2
    #     elif self.valeur == "D":
    #         return 3
    #     elif self.valeur == "R":
    #         return 4
    #     else:
    #         return 0

    # def __lt__(self, other):
    #     """Permet de ranger les cartes dans la main"""
    #     if self.atout:
    #         if self.atout == COEUR:
    #             ordre = ORDRE_COULEURS_DEFAUT
    #         if self.atout == CARREAUX:
    #             ordre = [CARREAUX, PIQUE, COEUR, TREFLE]
    #         if self.atout == PIQUE:
    #             ordre = [PIQUE, COEUR, TREFLE, CARREAUX]
    #         if self.atout == TREFLE:
    #             ordre = [TREFLE, COEUR, PIQUE, CARREAUX]
    #     else:
    #         ordre = ORDRE_COULEURS_DEFAUT

    #     if self.couleur.forme == other.couleur.forme:
    #         self_score = self.score
    #         other_score = other.score

    #         if self_score == 0 and other_score == 0:
    #             self_integer = int(self.valeur)
    #             other_integer = int(other.valeur)
    #             return_bool = True if self_integer < other_integer else False
    #         else:
    #             return_bool = True if self_score < other_score else False
    #     else:
    #         if ordre.index(self.couleur) < ordre.index(other.couleur):
    #             return_bool = True
    #         else:
    #             return_bool = False

    #     return return_bool

    def __repr__(self) -> str:
        return f"{self.valeur}{self.couleur.forme}"

    def __hash__(self) -> int:
        return hash((self.valeur, self.couleur.forme))

    def __eq__(self, other):
        return isinstance(other, CarteBelote) and hash(self) == hash(other)


class CarteSet(Set):
    def __init__(self, cartes=None) -> None:
        if cartes is None:
            cartes = []
        self.cartes = cartes

    def __contains__(self, x: CarteBelote) -> bool:
        if isinstance(x, CarteBelote) and x in self.cartes:
            return True
        return False

    def __iter__(self):
        return iter(self.cartes)

    def __len__(self) -> int:
        return len(self.cartes)

    def _ajouter_cartes(self, carte):
        self.cartes.append(carte)

    def _melanger(self):
        random.shuffle(self.cartes)

    def _donner_x_cartes(self, joueur, x):
        cartes_a_donner = self.cartes[0:x]
        for carte in cartes_a_donner:
            joueur._ajouter_carte_en_main(carte)
            carte.joueur = joueur
        del self.cartes[0:x]

    def _couper(self):
        if len(self.cartes) < 2:
            raise ValueError("Vous ne pouvez pas couper un jeu de moins de 2 cartes")
        rand_int = random.randint(1, len(self.cartes) - 1)
        self.cartes = self.cartes[rand_int:] + self.cartes[:rand_int]


class CarteSetBelote(CarteSet):
    def _sort_main(self):
        self._sort_force()

    def _sort_force(self):
        cartes_atouts = list(filter(lambda x: x.atout is True, self.cartes))
        cartes_non_atouts = list(filter(lambda x: x.atout is False, self.cartes))

        cartes_atouts_rangees = []
        for carte in cartes_atouts:
            index_force = ORDRE_ATOUT.index(carte.valeur)
            cartes_atouts_rangees.append((carte, index_force))

        cartes_atouts_rangees.sort(key=lambda x: x[1])

        cartes_non_atouts_rangees = []
        for carte in cartes_non_atouts:
            index_force = ORDRE_NON_ATOUT.index(carte.valeur)
            cartes_non_atouts_rangees.append((carte, index_force))

        cartes_non_atouts_rangees.sort(key=lambda x: x[1])

        return cartes_atouts_rangees + cartes_non_atouts_rangees

    def sort(self, pour: Literal["main", "force"]):
        """
        Ranger les d'un jeu de belote
        :param pour: Raison pour laquelle ranger les cartes
        :type pour: Literal["main"; "force"]:
            - "main": Pour ranger les cartes dans une main
            - "force": par ordre de force (ex: 8 plus fort que 7 même si les
            deux valent 0 points)
        """

        if pour == "main":
            self._sort_main()
        elif pour == "force":
            self._sort_force()
        else:
            raise NotImplementedError(
                f"Le paramètre 'pour' doit valoir \"main\" ou \"force\". '{pour=}'"
            )

    @property
    def carte_la_plus_forte(self):
        return self.cartes.sort(pour="force")[0]


class JeuDeCarte32(CarteSet):
    def __init__(self):
        super().__init__(cartes=None)

        for valeur in VALEURS:
            for couleur in COULEURS:
                self._ajouter_cartes(CarteBelote(valeur=valeur, couleur=couleur))

        self._melanger()
