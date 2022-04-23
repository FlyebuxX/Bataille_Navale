# =======================================================================================================
# IMPORTATIONS
# ========================================================================================================


from serveur import Serveur
from math import sqrt
from tkinter import *
import tkinter.font
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
        self.bateaux = []
        self.bateaux_coules = [[], [], [], [], []]
        self.bateaux_restants = 5
        self.cases_interdites = []
        self.cases_jouees = []
        self.tirs_reussis = []
        self.connexion_serveur = Serveur('Serveur', '26.215.237.217', 5000, 2)

        self.initialiser_plateau()

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
        self.connexion_serveur.configuration_serveur()  # paramétrage connexion
        self.connexion_serveur.recevoir_connexions()  # écoute d'une connexion entrante
        self.connexion_serveur.accepter_connexion()


class BatailleNavaleServeur:
    """
    Jeu de la Bataille Navale
    """

    def __init__(self, joueur1: str):
        self.joueur_serveur = Joueur(joueur1)
        self.phase = "pose_bateau"  # 'pose_bateau' / 'tour_joueur' / 'tour_adverse' /'fin'
        self.cases_adjacentes = {}
        self.images = []
        self.deux_derniers_clics = []
        self.longueurs_bateaux = [5, 4, 3, 3, 2]

        # ============================================================================ #
        # COMMUNICATION AVEC LE CLIENT ENNEMI                                          #
        # ============================================================================ #

        self.joueur_serveur.connexion()

        # envoyer le pseudo
        self.joueur_serveur.connexion_serveur.envoyer_message(self.joueur_serveur.pseudo)
        # recevoir le pseudo du client ennemi
        pseudo_ennemi_client = self.joueur_serveur.connexion_serveur.recevoir_message()
        self.ennemi_client = Joueur(pseudo_ennemi_client)

    def recevoir_clic(self):
        """
        Méthode qui permet de recevoir le clic du joueur adverse
        """
        # recoit la case du joueur adverse
        case = self.joueur_serveur.connexion_serveur.recevoir_message()
        resultat, nb_bateau = self.tir(case)
        x = self.joueur_serveur.jeu[case][0]
        y = self.joueur_serveur.jeu[case][1:]
        num_img = self.poser_image(x, y, resultat)
        if resultat == 'touche':
            self.ennemi_client.tirs_reussis.append([case, num_img])
        elif resultat == 'coule':
            for i in self.joueur_serveur.bateaux_coules[nb_bateau]:
                for case_touchee in self.ennemi_client.tirs_reussis:
                    case_2, num_img = case_touchee[0], case_touchee[1]
                    if case_2 == i:
                        img_coule = PhotoImage(file='images/coule.gif')
                        zone_dessin.itemconfig(num_img, image=img_coule)
                        case_touchee[1] = img_coule
        
            self.joueur_serveur.bateaux_restants -= 1
            if self.joueur_serveur.bateaux_restants == 0:
                self.phase = 'fin'
                self.pop_up("Bravo", str(self.ennemi_client.pseudo) + ' a gagné !')
            else:
                self.phase = 'tour_joueur'
        self.joueur_serveur.connexion_serveur.envoyer_message(resultat)
        self.joueur_serveur.connexion_serveur.envoyer_message(str(nb_bateau))

    # -------------------------------------------------------------------------------------------------- #
    # --- INTERACTION SCRIPT / CLIENT / SERVEUR : GUI                                                    #
    # -------------------------------------------------------------------------------------------------- #

    def pop_up(self, titre: str, texte_pop_up: str) -> None:
        """
        Méthode qui fait une fenêtre pop up
        :param titre : str, titre de la fenêtre
        :param texte_pop_up : str, texte à afficher
        :return : None
        """
        var_pop_up = Toplevel()  # création de la fenêtre pop up

        # centre la fenêtre
        y = int(tk.winfo_screenheight() / 2) - 35
        x = int(tk.winfo_screenwidth() / 2) - 250
        var_pop_up.geometry('500x70+' + str(x) + '+' + str(y))

        var_pop_up.title(titre)
        Label(var_pop_up, text=texte_pop_up).pack()
        Button(var_pop_up, text="Ok", command=var_pop_up.destroy).pack()
        var_pop_up.transient(tk)
        var_pop_up.grab_set()
        tk.wait_window(var_pop_up)

    def poser_image(self, x: int, y: int, type_tir: str) -> int:
        """
        Méthode qui crée une nouvelle image sur la zone de dessin
        :param x : int
        :param y : int
        :param type_tir : str, touche, eau, coule
        :return num_img : int, id de l'image posée
        """
        types = {
            'bateau': 'images/bateau.gif',
            'touche': 'images/touche.gif',
            'coule': 'images/coule.gif',
            'eau': 'images/eau.gif',
            'ancre': 'images/ancre.gif'
        }
        img = PhotoImage(file=types[type_tir])
        num_img = zone_dessin.create_image(x, y, image=img)
        self.images.append([num_img, img])

        return num_img

    # -------------------------------------------------------------------------------------------------- #
    # --- MÉTHODES RELATIVES AUX CASES DES GRILLES                                                       #
    # -------------------------------------------------------------------------------------------------- #

    def chercher_case(self, x: int, y: int) -> str:
        """
        Méthode qui permet de faire correspondre le clic d'un joueur à une case du plateau
        :param x : int
        :param y : int
        :return case : case du plateau où il y a eu un clic
        """
        # prend la grille selon la phase du jeu
        if self.phase == "pose_bateau":
            jeu = self.joueur_serveur.jeu
        elif self.phase == "tour_joueur":
            jeu = self.ennemi_client.jeu

        # trouver de quel milieu et donc de quelle case le clic se rapproche
        dist_courante, case = 1000, ''  # on fixe des valeurs par défaut
        for cle, valeur in jeu.items():
            distance_avec_point = sqrt((valeur[0] - x) ** 2 + (valeur[1] - y) ** 2)
            if distance_avec_point < dist_courante:
                dist_courante = distance_avec_point
                case = cle
        return case

    def coordonnees_cases(self) -> None:
        """
        Méthode qui associe chaque case du jeu aux coordonnées de leur milieu
        """
        # prend les coordonnées des points inférieurs droits et supérieurs gauches des cases
        # grille du joueur local
        cases = [(chr(i) + str(k),
                  ((round(94 + 36 * (k - 1) - k * 2), round(163 + 34 * (i - 65) + abs(65 - i) * 1.6)),  # coords sup
                   (round(94 + 36 * k - k * 2.3), round(163 + 34 * (i - 64) + abs(65 - i) * 1.6))))  # coords inf

                 for i in range(65, 75) for k in range(1, 11)
                 ]
        # définir le milieu de chaque case
        milieu = lambda x0, y0, x1, y1: ((x1 + x0) // 2, (y1 + y0) // 2)
        coords_joueur_courant = {
            elt[0]: milieu(elt[1][0][0], elt[1][0][1], elt[1][1][0], elt[1][1][1]) for elt in cases
        }

        # grille du joueur adverse
        cases = [(chr(i) + str(k),
                  ((round(722 + 36 * (k - 1) - k * 1.8), round(163 + 34 * (i - 65) + abs(65 - i) * 1.8)),  # coords sup
                   (round(722 + 36 * k - k * 1.8), round(163 + 34 * (i - 64) + abs(65 - i) * 1.8))))  # coords inf

                 for i in range(65, 75) for k in range(1, 11)
                 ]

        # définir le milieu de chaque case
        coords_ennemi = {
            elt[0]: milieu(elt[1][0][0], elt[1][0][1], elt[1][1][0], elt[1][1][1]) for elt in cases
        }

        self.joueur_serveur.jeu, self.ennemi_client.jeu = coords_joueur_courant, coords_ennemi

    def init_cases_adjacentes(self) -> None:
        """
        Méthode qui crée un dictionnaire des cases adjacentes de la grille
        """
        for i in range(65, 75):
            for j in range(1, 11):
                self.cases_adjacentes[chr(i) + str(j)] = []
                if i > 65:
                    self.cases_adjacentes[chr(i) + str(j)].append(chr(i - 1) + str(j))
                if i < 74:
                    self.cases_adjacentes[chr(i) + str(j)].append(chr(i + 1) + str(j))
                if j > 1:
                    self.cases_adjacentes[chr(i) + str(j)].append(chr(i) + str(j - 1))
                if j < 10:
                    self.cases_adjacentes[chr(i) + str(j)].append(chr(i) + str(j + 1))

    # -------------------------------------------------------------------------------------------------- #
    # --- MÉTHODES RELATIVES A LA GESTION DES CLICS                                                      #
    # -------------------------------------------------------------------------------------------------- #

    def detection_clic(self, event) -> None:
        """
        Méthode qui détecte le clic du joueur et agit selon la phase du jeu
        :param event : événement
        """
        jeu, case = {}, ''
        # prend la grille selon la phase du jeu
        if self.phase == "pose_bateau":
            jeu = self.joueur_serveur.jeu
        elif self.phase == 'tour_joueur':
            jeu = self.ennemi_client.jeu

        clic_valide = self.validation_clic((event.x, event.y))
        if clic_valide:
            if self.phase == "pose_bateau":
                if len(self.longueurs_bateaux) > 0:  # s'il y a encore des bateaux à poser
                    case = self.chercher_case(event.x, event.y)
                    if case in self.joueur_serveur.cases_interdites:  # si la case est valide
                        self.pop_up('Attention', 'Vous ne pouvez pas placer de bateau ici')
                        if len(self.deux_derniers_clics) > 0:  # pour réinitialiser s'il s'agit du 2e clic
                            self.deux_derniers_clics = []
                            self.images.pop()
                    else:
                        self.deux_derniers_clics.append((event.x, event.y))

                        if len(self.deux_derniers_clics) >= 2:  # il y a une coordonnée de départ, une de fin
                            self.images.pop()
                            case_dep = self.chercher_case(self.deux_derniers_clics[0][0],
                                                          self.deux_derniers_clics[0][1])
                            case_fin = self.chercher_case(self.deux_derniers_clics[1][0],
                                                          self.deux_derniers_clics[1][1])
                            self.verifier_position_bateau(case_dep, case_fin, self.longueurs_bateaux[0])
                            self.deux_derniers_clics = []
                        else:  # pose l'image de l'ancre pour savoir où on a cliqué la 1ère fois
                            event.x, event.y = jeu[case][0], jeu[case][1:]
                            self.poser_image(event.x, event.y, 'ancre')
                if len(self.longueurs_bateaux) == 0:  # s'il n'y a plus de bateaux à mettre
                    self.phase = 'tour_joueur'

            elif self.phase == 'tour_joueur':
                case = self.chercher_case(event.x, event.y)
                if case not in self.joueur_serveur.cases_jouees:
                    self.joueur_serveur.connexion_serveur.envoyer_message(case)
                    resultat = self.joueur_serveur.connexion_serveur.recevoir_message()
                    nb_bateau = self.joueur_serveur.connexion_serveur.recevoir_message()

                    nx, ny = [(value[0], value[1]) for key, value in self.ennemi_client.jeu.items() if key == case]
                    num_img = self.poser_image(nx, ny, resultat)
                    self.joueur_serveur.cases_jouees.append(case)
                    if resultat == 'touche':
                        self.joueur_serveur.tirs_reussis.append([case, num_img])

                    if resultat == 'coule':
                        for i in self.joueur_serveur.bateaux_coules[nb_bateau]:
                            for case_touchee in self.joueur_serveur.tirs_reussis:
                                case_2, num_img = case_touchee[0], case_touchee[1]
                                if case_2 == i:
                                    img_coule = PhotoImage(file='images/coule.gif')
                                    zone_dessin.itemconfig(num_img, image=img_coule)
                                    case_touchee[1] = img_coule
                        self.ennemi_client.bateaux_restants -= 1
                    
                    if self.ennemi_client.bateaux_restants == 0:
                        self.pop_up('Bravo !', str(self.joueur_serveur.pseudo) + ' a gagné')
                        self.phase = 'fin'
                    else:
                        self.phase = 'tour_adverse'
                        self.recevoir_clic()

    def validation_clic(self, coords: tuple) -> bool:
        """
        Méthode qui renvoie si le clic est valide
        :param coords : tuple, coordonnées du clic
        :return : bool
        """
        x = coords[0]
        y = coords[1]
        if self.phase == "tour_joueur" and 723 <= x <= 1062 and 163 < y < 520:
            return True
        elif self.phase == "pose_bateau" and 93 <= x <= 431 and 163 <= y <= 518:
            return True
        return False

    def tir(self, case: str) -> str:
        """
        Méthode qui renvoie le résultat du tir : à l'eau / touché / coulé
        :param case : str, case du tir
        :return : str, le résultat du tir
        """
        resultat = 'eau'  # valeurs par défaut
        for bateau in range(len(self.joueur_serveur.bateaux)):
            bat = self.joueur_serveur.bateaux[bateau]
            # si on touche un bateau
            if case in bat:
                for i in range(len(bat)):
                    if bat[i] == case:
                        bat.pop(i)
                
                if len(bat) == 0:
                    resultat = 'coule'
                    
                else:
                    resultat = 'touche'
                    # ajoute la case touché pour remplacer ensuite par 'coulé'
                    self.joueur_serveur.bateaux_coules[bateau].append(case)
        return resultat, bateau

    # -------------------------------------------------------------------------------------------------- #
    # --- POSE DES BATEAUX                                                                               #
    # -------------------------------------------------------------------------------------------------- #

    def verifier_position_bateau(self, case_dep, case_fin, longueur_bateau):
        """
        Méthode qui vérifie si la position des bateaux renseignée sont valides
        :param case_dep : str, début de la position du bateau à poser
        :param case_fin : str, fin de la position du bateau à poser
        :param longueur_bateau : longueur du bateau attendue
        """
        if case_dep[0] == case_fin[0]:  # même lettre, pose horizontale
            if int(case_fin[1:]) - int(case_dep[1:]) < 0:
                case_fin, case_dep = case_dep, case_fin
            if int(case_fin[1:]) - int(case_dep[1:]) + 1 == longueur_bateau:
                self.poser_bateau(case_dep, case_fin)
            else:
                self.pop_up('Attention',
                            'Emplacement invalide: vous devez poser un bateau de taille ' + str(longueur_bateau))

        elif case_dep[1:] == case_fin[1:]:  # même numéro, pose verticale
            if ord(case_fin[0]) - ord(case_dep[0]) < 0:
                case_fin, case_dep = case_dep, case_fin
            if ord(case_fin[0]) - ord(case_dep[0]) + 1 == longueur_bateau:
                self.poser_bateau(case_dep, case_fin)
            else:
                self.pop_up('Attention',
                            'Emplacement invalide: vous devez poser un bateau de taille ' + str(longueur_bateau))

    def poser_bateau(self, case_dep: str, case_fin: str) -> None:
        """
        Poser les bateaux sur son plateau de jeu
        :param case_dep : str, début de la position du bateau à poser
        :param case_fin : str, fin de la position du bateau à poser
        """
        cases_a_poser = []
        cases_bateaux = []

        valide = True

        for cle, valeur in self.joueur_serveur.jeu.items():
            lettre, num_case = cle[0], int(cle[1:])

            if case_dep[0] == case_fin[0]:  # même lettre, pose horizontale
                if lettre == case_dep[0] and int(case_dep[1:]) <= num_case <= int(case_fin[1:]):
                    cases_a_poser.append(valeur)
                    cases_bateaux.append(lettre + str(num_case))

            else:  # même numéro, pose verticale
                if num_case == int(case_dep[1:]) and ord(case_dep[0]) <= ord(lettre) <= ord(case_fin[0]):
                    cases_a_poser.append(valeur)
                    cases_bateaux.append(lettre + str(num_case))

        # on vérifie que l'emplacement du bateau est valide

        for case in cases_bateaux:
            if case in self.joueur_serveur.cases_interdites and valide:
                valide = False
                self.pop_up('Attention', 'Vous ne pouvez pas placer de bateau ici')

        if valide:
            self.longueurs_bateaux.pop(0)
            # on pose les images du bateau
            for case in cases_a_poser:
                x, y = case[0], case[1:]
                self.poser_image(x, y, 'bateau')

            # on met à jour la liste des cases interdites
            for case in cases_bateaux:
                for i in self.cases_adjacentes[case]:
                    self.joueur_serveur.cases_interdites.append(i)

            # on met à jour la liste des bateaux
            self.joueur_serveur.bateaux.append([case for case in cases_bateaux])

            if len(self.longueurs_bateaux) > 0:
                # on met à jour le message indiquant le nombre de bateaux à poser
                label['text'] = 'Poser un bateau de longueur ' + str(self.longueurs_bateaux[0])
            else:
                label['text'] = 'Que la bataille commence !'


# =======================================================================================================
# PROGRAMME PRINCIPAL
# =======================================================================================================


bataille_navale_client = BatailleNavaleServeur(input('Nom du joueur (serveur) : '))

# GUI
tk = Tk()
tk.title("Bataille Navale: Joueur " + bataille_navale_client.joueur_serveur.pseudo)
zone_dessin = Canvas(width="1100", height="600", bg="white")
zone_dessin.pack()

# Centrer la fenêtre
nouveau_x, nouveau_y = int(tk.winfo_screenwidth() / 2) - 550, int(tk.winfo_screenheight() / 2) - 350
tk.geometry('1100x650+' + str(nouveau_x) + '+' + str(nouveau_y))
board_image = PhotoImage(file="images/jeu.gif")
fond_board = zone_dessin.create_image(550, 300, image=board_image)
zone_dessin.bind('<Button-1>', bataille_navale_client.detection_clic)

# Message
mess = 'Poser un bateau de longueur ' + str(bataille_navale_client.longueurs_bateaux[0])
font = tkinter.font.Font(family='Helvetica', size=14)
label = Label(tk, text=mess, bg='#d1d0cb', height=2, padx=2, pady=2, fg='#142396', font=font)
label.pack(side=BOTTOM)

# Jeu
bataille_navale_client.coordonnees_cases()
bataille_navale_client.init_cases_adjacentes()

tk.mainloop()
