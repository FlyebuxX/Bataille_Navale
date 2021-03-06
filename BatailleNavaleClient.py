# =================================================================================================================== #
# === IMPORTATIONS                                                                                                    #
# =================================================================================================================== #


from JoueurClient import JoueurClient
from math import sqrt
from tkinter import *
from pygame import mixer
import tkinter.font
# =================================================================================================================== #
# === CLASS                                                                                                           #
# =================================================================================================================== #


class BatailleNavaleClient:
    """
    Jeu de la Bataille Navale
    """

    def __init__(self, pseudo_joueur_client: str):
        self.joueur_client = JoueurClient(pseudo_joueur_client)
        self.phase = "pose_bateau"  # 'pose_bateau' / 'tour_joueur' / 'tour_adverse' /'fin'
        self.cases_adjacentes = {}
        self.images = []
        self.deux_derniers_clics = []
        self.longueurs_bateaux = [5, 4, 3, 3, 2]
        self.bateaux_touches = []
        self.mode = 'sombre'

        # =========================================================================================================== #
        # === COMMUNICATION AVEC LE CLIENT ENNEMI                                                                     #
        # =========================================================================================================== #

        self.joueur_client.connexion()

        # recevoir le pseudo du serveur ennemi
        pseudo_ennemi_serveur = self.joueur_client.connexion_client.recevoir_message()
        self.ennemi_serveur = JoueurClient(pseudo_ennemi_serveur)
        # envoyer le pseudo
        self.joueur_client.connexion_client.envoyer_message(self.joueur_client.pseudo)

    def recevoir_clic(self) -> None:
        """
        M??thode qui permet de recevoir le clic du joueur adverse
        :param : None
        :return : None
        """
        self.phase = ''
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
            mixer.music.load("sons/pirate.mp3")
            mixer.music.play()
            self.pop_up("Perdu", str(self.ennemi_serveur.pseudo) + ' a gagn??')
            label['text'] = str(self.ennemi_serveur.pseudo) + " a gagn??"
        else:
            self.phase, label['text'] = 'tour_joueur', 'A ton tour !'

    # --------------------------------------------------------------------------------------------------------------- #
    # --- INTERACTION SCRIPT / CLIENT / SERVEUR : GUI                                                                 #
    # --------------------------------------------------------------------------------------------------------------- #

    def pop_up(self, titre: str, texte_pop_up: str) -> None:
        """
        M??thode qui fait une fen??tre pop up
        :param titre : str, titre de la fen??tre
        :param texte_pop_up : str, texte ?? afficher
        :return : None
        """
        var_pop_up = Toplevel()  # cr??ation de la fen??tre pop up

        # centre la fen??tre
        y = int(tk.winfo_screenheight() / 2) - 35
        x = int(tk.winfo_screenwidth() / 2) - 250
        var_pop_up.geometry('500x70+' + str(x) + '+' + str(y))

        var_pop_up.title(titre)
        Label(var_pop_up, text=texte_pop_up).pack()
        Button(var_pop_up, text="Ok", command=var_pop_up.destroy).pack()
        var_pop_up.transient(tk)
        var_pop_up.grab_set()
        tk.wait_window(var_pop_up)

    def changer_mode(self) -> None:
        """
        M??thode qui permet de changer le colormode
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
        M??thode qui cr??e une nouvelle image sur la zone de dessin
        :param x : int
        :param y : int
        :param type_tir : str, touche, eau, coule
        :return num_img : int, id de l'image pos??e
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

    def jouer_son(self, type_tir) -> None:
        """
        M??thode qui lance la lecture d'un son
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

    # --------------------------------------------------------------------------------------------------------------- #
    # --- M??THODES RELATIVES AUX CASES DES GRILLES                                                                    #
    # --------------------------------------------------------------------------------------------------------------- #

    def chercher_case(self, x: int, y: int) -> str:
        """
        M??thode qui permet de faire correspondre le clic d'un joueur ?? une case du plateau
        :param x : int
        :param y : int
        :return case : str, case du plateau o?? il y a eu un clic
        """
        jeu = {}
        # prend la grille selon la phase du jeu
        if self.phase == "pose_bateau":
            jeu = self.joueur_client.jeu
        elif self.phase == "tour_joueur":
            jeu = self.ennemi_serveur.jeu

        # trouver de quel milieu et donc de quelle case le clic se rapproche
        dist_courante, case = 1000, ''  # on fixe des valeurs par d??faut
        for cle, valeur in jeu.items():
            distance_avec_point = sqrt((valeur[0] - x) ** 2 + (valeur[1] - y) ** 2)
            if distance_avec_point < dist_courante:
                dist_courante, case = distance_avec_point, cle
        return case

    def coordonnees_cases(self) -> None:
        """
        M??thode qui associe chaque case du jeu aux coordonn??es de leur milieu
        :param : None
        :return : None
        """
        # prend les coordonn??es des points inf??rieurs droits et sup??rieurs gauches des cases
        # grille du joueur local
        cases = [(chr(i) + str(k),
                  ((round(94 + 36 * (k - 1) - k * 2), round(163 + 34 * (i - 65) + abs(65 - i) * 1.6)),  # coords sup
                   (round(94 + 36 * k - k * 2.3), round(163 + 34 * (i - 64) + abs(65 - i) * 1.6))))  # coords inf

                 for i in range(65, 75) for k in range(1, 11)
                 ]
        # d??finir le milieu de chaque case
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
        # d??finir le milieu de chaque case
        coords_ennemi = {
            elt[0]: milieu(elt[1][0][0], elt[1][0][1], elt[1][1][0], elt[1][1][1]) for elt in cases
        }

        self.joueur_client.jeu, self.ennemi_serveur.jeu = coords_joueur_courant, coords_ennemi

    def init_cases_adjacentes(self) -> None:
        """
        M??thode qui cr??e un dictionnaire des cases adjacentes de la grille
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

    # --------------------------------------------------------------------------------------------------------------- #
    # --- M??THODES RELATIVES A LA GESTION DES CLICS                                                                   #
    # --------------------------------------------------------------------------------------------------------------- #

    def detection_clic(self, event) -> None:
        """
        M??thode qui d??tecte le clic du joueur et agit selon la phase du jeu
        :param event : ??v??nement
        :return : None
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
                if len(self.longueurs_bateaux) > 0:  # s'il y a encore des bateaux ?? poser
                    case = self.chercher_case(event.x, event.y)
                    if case in self.joueur_client.cases_interdites:  # si la case est valide
                        self.pop_up('Attention', 'Vous ne pouvez pas placer de bateau ici')
                        if len(self.deux_derniers_clics) > 0:  # pour r??initialiser s'il s'agit du 2e clic
                            self.deux_derniers_clics = []
                            self.images.pop()
                    else:
                        self.deux_derniers_clics.append((event.x, event.y))

                        if len(self.deux_derniers_clics) >= 2:  # il y a une coordonn??e de d??part, une de fin
                            self.images.pop()
                            case_dep = self.chercher_case(self.deux_derniers_clics[0][0],
                                                          self.deux_derniers_clics[0][1])
                            case_fin = self.chercher_case(self.deux_derniers_clics[1][0],
                                                          self.deux_derniers_clics[1][1])
                            self.verifier_position_bateau(case_dep, case_fin, self.longueurs_bateaux[0])
                            self.deux_derniers_clics = []

                        else:  # pose l'image de l'ancre pour savoir o?? on a cliqu?? la 1??re fois
                            event.x, event.y = jeu[case][0], jeu[case][1:]
                            self.poser_image(event.x, event.y, 'ancre')

                if len(self.longueurs_bateaux) == 0:  # s'il n'y a plus de bateaux ?? mettre
                    self.phase = 'tour_adverse'
                    label['text'] = "A l'adversaire !"
                    zone_dessin.after(2000, self.recevoir_clic)  # le client re??oit la case en premier

            elif self.phase == 'tour_joueur':
                mixer.pause()
                case = self.chercher_case(event.x, event.y)
                if case not in self.joueur_client.cases_jouees:
                    self.phase = 'tour_adverse'
                    self.joueur_client.connexion_client.envoyer_message(case)
                    resultat = self.joueur_client.connexion_client.recevoir_message()
                    nb_bateau = int(self.joueur_client.connexion_client.recevoir_message())

                    nx, ny = jeu[case][0], jeu[case][1]
                    num_img = self.poser_image(nx, ny, resultat)
                    self.jouer_son(resultat)
                    self.joueur_client.cases_jouees.append(case)

                    if resultat == 'touche':
                        self.joueur_client.bateaux_coules[nb_bateau].append(num_img)
                    elif resultat == 'coule':
                        for elt in self.images:
                            if elt[1] in self.joueur_client.bateaux_coules[nb_bateau]:
                                img_coule = PhotoImage(file='images/coule.gif')
                                zone_dessin.itemconfig(elt[1], image=img_coule)
                                elt[1] = img_coule
                        self.jouer_son('coule')
                        self.ennemi_serveur.bateaux_restants -= 1

                    if self.ennemi_serveur.bateaux_restants == 0:
                        mixer.music.load("sons/pirate.mp3")
                        mixer.music.play()
                        self.pop_up('Bravo !', str(self.joueur_client.pseudo) + ' a gagn?? !')
                        self.phase, label['text'] = 'fin', str(self.joueur_client.pseudo) + " a gagn??"
                    else:
                        label['text'] = "A l'adversaire !"
                        zone_dessin.after(100, self.recevoir_clic)

    def validation_clic(self, coords: tuple) -> bool:
        """
        M??thode qui renvoie si le clic est valide
        :param coords : tuple, coordonn??es du clic
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
        M??thode qui renvoie le r??sultat du tir : ?? l'eau / touch?? / coul??
        :param case : str, case du tir
        :return resultat : str, r??sultat du tir
        :return longueur : int, longueur du bateau ??ventuellement touch??
        """
        resultat, len_bateau = 'eau', 0  # valeurs par d??faut
        
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

    # --------------------------------------------------------------------------------------------------------------- #
    # --- POSE DES BATEAUX                                                                                            #
    # --------------------------------------------------------------------------------------------------------------- #

    def verifier_position_bateau(self, case_dep, case_fin, longueur_bateau) -> None:
        """
        M??thode qui v??rifie si la position des bateaux renseign??e sont valides
        :param case_dep : str, d??but de la position du bateau ?? poser
        :param case_fin : str, fin de la position du bateau ?? poser
        :param longueur_bateau : longueur du bateau attendue
        :return : None
        """
        if case_dep[0] == case_fin[0]:  # m??me lettre, pose horizontale
            if int(case_fin[1:]) - int(case_dep[1:]) < 0:
                case_fin, case_dep = case_dep, case_fin
            if int(case_fin[1:]) - int(case_dep[1:]) + 1 == longueur_bateau:
                self.poser_bateau(case_dep, case_fin)
            else:
                self.pop_up('Attention',
                            'Emplacement invalide: vous devez poser un bateau de taille ' + str(longueur_bateau))

        elif case_dep[1:] == case_fin[1:]:  # m??me num??ro, pose verticale
            if ord(case_fin[0]) - ord(case_dep[0]) < 0:
                case_fin, case_dep = case_dep, case_fin
            if ord(case_fin[0]) - ord(case_dep[0]) + 1 == longueur_bateau:
                self.poser_bateau(case_dep, case_fin)
            else:
                self.pop_up('Attention',
                            'Emplacement invalide: vous devez poser un bateau de taille ' + str(longueur_bateau))
        
        else: # pose en diagonale
            self.pop_up('Attention',
                        'Emplacement invalide: vous devez poser un bateau de taille ' + str(longueur_bateau))

    def poser_bateau(self, case_dep: str, case_fin: str) -> None:
        """
        Poser les bateaux sur son plateau de jeu
        :param case_dep : str, d??but de la position du bateau ?? poser
        :param case_fin : str, fin de la position du bateau ?? poser
        :return : None
        """
        cases_a_poser, cases_bateaux = [], []
        valide = True

        for cle, valeur in self.joueur_client.jeu.items():
            lettre, num_case = cle[0], int(cle[1:])

            if case_dep[0] == case_fin[0]:  # m??me lettre, pose horizontale
                if lettre == case_dep[0] and int(case_dep[1:]) <= num_case <= int(case_fin[1:]):
                    cases_a_poser.append(valeur)
                    cases_bateaux.append(lettre + str(num_case))

            else:  # m??me num??ro, pose verticale
                if num_case == int(case_dep[1:]) and ord(case_dep[0]) <= ord(lettre) <= ord(case_fin[0]):
                    cases_a_poser.append(valeur)
                    cases_bateaux.append(lettre + str(num_case))

        # on v??rifie que l'emplacement du bateau est valide
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

            # on met ?? jour la liste des cases interdites
            for case in cases_bateaux:
                for i in self.cases_adjacentes[case]:
                    self.joueur_client.cases_interdites.append(i)

            # on met ?? jour la liste des bateaux
            self.joueur_client.bateaux.append([case for case in cases_bateaux])

            if len(self.longueurs_bateaux) > 0:
                # on met ?? jour le message indiquant le nombre de bateaux ?? poser
                label['text'] = 'Poser un bateau de longueur ' + str(self.longueurs_bateaux[0])
            else:
                label['text'] = 'Que la bataille commence !'

        self.jouer_son('bateau')


# =================================================================================================================== #
# === FONCTIONS                                                                                                       #
# =================================================================================================================== #


def afficher_regles() -> None:
    """
    Fonction qui permet l'affichage des r??gles du jeu
    :param : None
    :return : None
    """
    global bouton_retour
    zone_dessin.itemconfig(fond, image=regles_image)
    bouton_jouer.destroy()
    bouton_quitter.destroy()
    bouton_regles.destroy()

    bouton_retour = Button(tk, image=image_bouton_retour, command=menu, cursor='pirate')
    bouton_retour.place(x=890, y=520)


def debut_jeu() -> None:
    """
    Fonction qui permet le lancement du jeu
    :param : None
    :return : None
    """
    global label

    var_pop_up = Toplevel()  # cr??ation de la fen??tre pop up

    # centre la fen??tre
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

    bouton_jouer.destroy()
    bouton_quitter.destroy()
    bouton_regles.destroy()

    zone_dessin.itemconfig(fond, image=board_image_sombre)
    zone_dessin.bind('<Button-1>', bataille_navale_client.detection_clic)

    font = tkinter.font.Font(family='Helvetica', size=14)

    pseudo_joueur = bataille_navale_client.joueur_client.pseudo
    Label(tk, text=pseudo_joueur, bg='#d1d0cb', fg='#142396', font=font).place(x=92, y=90)

    pseudo_ennemi = bataille_navale_client.ennemi_serveur.pseudo
    Label(tk, text=pseudo_ennemi, bg='#d1d0cb', fg='#142396', font=font).place(x=722, y=90)

    Button(tk, text='Mode sombre/clair', command=bataille_navale_client.changer_mode).place(x=940, y=550)

    # Message
    mess = 'Poser un bateau de longueur ' + str(bataille_navale_client.longueurs_bateaux[0])
    label = Label(tk, text=mess, bg='#d1d0cb', height=2, padx=2, pady=2, fg='#142396', font=font)
    label.pack(side=BOTTOM)

    # Jeu
    bataille_navale_client.coordonnees_cases()
    bataille_navale_client.init_cases_adjacentes()


def menu() -> None:
    """
    Fonction d??finissant le menu du jeu
    :param : None
    :return : None
    """
    global bouton_retour, bouton_jouer, bouton_regles, bouton_quitter

    bouton_retour.destroy()
    zone_dessin.itemconfig(fond, image=menu_image)
    bouton_jouer = Button(tk, image=image_bouton_jouer, command=debut_jeu, padx=204, pady=66, cursor='pirate')
    bouton_jouer.place(x=758, y=450)
    bouton_regles = Button(tk, image=image_bouton_regles, command=afficher_regles, padx=216, pady=67, cursor='pirate')
    bouton_regles.place(x=294, y=485)
    bouton_quitter = Button(tk, image=image_bouton_quitter, command=tk.destroy, padx=242, pady=67, cursor='pirate')
    bouton_quitter.place(x=60, y=484)


# =================================================================================================================== #
# === PROGRAMME PRINCIPAL                                                                                             #
# =================================================================================================================== #

# param??trage du son
mixer.init()
mixer.music.load('sons/pirate.mp3')
mixer.music.play(-1)

# GUI
tk = Tk()
tk.title("Bataille Navale")
zone_dessin = Canvas(width="1100", height="600", bg="white")
zone_dessin.pack()

# Centrer la fen??tre
nouveau_x, nouveau_y = int(tk.winfo_screenwidth() / 2) - 550, int(tk.winfo_screenheight() / 2) - 350
tk.geometry('1100x650+' + str(nouveau_x) + '+' + str(nouveau_y))

tk.resizable(width=False, height=False)

# Images et widgets
menu_image = PhotoImage(file="images/menu.gif")
fond = zone_dessin.create_image(550, 300, image=menu_image)
image_bouton_jouer = PhotoImage(file='images/jouer.gif')
bouton_jouer = Button(tk, image=image_bouton_jouer, command=debut_jeu, padx=204, pady=66, cursor='pirate')
bouton_jouer.place(x=758, y=450)
image_bouton_regles = PhotoImage(file='images/regles_bouton.gif')
bouton_regles = Button(tk, image=image_bouton_regles, command=afficher_regles, padx=216, pady=67, cursor='pirate')
bouton_regles.place(x=294, y=485)
image_bouton_quitter = PhotoImage(file='images/quitter.gif')
bouton_quitter = Button(tk, image=image_bouton_quitter, command=tk.destroy, padx=242, pady=67, cursor='pirate')
bouton_quitter.place(x=60, y=484)

regles_image = PhotoImage(file="images/regles.gif")
board_image_clair = PhotoImage(file="images/jeu.gif")
board_image_sombre = PhotoImage(file="images/jeu_2.gif")
image_bouton_retour = PhotoImage(file='images/retour.gif')

tk.mainloop()
mixer.music.stop()
