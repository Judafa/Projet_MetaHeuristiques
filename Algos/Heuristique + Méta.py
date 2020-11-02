#Created by Renee on 10/20/20.

import pandas as pd
import math
from collections import OrderedDict
import pathlib
import time





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
'''Cette fonction prend en entrée une cible (paire de coordonnées), un dictionnaire qui représente la liste d'adjacence du graphe de captation et un ensemble D qui contient le cibles qui sont k-couvertes.
Elle retourne la qualité d'une cible qui est représentée par le nombre de voisins qui ne sont pas k-couverts inclu la cible elle-même'''
def qualite(cible, adj_capt, D):
    qual = 0
    if(cible not in D): #Si la cible n'est pas couverte elle contribue à sa qualité
            qual += 1
    for voisin in adj_capt[cible]:
        if(voisin not in D):
            qual += 1
    return qual






###Description de la fonction adjacence :
'''Cette fonction prend en entrée la liste des cibles, le rayon de captation et le rayon de communication et retourne deux listes d'adjacence sous forme de 2 dictionnaires :
    - La première associe à chaque cible (la clé) c1 une liste des cibles (la valeur) qui sont à une distance <= Rcapt de c1
    - La deuxième associe à chaque cible (la clé) c1 une liste des cibles (la valeur) qui sont à une distance <= Rcom de c1
'''
#Note : Comme (0.00, 0.00) (le puits) est une cible particulière qui n'a pas besoin d'être k-couverte, on choisit de ne pas l'inclure dans les listes des valeurs même si elle satisfait les conditions nécéssaires pour y être
#Toutefois elle est nécessairement présente comme clé dans la liste d'adjacence du graphe de communication car elle communique toujours avec au moins une autre cible
def adjacence(cibles, Rcapt, Rcom):
    adjacence_capt = {}
    adjacence_com = {}
    for cible1 in cibles:
        for cible2 in cibles:
            if(distance(cible1, cible2) <= Rcapt and cible1 != cible2 and cible2 != ("0.00","0.00")): #On n'inclut pas la cible elle-même dans sa liste des voisins
                ajouter_elem_a_dict_type1(adjacence_capt, cible1, cible2)
                ajouter_elem_a_dict_type1(adjacence_com, cible1, cible2)
            elif(distance(cible1, cible2) <= Rcom and cible1 != cible2 and cible2 != ("0.00","0.00")): #On n'inclut pas la cible elle-même dans sa liste des voisins
                ajouter_elem_a_dict_type1(adjacence_com, cible1, cible2)
    return (adjacence_capt, adjacence_com)





###Description de la fonction parcours :
'''C'est une fonction qui prend en entrée le dictionnaire représentant la liste d'adjacence de captation, le dictionnaire représentant la liste d'adjacence de communication et l'entier k qui précise le degré de couverture.
Cette fonction effectue un parcours de graphe tout au long duquel elle ajoute des capteurs en assurant la k-couverture de chaque cible parcourue et l'existence du chemin entre les cibles et le puits. (Plus d'explication dans le rapport).
Elle retourne C, len(C), cibles_nombre_capteurs, len(D) le tuple : (liste des cibles où on a des capteurs, nombre de capteurs, un dictionnaire indiquant pour chaque cible le nombre de capteurs qui la couvrent,
nombre de cibles k-couvertes)'''
def parcours(adjacence_capt, adjacence_com, k):
    W = []  #Liste qui va contenir les cibles qui ne sont pas encore explorées lors du parcours par profondeur
    D = set() #ensemble des cibles k-couvertes
    n = len(adjacence_com) - 1 #nombre total des cibles sans compter le puits
    p = list(adjacence_com.keys())[0] #Selon le format des données le puits est toujours la première clé
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
        '''a = 0 #nombre de cibles visitées ?
        for elem in cibles_visitées:
            if(cibles_visitées[elem]==1):
                a += 1'''

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
                return C, len(C), cibles_nombre_capteurs, len(D)
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
            return C, len(C), cibles_nombre_capteurs, len(D)
        else: #sinon on met à jour la cible courante pour qu'elle soit le dernier élément de W et on revient à la boucle while principale
            cible_courante = W.pop()
    return C, len(C), len(D)



def degre_couv(cible, adj_capt, C):
    s = 0
    for elem in adj_capt[cible]:
        if(elem in C):
            s += 1
    if(cible in C):
        s += 1
    return s

#Description de la fonction construire_chemin:
'''Cette fonction prend en entrée le disctionnaire représentant la liste d'adjacence de communication et la liste des capteurs pour retourner deux dictionnaires :
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





#essaye à la fin
'''def liste_pred_succ(pred, succ, capteur):
    liste_pred = []
    liste_liste_succ = []
    p = pred[capteur]
    while(True):
        liste_pred.append(p)
        if(p == ("0.00", "0.00")):
            break
        p = pred[p]
    s = succ[capteur]
    while(s in succ):
        liste_liste_succ.extend(s)
        s = succ[s]'''





###Description de la fonction post_traitement :
'''C'est une fonction qui prend en entrée un dictionnaire représentant la liste d'adjacence de captation, un autre représentant la liste d'adjacence de communication, le degré de couverture k, le dictionnaire de prédécesseurs
et le dictionnaire de successeurs définissant le chemin de communication, un dictionnaire indiquant le nombre de capteurs captant chaque cible, et une liste de capteurs.
Cette fonction parcourt les cibles et élimine les capteurs inutiles c.à.d les capteurs dont la supression n'affecte pas la réalisabilité de la solution.
Elle retourne la nouvelle liste de capteurs et le nouveau dictionnaire indiquanr pour chaque cible le degré de couverture.'''
def post_traitement(adj_capt, adj_com, k, preds, succs, C):
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
            pred = preds[capteur] #pred est le prédécesseur du capteur dans le chemin
            succ = succs[capteur] #succ est la liste des successeurs du capteur dans le chemin
            for elem in succ: #pour chaque successeur du capteur
                if(elem not in adj_com[pred]): #si le successeur ne peut pas communiquer avec pred alors le capteur est utile pour la communication (on peut faire mieux et vérifier la communication du successeur avec tous les preds de pred)
                    inutile = False
                    break
                '''#Mieux:
                    f = False
                    p = pred[pred]
                    while(p != ("0.00", "0.00")):
                        if(elem in  adj_com[p]):
                            f = True
                        p = pred[p]
                    if (f == False):
                        inutile = False
                        break #(on doit enlever le premier break)
                    elif(inutile == False):
                        inutile = True'''
        
        if(inutile == True): #si le capteur est inutile
            nouveau_C.remove(capteur)
    return nouveau_C





###Description de la fonction supprimer_ajouter :
'''C'est une fonction qui prend en entrée un capteur (paire de coordonnées), une liste de capteurs, un dictionnaire représentant une liste d'adjacence de captatio, un autre représentant une liste d'adjacence de communication,
un dictionnaire indiquant pour chaque cible le nombre de capteurs captant cette cible, un dictionnaire de prédécesseurs et de successeur décrivant un chemin de communication et le degré de couverture k.
Cette fonction permet de construire un élément du voisinage en supprimant un capteur et ajoutant un autre de façon à ce que la réalisabilité est conservée.
Elle retourne un tuple où le premier élément indique la réalisabilité de la nouvelle solution, le deuxième la nouvelle liste de capteurs et le troisième le dictionnaire indiquant pour chaque cible le nouveau nombre de capteurs
captant cette cible.'''
def supprimer_ajouter(capteur, C, adj_capt, adj_com, pred, succ, k):
    '''liste_cibles = list(adj_com.keys())
    for cible in liste_cibles:
                s = 0
                for elem in adj_capt[cible]:
                    if elem in C:
                        s += 1
                if(cible in C):
                    s += 1
                if(s < k):
                    print("in aj supp 1", cible)'''
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
    for voisin_capt in l:''' #un autre choix autre que celui ci dessous peut être parmi toutes les cibles
    for voisin_capt in adj_capt[capteur]: # on choisit le nouveau capteur parmi les voisins du capteur à supprimer
        valide = True #indique la validité du voisin pour être le nouveau capteur
        if(voisin_capt not in C): #si le voisin n'est pas dans C

            '''
            #Mieux:
            f = False
            p = pred[capteur]
            while(p != ("0.00", "0.00")):
                if(p in adj_com[voisin_capt] or voisin_capt in adj_com[("0.00", "0.00")]):
                    f = True
                    breaks
                p = pred[p]
            if(f == True):
            '''
            if(pred[capteur] in adj_com[voisin_capt] or voisin_capt in adj_com[("0.00", "0.00")]): #si le voisin peut communiquer avec le prédécesseur du capteur à supprimer ou directement avec le puits (on peut faire mieux)
                for elem in succ[capteur]: #pour chaque successeur du capteur
                    
                    if(elem not in adj_com[voisin_capt]): #si le successeur ne peut pas communiquer avec le nouveau capteur (on peut faire mieux)
                       valide = False #alors le voisin n'est pas valide
                    '''
                    #Mieux
                    val = False
                    p = pred[capteur]
                    while(p != ("0.00", "0.00")):
                        if(p in adj_com[elem] or elem in adj_com[("0.00", "0.00")]):
                            val = True
                            break
                        p = pred[p]
                    if(val == True and valide == False):
                        valide = True
                    '''
            
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
            '''liste_cibles = list(adj_com.keys())
            for cible in liste_cibles:
                s = 0
                for elem in adj_capt[cible]:
                    if elem in nouv_C:
                        s += 1
                if(cible in nouv_C):
                    s += 1
                if(s < k):
                    print("in aj supp 2", cible)'''
            break
    return (valide, nouv_C)





###Descritption de la fonction voisinage :
'''Cette fonction prend en entrée une liste de capteurs, un dictionnaire représentant la liste d'adjacence de captation, un autre représentant la liste d'adjacence de communication, un dictionnaire indiquant pour chaque cible
le nombre de capteurs captant cette cible, un dictionnaire de pédécesseurs et de successeurs définissant un chemin de communication et le degré de couverture k.
Cette fonction génère à partir d'une solution réalisable le voisinage formé par les éléments transformés et valides à partir de C.
Elle retourne une liste de listes de capteurs définissant le voisinage, un dictionnaire associant pour chaque élément de voisinage (par son indice) sa valeur, une liste des capteurs supprimés pour chaque élément du voisinage, et une liste de dictionnaires indiquant pour chaque élément du voisinage
le degré de couverture de chaque cible.'''
def voisinage(C, adj_capt, adj_com, pred, succ, k):
    voisinage = [] #va contenir des listes formant le voisinage de C
    valeurs_voisinage = {} #va contenir la valeur de chaque élément de voisinage après traitement
    #minimum = len(C) #variable qui va contenir la valeur minimale dans le voisinage
    #final_C = [] 
    capteurs_supprimés = []
    for capteur in C: #pour chaque capteur dans C
        existe, nouv_C = supprimer_ajouter(capteur, C, adj_capt, adj_com, pred, succ, k) #on effectue la transformation supprimer_ajouter
        if(existe == True): #si la transformation donne une liste rélisable
            nouv_pred, nouv_succ = construire_chemin(adj_com, nouv_C) #on construit le chemin de la transformation
            final_C = post_traitement(adj_capt, adj_com, k, nouv_pred, nouv_succ, nouv_C) #puis on élimine les capteurs inutiles
            voisinage.append(final_C) #on ajoute le résultat final dans le voisinage
            index = len(voisinage) - 1 #c'est l'indice de la liste ajoutée dans voisinage
            valeurs_voisinage[index] = len(final_C) #on ajoute la valeur de cette liste dans valeurs_voisinage
            capteurs_supprimés.append(capteur)      
    return voisinage, valeurs_voisinage, capteurs_supprimés





###Description de la fonction parcours_voisinage :
'''C'est une fonction qui prend en entrée une liste de capteurs, un dictionnaire représentant la liste d'adjacence de captation, un autre représentant la liste d'adjacence de communication, un autre indiquant le degré de couverture
pour chaque cible, le degré de couverture k et la taille de la liste tabou.
Cette fonction parcourt les voisinages tout en utilisant une liste tabou pour éviter la définition de certains voisinages.
Elle retourne le meilleur chemin trouvé lors du parcours, sa valeur, le nombre de voisinages explorés, la valeur initiale, et le nouveau dictionnaire des degrés de couverture.'''
def parcours_voisinages(C, adj_capt, adj_com, k, taille_tabou, nb_itérations):
    liste_tabou = []
    i = 0
    meilleur_chemin = C.copy()
    chemin_courant = C.copy()
    minimum = len(C) #va contenir le minimum par rapport à tous les voisinages
    meilleur_index = 0
    minimums = []
    meilleur_it = 0
    while(i < nb_itérations): #on explore au maximum len(C) voisinages
        minimums.append(minimum)
        if(vérifier_réalisabilité(adj_capt, adj_com, chemin_courant, k) == False):
            print(chemin_courant)
            print("**************************")
            print("Erreur : solution non réalisable")
        '''if(i > 80):
            print(chemin_courant)
            print("**************************")
            print(cnc_courant)'''
        #print(i)
        #print(minimum)
        #print(vérifier_cnc(adj_capt, chemin_courant, cnc_courant, list(cnc_courant.keys())))
        pred, succ = construire_chemin(adj_com, chemin_courant) #on trouve le chemin de la solution courante
        vois, vals, capteurs_supprimés = voisinage(chemin_courant, adj_capt, adj_com, pred, succ, k) #on trouve le voisinage de la solution courante
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
            meilleur_it = i
        if(len(liste_tabou) < taille_tabou): #traitement FIFO pour la liste tabou
            liste_tabou.append(capteurs_supprimés[min_index])
        else:
            liste_tabou.remove(liste_tabou[0])
            liste_tabou.append(capteurs_supprimés[min_index])
        chemin_courant = vois[min_index].copy()
        #print("Min local : ", min_local)
        i += 1
    return meilleur_chemin, minimum, meilleur_it, len(C), minimums





###Description de la fonction vérifier_réalisabilité :
'''C'est une fonction qui prend en entrée un dictionnaire représentant la liste d'adjacence de captation, un autre représentant la liste d'adjacence de communication, une liste de capteurs et le degré de couverture k.
Elle retourne True si C est réalisable et False sinon.'''
def vérifier_réalisabilité(adj_capt, adj_com, C, k):
    liste_cibles = list(adj_capt.keys())
    if(("0.00", "0.00")):
        liste_cibles.remove(("0.00", "0.00"))
    for elem in liste_cibles:
        s = 0
        for elem2 in adj_capt[elem]:
            if(elem2 in C):
                s = s + 1
        if(elem in C):
            s = s + 1
        if(s < k):
            print("here : ", elem)
            print(s)
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
        print("non comm")
        return False
    return True



def vérifier_cnc(adj_capt, C, cnc, liste_cibles):
    a = True
    for cible in liste_cibles:
        s = 0
        for voisin in adj_capt[cible]:
            if(voisin in C):
                s += 1
        if(cible in C):
            s += 1
        if(cnc[cible] != s):
            print(cible)
            a = False
            #return False
    return a


            
'''data = read_data("instances/captANOR625_12_100.dat")
adj_capt, adj_com = adjacence(data, 2, 2)
C, lc, cnc, ld = parcours(adj_capt, adj_com, 3)
print(vérifier_réalisabilité(adj_capt, adj_com, C, 3))
preds, succs = construire_chemin(adj_com, C)
nouv_C, final_cnc = post_traitement(adj_capt, adj_com, 3, preds, succs, cnc, C)
print(vérifier_réalisabilité(adj_capt, adj_com, nouv_C, 3))

#print("********************************************")
meilleur_chemin, minimum, i, lc, meilleur_cnc = parcours_voisinages(nouv_C, adj_capt, adj_com, final_cnc, 3, 3)
print(len(nouv_C))
print(minimum)'''

'''data = read_data("instances/captANOR625_12_100.dat")
adj_capt, adj_com = adjacence(data, 1, 2)
C, lc, ld = parcours(adj_capt, adj_com, 2)
print(vérifier_réalisabilité(adj_capt, adj_com, C, 2))
preds, succs = construire_chemin(adj_com, C)
nouv_C = post_traitement(adj_capt, adj_com, 2, preds, succs, C)
print(vérifier_réalisabilité(adj_capt, adj_com, nouv_C,2))

#print("********************************************")
meilleur_chemin, minimum, i, lc = parcours_voisinages(nouv_C, adj_capt, adj_com, 2, 1, 100)
print(len(nouv_C))
print(minimum)'''
                
              
'''for path in pathlib.Path("instances").iterdir():
    if path.is_file() and str(path) != "instances/.DS_Store":
        data = read_data(path)
        for k in [1,2,3]:
            adj_capt1 = adjacence(data, 1, 1)[0]
            adj_com1 = adjacence(data, 1, 1)[1]
            adj_capt2 = adjacence(data, 1, 2)[0]
            adj_com2 = adjacence(data, 1, 2)[1]
            adj_capt3 = adjacence(data, 2, 2)[0]
            adj_com3 = adjacence(data, 2, 2)[1]
            adj_capt4 = adjacence(data, 2, 3)[0]
            adj_com4 = adjacence(data, 2, 3)[1]
            f = open("results.txt", "a")
            time1 = time.time()
            f.write("File : " + str(path) + ", K = " + str(k) + ", Rcapt = " + str(1) + ", Rcom = " + str(1) + ", Resultat : " + str(parcours(adj_capt1, adj_com1, k)[1]) + ", Time : " + str(time.time() - time1) +  "\n")
            time2 = time.time()
            f.write("File : " + str(path) + ", K = " + str(k) + ", Rcapt = " + str(1) + ", Rcom = " + str(2) + ", Resultat : " + str(parcours(adj_capt2, adj_com2, k)[1]) + ", Time : " + str(time.time() - time2) +  "\n")
            time3 = time.time()
            f.write("File : " + str(path) + ", K = " + str(k) + ", Rcapt = " + str(2) + ", Rcom = " + str(2) + ", Resultat : " + str(parcours(adj_capt3, adj_com3, k)[1]) + ", Time : " + str(time.time() - time3) +  "\n")
            time4 = time.time()
            f.write("File : " + str(path) + ", K = " + str(k) + ", Rcapt = " + str(2) + ", Rcom = " + str(3) + ", Resultat : " + str(parcours(adj_capt4, adj_com4, k)[1]) + ", Time : " + str(time.time() - time4) +  "\n")
            f.write("***************** Amélioration ******************")
            f.write("\n")
            time11 = time.time()
            C1, lc1, ld1 = parcours(adj_capt1, adj_com1, k)
            preds1, succs1 = construire_chemin(adj_com1, C1)
            res1 = len(post_traitement(adj_capt1, adj_com1, k, preds1, succs1, C1))
            time12 = time.time()
            C2, lc2, ld2 = parcours(adj_capt2, adj_com2, k)
            preds2, succs2 = construire_chemin(adj_com2, C2)
            res2 = len(post_traitement(adj_capt2, adj_com2, k, preds2, succs2, C2))
            time22 = time.time()
            C3, lc3, ld3 = parcours(adj_capt3, adj_com3, k)
            preds3, succs3 = construire_chemin(adj_com3, C3)
            res3 = len(post_traitement(adj_capt3, adj_com3, k, preds3, succs3, C3))
            time33 = time.time()
            C4, lc4, ld4 = parcours(adj_capt4, adj_com4, k)
            preds4, succs4 = construire_chemin(adj_com4, C4)
            res4 = len(post_traitement(adj_capt4, adj_com4, k, preds4, succs4, C4))
            time44 = time.time()
            if(vérifier_réalisabilité(adj_capt1, adj_com1, C1, k) == False or vérifier_réalisabilité(adj_capt2, adj_com2, C2, k) == False or vérifier_réalisabilité(adj_capt3, adj_com3, C3, k) == False or vérifier_réalisabilité(adj_capt4, adj_com4, C4, k) == False):
                print("Erreur")
                
            
            f.write("Avant : " + str(lc1) + ", Après : " + str(res1) + ", K = " + str(k) + ", Rcapt = " + str(1) + ", Rcom = " + str(1) + ", File : " + str(path) + ", Time : " + str(time12 - time11) + "\n")
            f.write("Avant : " + str(lc2) + ", Après : " + str(res2) + ", K = " + str(k) + ", Rcapt = " + str(1) + ", Rcom = " + str(2) + ", File : " + str(path) + ", Time : " + str(time22 - time12) + "\n")
            f.write("Avant : " + str(lc3) + ", Après : " + str(res3) + ", K = " + str(k) + ", Rcapt = " + str(2) + ", Rcom = " + str(2) + ", File : " + str(path) + ", Time : " + str(time33 - time22) + "\n")
            f.write("Avant : " + str(lc4) + ", Après : " + str(res4) + ", K = " + str(k) + ", Rcapt = " + str(2) + ", Rcom = " + str(3) + ", File : " + str(path) + ", Time : " + str(time44 - time33) + "\n")
            f.write("\n")
            f.close()'''
                    
mins = {}
path = "instances/captANOR150_7_4.dat"
if str(path) != "instances/captANOR625_12_100.dat":
   data = read_data(path)
   for taille_tabou in [3]:
       for k in [1]:
            for (Rcapt, Rcom) in [(1, 1)]:
               f = open("resultsMeta_100_iterations.txt", "a")
               adj_capt, adj_com = adjacence(data, Rcapt, Rcom)
               print(path, " taille tabou    :    ", taille_tabou, ", k    :    ", k, ", Rcapt    :    ", Rcapt, "Rcom    :    ", Rcom)

               C, lc, ld = parcours(adj_capt, adj_com, k)
               f.write("Réalisabilité de la solution initiale : " + str(vérifier_réalisabilité(adj_capt, adj_com, C, k)))
               f.write("\n")
               preds, succs = construire_chemin(adj_com, C)
               nouv_C = post_traitement(adj_capt, adj_com, k, preds, succs, C)
               f.write("Réalisabilité de la solution après traitement : " + str(vérifier_réalisabilité(adj_capt, adj_com, nouv_C, k)))
               print(vérifier_réalisabilité(adj_capt, adj_com, nouv_C, k))
               f.write("\n")
               time1 = time.time()
               meilleur_chemin, minimum, i, lc, minimums = parcours_voisinages(nouv_C, adj_capt, adj_com, k, taille_tabou, 100)
               time2 = time.time()
               f.write("File : " + str(path) + ", K = " + str(k) + ", Rcapt = " + str(Rcapt) + ", Rcom = " + str(Rcom) + ", Resultat après parcours: " + str(minimum)
                       + ", Résultat initial : " + str(len(nouv_C)) + ", Time : " + str(time2 - time1) +  "\n")
               f.write("\n")
               f.close()
               mins[(str(path), taille_tabou, k, Rcapt, Rcom)] = minimums
f.close()

    
