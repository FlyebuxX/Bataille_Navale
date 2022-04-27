# =======================================================================================================
# IMPORTATIONS
# =======================================================================================================


from JoueurServeur import JoueurServeur
from math import sqrt
from tkinter import *
from pygame import mixer
import tkinter.font
# =======================================================================================================
# CLASS
# =======================================================================================================


class BatailleNavaleServeur:
    """
    Jeu de la Bataille Navale
    """

    def __init__(self, pseudo_joueur_serveur: str):
        self.joueur_serveur = JoueurServeur(pseudo_joueur_serveur)
        self.phase = "pose_bateau"  # 'pose_bateau' / 'tour_joueur' / 'tour_adverse' /'fin'
        self.cases_adjacentes = {}
        self.images = []
        self.deux_derniers_clics = []
        self.longueurs_bateaux = [5, 4, 3, 3, 2]
        self.bateaux_touches = []
        self.mode = 'sombre'

        # ============================================================================ #
        # COMMUNICATION AVEC LE CLIENT ENNEMI                                          #
        # ============================================================================ #

        self.joueur_serveur.connexion()

        # envoyer le pseudo
        self.joueur_serveur.connexion_serveur.envoyer_message(self.joueur_serveur.pseudo)
        # recevoir le pseudo du client ennemi
        pseudo_ennemi_client = self.joueur_serveur.connexion_serveur.recevoir_message()
        self.ennemi_client = JoueurServeur(pseudo_ennemi_client)

    def recevoir_clic(self):
        """
        Méthode qui permet de recevoir le clic du joueur adverse
        :param : None
        :return : None
        """
        # recevoir la case du joueur adverse
        case = self.joueur_serveur.connexion_serveur.recevoir_message()
        resultat, nb_bateau = self.tir(case)
        x, y = self.joueur_serveur.jeu[case][0], self.joueur_serveur.jeu[case][1:]
        num_img = self.poser_image(x, y, resultat)
        self.joueur_serveur.connexion_serveur.envoyer_message(resultat)
        self.joueur_serveur.connexion_serveur.envoyer_message(str(nb_bateau))

        if resultat == 'touche':
            self.ennemi_client.bateaux_coules[nb_bateau].append(num_img)

        elif resultat == 'coule':
            for elt in self.images:
                if elt[1] in self.ennemi_client.bateaux_coules[nb_bateau]:
                    img_coule = PhotoImage(file='images/coule.gif')
                    zone_dessin.itemconfig(elt[1], image=img_coule)
                    elt[1] = img_coule

            self.joueur_serveur.bateaux_restants -= 1

        if self.joueur_serveur.bateaux_restants == 0:
            self.phase = 'fin'
            self.pop_up("Perdu", str(self.ennemi_client.pseudo) + ' a gagné')
            label['text'] = str(self.ennemi_client.pseudo) + " a gagné"
        else:
            self.phase, label['text'] = 'tour_joueur', 'A ton tour !'

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

    def changer_mode(self):
        """
        Méthode qui permet de changer le colormode
        :param : None
        :return : None
        """
        if self.mode == 'clair':
            self.mode = 'sombre'
            zone_dessin.itemconfig(fond, image=board_image_sombre)
        else:
            self.mode = 'clair'
            zone_dessin.itemconfig(fond, image=board_image_clair)

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
            'ancre': 'images/ancre_2.gif'
        }

        img = PhotoImage(file=types[type_tir])
        case = self.chercher_case(x, y)
        num_img = zone_dessin.create_image(x, y, image=img)
        self.images.append([case, num_img, img])

        return num_img

    def jouer_son(self, type_tir):
        """
        Méthode qui lance la lecture d'un son
        :param type_tir : str
        :return : None
        """
        if type_tir == 'eau':
            mixer.music.load("sons/eau.wav")
        if type_tir == 'touche':
            mixer.music.load("sons/explosion.wav")
        elif type_tir == 'bateau':
            mixer.music.load("sons/bateau.wav")
        elif type_tir == 'coule':
            mixer.music.load("sons/coule.wav")

        mixer.music.play()

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
            jeu = self.joueur_serveur.jeu
        elif self.phase == "tour_joueur":
            jeu = self.ennemi_client.jeu

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

        self.joueur_serveur.jeu, self.ennemi_client.jeu = coords_joueur_courant, coords_ennemi

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
        :return : None
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
                    label['text'] = 'A ton tour !'  # le serveur joue en premier

            elif self.phase == 'tour_joueur':
                case = self.chercher_case(event.x, event.y)
                if case not in self.joueur_serveur.cases_jouees:
                    self.joueur_serveur.connexion_serveur.envoyer_message(case)
                    resultat = self.joueur_serveur.connexion_serveur.recevoir_message()
                    nb_bateau = int(self.joueur_serveur.connexion_serveur.recevoir_message())

                    nx, ny = jeu[case][0], jeu[case][1]
                    num_img = self.poser_image(nx, ny, resultat)
                    self.jouer_son(resultat)
                    self.joueur_serveur.cases_jouees.append(case)

                    if resultat == 'touche':
                        self.joueur_serveur.bateaux_coules[nb_bateau].append(num_img)
                    elif resultat == 'coule':
                        for elt in self.images:
                            if elt[1] in self.joueur_serveur.bateaux_coules[nb_bateau]:
                                img_coule = PhotoImage(file='images/coule.gif')
                                zone_dessin.itemconfig(elt[1], image=img_coule)
                                elt[1] = img_coule
                        self.jouer_son('coule')
                        self.ennemi_client.bateaux_restants -= 1

                    if self.ennemi_client.bateaux_restants == 0:
                        self.pop_up('Bravo', str(self.joueur_serveur.pseudo) + ' a gagné !')
                        self.phase, label['text'] = 'fin', str(self.joueur_serveur.pseudo) + " a gagné"
                    else:
                        self.phase, label['text'] = 'tour_adverse', "A l'adversaire !"
                        zone_dessin.after(100, self.recevoir_clic)

    def validation_clic(self, coords: tuple) -> bool:
        """
        Méthode qui renvoie si le clic est valide
        :param coords : tuple, coordonnées du clic
        :return : bool
        """
        x, y = coords[0], coords[1]

        if self.phase == "tour_joueur" and 723 <= x <= 1062 and 163 < y < 520:
            return True
        elif self.phase == "pose_bateau" and 93 <= x <= 431 and 163 <= y <= 518:
            return True
        return False

    def tir(self, case: str) -> tuple:
        """
        Méthode qui renvoie le résultat du tir : à l'eau / touché / coulé
        :param case : str, case du tir
        :return resultat : str, résultat du tir
        :return longueur : int, longueur du bateau éventuellement touché
        """
        resultat, len_bateau = 'eau', 0  # valeurs par défaut

        for bateau in range(len(self.joueur_serveur.bateaux)):
            bat = self.joueur_serveur.bateaux[bateau]
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
        :return : None
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
        :return : None
        """
        cases_a_poser, cases_bateaux = [], []
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
            # pose les images du bateau
            for case in cases_a_poser:
                x, y = case[0], case[1:]
                self.poser_image(x, y, 'bateau')

            # mise à jour la liste des cases interdites
            for case in cases_bateaux:
                for i in self.cases_adjacentes[case]:
                    self.joueur_serveur.cases_interdites.append(i)

            # mise à  jour la liste des bateaux
            self.joueur_serveur.bateaux.append([case for case in cases_bateaux])

            if len(self.longueurs_bateaux) > 0:
                # mise à jour le message indiquant le nombre de bateaux à poser
                label['text'] = 'Poser un bateau de longueur ' + str(self.longueurs_bateaux[0])
            else:
                label['text'] = 'Que la bataille commence !'

        self.jouer_son('bateau')


# =======================================================================================================
# FONCTIONS
# =======================================================================================================


def afficher_regles():
    """
    Fonction qui permet l'affichage des règles du jeu
    :param : None
    :return : None
    """
    global bouton_retour
    zone_dessin.itemconfig(fond, image=regles_image)
    bouton_jouer.destroy()
    bouton_quitter.destroy()
    bouton_regles.destroy()

    bouton_retour = Button(tk, image=image_bouton_retour, command=menu)
    bouton_retour.place(x=890, y=520)


def debut_jeu():
    """
    Fonction qui permet le lancement du jeu
    :param : None
    :return : None
    """
    global label

    var_pop_up = Toplevel()  # création de la fenêtre pop up

    # centre la fenêtre
    y = int(tk.winfo_screenheight() / 2) - 35
    x = int(tk.winfo_screenwidth() / 2) - 250
    var_pop_up.geometry('500x70+' + str(x) + '+' + str(y))

    # mise en place des canaux son
    mixer.init()

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
    bataille_navale_serveur = BatailleNavaleServeur(pseudo.get())

    bouton_jouer.destroy()
    bouton_quitter.destroy()
    bouton_regles.destroy()

    zone_dessin.itemconfig(fond, image=board_image_sombre)
    zone_dessin.bind('<Button-1>', bataille_navale_serveur.detection_clic)

    font = tkinter.font.Font(family='Helvetica', size=14)
    pseudo_joueur = bataille_navale_serveur.joueur_serveur.pseudo
    Label(tk, text=pseudo_joueur, bg='#d1d0cb', fg='#142396', font=font).place(x=92, y=90)

    pseudo_ennemi = bataille_navale_serveur.ennemi_client.pseudo
    Label(tk, text=pseudo_ennemi, bg='#d1d0cb', fg='#142396', font=font).place(x=722, y=90)

    Button(tk, text='Mode sombre/clair', command=bataille_navale_serveur.changer_mode).place(x=940, y=550)

    # Message
    mess = 'Poser un bateau de longueur ' + str(bataille_navale_serveur.longueurs_bateaux[0])
    label = Label(tk, text=mess, bg='#d1d0cb', height=2, padx=2, pady=2, fg='#142396', font=font)
    label.pack(side=BOTTOM)

    # Jeu
    bataille_navale_serveur.coordonnees_cases()
    bataille_navale_serveur.init_cases_adjacentes()


def menu():
    """
    Fonction définissant le menu du jeu
    :param : None
    :return : None
    """
    global bouton_retour, bouton_jouer, bouton_regles, bouton_quitter

    bouton_retour.destroy()
    zone_dessin.itemconfig(fond, image=menu_image)
    bouton_jouer = Button(tk, image=image_bouton_jouer, command=debut_jeu, padx=204, pady=66)
    bouton_jouer.place(x=50, y=475)
    bouton_regles = Button(tk, image=image_bouton_regles, command=afficher_regles, padx=216, pady=67)
    bouton_regles.place(x=300, y=475)
    bouton_quitter = Button(tk, image=image_bouton_quitter, command=tk.destroy, padx=242, pady=67)
    bouton_quitter.place(x=560, y=475)


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

# Images et widgets
menu_image = PhotoImage(file="images/menu.gif")
fond = zone_dessin.create_image(550, 300, image=menu_image)
image_bouton_jouer = PhotoImage(file='images/jouer.gif')
bouton_jouer = Button(tk, image=image_bouton_jouer, command=debut_jeu, padx=204, pady=66)
bouton_jouer.place(x=50, y=475)
image_bouton_regles = PhotoImage(file='images/regles_bouton.gif')
bouton_regles = Button(tk, image=image_bouton_regles, command=afficher_regles, padx=216, pady=67)
bouton_regles.place(x=300, y=475)
image_bouton_quitter = PhotoImage(file='images/quitter.gif')
bouton_quitter = Button(tk, image=image_bouton_quitter, command=tk.destroy, padx=242, pady=67)
bouton_quitter.place(x=560, y=475)

regles_image = PhotoImage(file="images/regles.gif")
board_image_clair = PhotoImage(file="images/jeu.gif")
board_image_sombre = PhotoImage(file="images/jeu_2.gif")
image_bouton_retour = PhotoImage(file='images/retour.gif')

tk.mainloop()
