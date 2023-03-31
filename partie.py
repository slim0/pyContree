import random

from cartes import CarteSetBelote, JeuDeCarte32
from joueurs import ANNONCE_NULLE


class Partie:
    def __init__(self, equipeA, equipeB, score_victoire: int = 1001):
        self.score_victoire = score_victoire
        self.jeu_de_carte = JeuDeCarte32()
        self.equipeA = equipeA
        self.equipeB = equipeB
        self.donneur = self.joueurs[0]
        self.equipe_gagnante = None
        self.scores = [0, 0]

    def score(self):
        print(f"Equipe A: {self.equipeA.score}")
        print(f"Equipe B: {self.equipeB.score}")

    @property
    def joueurs(self):
        return [
            self.equipeA.joueur1,
            self.equipeB.joueur1,
            self.equipeA.joueur2,
            self.equipeB.joueur2,
        ]

    def lancer_tourne(self):
        while self.equipe_gagnante is None:
            print(f"donneur: {self.donneur}")
            fin_tourne = Tourne(partie=self).lancer()
            self.equipeA.score += fin_tourne.score_equipeA
            self.equipeB.score += fin_tourne.score_equipeB
            self.donneur = fin_tourne.nouveau_donneur

            if (
                self.equipeA.score >= self.score_victoire
                or self.equipeB.score >= self.score_victoire
            ):
                equipes = [self.equipeA, self.equipeB]
                equipes.sort(lambda x: x.score, reverse=True)
                self.equipe_gagnante = equipes[0]

        print(f"Bravo {self.equipe_gagnante} !!")


class PhaseAnnonce:
    def __init__(self, ordre_initial) -> None:
        self.joueurs_devant_annoncer = ordre_initial

        self.meilleure_annonce = ANNONCE_NULLE

    def lancer(self):
        while True in list(
            map(lambda x: x.doit_annoncer, self.joueurs_devant_annoncer)
        ):
            for joueur in self.joueurs_devant_annoncer:
                if joueur.doit_annoncer is True:
                    annonce = joueur._annoncer(meilleure_annonce=self.meilleure_annonce)
                    if annonce is not None:
                        self.meilleure_annonce = annonce
                        for joueur_devant_annoncer in list(
                            filter(lambda x: x != joueur, self.joueurs_devant_annoncer)
                        ):
                            joueur_devant_annoncer.doit_annoncer = True

        return self.meilleure_annonce


class PhaseJeu:
    def __init__(self, tourne, ordre_initial) -> None:
        self.tourne = tourne
        self.joueurs = ordre_initial

    def lancer(self):
        while True:
            pli = CarteSetBelote()
            for joueur in self.joueurs:
                carte_jouee = joueur._jouer_carte(cartes_jouees=pli)
                pli.append(carte_jouee)

            pli.sort()

            carte_jouee_gagnante = pli[-1]

            carte_gagnante = carte_jouee_gagnante.carte
            joueur_gagnant = carte_jouee_gagnante.joueur

            if len(self.joueurs[0].main) == 0:
                break


class Tourne:
    schema_donne = (3, 2, 3)

    class FinTourneInterface:
        def __init__(self, score_equipeA, score_equipeB, nouveau_donneur):
            self.score_equipeA = score_equipeA
            self.score_equipeB = score_equipeB
            self.nouveau_donneur = nouveau_donneur

    def __init__(self, partie: Partie):
        self.partie = partie
        self.score_equipeA = 0
        self.score_equipeB = 0

        self.partie.jeu_de_carte._couper()

    def _resultat_fin_tourne(self) -> FinTourneInterface:
        return self.FinTourneInterface(
            score_equipeA=self.score_equipeA,
            score_equipeB=self.score_equipeB,
            nouveau_donneur=self.joueur_suivant(joueur_precedent=self.partie.donneur),
        )

    def lancer(self) -> FinTourneInterface:
        print(f"Ordre initial: {self.ordre_initial}")

        reponse = self.melangeur._demander_melanger()
        if reponse:
            self.partie.jeu_de_carte._melanger()

        self._distribuer()

        phase_annonce = PhaseAnnonce(ordre_initial=self.ordre_initial)
        self.meilleure_annonce = phase_annonce.lancer()

        if self.meilleure_annonce.score_a_faire == 0:
            joueurs_ordre_random = self.joueurs
            random.shuffle(joueurs_ordre_random)
            for joueur in joueurs_ordre_random:
                joueur.doit_annoncer = True
                self.partie.jeu_de_carte.cartes += joueur.main
                joueur.main = []
            return self._resultat_fin_tourne()

        for joueur in self.joueurs:
            for carte in joueur.main:
                if carte.couleur.forme == self.meilleure_annonce.atout.forme:
                    carte.atout = True

        phase_jeu = PhaseJeu(tourne=self, ordre_initial=self.ordre_initial)
        phase_jeu.lancer()

    @property
    def ordre_initial(self):
        joueur1 = self.joueur_suivant(joueur_precedent=self.partie.donneur)
        joueur2 = self.joueur_suivant(joueur_precedent=joueur1)
        joueur3 = self.joueur_suivant(joueur_precedent=joueur2)
        joueur4 = self.joueur_suivant(joueur_precedent=joueur3)

        return [joueur1, joueur2, joueur3, joueur4]

    @property
    def joueurs(self):
        return self.partie.joueurs

    def joueur_suivant(self, joueur_precedent):
        index_joueur_precedent = self.joueurs.index(joueur_precedent)
        index_joueur_suivant = index_joueur_precedent + 1
        if index_joueur_suivant == 4:
            index_joueur_suivant = 0

        return self.joueurs[index_joueur_suivant]

    @property
    def melangeur(self):
        return self.joueurs[self.joueurs.index(self.partie.donneur) - 1]

    def _distribuer(self):
        schema_donne = (3, 2, 3)
        for x in schema_donne:
            for joueur in self.partie.joueurs:
                self.partie.jeu_de_carte._donner_x_cartes(joueur=joueur, x=x)

        for joueur in self.partie.joueurs:
            joueur.main.sort(pour="main")

    def _etat(self):
        for joueur in self.partie.joueurs:
            print(f"{joueur.nom}: {joueur.main}")