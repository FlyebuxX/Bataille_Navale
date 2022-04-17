# =======================================================================================================
# IMPORTATIONS
# =======================================================================================================


from serveur import Serveur
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
        self.serveur = Serveur('Machine_Name', 'HOST', 'PORT', 2)

    def initialiser_plateau(self) -> None:
        """
        Méthode qui crée un plateau de jeu
        :return : None
        """
        jeu_joueur = [[i if i > 0 else '' for i in range(11)]] + [[chr(i)] + ['_'] * 9 for i in range(65, 75)]
        self.jeu = jeu_joueur

    def connexion(self):
        """
        Connexion du serveur avec le client
        :return : None
        """
        self.serveur.configuration_serveur()  # paramétrage connexion
        self.serveur.recevoir_connexions()  # écoute d'une connexion entrante
        self.serveur.accepter_connexion()


class BatailleNavale:
    """
    Jeu de la Bataille Navale
    """

    def __init__(self, joueur2: str):
        self.joueur_serveur = Joueur(joueur2)
        self.joueur_serveur.initialiser_plateau()

        self.set = {
            self.joueur_serveur.pseudo: self.joueur_serveur.jeu,
        }

    def afficher_plateau(self, plateau: list) -> None:
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


bataille_navale = BatailleNavale('Nom du joueur (serveur) : ')
