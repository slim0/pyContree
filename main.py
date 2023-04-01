from joueurs import Equipe, Joueur
from partie import Partie

simon = Joueur(nom="Simon")
helene = Joueur(nom="Hélène")
etienne = Joueur(nom="Etienne")
julien = Joueur(nom="Julien")

equipeA = Equipe(joueur1=simon, joueur2=helene)
equipeB = Equipe(joueur1=etienne, joueur2=julien)

partie = Partie(equipeA=equipeA, equipeB=equipeB)
manche = partie.lancer_manche()
