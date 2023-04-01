import random
from collections.abc import MutableSequence
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

    @property
    def score(self):
        if self.atout:
            if self.valeur == "V":
                return 20
            if self.valeur == "9":
                return 14

        if self.valeur == "1":
            return 11
        elif self.valeur == "10":
            return 10
        elif self.valeur == "V":
            return 2
        elif self.valeur == "D":
            return 3
        elif self.valeur == "R":
            return 4
        else:
            return 0

    def __lt__(self, other):
        """Permet de ranger les cartes dans la main"""
        if self.atout:
            if self.atout == COEUR:
                ordre = ORDRE_COULEURS_DEFAUT
            if self.atout == CARREAUX:
                ordre = [CARREAUX, PIQUE, COEUR, TREFLE]
            if self.atout == PIQUE:
                ordre = [PIQUE, COEUR, TREFLE, CARREAUX]
            if self.atout == TREFLE:
                ordre = [TREFLE, COEUR, PIQUE, CARREAUX]
        else:
            ordre = ORDRE_COULEURS_DEFAUT

        if self.couleur.forme == other.couleur.forme:
            self_score = self.score
            other_score = other.score

            if self_score == 0 and other_score == 0:
                self_integer = int(self.valeur)
                other_integer = int(other.valeur)
                return_bool = True if self_integer < other_integer else False
            else:
                return_bool = True if self_score < other_score else False
        else:
            if ordre.index(self.couleur) < ordre.index(other.couleur):
                return_bool = True
            else:
                return_bool = False

        return return_bool

    def __repr__(self) -> str:
        return f"{self.valeur}{self.couleur.forme}"

    def __hash__(self) -> int:
        return hash((self.valeur, self.couleur.forme))

    def __eq__(self, other):
        return isinstance(other, CarteBelote) and hash(self) == hash(other)


class CarteSetBelote(MutableSequence):
    def __init__(self, cartes=None) -> None:
        if cartes is None:
            cartes = []
        self.cartes = cartes

    def __repr__(self) -> str:
        return self.cartes.__repr__()

    def __getitem__(self, index):
        return self.cartes[index]

    def __setitem__(self, index, value):
        self.cartes[index] = value

    def __delitem__(self, index):
        del self.cartes[index]

    def __len__(self) -> int:
        return len(self.cartes)

    def insert(self, index, carte):
        return self.cartes.insert(index, carte)

    def sort(self, reverse=False):
        self.cartes.sort(reverse=reverse)

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

    def _trier_par_couleur(self):
        coeurs, piques, carreaux, trefles = (
            CarteSetBelote(),
            CarteSetBelote(),
            CarteSetBelote(),
            CarteSetBelote(),
        )
        for carte in self.cartes:
            coeurs.append(carte) if carte.couleur.forme == "♥" else ...
            piques.append(carte) if carte.couleur.forme == "♠" else ...
            carreaux.append(carte) if carte.couleur.forme == "♦" else ...
            trefles.append(carte) if carte.couleur.forme == "♣" else ...

        return coeurs, piques, carreaux, trefles

    @property
    def _ranger_par_force(self):
        coeurs, piques, carreaux, trefles = self._trier_par_couleur()
        coeurs.sort(reverse=True)
        piques.sort(reverse=True)
        carreaux.sort(reverse=True)
        trefles.sort(reverse=True)

        cartes_par_couleur = []

        if coeurs:
            cartes_par_couleur.append(coeurs)

        if piques:
            cartes_par_couleur.append(piques)

        if carreaux:
            cartes_par_couleur.append(carreaux)

        if trefles:
            cartes_par_couleur.append(trefles)

        cartes_par_couleur.sort(key=lambda x: x[0].atout is False)

        result = CarteSetBelote()
        for cartes in cartes_par_couleur:
            for carte in cartes:
                result.append(carte)

        return result

    @property
    def _carte_la_plus_forte(self):
        return self._ranger_par_force[0]


class JeuDeBelote(CarteSetBelote):
    def __init__(self):
        super().__init__(cartes=None)

        for valeur in VALEURS:
            for couleur in COULEURS:
                self._ajouter_cartes(CarteBelote(valeur=valeur, couleur=couleur))

        self._melanger()
