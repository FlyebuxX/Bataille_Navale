# =================================================================================================================== #
# === IMPORTATIONS                                                                                                    #
# =================================================================================================================== #


from serveur import Serveur
# =================================================================================================================== #
# === CLASS                                                                                                           #
# =================================================================================================================== #


class JoueurServeur:
    """
    Joueur de la bataille navale
    """

    def __init__(self, pseudo: str):
        self.pseudo = pseudo
        self.jeu = {}
        self.bateaux = []
        self.bateaux_coules = [[], [], [], [], []]
        self.bateaux_restants = 5
        self.cases_interdites = []
        self.cases_jouees = []
        self.connexion_serveur = Serveur('Serveur', '26.215.237.217', 5000, 2)

        self.initialiser_plateau()

    def initialiser_plateau(self) -> None:
        """
        Méthode qui crée un plateau de jeu
        :param : None
        :return : None
        """
        jeu_joueur = [[i if i > 0 else '' for i in range(11)]] + [[chr(i)] + ['_'] * 9 for i in range(65, 75)]
        self.jeu = jeu_joueur

    def connexion(self):
        """
        Connexion du serveur avec le client
        :param : None
        :return : None
        """
        self.connexion_serveur.configuration_serveur()  # paramétrage connexion
        self.connexion_serveur.recevoir_connexions()  # écoute d'une connexion entrante
        self.connexion_serveur.accepter_connexion()  # mise en relation avec le client
