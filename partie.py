import random

from cartes import CarteSetBelote, JeuDeBelote, Pli
from joueurs import ANNONCE_NULLE, Joueur


class Partie:
    def __init__(self, equipeA, equipeB, score_victoire: int = 1001):
        self.score_victoire = score_victoire
        self.jeu_de_carte = JeuDeBelote()
        self.equipeA = equipeA
        self.equipeB = equipeB
        self.donneur = self.joueurs[0]
        self.equipe_gagnante = None
        self.scores = [0, 0]

    def score(self):
        print(f"Equipe A: {self.equipeA.score}")
        print(f"Equipe B: {self.equipeB.score}")

    @property
    def joueurs(self) -> list[Joueur]:
        return [
            self.equipeA.joueur1,
            self.equipeB.joueur1,
            self.equipeA.joueur2,
            self.equipeB.joueur2,
        ]

    def lancer_manche(self):
        while self.equipe_gagnante is None:
            print(f"donneur: {self.donneur}")
            fin_manche = Manche(partie=self).lancer()
            self.equipeA.score += fin_manche.score_equipeA
            self.equipeB.score += fin_manche.score_equipeB
            self.donneur: Joueur = fin_manche.nouveau_donneur

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
        self.joueurs_devant_annoncer: Joueur = ordre_initial
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
    def __init__(self, manche, ordre_initial) -> None:
        self.manche = manche
        self.joueurs: list[Joueur] = ordre_initial

    def lancer(self):
        while True:
            pli = Pli()
            for joueur in self.joueurs:
                carte_jouee = joueur._jouer_carte(
                    pli=pli, couleur_atout=self.manche.meilleure_annonce.atout.couleur
                )
                pli.append(carte_jouee)
                print(f"Carte jouée: {carte_jouee}")

            pli_par_force = pli._ranger_par_force(
                couleur_atout=self.manche.meilleure_annonce.atout.couleur
            )

            carte_jouee_gagnante = pli_par_force[0]
            joueur_gagnant = carte_jouee_gagnante.joueur
            joueur_gagnant.plis.append(pli)
            print(f"Pli remporté par {joueur_gagnant}\n")

            index_joueur_gagnant = self.joueurs.index(joueur_gagnant)
            self.joueurs = (
                self.joueurs[index_joueur_gagnant:]
                + self.joueurs[:index_joueur_gagnant]
            )

            if len(self.joueurs[0].main) == 0:
                pli.dernier_pli = True
                break


class Manche:
    schema_donne = (3, 2, 3)

    class FinMancheInterface:
        def __init__(self, score_equipeA, score_equipeB, nouveau_donneur):
            self.score_equipeA = score_equipeA
            self.score_equipeB = score_equipeB
            self.nouveau_donneur = nouveau_donneur

    def __init__(self, partie: Partie):
        self.partie = partie
        self.score_equipeA = 0
        self.score_equipeB = 0
        self.meilleure_annonce = None

        self.partie.jeu_de_carte._couper()

    def _resultat_fin_manche(self) -> FinMancheInterface:
        return self.FinMancheInterface(
            score_equipeA=self.score_equipeA,
            score_equipeB=self.score_equipeB,
            nouveau_donneur=self.joueur_suivant(joueur_precedent=self.partie.donneur),
        )

    def lancer(self) -> FinMancheInterface:
        print(f"Ordre initial: {self.ordre_initial}")

        reponse = self.melangeur._demander_melanger()
        if reponse:
            self.partie.jeu_de_carte._melanger()

        self._distribuer()

        phase_annonce = PhaseAnnonce(ordre_initial=self.ordre_initial)
        self.meilleure_annonce = phase_annonce.lancer()

        if self.meilleure_annonce.joueur is None:
            joueurs_ordre_random = self.joueurs
            random.shuffle(joueurs_ordre_random)
            for joueur in joueurs_ordre_random:
                self.partie.jeu_de_carte.cartes += joueur.main
                joueur._reinit()
            return self._resultat_fin_manche()

        for joueur in self.joueurs:
            for carte in joueur.main:
                if carte.couleur.forme == self.meilleure_annonce.atout.forme:
                    carte.atout = True

        phase_jeu = PhaseJeu(manche=self, ordre_initial=self.ordre_initial)
        phase_jeu.lancer()

        score_equipeA, score_equipeB = self._compter_points()
        equipe_prenante = self.meilleure_annonce.joueur.equipe
        if equipe_prenante == self.partie.equipeA:
            if score_equipeA >= self.meilleure_annonce.score_a_faire:
                print(f"Bravo {equipe_prenante}, contrat rempli")
                self.score_equipeA = (
                    score_equipeA + self.meilleure_annonce.score_a_faire
                )
                self.score_equipeB = score_equipeB
            else:
                print(f"Contrat chuté par {equipe_prenante}")
                self.score_equipeB = self.meilleure_annonce.score_a_faire + 162
                self.score_equipeA = 0
        else:
            if score_equipeB >= self.meilleure_annonce.score_a_faire:
                print(f"Bravo {equipe_prenante}, contrat rempli")
                self.score_equipeB = (
                    score_equipeB + self.meilleure_annonce.score_a_faire
                )
                self.score_equipeA = score_equipeA
            else:
                print(f"Contrat chuté par {equipe_prenante}")
                self.score_equipeA = self.meilleure_annonce.score_a_faire + 162
                self.score_equipeB = 0

        return self._resultat_fin_manche()

    @property
    def ordre_initial(self):
        joueur1 = self.joueur_suivant(joueur_precedent=self.partie.donneur)
        joueur2 = self.joueur_suivant(joueur_precedent=joueur1)
        joueur3 = self.joueur_suivant(joueur_precedent=joueur2)
        joueur4 = self.joueur_suivant(joueur_precedent=joueur3)

        return [joueur1, joueur2, joueur3, joueur4]

    def _compter_points(self):
        score_equipeA = (
            self.partie.equipeA.joueur1._total_points
            + self.partie.equipeA.joueur2._total_points
        )
        score_equipeB = (
            self.partie.equipeB.joueur1._total_points
            + self.partie.equipeB.joueur2._total_points
        )
        return score_equipeA, score_equipeB

    @property
    def joueurs(self) -> list[Joueur]:
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
            joueur.main.sort()

    def _etat(self):
        for joueur in self.partie.joueurs:
            print(f"{joueur.nom}: {joueur.main}")
