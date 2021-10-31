import numpy as np


class Algo_Simplex:

    def __init__(self, c, b, C, version = "max"):
        if version == "min":
            self.sens = -1
        else:
            self.sens = 1
        self.c = np.concatenate((c, np.zeros((len(C)))))
        self.b = b
        self.C = np.concatenate((C, np.identity(len(C))), axis=1)
        self.nb_contraintes = len(self.C)
        self.nb_variables = len(self.C[0])
        self.base_indices = list(range(self.nb_variables - self.nb_contraintes, self.nb_variables))
        self.N_indices = list(range(0, self.nb_variables - self.nb_contraintes))
        self.B = self.C[:, self.base_indices]
        self.N = self.C[:, self.N_indices]


    def changer_base(self, variable_sortante, variable_entrante):
        self.base_indices = [variable_sortante if x == variable_entrante else x for x in self.base_indices]
        self.N_indices = [variable_entrante if x == variable_sortante else x for x in self.N_indices]
        self.B = self.C[:, self.base_indices]
        self.N = self.C[:, self.N_indices]


    def run_algo(self):

        BN = np.linalg.multi_dot((np.linalg.inv(self.B), self.N))
        D = self.c[self.N_indices] - np.linalg.multi_dot((self.c[self.base_indices], BN))
        infini = False
        while self.pas_tous_du_bon_signe(D) and not infini:
            #Choix e l'indice entrant
            max = -1 * self.sens * float('inf')
            indice_entrant = self.N_indices[0]
            for i in range(len(D)):
                if self.sens * D[i] > self.sens * max:
                    max = D[i]
                    indice_entrant = self.N_indices[i]

            #On vérifie le critère d'infinité de la solution
            pas_infini = False
            for e in BN[:, indice_entrant]:
                if e > 0:
                    pas_infini = True
            if not pas_infini:
                infini = True
            #Si ce n'est pas infini, on continue
            else:
                min = self.sens * float('inf')
                indice_sortant = 0
                for i in range(0, self.nb_contraintes):
                    if BN[i, indice_entrant] != 0:
                        if self.sens * self.b[i] / BN[i, indice_entrant] < self.sens * min:
                            min = self.b[i] / BN[i, indice_entrant]
                            indice_sortant = self.base_indices[i]
                self.changer_base(indice_entrant, indice_sortant)
                BN = np.linalg.multi_dot((np.linalg.inv(self.B), self.N))
                D = self.c[self.N_indices] - np.linalg.multi_dot((self.c[self.base_indices], BN))
        if infini:
            print("Le problème n'a pas de solution")
            return
        else:
            return np.linalg.multi_dot((np.transpose(self.c[self.base_indices]), np.linalg.inv(self.B), self.b))







    def pas_tous_du_bon_signe(self, D):
        for e in D:
            if e > 0:
                return True
        return False













