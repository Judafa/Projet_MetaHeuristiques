import numpy as np
import pandas as pd


class Probleme_Instance:

    def __init__(self, Rcapt, Rcom, k, filepath):
        self.Rcapt = Rcapt
        self.Rcom = Rcom
        self.k = k

        data = pd.read_csv(filepath, header=None, names=["coord"])  # mettre les données dans le même folder que ce code
        self.n = len(data) - 1
        self.coord_puis = np.asarray([float(data.loc[:]['coord'][0].split()[1]), float(data.loc[:]['coord'][0].split()[2])])
        self.coord_capteurs = np.zeros((self.n, 2))
        for i in range(1, self.n):
            self.coord_capteurs[i][0] = float(data.loc[:]['coord'][i].split()[1])
            self.coord_capteurs[i][1] = float(data.loc[:]['coord'][i].split()[2])
        self.distances_Capt, self.distances_Com, self.distances_puis = self.calculer_distances()

    def calculer_distances(self):
        distances_Com = np.zeros((self.n, self.n))
        distances_Capt = np.zeros((self.n, self.n))
        distances_puis = np.zeros(self.n)
        for i in range(0, self.n):
            distances_puis[i] = ((self.coord_capteurs[i][0] - self.coord_puis[0]) ** 2 +
                                 (self.coord_capteurs[i][1] - self.coord_puis[1]) ** 2) ** 0.5 <= self.Rcom
            for j in range(i + 1, self.n):
                distances_Capt[i, j] = ((self.coord_capteurs[i][0] - self.coord_capteurs[j][0]) ** 2 +
                                        (self.coord_capteurs[i][1] - self.coord_capteurs[j][
                                            1]) ** 2) ** 0.5 <= self.Rcapt
                distances_Capt[j, i] = distances_Capt[j, i]

                distances_Com[i, j] = ((self.coord_capteurs[i][0] - self.coord_capteurs[j][0]) ** 2 +
                                       (self.coord_capteurs[i][1] - self.coord_capteurs[j][
                                           1]) ** 2) ** 0.5 <= self.Rcom
                distances_Com[j, i] = distances_Com[j, i]

        return distances_Capt, distances_Com, distances_puis
