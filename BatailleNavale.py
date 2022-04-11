# =======================================================================================================
# IMPORTATIONS
# =======================================================================================================


# =======================================================================================================
# CLASS
# =======================================================================================================


class Joueur:
    """
    Joueur de la bataille navale
    """
    def __init__(self, pseudo: str):
        self.pseudo = pseudo
        self.jeu = []

    def creer_plateau(self) -> None:
        """
        Méthode qui crée un plateau de jeu
        :return: None
        """
        jeu_joueur = [[i if i > 0 else '' for i in range(11)]] + [[chr(i)] + ['_'] * 9 for i in range(65, 75)]
        self.jeu = jeu_joueur


class BatailleNavale:
    """
    Jeu de la Bataille Navale
    """
    def __init__(self, joueur1=Joueur('Léna'), joueur2=Joueur('Val')):
        joueur1.creer_plateau()
        joueur2.creer_plateau()

        self.joueurs = {
            joueur1.pseudo: joueur1.jeu,
            joueur2.pseudo: joueur2.jeu
        }

    @staticmethod
    def afficher_plateau(plateau: list) -> None:
        """
        Méthode qui affiche le plateau d'un joueur
        :param plateau: list
        :return: None
        """
        for ligne in plateau:
            print(ligne)


# =======================================================================================================
# PROGRAMME PRINCIPAL
# =======================================================================================================


bataille_navale = BatailleNavale()
bataille_navale.afficher_plateau(bataille_navale.joueurs['Val'])
