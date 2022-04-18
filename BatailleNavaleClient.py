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

    def initialiser_plateau(self) -> None:
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
        self.joueur_client.initialiser_plateau()

        self.set = {
            self.joueur_client.pseudo: self.joueur_client.jeu,
        }

        # recevoir le pseudo de l'ennemi

        # pseudo_ennemi = self.joueur_client.connexion_client.recevoir_message()
        # deck_ennemi = self.joueur_client.connexion_client.recevoir_message()
        # self.ennemi = Joueur(pseudo_ennemi, deck_ennemi)
        # self.set[pseudo_ennemi] = self.ennemi.jeu
        self.ennemi = Joueur('Jack')
        self.set['Jack'] = self.ennemi.jeu

        self.images = []

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

    def validation_clic(self, coords: tuple) -> bool:
        """
        Méthode qui renvoie si le clic est valide
        :param coords : tuple, coordonnées du clic
        :return : bool
        """
        x = coords[0]
        y = coords[1]
        if 723 <= x <= 1062 and 163 < y < 520:
            return True
        return False

    def poser_image(self, x: int, y: int, type_tir: str) -> None:
        """
        Méthode qui crée une nouvelle image sur la zone de dessin
        :param x : int
        :param y : int
        :param type_tir : str, touche, eau, coule
        :return : None
        """
        types = {'touche': 'images/touche.gif', 'coule': 'images/coule.gif', 'eau': 'eau.gif'}
        img = PhotoImage(file=types[type_tir])
        zone_dessin.create_image(x, y, image=img)
        self.images.append(img)

    def detection_clic(self, event) -> tuple:
        """
        Méthode qui renvoie les coordonnées du clic de souris détecté sur l'écran
        :param event : événement
        :return event.x : int
        :return event.y : int
        :return clic_valide : bool
        """
        clic_valide = self.validation_clic((event.x, event.y))
        if clic_valide:
            # if touche ....  elif coule .... else eau ....
            event.x, event.y = self.centrer_image(event.x, event.y)
            self.poser_image(event.x, event.y, 'coule')

        return event.x, event.y, clic_valide

    def centrer_image(self, x: int, y: int) -> tuple:
        """
        Méthode qui renvoie les coordonnées du milieu de la case cliquée
        :param x : int
        :param y : int
        :return x : int
        :return y : int
        """
        x_valid = [739, 773, 807, 842, 875, 909, 944, 978, 1012, 1045]
        y_valid = [181, 217, 253, 288, 324, 360, 395, 430, 467, 503]
        x_diff, y_diff = 20, 20
        i = -1
        while x_diff >= 17:
            i += 1
            x_diff = abs(x_valid[i] - x)
        x = x_valid[i]
        i = -1
        while y_diff >= 17:
            i += 1
            y_diff = abs(y_valid[i] - y)
        y = y_valid[i]
        return x, y

    def coordonnees_cases(self) -> None:
        """
        Méthode qui associe chaque case du jeu à des coordonnées, coin supérieur gauche et coin inférieur droit
        """
        coords = {chr(i) + str(k): [
            (round(722 + 36 * (k - 1) - k * 1.8), round(163 + 34 * (i - 65) + abs(65 - i) * 1.8)),  # coords sup
            (round(722 + 36 * k - k * 1.8), round(163 + 34 * (i - 64) + abs(65 - i) * 1.8))  # coords inf
        ]
             for i in range(65, 75) for k in range(1, 11)
        }

        self.ennemi.jeu = coords


# =======================================================================================================
# PROGRAMME PRINCIPAL
# =======================================================================================================


bataille_navale_client = BatailleNavaleClient(input('Nom du joueur (client) : '))
tk = Tk()
tk.title("Bataille Navale")
zone_dessin = Canvas(width="1100", height="600", bg="white")
zone_dessin.pack()
board_image = PhotoImage(file="images/jeu.gif")
fond_board = zone_dessin.create_image(550, 300, image=board_image)
bataille_navale_client.coordonnees_cases()
zone_dessin.bind('<Button-1>', bataille_navale_client.detection_clic)
tk.mainloop()
