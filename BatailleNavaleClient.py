# =======================================================================================================
# IMPORTATIONS
# ========================================================================================================


from client import Client
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
        self.client = Client('Machine_Name', 'HOST', 'PORT')

    def creer_plateau(self) -> None:
        """
        Méthode qui crée un plateau de jeu
        :return: None
        """
        jeu_joueur = [[i if i > 0 else '' for i in range(11)]] + [[chr(i)] + ['_'] * 9 for i in range(65, 75)]
        self.jeu = jeu_joueur

    def connexion(self) -> None:
        """
        Connexion du client au serveur
        :return: None
        """
        self.client.connect_device()


class BatailleNavaleClient:
    """
    Jeu de la Bataille Navale
    """
    def __init__(self, joueur1: str):
        self.joueur_client = Joueur(joueur1)
        self.joueur_client.creer_plateau()

        self.set = {
            self.joueur_client.pseudo: self.joueur_client.jeu,
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


bataille_navale = BatailleNavaleClient(input('Nom du joueur (client) : '))
