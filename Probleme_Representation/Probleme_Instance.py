import numpy as np


class Probleme_Instance:

    def __init__(self, Rcapt, Rcom, k, coord_puis, coord_capteurs):
        self.Rcapt = Rcapt
        self.Rcom = Rcom
        self.k = k
        self.coord_puis = coord_puis
        self.coord_capteurs = coord_capteurs
        self.n = len(coord_capteurs)

    def calculer_distances(self):
        distances = np.zeros((self.n, self.n))
        distances_puis = np.zeros(self.n)
        for i in range(0, self.n):
            distances_puis[i] += ((self.coord_capteurs[i][0] - self.coord_puis[0]) ** 2 +
                                  (self.coord_capteurs[i][1] - self.coord_puis[1]) ** 2) ** 0.5
            for j in range(i + 1, self.n):
                distances[i, j] += ((self.coord_capteurs[i][0] - self.coord_capteurs[j][0]) ** 2 +
                                    (self.coord_capteurs[i][1] - self.coord_capteurs[j][1]) ** 2) ** 0.5
                distances[j, i] += distances[j, i]

        return distances, distances_puis
