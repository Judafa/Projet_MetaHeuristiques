#Created by Renee on 10/20/20.

import pandas as pd
import math
from collections import OrderedDict

def read_data(filepath):
    data = pd.read_csv(filepath, header = None, names = ["coord"]) #mettre les données dans le même folder que ce code
    cibles = []
    i = 0
    while(i < len(data)):
        cible = (data.loc[:]['coord'][i].split()[1], data.loc[:]['coord'][i].split()[2])
        if(i == len(data) - 1):
            cible = (cible[0], cible[1][:len(cible[1]) - 1])
        cibles.append(cible)
        i += 1
    return cibles

def distance(cible1, cible2):
    return(math.sqrt((float(cible1[0]) - float(cible2[0]))**2+(float(cible1[1]) - float(cible2[1]))**2))

def adjacence(cibles, Rcapt, Rcom):
    adjacence_capt = {}
    adjacence_com = {}
    for cible1 in cibles:
        for cible2 in cibles:
            #print(distance(cible1, cible2))
            #print(distance(cible1, cible2) <= Rcapt)
            if(distance(cible1, cible2) <= Rcapt and cible1 != cible2 and cible2!=("0.00","0.00")):
                #print("here")
                if(cible1 in adjacence_capt):
                    adjacence_capt[cible1].append(cible2)
                else:
                    adjacence_capt[cible1] = [cible2]
                if(cible1 in adjacence_com):
                    adjacence_com[cible1].append(cible2)
                else:
                    adjacence_com[cible1] = [cible2]
            elif(distance(cible1, cible2) <= Rcom and cible1 != cible2 and cible2 != ("0.00","0.00")):
                if(cible1 in adjacence_com):
                    adjacence_com[cible1].append(cible2)
                else:
                    adjacence_com[cible1] = [cible2]
    return (adjacence_capt, adjacence_com)

def ajouter_elem_a_dict_type1(d, elem, val):
    if(elem in d):
        d[elem].append(val)
    else:
        d[elem] = [val]

def ajouter_elem_a_dict_type2(d, elem):
    if(elem in d):
        d[elem] += 1
    else:
        d[elem] = 1

def qualite(cible, adj_capt, D):
    qual = 0
    if(cible not in D):
            qual += 1
    for voisin in adj_capt[cible]:
        if(voisin not in D):
            qual += 1
    return qual
    

def parcours(adjacence_capt, adjacence_com, k):
    W = []
    D = set()
    n = len(adjacence_com) - 1 #sans compter le puits
    p = list(adjacence_com.keys())[0]
    qualites_voisins = {}
    for elem in adjacence_com[p]:
        qualites_voisins[elem] = qualite(elem, adjacence_capt, D)
    max_qualite = 0
    max_voisin = ("","")
    for elem in qualites_voisins:
        if(qualites_voisins[elem] > max_qualite):
            max_voisin = elem
    
    c = max_voisin
    C = [c]
    capteurs_cibles = {}
    cibles_nombre_capteurs = {}
    cibles_vois_c_com = {}
    cible_courante = c
    cibles_visitées = {}
    for cible in list(adjacence_capt.keys())[1:]:
        cibles_visitées[cible] = 0
        cibles_vois_c_com[cible] = 0
    cibles_visitées[c] = 1
    for cible in adjacence_capt[c]:
        ajouter_elem_a_dict_type1(capteurs_cibles, c, cible)
        ajouter_elem_a_dict_type2(cibles_nombre_capteurs, cible)
        if(cibles_nombre_capteurs[cible] == k):
                D.add(cible)
    for cible in adjacence_com[c]:
        ajouter_elem_a_dict_type2(cibles_vois_c_com, cible)
    ajouter_elem_a_dict_type1(capteurs_cibles, c, c)
    ajouter_elem_a_dict_type2(cibles_nombre_capteurs, c)
    if(cibles_nombre_capteurs[c] == k):
        D.add(c)
    ajouter_elem_a_dict_type2(cibles_vois_c_com, c)
    for elem in adjacence_com[p]:
        if(elem != c):
            W.append(elem)
    while(len(D) != n):
        #print("D, n : ",len(D), " ", n)
        #print("W : ", len(W))
        
        a = 0
        for elem in cibles_visitées:
            if(cibles_visitées[elem]==1):
                a += 1
        #print("visited : ", a)
        for voisin in adjacence_capt[cible_courante]:
            if(voisin not in W and cibles_visitées[voisin] == 0):
                W.append(voisin)
                #print("here")
        
        if(cibles_visitées[cible_courante] == 1):
            v = adjacence_capt[cible_courante][0]
            m = len(adjacence_capt[cible_courante])
            i = 1
            while(i < m and cibles_visitées[v] == 1):
                v = adjacence_capt[cible_courante][i]
                i += 1
            if(cibles_visitées[v] == 1 and len(W) > 0):
                v = W.pop()
                while(cibles_visitées[v] == 1 and len(W) > 0):
                    v = W.pop()
                if(cibles_visitées[v] == 0):
                    cible_courante = v
            if(cibles_visitées[v] == 1 and len(W) == 0):
                #print("here")
                #print(len(D))
                return C, len(C)
            else:
                cible_courante = v
        
        if(cible_courante not in D):
            s = 0
            for voisin in adjacence_capt[cible_courante]:
                if(voisin in C):
                    s += 1
            if(s < k):
                voisins_capt = adjacence_capt[cible_courante]
                voisins_capt.append(cible_courante)
                voisins_com_C = {}
                for elem in voisins_capt:
                    if(cibles_vois_c_com[elem]>0): #pour assurer la communication
                        '''degre_elem = 0
                        for voisin in adjacence_capt[elem]:
                            if(voisin not in D):
                                degre_elem += 1'''
                        voisins_com_C[elem] = qualite(elem, adjacence_capt, D)
                ordered_voisins_com_C = OrderedDict(sorted(voisins_com_C.items(), 
                                  key=lambda kv: kv[1], reverse=True))
                nouv_capt = list(ordered_voisins_com_C.keys())[:k-s]
                C.extend(nouv_capt)
                #print(C)
                for nouv_c in nouv_capt:
                    for v_c in adjacence_capt[nouv_c]:
                        ajouter_elem_a_dict_type1(capteurs_cibles, nouv_c, v_c)
                        ajouter_elem_a_dict_type2(cibles_nombre_capteurs, v_c)
                        if(cibles_nombre_capteurs[v_c] == k):
                            D.add(v_c)
                        ajouter_elem_a_dict_type2(cibles_vois_c_com, v_c)
                    ajouter_elem_a_dict_type1(capteurs_cibles, nouv_c, nouv_c)
                    ajouter_elem_a_dict_type2(cibles_nombre_capteurs, nouv_c)
                    if(cibles_nombre_capteurs[nouv_c] == k):
                        D.add(nouv_c)
                    for v_c2 in adjacence_com[nouv_c]:
                        ajouter_elem_a_dict_type2(cibles_vois_c_com, v_c2)
            D.add(cible_courante)
            
        cibles_visitées[cible_courante] = 1
        #print(C)
        if(len(W) == 0):
            return C
        else:
            #print(cible_courante, "not visited")
            cible_courante = W.pop()
            #print("nouvelle : ", cible_courante)
    return C, len(C), len(D)
                
                
                
            
    
                
                
                    
            
        
    
    
