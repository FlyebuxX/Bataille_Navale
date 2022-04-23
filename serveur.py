# =====================================================================================================================
# IMPORTATIONS
# =====================================================================================================================


import socket
# =====================================================================================================================
# CLASS
# =====================================================================================================================


class Serveur:
    """
    Class relative au serveur
    """

    def __init__(self, nom_machine, host, port, max_connexions):
        self.machine_name = nom_machine
        self.HOST = host
        self.PORT = port
        self.MAX_CONNECTIONS = max_connexions
        self.CONNEXION_PRINCIPALE = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connexion_avec_client = None
        self.informations_client = None
        self.__repr__()

    def configuration_serveur(self):
        """
        Configuration du serveur
        """
        self.CONNEXION_PRINCIPALE.bind((self.HOST, self.PORT))

    def recevoir_connexions(self):
        """
        Méthode qui écoute une connexion entrante
        """
        self.CONNEXION_PRINCIPALE.listen(self.MAX_CONNECTIONS)

    def accepter_connexion(self):
        """
        Méthode qui accepte une nouvelle connexion et engage un tchat avec un client
        """
        (connexion_avec_client, informations_client) = self.CONNEXION_PRINCIPALE.accept()

        self.connexion_avec_client = connexion_avec_client
        self.informations_client = informations_client

    def encoder_message(self, message):
        """
        Méthode qui encode un message
        :return message encoded :
        """
        return message.encode()

    def envoyer_message(self, message: str) -> str:
        """
        Envoyer un message
        :param message : message
        :return message_converti : str
        """

        message_a_envoyer = self.encoder_message(message)
        self.connexion_avec_client.send(message_a_envoyer)

        return message

    def recevoir_message(self) -> str:
        """
        Récupérer un message
        :return message_serveur_decode : str
        """
        message_serveur = self.connexion_avec_client.recv(1024)
        message_serveur_decode = message_serveur.decode()

        if "quit" in message_serveur_decode.lower():
            self.fin_connexion()
        return message_serveur_decode

    def fin_connexion(self) -> None:
        """
        Finir la connexion
        :return : None
        """
        self.connexion_avec_client.close()

    def __repr__(self):
        """
        Method that displays infos
        """
        infos = ["Affichage de l'IP machine ", socket.gethostbyname_ex(socket.gethostname())]

        for elt in infos:
            print(elt)
