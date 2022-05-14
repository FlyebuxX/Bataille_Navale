# =================================================================================================================== #
# === IMPORTATIONS                                                                                                    #
# =================================================================================================================== #


import socket
# =================================================================================================================== #
# === CLASS                                                                                                           #
# =================================================================================================================== #


class Client:

    """
    Classe relative au client
    """

    def __init__(self, nom_machine: str, host: str, port: int):
        self.machine_name = nom_machine
        self.HOST = host
        self.PORT = port
        self.CONNEXION_AVEC_SERVEUR = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_info = None

    def connecter_appareil(self) -> None:
        """
        Méthode qui permet de connecter le client au serveur
        :param : None
        :return : None
        """
        self.CONNEXION_AVEC_SERVEUR.connect((self.HOST, self.PORT))

    def encoder_message(self, message):
        """
        Méthode qui encode un massage
        :param message : str, message à encoder
        :return message.encode() : message encodé
        """
        return message.encode()

    def envoyer_message(self, message: str) -> str:
        """
        Envoyer un message
        :param message : message
        :return message : str, message
        """
        message_a_envoyer = self.encoder_message(message)
        self.CONNEXION_AVEC_SERVEUR.send(message_a_envoyer)

        return message

    def recevoir_message(self) -> str:
        """
        Récupérer un message
        :param : None
        :return message_serveur_decode : str
        """
        message_serveur = self.CONNEXION_AVEC_SERVEUR.recv(1024)
        message_serveur_decode = message_serveur.decode()

        if "quit" in message_serveur_decode.lower():
            self.fin_connexion()
        return message_serveur_decode

    def fin_connexion(self) -> None:
        """
        Finir la connexion
        :param : None
        :return : None
        """
        self.CONNEXION_AVEC_SERVEUR.close()

    def __repr__(self):
        """
        Afficher les informations relatives au client
        :param : None
        :return : None
        """
        infos = ["Affichage de l'IP machine ", socket.gethostbyname_ex(socket.gethostname())]

        for element in infos:
            print(element)
