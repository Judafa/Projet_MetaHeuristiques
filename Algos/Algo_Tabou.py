import pandas as pd
import math
from collections import OrderedDict
import pathlib
import time
import numpy as np


class Algo_Tabou:

    def __init__(self, Rcapt, Rcom, k, filepath):

        self.Rcapt = Rcapt
        self.Rcom = Rcom
        self.k = k
        self.path = filepath
        data = pd.read_csv(self.path, header=None, names=["coord"])  # il faut mettre les données dans le même folder que ce code

        self.toutes_les_cibles = np.zeros((len(data), 2))
        self.C = np.zeros((len(data)))
        i = 0
        while i < len(data):
            if i == len(data) - 1:  # On considère ce cas pour éliminer le ; de la dernière ligne du fichier
                cible = [float(data.loc[:]['coord'][i].split()[1]), float(data.loc[:]['coord'][i].split()[2][:len(data.loc[:]['coord'][i].split()[2]) - 1])]
            else:
                cible = [float(data.loc[:]['coord'][i].split()[1]), float(data.loc[:]['coord'][i].split()[2])]
            self.toutes_les_cibles[i, 0] = cible[0]
            self.toutes_les_cibles[i, 1] = cible[1]
            i += 1

        # On construit les dictionnaires de communication et de captation
        self.adjacence_capt = {}
        self.adjacence_com = {}
        for i in range(len(self.toutes_les_cibles)):
            for j in range(len(self.toutes_les_cibles)):
                if self.distance(self.toutes_les_cibles[i], self.toutes_les_cibles[j]) <= Rcapt and i != j and j != 0:  # On n'inclut pas la cible elle-même dans sa liste des voisins
                    self.ajouter_elem_a_dict_type1(self.adjacence_capt, i, j)

                if self.distance(self.toutes_les_cibles[i], self.toutes_les_cibles[j]) <= Rcom and i != j and j != 0:  # On n'inclut pas la cible elle-même dans sa liste des voisins
                    self.ajouter_elem_a_dict_type1(self.adjacence_com, i, j)



    def run(self, taille_tabou, nb_iterations):
        mins = {}

        lc, ld = self.parcours()
        print("Réalisabilité de la solution initiale : " + str(self.vérifier_réalisabilité(self.C)))
        print("\n")
        preds, succs = self.construire_chemin(self.C)
        self.post_traitement(preds, succs, self.C)
        print("Réalisabilité de la solution après traitement : " + str(self.vérifier_réalisabilité(self.C)))
        print(self.vérifier_réalisabilité(self.C))
        print("\n")
        time1 = time.time()
        meilleur_chemin, minimum, i, lc, minimums = self.parcours_voisinages(taille_tabou, nb_iterations)
        time2 = time.time()
        print("File : " + str(self.path) + ", K = " + str(self.k) + ", Rcapt = " + str(self.Rcapt) + ", Rcom = " + str(
                self.Rcom) + ", Resultat après parcours: " + str(minimum)
            + ", Résultat initial : " + str(sum(self.C)))

        mins[(str(self.path), taille_tabou, self.k, self.Rcapt, self.Rcom)] = minimums

    ###Description de la fonction parcours :
    '''C'est une fonction qui prend en entrée le dictionnaire représentant la liste d'adjacence de captation, le dictionnaire représentant la liste d'adjacence de communication et l'entier k qui précise le degré de couverture.
    Cette fonction effectue un parcours de graphe tout au long duquel elle ajoute des capteurs en assurant la k-couverture de chaque cible parcourue et l'existence du chemin entre les cibles et le puits. (Plus d'explication dans le rapport).
    Elle retourne C, len(C), cibles_nombre_capteurs, len(D) le tuple : (liste des cibles où on a des capteurs, nombre de capteurs, un dictionnaire indiquant pour chaque cible le nombre de capteurs qui la couvrent,
    nombre de cibles k-couvertes)'''
    def parcours(self):
        W = []  # Liste qui va contenir les cibles qui ne sont pas encore explorées lors du parcours par profondeur
        D = set()  # ensemble des cibles k-couvertes
        n = len(self.adjacence_com) - 1  # nombre total des cibles sans compter le puits
        p = list(self.adjacence_com.keys())[0]  # Selon le format des données le puits est toujours la première clé
        qualites_voisins_p = {}  # dictionnaire indiquant pour chaque voisin du puits dans le graphe de communication sa qualité
        for elem in self.adjacence_com[p]:
            qualites_voisins_p[elem] = self.qualite(elem, D)
        max_qualite = 0  # variable qui va contenir la qualité maximum d'un voisin du puits dans Gcom
        max_voisin = -1  # variable qui va contenir le voisin de p dans Gcom de qualité maximum
        for elem in qualites_voisins_p:
            if (qualites_voisins_p[elem] > max_qualite):
                max_voisin = elem
                max_qualite = qualites_voisins_p[elem]
        c = max_voisin  # c, le voisin de puits de qualité maximmum dans Gcom va être la première cible où on place le premier capteur
        self.C[c] = 1
        capteurs_cibles = {}  # dictionnaire qui pour chaque capteur indique une liste des cibles couvertes par ce capteur
        cibles_nombre_capteurs = {}  # dictionnaire qui pour chaque cible indique le nombre de capteurs qui la couvrent
        cibles_vois_c_com = {}  # nombre de voisins pour une cible qui sont à la fois dans Gcom et dans C
        cible_courante = c
        cibles_visitées = {}  # dictionnaire qui donne 1 comme valeur à une cible qui est a été visitée et 0 à une qui n'est pas encore visitée
        liste_cibles = list(self.adjacence_capt.keys())  # liste contenant les cibles
        if 0 in liste_cibles:
            liste_cibles.remove(0)

        for cible in liste_cibles:  # initialisation de cibles_visitées et cibles_vois_c_com où on met toutes les valeurs à 0
            cibles_visitées[cible] = 0
            cibles_vois_c_com[cible] = 0
        cibles_visitées[c] = 1  # la cible c a été visitée

        for cible in self.adjacence_capt[c]:  # Pour les voisins de c dans Gcapt
            self.ajouter_elem_a_dict_type1(capteurs_cibles, c, cible)  # on ajoute c dans la liste des capteurs qui couvrent chaque voisin dans le dictionnaire capteurs_cibles
            self.ajouter_elem_a_dict_type2(cibles_nombre_capteurs, cible)  # et on incrémente le nombre de capteurs qui couvrent chaque voisin dans cibles_nombre_capteurs
            if cibles_nombre_capteurs[cible] == self.k:  # Si pour un voisin de C on trouve qu'il est couvert par k capteurs on l'ajoute à l'ensemble D
                D.add(cible)

        for cible in self.adjacence_com[c]:  # Pour chaque voisin de c dans Gcom on incrémente le nombre de capteurs avec lesquels il peut communiquer dans cibles_vois_c_com
            self.ajouter_elem_a_dict_type2(cibles_vois_c_com, cible)

        for cible in self.adjacence_com[0]:  # Pour chaque voisin du puits dans Gcom on incrémente le nombre de capteurs avec lesquels il peut communiquer dans cibles_vois_c_com car le but c'est de communiquer avec le puits
            self.ajouter_elem_a_dict_type2(cibles_vois_c_com, cible)

        self.ajouter_elem_a_dict_type1(capteurs_cibles, c, c)  # On n'oublie pas d'ajouter le capteur c lui-même à la liste des cibles couvertes par c
        self.ajouter_elem_a_dict_type2(cibles_nombre_capteurs, c)  # On n'oublie pas d'incrémenter le nombre de capteurs couvrant c aussi
        if cibles_nombre_capteurs[c] == self.k:  # On teste si c est couvert par k capteurs après ces modifications et s'il l'est on l'ajoute à D
            D.add(c)

        self.ajouter_elem_a_dict_type2(cibles_vois_c_com, c)  # On incrémente aussi le nombre de capteurs avec qui c peut communiquer dans C (il fait partie de C)
        for elem in self.adjacence_com[p]:  # On ajoute les voisins de puits non explorés dans W
            if elem != c:
                W.append(elem)

        while len(D) != n:  # Tant qu'il y a des cibles non k-couvertes

            for voisin in self.adjacence_capt[cible_courante]:  # Pour tout voisin de captation de la cible courante, si ce voisin n'a pas été visité ni ajouté à W on l'ajoute
                if voisin not in W and cibles_visitées[voisin] == 0:
                    W.append(voisin)
            '''On peut supprimer cette partie et ne rien faire si cette condition est vérifiée et le parcours va se faire grâce à W'''
            if cibles_visitées[cible_courante] == 1:  # Si la cible courante a été visitée (c.à.d elle a été k-couverte donc on va passer à une autre)
                v = self.adjacence_capt[cible_courante][0]  # premier candidat à remplacer la cible courante (son premier voisin dans la liste d'adjacence de captation)
                m = len(self.adjacence_capt[cible_courante])
                i = 1

                while i < m and cibles_visitées[v] == 1:  # Si le candidat a été visité on parcours la liste de voisinage de captation jusqu'à ce qu'on trouve un voisin non visité pour remplacer la cible courante
                    v = self.adjacence_capt[cible_courante][i]
                    i += 1
                if cibles_visitées[v] == 1 and len(W) > 0:  # Dans le cas où on ne trouve aucun candidat non visité et si W n'est pas vide on parcours les éléments de W jusqu'à trouver une cible non visitée
                    v = W.pop()
                    while cibles_visitées[v] == 1 and len(W) > 0:  # Tant que le candidat courant et W contient toujours d'éléments on continue la recherche d'un remplaçant dans W
                        v = W.pop()
                    if cibles_visitées[v] == 0:  # Si la recherche termine et on trouve un candidat non visité on change la cible courante
                        cible_courante = v
                if cibles_visitées[v] == 1 and len(W) == 0:  # Si la recherche termine car W est devenue vide sans trouver un candidat non visité alors le parcours termine
                    return sum(self.C), cibles_nombre_capteurs, len(D)
                else:
                    cible_courante = v

            if cible_courante not in D:  # Si la cible courante n'est pas dans D (alors n'est pas visitée)

                s = 0  # variable qui va contenir le nombre de voisins de captation de cible courante qui sont des capteurs (donc le degré de captation de cible courante)
                for voisin in self.adjacence_capt[cible_courante]:
                    if self.C[voisin] == 1:
                        s += 1

                if self.C[cible_courante] == 1:  # On prend en considération la cible courante dans le degré de captation si elle a un capteur
                    s += 1

                if s < self.k:  # Si s < k alors la cible courante n'est pas k-couverte

                    voisins_capt = self.adjacence_capt[cible_courante].copy()
                    voisins_capt.append(cible_courante)  # On ajoute la cible courante à la liste des voisins de captation de la cible courante pour vérifier qu'elle est aussi captée

                    t = 0
                    nouv_capt = []
                    while t < self.k - s:
                        voisins_qualités = {}  # dictionnaire qui va associer à chaque voisin de captation de la cible courante et à la cible courante elle-même la qualité
                        for elem in voisins_capt:

                            if self.C[elem] == 0:  # On cherche la cible de meilleure qualité pour mettre le capteur alors on doit vérifier qu'il n'y a pas un capteur déjà installé sur cette cible

                                if cibles_vois_c_com[elem] > 0:  # pour assurer la communication (ceci signifie que pour l'élément considéré il a au moins un voisin de communication dans C ou il peut communiquer directement avec le puits)

                                    voisins_qualités[elem] = self.qualite(elem, D)

                        ordered_voisins_qualités = OrderedDict(sorted(voisins_qualités.items(),
                                                                      key=lambda kv: kv[1],
                                                                      reverse=True))  # tri par ordre décroissant de qualité

                        nc = list(ordered_voisins_qualités.keys())[0]  # on choisit la cible ayant la meilleure qualité

                        nouv_capt.append(nc)
                        self.C[nc] = 1  # on ajoute ces capteurs à C
                        self.ajouter_elem_a_dict_type2(cibles_vois_c_com, nc)  # car le capteur est dans C
                        for v_c2 in self.adjacence_com[nc]:  # pour tout voisin de communication du capteur on incrémente le nombre de capteurs de C avec lesquels ce voisin peut communiquer
                            self.ajouter_elem_a_dict_type2(cibles_vois_c_com, v_c2)
                        for v_c in self.adjacence_capt[nc]:  # pour chacun de ces voisins de captation
                            self.ajouter_elem_a_dict_type1(capteurs_cibles, nc, v_c)  # on ajoute ce capteur à la liste des capteurs de ce voisin

                            self.ajouter_elem_a_dict_type2(cibles_nombre_capteurs, v_c)  # et on incrémente le nombre de capteurs captant ce voisin dans cibles_nombre_capteurs

                            if cibles_nombre_capteurs[v_c] == self.k:  # puis on vérifie si ce voisin est k-couvert et s'il l'est on l'ajoute dans D
                                D.add(v_c)

                        self.ajouter_elem_a_dict_type1(capteurs_cibles, nc, nc)  # on fait le même pour le capteur lui même
                        self.ajouter_elem_a_dict_type2(cibles_nombre_capteurs, nc)
                        if cibles_nombre_capteurs[nc] == self.k:
                            D.add(nc)
                        t += 1

                D.add(cible_courante)  # cible courante est k-couverte donc on l'ajoute dans D

            cibles_visitées[cible_courante] = 1  # On indique qu'on a visité la cible courante

            if len(W) == 0:  # si W est vide alors le parcours termine
                return sum(self.C), cibles_nombre_capteurs, len(D)
            else:  # sinon on met à jour la cible courante pour qu'elle soit le dernier élément de W et on revient à la boucle while principale
                cible_courante = W.pop()
        return sum(self.C), len(D)

    ###Description de la fonction post_traitement :
    '''C'est une fonction qui prend en entrée un dictionnaire représentant la liste d'adjacence de captation, un autre représentant la liste d'adjacence de communication, le degré de couverture k, le dictionnaire de prédécesseurs
    et le dictionnaire de successeurs définissant le chemin de communication, un dictionnaire indiquant le nombre de capteurs captant chaque cible, et une liste de capteurs.
    Cette fonction parcourt les cibles et élimine les capteurs inutiles c.à.d les capteurs dont la supression n'affecte pas la réalisabilité de la solution.
    Elle retourne la nouvelle liste de capteurs et le nouveau dictionnaire indiquanr pour chaque cible le degré de couverture.'''

    def post_traitement(self, preds, succs, nouv_C):
        #nouveau_C = self.C.copy()

        for capteur in range(1, len(nouv_C)):  # Pour chaque capteur dans C
            if nouv_C[capteur] == 1:
                inutile = True
                if self.degre_couv(capteur) > self.k:  # si le capteur est couvert par un nombre de capteurs > k
                    for cible in self.adjacence_capt[capteur]:  # pour chaque cible captée par ce capteur
                        if self.degre_couv(cible) == self.k:  # si on a une cible qui est captée exactement par k capteurs alors ce capteur est utile
                            inutile = False
                            break
                else:  # si le capteur est capté exactement par k capteurs alors il est utile
                    inutile = False

                if inutile:  # si le capteur et ces voisins de captations sont tous captés par > k capteurs
                    pred = preds[capteur]  # pred est le prédécesseur du capteur dans le chemin
                    succ = succs[capteur]  # succ est la liste des successeurs du capteur dans le chemin
                    for elem in succ:  # pour chaque successeur du capteur
                        if (elem not in self.adjacence_com[
                            pred]):  # si le successeur ne peut pas communiquer avec pred alors le capteur est utile pour la communication (on peut faire mieux et vérifier la communication du successeur avec tous les preds de pred)
                            inutile = False
                            break

                if inutile:  # si le capteur est inutile
                    nouv_C[capteur] = 0
        return


    # Description de la fonction construire_chemin:
    '''Cette fonction prend en entrée le disctionnaire représentant la liste d'adjacence de communication et la liste des capteurs pour retourner deux dictionnaires :
        - Le premier affecte à chaque capteur le capteur prédécesseur
        - Le deuxième affecte à chaque capteur la liste de successeurs'''
    def construire_chemin(self, nouv_C):
        capt_a_0 = []  # On veut que la première cible du chemin soit le puits donc on cherche le deuxième capteur de façon à ce qu'il soit un voisin de communication du puits
        i = 1
        while i < len(nouv_C):
            if nouv_C[i] == 1 and 0 in self.adjacence_com[i]:
                capt_a_0.append(int(i))
                break
            i += 1

        succ = {}  # dictionnaire qui va contenir les successeurs
        for elem in range(1, len(nouv_C)):  # initialisation de succ
            succ[elem] = []

        succ[0] = capt_a_0  # On a déjà trouvé l'un des successeurs du puits
        ajouté = {}  # dictionnaire indiquant pour chaque capteur de C si ce capteur a été ajouté dans le chemin (autrement : il a un prédécesseur ajouté)
        pred = {}
        for e in capt_a_0:
            pred[e] = 0  # et alors le prédécesseur de ce successeur est le puits
            ajouté[e] = True
        for elem in range(1, len(nouv_C)):  # initialisation de ajouté
            if nouv_C[elem] == 1:
                ajouté[elem] = False
        nombre_restant = sum(nouv_C)  # le nombre restant des capteurs à ajouter dans le chemin
        i = 1
        while nombre_restant > 0:  # tant qu'il y a des capteurs non ajoutés dans le chemin
            #print(nombre_restant)
            if nombre_restant == 45:
                a = 1
            if nouv_C[int(i)] == 1:
                if not ajouté[i]:  # si le capteur i n'est pas ajouté
                    if i in self.adjacence_com[0]:  # s'il peut communiquer directement avec le puits
                        ajouté[i] = True  # on l'ajoute
                        pred[i] = 0  # on indique que son prédécesseur est le puits
                        succ[0].append(i)  # on l'ajoute à la liste de successeurs du puits
                        nombre_restant -= 1  # et on décrémente le nombre de capteurs restants

                    else:  # sinon
                        for voisin in self.adjacence_com[i]:  # pour chaque voisin de communication de ce ce capteur

                            if nouv_C[voisin] == 1:  # si le voisin est dans C

                                if ajouté[voisin]:  # et si le voisin a été ajouté dans le chemin
                                    ajouté[i] = True  # on ajoute le capteur dans le chemin
                                    pred[i] = voisin  # on précise que le prédécesseur du capteur est ce voisin
                                    succ[voisin].append(i)  # et on ajoute le capteur à la liste des successeurs du voisin
                                    nombre_restant -= 1  # finalement on décrémente le nombre restant
                                    break  # on sort de la boucle quand on ajoute le capteur
            j = i + 1
            while True:
                if nouv_C[j] == 1:
                    i = int(j)
                    break
                else:
                    j = (j + 1) % (len(nouv_C)-1)
                    if j == 0:
                        j = 1

        return pred, succ


    ###Description de la fonction supprimer_ajouter :
    '''C'est une fonction qui prend en entrée un capteur (paire de coordonnées), une liste de capteurs, un dictionnaire représentant une liste d'adjacence de captatio, un autre représentant une liste d'adjacence de communication,
    un dictionnaire indiquant pour chaque cible le nombre de capteurs captant cette cible, un dictionnaire de prédécesseurs et de successeur décrivant un chemin de communication et le degré de couverture k.
    Cette fonction permet de construire un élément du voisinage en supprimant un capteur et ajoutant un autre de façon à ce que la réalisabilité est conservée.
    Elle retourne un tuple où le premier élément indique la réalisabilité de la nouvelle solution, le deuxième la nouvelle liste de capteurs et le troisième le dictionnaire indiquant pour chaque cible le nouveau nombre de capteurs
    captant cette cible.'''
    def supprimer_ajouter(self, capteur, pred, succ):

        nouv_C = self.C.copy()
        à_couvrir = []  # va contenir les capteurs qu'on doit couvrir une fois on supprime le capteur en entrée
        for voisin_capt in self.adjacence_capt[capteur]:  # pour chaque voisin de captation de capteur
            if self.degre_couv(voisin_capt) == self.k:  # si le voisin est capté par par exactement k capteurs alors quand on va supprimer capteur on doit le couvrir par le nouveau capteur ajouté
                à_couvrir.append(voisin_capt)  # on l'ajoute alors à la liste à couvrir
        if self.degre_couv(capteur) == self.k:  # si le capteur lui-même est capté exactement par k capteur
            à_couvrir.append(capteur)  # on l'ajoute à la liste à couvrir

        for voisin_capt in self.adjacence_capt[capteur]:  # on choisit le nouveau capteur parmi les voisins du capteur à supprimer
            valide = True  # indique la validité du voisin pour être le nouveau capteur
            if nouv_C[voisin_capt] == 0:  # si le voisin n'est pas dans C

                if pred[capteur] in self.adjacence_com[voisin_capt] or voisin_capt in self.adjacence_com[0]:  # si le voisin peut communiquer avec le prédécesseur du capteur à supprimer ou directement avec le puits (on peut faire mieux)
                    for elem in succ[capteur]:  # pour chaque successeur du capteur

                        if elem not in self.adjacence_com[voisin_capt]:  # si le successeur ne peut pas communiquer avec le nouveau capteur (on peut faire mieux)
                            valide = False  # alors le voisin n'est pas valide

                else:  # si le voisin ne peut pas communique avec le prédécesseur de capteur ou avec le puits

                    valide = False  # alors il n'est pas valide
            else:  # si le voisin est dans C déjà alors il n'est pas valide
                valide = False

            if valide:  # si le voisin conserve la communication
                for elem in à_couvrir:  # pour tout élément de à couvrir

                    if elem not in self.adjacence_capt[voisin_capt] and elem != voisin_capt:  # si pour un élément différent du voisin cet élément n'est pas couvert par le voisin
                        valide = False  # alors le voisin n'est pas valide
                        break

            if valide:  # si le voisin est valide alors
                nouv_C[capteur] = 0  # on supprime le capteur
                nouv_C[voisin_capt] = 1 # on ajoute le voisin
                break
        return valide, nouv_C

    ###Descritption de la fonction voisinage :
    '''Cette fonction prend en entrée une liste de capteurs, un dictionnaire représentant la liste d'adjacence de captation, un autre représentant la liste d'adjacence de communication, un dictionnaire indiquant pour chaque cible
    le nombre de capteurs captant cette cible, un dictionnaire de pédécesseurs et de successeurs définissant un chemin de communication et le degré de couverture k.
    Cette fonction génère à partir d'une solution réalisable le voisinage formé par les éléments transformés et valides à partir de C.
    Elle retourne une liste de listes de capteurs définissant le voisinage, un dictionnaire associant pour chaque élément de voisinage (par son indice) sa valeur, une liste des capteurs supprimés pour chaque élément du voisinage, et une liste de dictionnaires indiquant pour chaque élément du voisinage
    le degré de couverture de chaque cible.'''
    def voisinage(self, pred, succ):
        voisinage = []  # va contenir des listes formant le voisinage de C
        valeurs_voisinage = {}  # va contenir la valeur de chaque élément de voisinage après traitement
        # minimum = len(C) #variable qui va contenir la valeur minimale dans le voisinage
        # final_C = []
        capteurs_supprimés = []

        for capteur in range(1, len(self.C)):  # pour chaque capteur dans C
            if self.C[capteur] == 1:
                existe, nouv_C = self.supprimer_ajouter(capteur, pred, succ)  # on effectue la transformation supprimer_ajouter
                if existe:  # si la transformation donne une liste rélisable
                    nouv_pred, nouv_succ = self.construire_chemin(nouv_C)  # on construit le chemin de la transformation
                    self.post_traitement(nouv_pred, nouv_succ, nouv_C)  # puis on élimine les capteurs inutiles
                    voisinage.append(nouv_C)  # on ajoute le résultat final dans le voisinage
                    index = len(voisinage) - 1  # c'est l'indice de la liste ajoutée dans voisinage
                    valeurs_voisinage[index] = sum(self.C)  # on ajoute la valeur de cette liste dans valeurs_voisinage
                    capteurs_supprimés.append(capteur)

        return voisinage, valeurs_voisinage, capteurs_supprimés

    ###Description de la fonction parcours_voisinage :
    '''C'est une fonction qui prend en entrée une liste de capteurs, un dictionnaire représentant la liste d'adjacence de captation, un autre représentant la liste d'adjacence de communication, un autre indiquant le degré de couverture
    pour chaque cible, le degré de couverture k et la taille de la liste tabou.
    Cette fonction parcourt les voisinages tout en utilisant une liste tabou pour éviter la définition de certains voisinages.
    Elle retourne le meilleur chemin trouvé lors du parcours, sa valeur, le nombre de voisinages explorés, la valeur initiale, et le nouveau dictionnaire des degrés de couverture.'''

    def parcours_voisinages(self, taille_tabou, nb_itérations):
        liste_tabou = []
        i = 0
        chemin_courant = self.C.copy()
        #chemin_courant = self.C.copy()
        minimum = sum(self.C)  # va contenir le minimum par rapport à tous les voisinages
        meilleur_index = 0
        minimums = []
        meilleur_it = 0
        while i < nb_itérations:  # on explore au maximum len(C) voisinages
            minimums.append(minimum)
            if not self.vérifier_réalisabilité(chemin_courant):
                print(self.C)
                print("**************************")
                print("Erreur : solution non réalisable")
            '''if(i > 80):
                print(chemin_courant)
                print("**************************")
                print(cnc_courant)'''
            # print(i)
            # print(minimum)
            # print(vérifier_cnc(adj_capt, chemin_courant, cnc_courant, list(cnc_courant.keys())))
            pred, succ = self.construire_chemin(self.C)  # on trouve le chemin de la solution courante
            # for i in range(0, len(self.C)):
            #     if self.C[i] == 1:
            #         a = pred[i]
            vois, vals, capteurs_supprimés = self.voisinage(pred, succ)  # on trouve le voisinage de la solution courante
            j = 0
            #vois2 = vois.copy()
            #capteurs_supprimés2 = capteurs_supprimés.copy()
            while j < len(vois):  # pour chaque liste du voisinage
                for capt in liste_tabou:  # pour chaque capteur dans la liste tabou
                    # print(len(capteurs_supprimés))
                    # print(len(vois))
                    if capt in vois[j]:  # si le capteur est dans la listes
                        del vois[j]  # on supprime cet élément de la liste du voisinage
                        capteurs_supprimés.remove(capteurs_supprimés[j])
                        break
                j += 1
            #vois = vois2.copy()
            #capteurs_supprimés = capteurs_supprimés2.copy()
            e = 0
            vals = {}  # on a modifié le voisinage don on doit mettre à jour le dictionnaire des valeurs
            while e < len(vois):
                vals[e] = len(vois[e])
                e += 1
            if len(vois) == 0:  # si le voisinage est vide on arrête les itérations
                break
            min_local = len(vois[0])  # va contenir le minimum local dans un voisinage
            min_index = 0
            for index in vals:  # si la valeur d'un élément est < min_local alors on met min_local à jour
                if vals[index] < min_local:
                    min_local = vals[index]
                    min_index = index
            if min_local < minimum:  # si le min_local < minimum on met minimum à jour
                minimum = min_local
                self.C = vois[min_index].copy()
                meilleur_it = i
            if len(liste_tabou) < taille_tabou:  # traitement FIFO pour la liste tabou
                liste_tabou.append(capteurs_supprimés[min_index])
            else:
                liste_tabou.remove(liste_tabou[0])
                liste_tabou.append(capteurs_supprimés[min_index])
            chemin_courant = vois[min_index].copy()
            # print("Min local : ", min_local)
            i += 1
        return self.C, minimum, meilleur_it, sum(self.C), minimums

    def degre_couv(self, cible):
        s = 0
        for elem in self.adjacence_capt[cible]:
            if self.C[elem] == 1:
                s += 1
        if self.C[cible] == 1:
            s += 1
        return s

    ###Description de la fonction vérifier_réalisabilité :
    '''C'est une fonction qui prend en entrée un dictionnaire représentant la liste d'adjacence de captation, un autre représentant la liste d'adjacence de communication, une liste de capteurs et le degré de couverture k.
    Elle retourne True si C est réalisable et False sinon.'''

    def vérifier_réalisabilité(self, nouv_C):
        liste_cibles = list(self.adjacence_capt.keys())
        if 0 in liste_cibles:
            liste_cibles.remove(0)
        for elem in liste_cibles:
            s = 0
            for elem2 in self.adjacence_capt[elem]:
                if nouv_C[elem2] == 1:
                    s = s + 1
            if nouv_C[elem] == 1:
                s = s + 1
            if s < self.k:
                print("here : ", elem)
                print(s)
                return False
        a = []
        for elem in range(1, len(nouv_C)):
            for elem2 in self.adjacence_com[elem]:
                if nouv_C[elem2] == 1:
                    a.append(elem)
                    break
            if elem in self.adjacence_com[0]:
                a.append(elem)
        s = []
        for i in range(1, len(nouv_C)):
            if nouv_C[i] == 1:
                s.append(i)
        if set(a) != set(s):
            print("non comm")
            return False
        return True

    def vérifier_cnc(self, cnc, liste_cibles):
        a = True
        for cible in liste_cibles:
            s = 0
            for voisin in self.adjacence_capt[cible]:
                if self.C[voisin] == 1:
                    s += 1
            if self.C[cible] == 1:
                s += 1
            if cnc[cible] != s:
                print(cible)
                a = False
                # return False
        return a





    ### Description de la fonction ajouter_elem_a_dict_type1 :
    '''C'est une fonction qui prend en entrée un dictionnaire d, un élément qu'on veut ajouter comme clé (ou modifier sa valeur) au dictionnaire et la valeur qu'on veut ajouter à la liste valeur de la clé (pas besoin de retourner, le dictionnaire
    est une structure immutable qui préserve la modification même si celle là a été effectuée dans une fonction)'''
    def distance(self, cible1, cible2):
        return math.sqrt((float(cible1[0]) - float(cible2[0])) ** 2 + (float(cible1[1]) - float(cible2[1])) ** 2)

    ### Description de la fonction ajouter_elem_a_dict_type1 :
    '''C'est une fonction qui prend en entrée un dictionnaire d, un élément qu'on veut ajouter comme clé (ou modifier sa valeur) au dictionnaire et la valeur qu'on veut ajouter à la liste valeur de la clé (pas besoin de retourner, le dictionnaire
    est une structure immutable qui préserve la modification même si celle là a été effectuée dans une fonction)'''
    def ajouter_elem_a_dict_type1(self, d, elem, val):
        if elem in d:
            d[elem].append(val)
        else:
            d[elem] = [val]

    ### Description de la fonction ajouter_elem_a_dict_type2 :
    '''C'est une fonction qui prend en entrée un dictionnaire d, un élément qu'on veut ajouter comme clé (ou modifier sa valeur) au dictionnaire et ajoute 1 à sa valeur'''
    def ajouter_elem_a_dict_type2(self, d, elem):
        if elem in d:
            d[elem] += 1
        else:
            d[elem] = 1

    ### Description de la qualite :
    '''Cette fonction prend en entrée une cible (paire de coordonnées), un dictionnaire qui représente la liste d'adjacence du graphe de captation et un ensemble D qui contient le cibles qui sont k-couvertes.
    Elle retourne la qualité d'une cible qui est représentée par le nombre de voisins qui ne sont pas k-couverts inclu la cible elle-même'''
    def qualite(self, cible, D):
        qual = 0
        if cible not in D:  # Si la cible n'est pas couverte elle contribue à sa qualité
            qual += 1
        for voisin in self.adjacence_capt[cible]:
            if voisin not in D:
                qual += 1
        return qual
