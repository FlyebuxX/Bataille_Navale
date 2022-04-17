# =======================================================================================================
# IMPORTATIONS
# ========================================================================================================

from tkinter import *
from client import Client
# =======================================================================================================
# CLASS
# =======================================================================================================


class Joueur:
    """
    Joueur de la bataille navale
    """
    def __init__(self, pseudo: str, deck=[]):
        self.pseudo = pseudo
        self.jeu = deck
        self.connexion_client = Client('Machine_Name', 'HOST', 'PORT')

    def creer_plateau(self) -> None:
        """
        Méthode qui crée un plateau de jeu
        :return : None
        """
        jeu_joueur = [[i if i > 0 else '' for i in range(11)]] + [[chr(i)] + ['_'] * 9 for i in range(65, 75)]
        self.jeu = jeu_joueur

    def connexion(self) -> None:
        """
        Connexion du client au serveur
        :return : None
        """
        self.connexion_client.connecter_appareil()


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

        # recevoir le pseudo de l'ennemi
        ennemi = self.joueur_client.connexion_client.get_message()
        self.ennemi = Joueur(ennemi)
        self.set[ennemi] = self.ennemi.jeu

    def convertisseur_dico_vers_str(self, jeu_liste) -> str:
        """
        Méthode qui convertit un jeu en chaîne de caractère
        :param jeu_liste : list
        :return dico_vers_str : conversion de la liste en string
        """
        dico_vers_str = ''
        for ligne in jeu_liste:
            for element in ligne:
                dico_vers_str += str(element)

        return dico_vers_str

    def envoyer_jeu(self) -> None:
        """
        Méthode qui permet d'envoyer le jeu du client, de la forme d'un dictionnaire vers une chaîne de caractères
        """
        jeu_str = self.convertisseur_dico_vers_str(self.joueur_client.jeu)
        self.joueur_client.connexion_client.envoyer_message(jeu_str)

    def afficher_plateau(self, plateau: list) -> None:
        """
        Méthode qui affiche le plateau d'un joueur
        :param plateau: list
        :return: None
        """
        for ligne in plateau:
            print(ligne)

    def detection_clic(self, event) -> tuple:
        """
        Méthode qui renvoie les coordonnées du clic de souris détecté sur l'écran
        """
        return event.x, event.y


# =======================================================================================================
# PROGRAMME PRINCIPAL
# =======================================================================================================


bataille_navale_client = BatailleNavaleClient(input('Nom du joueur (client) : '))
fenetre = Tk()
fenetre.title("Bataille Navale")
zone_dessin = Canvas(width="1100", height="600", bg="white")
zone_dessin.pack()
board_image = PhotoImage(file="images/jeu.gif")
fond_board = zone_dessin.create_image(550, 300, image=board_image)
zone_dessin.bind('<Button-1>', bataille_navale_client.detection_clic)
fenetre.mainloop()
