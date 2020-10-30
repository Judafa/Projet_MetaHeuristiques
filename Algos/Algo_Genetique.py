import random as rd
import numpy as np
import matplotlib
from Algos import Gen_Algo_Modified


class Genetique:

    def __init__(self, pbl_repr, algorithm_param):
        self.prl_repr = pbl_repr
        self.algorithm_param = algorithm_param
        self.model = None
        self.n = self.prl_repr.n
        self.k = self.prl_repr.k
        self.distances_Capt = self.prl_repr.distances_Capt
        self.distances_Com = self.prl_repr.distances_Com
        self.distances_puis = self.prl_repr.distances_puis

    # fonction a optimiser, pour l'instant moindres carrées
    def f(self, X):
        return np.sum(
            [np.sum((np.dot(X, self.distances_Capt[i])) - self.k) ** 2 for i in range(self.n)])

    def run(self):

        self.model = Gen_Algo_Modified.geneticalgorithm(function=self.f,
                                                        dimension=self.n,
                                                        variable_type='bool',
                                                        algorithm_parameters=self.algorithm_param)
        self.model.run()

    def erreur_compte(self, X):
        return np.sum(
            [np.sum(np.dot(X, self.distances_Capt[i])) < self.k for i in range(self.n)])
