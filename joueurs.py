from typing import Optional

from cartes import COEUR, COULEURS, CarteBelote, CarteSetBelote, Couleur, Pli


class Annonce:
    VALID_SCORES = list(range(80, 170, 10)) + [0, 1000, 2000]

    def __init__(self, atout, score_a_faire, joueur):
        if int(score_a_faire) not in self.VALID_SCORES:
            raise ValueError("score_a_faire non valide")

        if not isinstance(atout, Couleur):
            raise ValueError("couleur non valide")

        self.atout = atout
        self.score_a_faire = score_a_faire
        self.joueur = joueur

    def __lt__(self, other):
        if self.score_a_faire < other.score_a_faire:
            return True


ANNONCE_NULLE = Annonce(atout=COEUR, score_a_faire=0, joueur=None)


def poser_question(question, reponses_possibles):
    reponse = None
    while reponse not in reponses_possibles:
        reponse = input(question)
    return reponse


class Joueur:
    def __init__(self, nom: str):
        self.nom: str = nom
        self.belote: bool = False
        self.main: CarteSetBelote = CarteSetBelote()
        self.doit_annoncer: bool = True
        self.equipe: Optional[Equipe] = None  # Défini lors de la création de l'équipe
        self.plis: list[Pli] = []

    def __repr__(self) -> str:
        return self.nom

    def _reinit(self):
        self.doit_annoncer = True
        self.belote = False
        self.main = CarteSetBelote()
        self.plis = []

    @property
    def _total_points(self):
        score = 0
        for pli in self.plis:
            score += pli._points
        if self.belote:
            score += 20
        return score

    def _afficher_main(self):
        print(self.main)

    def _annoncer(self, meilleure_annonce):
        self._afficher_main()
        reponse = poser_question(f"Souhaitez-vous annoncer {self} ?", ["o", "n"])

        if reponse == "o":
            couleur = poser_question("Couleur ?", list(map(lambda x: x.nom, COULEURS)))
            couleur = list(filter(lambda x: x.nom == couleur, COULEURS))[0]

            scores_possibles = list(
                map(
                    lambda x: str(x),
                    filter(
                        lambda x: x > meilleure_annonce.score_a_faire,
                        Annonce.VALID_SCORES,
                    ),
                )
            )

            score = poser_question("Score ?", scores_possibles)
            annonce = Annonce(atout=couleur, score_a_faire=int(score), joueur=self)
        else:
            annonce = None

        self.doit_annoncer = False
        return annonce

    def _demander_melanger(self) -> bool:
        reponse = input(f"Souhaitez-vous mélanger {self.nom}? [o/n]: ")
        if reponse == "o":
            return True
        return False

    def _ajouter_carte_en_main(self, carte):
        self.main.append(carte)

    def _faire_annonce(self) -> bool:
        reponse = input(f"Souhaitez-vous faire une annonce {self.nom}? [o/n]: ")
        if reponse == "o":
            return True
        return False

    def _couleur_demandee_en_main(self, couleur_demandee) -> bool:
        return (
            len(
                list(
                    filter(
                        lambda x: x.couleur.forme == couleur_demandee.couleur.forme,
                        self.main,
                    )
                )
            )
            > 0
        )

    def _atout_en_main(self) -> bool:
        return True if True in [carte.atout for carte in self.main] else False

    def _meilleur_atout_en_main(self, other_atout: CarteBelote) -> bool:
        if other_atout.atout is False:
            raise ValueError("Vous devez appeler cette fonction avec un autre atout")
        meilleurs_atouts_en_main = list(
            filter(lambda x: x.atout and x > other_atout, self.main)
        )
        if meilleurs_atouts_en_main:
            return True

        return False

    def _jouer_carte(self, pli: Pli, couleur_atout: Couleur):
        premiere_carte_jouee = pli[0] if pli else None

        print(f"À toi de jouer {self}")
        self._afficher_main()

        while True:
            index_carte = 999
            while index_carte not in range(0, len(self.main)):
                index_carte = input("Index de la carte à jouer: ")
                try:
                    index_carte = int(index_carte)
                except:
                    ...

            carte_a_jouer = self.main[index_carte]

            if premiere_carte_jouee is not None:
                carte_gagnante = pli._carte_la_plus_forte(couleur_atout=couleur_atout)

                if carte_a_jouer.couleur.forme != premiere_carte_jouee.couleur.forme:
                    couleur_en_main: bool = self._couleur_demandee_en_main(
                        couleur_demandee=premiere_carte_jouee
                    )
                    if couleur_en_main:
                        print(
                            f"Vous possèder du {premiere_carte_jouee.couleur.forme} "
                            "en main. "
                            f"Vous ne pouvez pas jouer du {carte_a_jouer.couleur.forme}"
                        )

                        continue

                    else:
                        if self._atout_en_main():
                            if (
                                carte_a_jouer.atout is False
                                and carte_gagnante.joueur.equipe != self.equipe
                            ):
                                print("Vous devez couper !")
                                continue

                else:
                    if premiere_carte_jouee.atout and carte_a_jouer.atout:
                        if carte_a_jouer < premiere_carte_jouee:
                            if self._meilleur_atout_en_main(other_atout=carte_gagnante):
                                print("Vous avez un atout supérieur en main")

            if self.belote and carte_a_jouer.atout:
                if carte_a_jouer.valeur in ("D", "R"):
                    atouts_en_main = list(filter(lambda x: x.atout is True, self.main))
                    valeurs_atouts = list(map(lambda x: x.valeur, atouts_en_main))
                    if "D" in valeurs_atouts or "R" in valeurs_atouts:
                        print("Belote")
                    else:
                        print("Rebelote")
            self.main.pop(index_carte)
            return carte_a_jouer


class Equipe:
    def __init__(self, joueur1, joueur2):
        self.joueur1: Joueur = joueur1
        self.joueur2: Joueur = joueur2

        joueur1.equipe = self
        joueur2.equipe = self
        self.score: int = 0

    def __repr__(self) -> str:
        return f"{self.joueur1.nom} & {self.joueur2.nom}"

    @property
    def joueurs(self) -> tuple:
        return (self.joueur1, self.joueur2)
