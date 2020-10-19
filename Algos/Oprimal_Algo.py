import pulp as p
import numpy as np
import Probleme_Representation.Probleme_Instance

class Optimal_Algo:

    def trouver_solution_optimale(self, probleme_instance):

        Rcapt = probleme_instance.Rcapt
        Rcom = probleme_instance.Rcom
        puis = probleme_instance.coord_puis
        capteurs = probleme_instance.coord_capteurs
        k = probleme_instance.k
        n = len(capteurs)
        distances, distances_puis = probleme_instance.calculer_distances()

        Lp_prob = p.LpProblem('k-couverture', p.LpMinimize)

        #On créée les variables du probleme d'optimisation en nombres entiers
        #pour i allant de 0 à n-1, x_i = 1 si il y a un capteur sur le site i, 0 sinon
        xs = [p.LpVariable("x{0}".format(i), cat="Binary")
              for i in range(n)]

        #On ajoute la fonction objectif
        objective = p.lpSum([xs[i] for i in range(n)])
        Lp_prob += objective

        #On ajoute les contraintes
        #La k-couverture est respectée
        for i in range(n):
            Lp_prob += p.lpSum([xs[j] * (distances[i, j] <= Rcapt) for j in range(0, n)]) >= k
        #Chaque site dispose d'un chemin vers le puis
        for i in range(n):



