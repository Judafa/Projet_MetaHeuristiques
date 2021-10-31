import pandas as pd
import math
from collections import OrderedDict
import time


### Description de la fonction run_algo :
'''Utilisez cette fonction pour démarrer l'algorithme.
   filepath     : addresse relative du fichier, par exemple Algos/instances/captANOR900_15_20.dat
   Rcapt        : Rayon de captation
   Rcom         : Rayon de communication
   k            : degré de couvertue à atteindre
   taille_tabou : taille de la liste des tabous, typiquement 3 ou 7.
   temps_limite : critère d'arrêt. Peut être un temps (en MINUTES) ou un nombre d'itération de la métaheuristique, dépend de la valeur de condition
   condition    : détermine le critère d'arrêt. 0 si vous voulez un nombre maximum d'itération, 1 si vous voulez un temps maximal
   version      : détermine la méthode pour trouver, voisinage (1 ou 2)
   '''

def run_algo(filepath, Rcapt, Rcom, k, taille_tabou, temps_limite, condition=1, version=2):
    temps_limite *= 60
    data = read_data(filepath)

    adj_capt, adj_com = adjacence(data, Rcapt, Rcom)
    print("Résolution du problème au fichier : ", filepath, "\n taille tabou    :    ", taille_tabou, "\n k    :    ", k, "\n Rcapt    :    ", Rcapt,
          "\n Rcom    :    ", Rcom)

    C, lc, ld = parcours(adj_capt, adj_com, k)
    print("Réalisabilité de la solution initiale : " + str(
        vérifier_réalisabilité(adj_capt, adj_com, C, k)))
    preds, succs = construire_chemin(adj_com, C)
    nouv_C = post_traitement(adj_capt, adj_com, k, preds, succs, C, 2)
    print("Réalisabilité de la solution après traitement : " + str(
        vérifier_réalisabilité(adj_capt, adj_com, nouv_C, k)))
    t1 = time.time()
    meilleur_chemin, minimum, i, lc, minimums = parcours_voisinages(nouv_C, adj_capt, adj_com, k, taille_tabou, temps_limite, condition, version)
    t2 = time.time()
    print( "Algorithme terminé, resultat final : " + str(minimum)
            + "\n Résultat initial : " + str(len(nouv_C)) + "\n temps écoulé lors de la métaheuristique : " + str(
        t2 - t1) + "\n Taille tabou : " + str(taille_tabou) + "\n")



###Description de la fonction parcours :
'''C'est une fonction qui prend en entrée le dictionnaire représentant la liste d'adjacence de captation, le dictionnaire représentant la liste d'adjacence de communication et l'entier k qui précise le degré de couverture.
Cette fonction effectue un parcours de graphe tout au long duquel elle ajoute des capteurs en assurant la k-couverture de chaque cible parcourue et l'existence du chemin entre les capteurs et le puits. (Plus d'explication dans le rapport).
Elle retourne C, len(C), len(D)  : (liste des cibles où on a des capteurs, nombre de capteurs, nombre de cibles k-couvertes)'''
def parcours(adjacence_capt, adjacence_com, k):
    W = []  #Liste qui va contenir les cibles qui ne sont pas encore explorées lors du parcours par profondeur
    D = set() #ensemble des cibles k-couvertes
    n = len(adjacence_com) - 1 #nombre total des cibles sans compter le puits
    p = ("0.00", "0.00") #Selon le format des données le puits est toujours la première clé
    qualites_voisins_p = {} #dictionnaire indiquant pour chaque voisin du puits dans le graphe de communication sa qualité
    for elem in adjacence_com[p]:
        qualites_voisins_p[elem] = qualite(elem, adjacence_capt, D)
    max_qualite = 0 #variable qui va contenir la qualité maximum d'un voisin du puits dans Gcom
    max_voisin = ("","") #variable qui va contenir le voisin de p dans Gcom de qualité maximum
    for elem in qualites_voisins_p:
        if(qualites_voisins_p[elem] > max_qualite):
            max_voisin = elem
            max_qualite = qualites_voisins_p[elem]
    c = max_voisin #c, le voisin de puits de qualité maximmum dans Gcom va être la première cible où on place le premier capteur
    C = [c]
    capteurs_cibles = {} #dictionnaire qui pour chaque capteur indique une liste des cibles couvertes par ce capteur
    cibles_nombre_capteurs = {} #dictionnaire qui pour chaque cible indique le nombre de capteurs qui la couvrent
    cibles_vois_c_com = {} #nombre de voisins pour une cible qui sont à la fois dans Gcom et dans C
    cible_courante = c
    cibles_visitées = {} #dictionnaire qui donne 1 comme valeur à une cible qui est a été visitée et 0 à une qui n'est pas encore visitée
    liste_cibles = list(adjacence_capt.keys()) #liste contenant les cibles
    if(("0.00", "0.00") in liste_cibles):
        liste_cibles.remove(("0.00", "0.00"))
    for cible in liste_cibles: #initialisation de cibles_visitées et cibles_vois_c_com où on met toutes les valeurs à 0
        cibles_visitées[cible] = 0
        cibles_vois_c_com[cible] = 0
    cibles_visitées[c] = 1 #la cible c a été visitée
    for cible in adjacence_capt[c]: #Pour les voisins de c dans Gcapt
        ajouter_elem_a_dict_type1(capteurs_cibles, c, cible) #on ajoute c dans la liste des capteurs qui couvrent chaque voisin dans le dictionnaire capteurs_cibles
        ajouter_elem_a_dict_type2(cibles_nombre_capteurs, cible) #et on incrémente le nombre de capteurs qui couvrent chaque voisin dans cibles_nombre_capteurs
        if(cibles_nombre_capteurs[cible] == k): #Si pour un voisin de C on trouve qu'il est couvert par k capteurs on l'ajoute à l'ensemble D
                D.add(cible)
    for cible in adjacence_com[c]: #Pour chaque voisin de c dans Gcom on incrémente le nombre de capteurs avec lesquels il peut communiquer dans cibles_vois_c_com
        ajouter_elem_a_dict_type2(cibles_vois_c_com, cible)
    for cible in adjacence_com[("0.00", "0.00")]: #Pour chaque voisin du puits dans Gcom on incrémente le nombre de capteurs avec lesquels il peut communiquer dans cibles_vois_c_com car le but c'est de communiquer avec le puits
        ajouter_elem_a_dict_type2(cibles_vois_c_com, cible)
    ajouter_elem_a_dict_type1(capteurs_cibles, c, c) #On n'oublie pas d'ajouter le capteur c lui-même à la liste des cibles couvertes par c
    ajouter_elem_a_dict_type2(cibles_nombre_capteurs, c) #On n'oublie pas d'incrémenter le nombre de capteurs couvrant c aussi
    if(cibles_nombre_capteurs[c] == k): #On teste si c est couvert par k capteurs après ces modifications et s'il l'est on l'ajoute à D
        D.add(c)
    ajouter_elem_a_dict_type2(cibles_vois_c_com, c) #On incrémente aussi le nombre de capteurs avec qui c peut communiquer dans C (il fait partie de C)
    for elem in adjacence_com[p]: #On ajoute les voisins de puits non explorés dans W
        if(elem != c):
            W.append(elem)
            
   
    while(len(D) != n): #Tant qu'il y a des cibles non k-couvertes
        
        
        for voisin in adjacence_capt[cible_courante]: #Pour tout voisin de captation de la cible courante, si ce voisin n'a pas été visité ni ajouté à W on l'ajoute
            if(voisin not in W and cibles_visitées[voisin] == 0):
                W.append(voisin)
        '''On peut supprimer cette partie et ne rien faire si cette condition est vérifiée et le parcours va se faire grâce à W'''
        if(cibles_visitées[cible_courante] == 1): #Si la cible courante a été visitée (c.à.d elle a été k-couverte donc on va passer à une autre)
            v = adjacence_capt[cible_courante][0] #premier candidat à remplacer la cible courante (son premier voisin dans la liste d'adjacence de captation)
            m = len(adjacence_capt[cible_courante])
            i = 1
            while(i < m and cibles_visitées[v] == 1): #Si le candidat a été visité on parcours la liste de voisinage de captation jusqu'à ce qu'on trouve un voisin non visité pour remplacer la cible courante
                v = adjacence_capt[cible_courante][i]
                i += 1
            if(cibles_visitées[v] == 1 and len(W) > 0): #Dans le cas où on ne trouve aucun candidat non visité et si W n'est pas vide on parcours les éléments de W jusqu'à trouver une cible non visitée
                v = W.pop()
                while(cibles_visitées[v] == 1 and len(W) > 0): #Tant que le candidat courant et W contient toujours d'éléments on continue la recherche d'un remplaçant dans W
                    v = W.pop()
                if(cibles_visitées[v] == 0): #Si la recherche termine et on trouve un candidat non visité on change la cible courante
                    cible_courante = v
            if(cibles_visitées[v] == 1 and len(W) == 0): #Si la recherche termine car W est devenue vide sans trouver un candidat non visité alors le parcours termine
                return C, len(C), len(D)
            else:
                cible_courante = v
            
            
        if(cible_courante not in D): #Si la cible courante n'est pas dans D (alors n'est pas visitée)
            
                
            s = 0 #variable qui va contenir le nombre de voisins de captation de cible courante qui sont des capteurs (donc le degré de captation de cible courante)
            for voisin in adjacence_capt[cible_courante]:
                if(voisin in C):
                    s += 1
                
            
            if(cible_courante in C): #On prend en considération la cible courante dans le degré de captation si elle a un capteur
                s += 1
            
            if(s < k): #Si s < k alors la cible courante n'est pas k-couverte
                
                voisins_capt = adjacence_capt[cible_courante].copy()
                voisins_capt.append(cible_courante) #On ajoute la cible courante à la liste des voisins de captation de la cible courante pour vérifier qu'elle est aussi captée
                
                
                t = 0
                nouv_capt = []
                while(t < k-s):
                    voisins_qualités = {} #dictionnaire qui va associer à chaque voisin de captation de la cible courante et à la cible courante elle-même la qualité
                    for elem in voisins_capt:

                        if(elem not in C): #On cherche la cible de meilleure qualité pour mettre le capteur alors on doit vérifier qu'il n'y a pas un capteur déjà installé sur cette cible
                    
                            if(cibles_vois_c_com[elem]>0): #pour assurer la communication (ceci signifie que pour l'élément considéré il a au moins un voisin de communication dans C ou il peut communiquer directement avec le puits)
                                
                                voisins_qualités[elem] = qualite(elem, adjacence_capt, D)
                    
                    
                    ordered_voisins_qualités = OrderedDict(sorted(voisins_qualités.items(),
                                  key=lambda kv: kv[1], reverse=True)) #tri par ordre décroissant de qualité
                    
                    nc = list(ordered_voisins_qualités.keys())[0] #on choisit la cible ayant la meilleure qualité

                    
                    nouv_capt.append(nc)
                    C.append(nc) #on ajoute ces capteurs à C
                    ajouter_elem_a_dict_type2(cibles_vois_c_com, nc) #car le capteur est dans C
                    for v_c2 in adjacence_com[nc]: #pour tout voisin de communication du capteur on incrémente le nombre de capteurs de C avec lesquels ce voisin peut communiquer
                        ajouter_elem_a_dict_type2(cibles_vois_c_com, v_c2)
                    for v_c in adjacence_capt[nc]: #pour chacun de ces voisins de captation
                        ajouter_elem_a_dict_type1(capteurs_cibles, nc, v_c) #on ajoute ce capteur à la liste des capteurs de ce voisin
                        
                        ajouter_elem_a_dict_type2(cibles_nombre_capteurs, v_c) #et on incrémente le nombre de capteurs captant ce voisin dans cibles_nombre_capteurs
                        
                        if(cibles_nombre_capteurs[v_c] == k): #puis on vérifie si ce voisin est k-couvert et s'il l'est on l'ajoute dans D
                            D.add(v_c)
                    
                    ajouter_elem_a_dict_type1(capteurs_cibles, nc, nc) #on fait le même pour le capteur lui même
                    ajouter_elem_a_dict_type2(cibles_nombre_capteurs, nc)
                    if(cibles_nombre_capteurs[nc] == k):
                        D.add(nc)
                    t += 1
                
                    
                
            D.add(cible_courante) #cible courante est k-couverte donc on l'ajoute dans D
            
        cibles_visitées[cible_courante] = 1 #On indique qu'on a visité la cible courante
        
        if(len(W) == 0): #si W est vide alors le parcours termine
            return C, len(C), len(D)
        else: #sinon on met à jour la cible courante pour qu'elle soit le dernier élément de W et on revient à la boucle while principale
            cible_courante = W.pop()
    return C, len(C), len(D)




#Description de la fonction degre_couv:
'''Cette fonction prend en entrée une cible, le dictionnaire représentant la liste d'adjacence de captation du graphe, et une liste de capteurs et retourne pour une cible donnée le degré de couverture de cette cible'''
def degre_couv(cible, adj_capt, C):
    s = 0
    for elem in adj_capt[cible]:
        if(elem in C):
            s += 1
    if(cible in C):
        s += 1
    return s

#Description de la fonction construire_chemin:
'''Cette fonction prend en entrée le dictionnaire représentant la liste d'adjacence de communication et la liste des capteurs pour retourner deux dictionnaires :
    - Le premier affecte à chaque capteur le capteur prédécesseur
    - Le deuxième affecte à chaque capteur la liste de successeurs'''
def construire_chemin(adj_com, C):
    capt_a_0 = C[0] #On veut que la première cible du chemin soit le puits donc on cherche le deuxième capteur de façon à ce qu'il soit un voisin de communication du puits
    i = 0
    while(i < len(C)):
        if(("0.00", "0.00") in adj_com[C[i]]):
            capt_a_0 = C[i]
            break
        i += 1
    
    succ ={} #dictionnaire qui va contenir les successeurs
    for elem in C: #initialisation de succ
        succ[elem] = []
        
    succ[("0.00", "0.00")] = [capt_a_0] #On a déjà trouvé l'un des successeurs du puits
    pred = {capt_a_0 : ("0.00", "0.00")} #et alors le prédécesseur de ce successeur est le puits
    ajouté = {} #dictionnaire indiquant pour chaque capteur de C si ce capteur a été ajouté dans le chemin (autrement : il a un prédécesseur ajouté)
    for elem in C: #initialisation de ajouté
        ajouté[elem] = False
    ajouté[capt_a_0] = True #on a ajouté l'un des successeurs du puits
    nombre_restant = len(C) - 1 #le nombre restant des capteurs à ajouter dans le chemin
    i = 0
    while(nombre_restant > 0): #tant qu'il y a des capteurs non ajoutés dans le chemin
        #print(nombre_restant)
        if(ajouté[C[i]] == False): #si le capteur i n'est pas ajouté
            if(C[i] in adj_com[("0.00", "0.00")]): #s'il peut communiquer directement avec le puits
                    ajouté[C[i]] = True #on l'ajoute
                    pred[C[i]] = ("0.00", "0.00") #on indique que son prédécesseur est le puits
                    succ[("0.00", "0.00")].append(C[i]) #on l'ajoute à la liste de successeurs du puits
                    nombre_restant -= 1 #et on décrémente le nombre de capteurs restants
                        
            else: #sinon
                for voisin in adj_com[C[i]] : #pour chaque voisin de communication de ce ce capteur
                
                    if(voisin in C): #si le voisin est dans C
                    
                        if(ajouté[voisin] == True): #et si le voisin a été ajouté dans le chemin
                            ajouté[C[i]] = True #on ajoute le capteur dans le chemin
                            pred[C[i]] = voisin #on précise que le prédécesseur du capteur est ce voisin
                            succ[voisin].append(C[i]) #et on ajoute le capteur à la liste des successeurs du voisin
                            nombre_restant -= 1 #finalement on décrémente le nombre restant
                            break #on sort de la boucle quand on ajoute le capteur
        i = (i+1)%len(C) #tant qu'il y a des capteurs non ajoutés on va parcourir C pour pouvoir les ajouter
    return pred, succ





#Description de la fonction est_connexe:
'''Cette fonction prend en entrée : une liste de capteurs et le dictionnaire représentant la matrice d'adjacence de communication du graphe et retourne True si les capteurs avec le puits sont connexes et False sinon'''
def est_connexe(C, adj_com):
    liste_capteurs_parcourus = [("0.00", "0.00")]
    capteurs_visités = {}
    for elem in C:
        capteurs_visités[elem] = False
    pile = []
    for elem in adj_com[("0.00", "0.00")]:
        if(elem in C):
            pile.append(elem)
    while(len(pile) > 0):
        capteur_courant = pile.pop()
        liste_capteurs_parcourus.append(capteur_courant)
        capteurs_visités[capteur_courant] = True
        for voisin in adj_com[capteur_courant]:
            if(voisin in C):
                if(capteurs_visités[voisin] == False and voisin not in pile):
                    pile.append(voisin)
    if(len(liste_capteurs_parcourus) <= len(C)):
        return False
    else:
        return True
    
            
        
        
        
###Description de la fonction post_traitement :
'''C'est une fonction qui prend en entrée un dictionnaire représentant la liste d'adjacence de captation, un autre représentant la liste d'adjacence de communication, le degré de couverture k, le dictionnaire de prédécesseurs
et le dictionnaire de successeurs définissant le chemin de communication, une liste de capteurs et la version (1 pour la 1ere et 2 pour la 2eme utilisant la condition de connexité (améliorée)).
Cette fonction parcourt les cibles et élimine les capteurs inutiles c.à.d les capteurs dont la supression n'affecte pas la réalisabilité de la solution.
Elle retourne la nouvelle liste de capteurs.'''
def post_traitement(adj_capt, adj_com, k, preds, succs, C, version):
    nouveau_C = C.copy()
    
    for capteur in C: #Pour chaque capteur dans C
        inutile = True
        if(degre_couv(capteur, adj_capt, nouveau_C) > k) : #si le capteur est couvert par un nombre de capteurs > k
            for cible in adj_capt[capteur]: #pour chaque cible captée par ce capteur
                if(degre_couv(cible, adj_capt, nouveau_C) == k): #si on a une cible qui est captée exactement par k capteurs alors ce capteur est utile
                    inutile = False
                    break
        else: #si le capteur est capté exactement par k capteurs alors il est utile
            inutile = False
        
        if(inutile == True) : #si le capteur et ces voisins de captations sont tous captés par > k capteurs
            if(version == 1):
            #1ere version
                pred = preds[capteur] #pred est le prédécesseur du capteur dans le chemin
                succ = succs[capteur] #succ est la liste des successeurs du capteur dans le chemin
                for elem in succ: #pour chaque successeur du capteur
                    if(elem not in adj_com[pred]): #si le successeur ne peut pas communiquer avec pred alors le capteur est utile pour la communication (on peut faire mieux et vérifier la communication du successeur avec tous les preds de pred)
                        inutile = False
                        break
            if(version == 2):
            #2eme version
                C2 = nouveau_C.copy()
                C2.remove(capteur)
                if(est_connexe(C2, adj_com) == False):
                        inutile = False
            ###
                    
                    
        
        if(inutile == True): #si le capteur est inutile
            nouveau_C.remove(capteur)
        
    return nouveau_C





###Description de la fonction supprimer_ajouter :
'''C'est une fonction qui prend en entrée un capteur (paire de coordonnées), une liste de capteurs, un dictionnaire représentant une liste d'adjacence de captation, un autre représentant une liste d'adjacence de communication, un dictionnaire de prédécesseurs et de successeurs décrivant un chemin de communication, le degré de couverture k et la version utilisée (1 pour la 1ere et 2 pour la version améliorée utilisant la connexité).
Cette fonction permet de construire un élément du voisinage en supprimant un capteur et ajoutant un autre de façon à ce que la réalisabilité est conservée.
Elle retourne un tuple où le premier élément indique la réalisabilité de la nouvelle solution, et le deuxième la nouvelle liste de capteurs.'''
def supprimer_ajouter(capteur, C, adj_capt, adj_com, pred, succ, k, version):
    nouv_C = C.copy()
    à_couvrir = [] #va contenir les capteurs qu'on doit couvrir une fois on supprime le capteur en entrée
    for voisin_capt in adj_capt[capteur]: #pour chaque voisin de captation de capteur
        if(degre_couv(voisin_capt, adj_capt, nouv_C) == k): #si le voisin est capté par par exactement k capteurs alors quand on va supprimer capteur on doit le couvrir par le nouveau capteur ajouté
            à_couvrir.append(voisin_capt) #on l'ajoute alors à la liste à couvrir
    if(degre_couv(capteur, adj_capt, nouv_C) == k): #si le capteur lui-même est capté exactement par k capteur
        à_couvrir.append(capteur) #on l'ajoute à la liste à couvrir
    
    
    '''l = list(adj_capt.keys())
    if(("0.00", "0.00") in l):
        l.remove(("0.00", "0.00"))
    for voisin_capt in l:''' #un autre choix autre que celui ci dessous peut être parmi toutes les cibles mais l'autre donne de meilleures solutions
    for voisin_capt in adj_capt[capteur]: # on choisit le nouveau capteur parmi les voisins du capteur à supprimer
        valide = True #indique la validité du voisin pour être le nouveau capteur
        if(voisin_capt not in C): #si le voisin n'est pas dans C
        
            #2eme version
            if(version == 2):
                C2 = C.copy()
                C2.remove(capteur)
                C2.append(voisin_capt)
                if(est_connexe(C2, adj_com)):
                    valide = True
                else:
                    valide = False
            ###
            #1ere version
            if(version == 1):
                if(pred[capteur] in adj_com[voisin_capt] or voisin_capt in adj_com[("0.00", "0.00")]): #si le voisin peut communiquer avec le prédécesseur du capteur à supprimer ou directement avec le puits (on peut faire mieux)
                    for elem in succ[capteur]: #pour chaque successeur du capteur
                        
                        if(elem not in adj_com[voisin_capt]): #si le successeur ne peut pas communiquer avec le nouveau capteur (on peut faire mieux)
                           valide = False #alors le voisin n'est pas valide
                        
                        
                        
                
                else: #si le voisin ne peut pas communique avec le prédécesseur de capteur ou avec le puits
                    
                    valide = False #alors il n'est pas valide
        else: #si le voisin est dans C déjà alors il n'est pas valide
            valide = False
        
        if(valide == True): #si le voisin conserve la communication
            for elem in à_couvrir: #pour tout élément de à couvrir
                
                if(elem not in adj_capt[voisin_capt] and elem != voisin_capt): #si pour un élément différent du voisin cet élément n'est pas couvert par le voisin
                    valide = False #alors le voisin n'est pas valide
                    break
        if(valide == True): #si le voisin est valide alors
            nouv_C.remove(capteur) #on supprime le capteur
            nouv_C.append(voisin_capt) #on ajoute le voisin
            
            break
    return (valide, nouv_C)





###Descritption de la fonction voisinage :
'''Cette fonction prend en entrée une liste de capteurs, un dictionnaire représentant la liste d'adjacence de captation, un autre représentant la liste d'adjacence de communication, un dictionnaire de pédécesseurs et de successeurs définissant un chemin de communication, le degré de couverture k et la version utilisée pour le post-traitement et la création d'un voisinage (1 pour la 1ere et 2 pour l'améliorée)
Cette fonction génère à partir d'une solution réalisable le voisinage formé par les éléments transformés et valides à partir de C.
Elle retourne une liste de listes de capteurs définissant le voisinage, un dictionnaire associant pour chaque élément de voisinage (par son indice) sa valeur, une liste des capteurs supprimés pour chaque élément du voisinage.'''
def voisinage(C, adj_capt, adj_com, pred, succ, k, version):
    voisinage = [] #va contenir des listes formant le voisinage de C
    valeurs_voisinage = {} #va contenir la valeur de chaque élément de voisinage après traitement
    #minimum = len(C) #variable qui va contenir la valeur minimale dans le voisinage
    #final_C = []
    capteurs_supprimés = []
    for capteur in C: #pour chaque capteur dans C
        existe, nouv_C = supprimer_ajouter(capteur, C, adj_capt, adj_com, pred, succ, k, version) #on effectue la transformation supprimer_ajouter
        if(existe == True): #si la transformation donne une liste rélisable
            nouv_pred, nouv_succ = construire_chemin(adj_com, nouv_C) #on construit le chemin de la transformation
            final_C = post_traitement(adj_capt, adj_com, k, nouv_pred, nouv_succ, nouv_C, version) #puis on élimine les capteurs inutiles
            
    
            voisinage.append(final_C) #on ajoute le résultat final dans le voisinage
            index = len(voisinage) - 1 #c'est l'indice de la liste ajoutée dans voisinage
            valeurs_voisinage[index] = len(final_C) #on ajoute la valeur de cette liste dans valeurs_voisinage
            capteurs_supprimés.append(capteur)
    return voisinage, valeurs_voisinage, capteurs_supprimés





###Description de la fonction parcours_voisinage :
'''C'est une fonction qui prend en entrée une liste de capteurs, un dictionnaire représentant la liste d'adjacence de captation, un autre représentant la liste d'adjacence de communication, le degré de couverture k, la taille de la liste tabou, le nombre des itérations maximal (ou le temps d'exécution maximal (selon la condition)), la condition qui est un entier (si sa valeur est 1 on active la condition d'arrêt temporel sinon on laisse la condition d'arrêt selon les itérations), la version qui est un entier = 1 ou 2 (1 pour effectuer le post traitement et la création du voisinage en utilisant la première et 2 pour le faire en utilisant la première)
Cette fonction parcourt les voisinages tout en utilisant une liste tabou pour interdire le parcours de certains voisinages.
Elle retourne le meilleur chemin trouvé lors du parcours, sa valeur, le nombre de voisinages explorés jusqu'à la meilleure solution, la valeur initiale, et une liste des minimums rencontrés à chaque itération.'''
def parcours_voisinages(C, adj_capt, adj_com, k, taille_tabou, nb_itérations, condition, version):
    liste_tabou = []
    i = 0
    meilleur_chemin = C.copy()
    chemin_courant = C.copy()
    minimum = len(C) #va contenir le minimum par rapport à tous les voisinages
    meilleur_index = 0
    minimums = []
    meilleur_it = 0
    #pour la condition d'arrêt temporelle
    if(condition == 1):
        t1 = time.time()
        t2 = 3
    i = 0
    r = 0
    while(i < nb_itérations): #on explore au maximum nb_itérations voisinages
        minimums.append(minimum)
        
        if(vérifier_réalisabilité(adj_capt, adj_com, chemin_courant, k) == False):
            print(chemin_courant)
            print("**************************")
            print("Erreur : solution non réalisable")
            
        pred, succ = construire_chemin(adj_com, chemin_courant) #on trouve le chemin de la solution courante
        vois, vals, capteurs_supprimés = voisinage(chemin_courant, adj_capt, adj_com, pred, succ, k, version) #on trouve le voisinage de la solution courante
        j = 0
        vois2 = vois.copy()
        capteurs_supprimés2 = capteurs_supprimés.copy()
        while(j < len(vois)): #pour chaque liste du voisinage
            for capt in liste_tabou: #pour chaque capteur dans la liste tabou
                #print(len(capteurs_supprimés))
                #print(len(vois))
                if(capt in vois[j]): #si le capteur est dans la listes
                    vois2.remove(vois[j]) #on supprime cet élément de la liste du voisinage
                    capteurs_supprimés2.remove(capteurs_supprimés[j])
                    break
            j += 1
        vois = vois2.copy()
        capteurs_supprimés = capteurs_supprimés2.copy()
        e = 0
        vals = {} #on a modifié le voisinage don on doit mettre à jour le dictionnaire des valeurs
        while(e < len(vois)):
            vals[e] = len(vois[e])
            e += 1
        if(len(vois) == 0): #si le voisinage est vide on arrête les itérations
            break
        min_local = len(vois[0]) #va contenir le minimum local dans un voisinage
        min_index = 0
        for index in vals: #si la valeur d'un élément est < min_local alors on met min_local à jour
            if(vals[index] < min_local):
                min_local = vals[index]
                min_index = index
        if(min_local < minimum): #si le min_local < minimum on met minimum à jour
            minimum = min_local
            meilleur_chemin = vois[min_index].copy()
            meilleur_it = r
        if(len(liste_tabou) < taille_tabou): #traitement FIFO pour la liste tabou
            liste_tabou.append(capteurs_supprimés[min_index])
        else:
            liste_tabou.remove(liste_tabou[0])
            liste_tabou.append(capteurs_supprimés[min_index])
        chemin_courant = vois[min_index].copy()
        
        
        if(condition == 1):
            t2 = time.time()
            if(t2 - t1 > nb_itérations):
                break
        else:
            i += 1
        r+=1
    return meilleur_chemin, minimum, meilleur_it, len(C), minimums





###Description de la fonction vérifier_réalisabilité :
'''C'est une fonction qui prend en entrée un dictionnaire représentant la liste d'adjacence de captation, un autre représentant la liste d'adjacence de communication, une liste de capteurs et le degré de couverture k.
Elle retourne True si C est réalisable et False sinon.'''
def vérifier_réalisabilité(adj_capt, adj_com, C, k):
    liste_cibles = list(adj_capt.keys())
    if(("0.00", "0.00") in liste_cibles):
        liste_cibles.remove(("0.00", "0.00"))
    for elem in liste_cibles:
        s = 0
        for elem2 in adj_capt[elem]:
            if(elem2 in C):
                s = s + 1
        if(elem in C):
            s = s + 1
        if(s < k):
            return False
    a = []
    for elem in C:
        for elem2 in adj_com[elem]:
            if(elem2 in C):
                a.append(elem)
                break
        if(elem in adj_com[("0.00", "0.00")]):
            a.append(elem)
    if(set(a) != set(C)):
        return False
    return True


### Description de la fonction read_data :
'''Fonction qui prend en entrée le path du fichier des données et retourne une liste des cibles (une cible est une paire de coordonnées)'''
def read_data(filepath):
    data = pd.read_csv(filepath, header = None, names = ["coord"]) #il faut mettre les données dans le même folder que ce code
    cibles = []
    i = 0
    while(i < len(data)):
        cible = (data.loc[:]['coord'][i].split()[1], data.loc[:]['coord'][i].split()[2])
        if(i == len(data) - 1): #On considère ce cas pour éliminer le ; de la dernière ligne du fichier
            cible = (cible[0], cible[1][:len(cible[1]) - 1])
        cibles.append(cible)
        i += 1
    return cibles


###Description de la fonction adjacence :
'''Cette fonction prend en entrée la liste des cibles, le rayon de captation et le rayon de communication et retourne deux listes d'adjacence sous forme de 2 dictionnaires :
    - Le premier associe à chaque cible (la clé) c1 une liste des cibles (la valeur) qui sont à une distance <= Rcapt de c1
    - Le deuxième associe à chaque cible (la clé) c1 une liste des cibles (la valeur) qui sont à une distance <= Rcom de c1
'''
#Note : Comme (0.00, 0.00) (le puits) est une cible particulière qui n'a pas besoin d'être k-couverte, on choisit de ne pas l'inclure dans les listes des valeurs même si elle satisfait les conditions nécéssaires pour y être
#Toutefois elle est nécessairement présente comme clé dans la liste d'adjacence du graphe de communication car elle communique toujours avec au moins une autre cible
def adjacence(cibles, Rcapt, Rcom):
    adjacence_capt = {}
    adjacence_com = {}
    for cible in cibles:
        if(cible != ("0.00", "0.00")):
            adjacence_capt[cible] = []
            adjacence_com[cible] = []
    for cible1 in cibles:
        for cible2 in cibles:
            if(distance(cible1, cible2) <= Rcapt and cible1 != cible2 and cible2 != ("0.00","0.00")): #On n'inclut pas la cible elle-même dans sa liste des voisins
                ajouter_elem_a_dict_type1(adjacence_capt, cible1, cible2)
                ajouter_elem_a_dict_type1(adjacence_com, cible1, cible2)
            elif(distance(cible1, cible2) <= Rcom and cible1 != cible2 and cible2 != ("0.00","0.00")): #On n'inclut pas la cible elle-même dans sa liste des voisins
                ajouter_elem_a_dict_type1(adjacence_com, cible1, cible2)
    return (adjacence_capt, adjacence_com)





### Description de la fonction distance :
'''Cette fonction prend en entrée deux cibles (une paire de coordonnées) et retourne la distance euclidienne entre ces deux cibles'''
def distance(cible1, cible2):
    return(math.sqrt((float(cible1[0]) - float(cible2[0]))**2+(float(cible1[1]) - float(cible2[1]))**2))



### Description de la fonction ajouter_elem_a_dict_type1 :
'''C'est une fonction qui prend en entrée un dictionnaire d, un élément qu'on veut ajouter comme clé (ou modifier sa valeur) au dictionnaire et la valeur qu'on veut ajouter à la liste valeur de la clé (pas besoin de retourner, le dictionnaire
est une structure immutable qui préserve la modification même si celle là a été effectuée dans une fonction)'''
def ajouter_elem_a_dict_type1(d, elem, val):
    if(elem in d):
        d[elem].append(val)
    else:
        d[elem] = [val]





### Description de la fonction ajouter_elem_a_dict_type2 :
'''C'est une fonction qui prend en entrée un dictionnaire d, un élément qu'on veut ajouter comme clé (ou modifier sa valeur) au dictionnaire et ajoute 1 à sa valeur'''
def ajouter_elem_a_dict_type2(d, elem):
    if(elem in d):
        d[elem] += 1
    else:
        d[elem] = 1





### Description de la qualite :
'''Cette fonction prend en entrée une cible (paire de coordonnées), un dictionnaire qui représente la liste d'adjacence du graphe de captation et un ensemble D qui contient les cibles qui sont k-couvertes.
Elle retourne la qualité d'une cible qui est représentée par le nombre de voisins qui ne sont pas k-couverts en comptant en plus la cible elle-même'''
def qualite(cible, adj_capt, D):
    qual = 0
    if(cible not in D): #Si la cible n'est pas couverte elle contribue à sa qualité
            qual += 1
    for voisin in adj_capt[cible]:
        if(voisin not in D):
            qual += 1
    return qual




