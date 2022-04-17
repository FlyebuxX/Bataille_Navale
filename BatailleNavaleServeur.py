# =======================================================================================================
# IMPORTATIONS
# =======================================================================================================


from serveur import Server
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
        self.serveur = Server('Machine_Name', 'HOST', 'PORT', 2)

    def creer_plateau(self) -> None:
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
        self.serveur.bind_server()  # paramétrage connexion
        self.serveur.listen_connections()  # écoute d'une connexion entrante
        self.serveur.accept_connections()


class BatailleNavale:
    """
    Jeu de la Bataille Navale
    """

    def __init__(self, joueur2: str):
        self.joueur_serveur = Joueur(joueur2)
        self.joueur_serveur.creer_plateau()

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
