# =======================================================================================================
# IMPORTATIONS
# ========================================================================================================


from client import Client
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
        self.jeu = {}
        self.bateaux = []
        self.bateaux_coules = [[], [], [], [], []]
        self.bateaux_restants = 5
        self.cases_interdites = []
        self.cases_jouees = []
        self.connexion_client = Client('Serveur', '26.255.135.38', 5000)

        self.initialiser_plateau()

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
        self.phase = "pose_bateau"  # 'pose_bateau' / 'tour_joueur' / 'tour_adverse' /'fin'
        self.cases_adjacentes = {}
        self.images = []
        self.deux_derniers_clics = []
        self.longueurs_bateaux = [5, 4, 3, 3, 2]
        self.bateaux_touches = []

        # ============================================================================ #
        # COMMUNICATION AVEC LE CLIENT ENNEMI                                          #
        # ============================================================================ #

        self.joueur_client.connexion()

        # recevoir le pseudo du serveur ennemi
        pseudo_ennemi_serveur = self.joueur_client.connexion_client.recevoir_message()
        self.ennemi_serveur = Joueur(pseudo_ennemi_serveur)
        # envoyer le pseudo
        self.joueur_client.connexion_client.envoyer_message(self.joueur_client.pseudo)

    def recevoir_clic(self):
        """
        Méthode qui permet de recevoir le clic du joueur adverse
        """
        # recevoir la case du joueur adverse
        case = self.joueur_client.connexion_client.recevoir_message()
        resultat, nb_bateau = self.tir(case)
        x, y = self.joueur_client.jeu[case][0], self.joueur_client.jeu[case][1:]
        num_img = self.poser_image(x, y, resultat)
        self.joueur_client.connexion_client.envoyer_message(resultat)
        self.joueur_client.connexion_client.envoyer_message(str(nb_bateau))

        if resultat == 'touche':
            self.ennemi_serveur.bateaux_coules[nb_bateau].append(num_img)

        elif resultat == 'coule':
            for elt in self.images:
                if elt[1] in self.ennemi_serveur.bateaux_coules[nb_bateau]:
                    img_coule = PhotoImage(file='images/coule.gif')
                    zone_dessin.itemconfig(elt[1], image=img_coule)
                    elt[1] = img_coule

            self.joueur_client.bateaux_restants -= 1

        if self.joueur_client.bateaux_restants == 0:
            self.phase = 'fin'
            self.pop_up("Perdu", str(self.ennemi_serveur.pseudo) + ' a gagné')
            label['text'] = str(self.ennemi_serveur.pseudo) + " a gagné"
        else:
            self.phase = 'tour_joueur'
            label['text'] = 'A ton tour !'

        

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
        if type(y) == tuple:
            y = y[0]
        types = {
            'bateau': 'images/bateau.gif',
            'touche': 'images/touche.gif',
            'coule': 'images/coule.gif',
            'eau': 'images/eau.gif',
            'ancre': 'images/ancre.gif'
        }
        img = PhotoImage(file=types[type_tir])
        case = self.chercher_case(x, y)
        num_img = zone_dessin.create_image(x, y, image=img)
        self.images.append([case, num_img, img])

        return num_img

    # -------------------------------------------------------------------------------------------------- #
    # --- MÉTHODES RELATIVES AUX CASES DES GRILLES                                                       #
    # -------------------------------------------------------------------------------------------------- #

    def chercher_case(self, x: int, y: int) -> str:
        """
        Méthode qui permet de faire correspondre le clic d'un joueur à une case du plateau
        :param x : int
        :param y : int
        :return case : str, case du plateau où il y a eu un clic
        """
        jeu = {}
        # prend la grille selon la phase du jeu
        if self.phase == "pose_bateau":
            jeu = self.joueur_client.jeu
        elif self.phase == "tour_joueur":
            jeu = self.ennemi_serveur.jeu

        # trouver de quel milieu et donc de quelle case le clic se rapproche
        dist_courante, case = 1000, ''  # on fixe des valeurs par défaut
        for cle, valeur in jeu.items():
            distance_avec_point = sqrt((valeur[0] - x) ** 2 + (valeur[1] - y) ** 2)
            if distance_avec_point < dist_courante:
                dist_courante, case = distance_avec_point, cle
        return case

    def coordonnees_cases(self) -> None:
        """
        Méthode qui associe chaque case du jeu aux coordonnées de leur milieu
        :param : None
        :return : None
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

        self.joueur_client.jeu, self.ennemi_serveur.jeu = coords_joueur_courant, coords_ennemi

    def init_cases_adjacentes(self) -> None:
        """
        Méthode qui crée un dictionnaire des cases adjacentes de la grille
                :param : None
        :return : None
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
            jeu = self.joueur_client.jeu
        elif self.phase == 'tour_joueur':
            jeu = self.ennemi_serveur.jeu

        clic_valide = self.validation_clic((event.x, event.y))
        if clic_valide:
            if self.phase == "pose_bateau":
                if len(self.longueurs_bateaux) > 0:  # s'il y a encore des bateaux à poser
                    case = self.chercher_case(event.x, event.y)
                    if case in self.joueur_client.cases_interdites:  # si la case est valide
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
                    self.phase = 'tour_adverse'
                    label['text'] = "A l'adversaire !"
                    zone_dessin.after(1000, self.recevoir_clic)  # le client reçoit la case en premier

            elif self.phase == 'tour_joueur':
                case = self.chercher_case(event.x, event.y)
                if case not in self.joueur_client.cases_jouees:
                    self.joueur_client.connexion_client.envoyer_message(case)
                    resultat = self.joueur_client.connexion_client.recevoir_message()
                    nb_bateau = int(self.joueur_client.connexion_client.recevoir_message())
                    nx, ny = jeu[case][0], jeu[case][1]
                    num_img = self.poser_image(nx, ny, resultat)
                    self.joueur_client.cases_jouees.append(case)
                    if resultat == 'touche':
                        self.joueur_client.bateaux_coules[nb_bateau].append(num_img)

                    if resultat == 'coule':
                        for elt in self.images:
                            if elt[1] in self.joueur_client.bateaux_coules[nb_bateau]:
                                img_coule = PhotoImage(file='images/coule.gif')
                                zone_dessin.itemconfig(elt[1], image=img_coule)
                                elt[1] = img_coule

                        self.ennemi_serveur.bateaux_restants -= 1

                    if self.ennemi_serveur.bateaux_restants == 0:
                        self.pop_up('Bravo !', str(self.joueur_client.pseudo) + ' a gagné !')
                        self.phase = 'fin'
                        label['text'] = str(self.joueur_client.pseudo) + " a gagné"
                    else:
                        self.phase = 'tour_adverse'
                        label['text'] = "A l'adversaire !"
                        zone_dessin.after(1000, self.recevoir_clic)

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

    def tir(self, case: str) -> tuple:
        """
        Méthode qui renvoie le résultat du tir : à l'eau / touché / coulé
        :param case : str, case du tir
        :return : tuple, le résultat du tir et la longueur du bateau éventuellement touché
        """
        resultat, len_bateau = 'eau', 0  # valeurs par défaut
        for bateau in range(len(self.joueur_client.bateaux)):
            bat = self.joueur_client.bateaux[bateau]
            # si on touche un bateau
            if case in bat:
                for i in range(len(bat)):
                    if i < len(bat):
                        if bat[i] == case:
                            bat.pop(i)
                if len(bat) == 0:
                    resultat = 'coule'
                else:
                    resultat = 'touche'
                len_bateau = bateau
        return resultat, len_bateau

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
        cases_a_poser, cases_bateaux = [], []
        valide = True

        for cle, valeur in self.joueur_client.jeu.items():
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
            if case in self.joueur_client.cases_interdites and valide:
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
                    self.joueur_client.cases_interdites.append(i)

            # on met à jour la liste des bateaux
            self.joueur_client.bateaux.append([case for case in cases_bateaux])

            if len(self.longueurs_bateaux) > 0:
                # on met à jour le message indiquant le nombre de bateaux à poser
                label['text'] = 'Poser un bateau de longueur ' + str(self.longueurs_bateaux[0])
            else:
                label['text'] = 'Que la bataille commence !'

def afficher_regles():
    global bouton_retour
    zone_dessin.itemconfig(fond, image=regles_image)
    bouton_jouer.destroy()
    bouton_quitter.destroy()
    bouton_regles.destroy()
    bouton_retour = Button(tk, text='Retour', command=menu)
    bouton_retour.pack()

def debut_jeu():
    
    bouton_jouer.destroy()
    bouton_quitter.destroy()
    bouton_regles.destroy()
    var_pop_up = Toplevel()  # création de la fenêtre pop up

    # centre la fenêtre
    y = int(tk.winfo_screenheight() / 2) - 35
    x = int(tk.winfo_screenwidth() / 2) - 250
    var_pop_up.geometry('500x70+' + str(x) + '+' + str(y))

    var_pop_up.title('Bataille Navale')
    Label(var_pop_up, text='Nom du joueur :').pack()
    pseudo = StringVar(tk)
    pseudo_entree = Entry(var_pop_up, textvariable=pseudo)
    pseudo_entree.pack()
    pseudo_entree.focus_force()
    Button(var_pop_up, text="Ok", command=var_pop_up.destroy).pack()
    var_pop_up.transient(tk)
    var_pop_up.grab_set()
    tk.wait_window(var_pop_up)
    bataille_navale_client = BatailleNavaleClient(pseudo.get())

    zone_dessin.itemconfig(fond, image=board_image)
    zone_dessin.bind('<Button-1>', bataille_navale_client.detection_clic)

    # Message
    mess = 'Poser un bateau de longueur ' + str(bataille_navale_client.longueurs_bateaux[0])
    font = tkinter.font.Font(family='Helvetica', size=14)
    label = Label(tk, text=mess, bg='#d1d0cb', height=2, padx=2, pady=2, fg='#142396', font=font)
    label.pack(side=BOTTOM)

    # Jeu
    bataille_navale_client.coordonnees_cases()
    bataille_navale_client.init_cases_adjacentes()

def menu():
    global bouton_retour
    bouton_retour.destroy()
    zone_dessin.itemconfig(fond, image=menu_image)
    bouton_jouer = Button(tk, text='Jouer', command=debut_jeu)
    bouton_jouer.pack()
    bouton_regles = Button(tk, text='Règles', command=afficher_regles)
    bouton_regles.pack()
    bouton_quitter = Button (tk, text='Quitter', command=tk.destroy)
    bouton_quitter.pack()

# =======================================================================================================
# PROGRAMME PRINCIPAL
# =======================================================================================================

# GUI
tk = Tk()
tk.title("Bataille Navale")
zone_dessin = Canvas(width="1100", height="600", bg="white")
zone_dessin.pack()

# Centrer la fenêtre
nouveau_x, nouveau_y = int(tk.winfo_screenwidth() / 2) - 550, int(tk.winfo_screenheight() / 2) - 350
tk.geometry('1100x650+' + str(nouveau_x) + '+' + str(nouveau_y))

menu_image = PhotoImage(file="images/menu.gif")
fond = zone_dessin.create_image(550, 300, image=menu_image)
bouton_jouer = Button(tk, text='Jouer', command=debut_jeu)
bouton_jouer.pack()
bouton_regles = Button(tk, text='Règles', command=afficher_regles)
bouton_regles.pack()
bouton_quitter = Button (tk, text='Quitter', command=tk.destroy)
bouton_quitter.pack()

regles_image = PhotoImage(file="images/regles.gif")
board_image = PhotoImage(file="images/jeu.gif")

tk.mainloop()
