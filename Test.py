from Algos import Heuristique, Algo_Genetique
from Probleme_Representation import Probleme_Instance
import numpy as np

filepath = "D:/Julien/Projets info/Algos\Instances/captANOR225_8_10.dat"
Rcapt = 1
Rcom = 1
k = 1

#Ajustements pour l'algorithme génétique
algorithm_param = {'max_num_iteration': 100,
                           'population_size': 100,
                           'mutation_probability': 0.1,
                           'elit_ratio': 0.01,
                           'crossover_probability': 0.5,
                           'parents_portion': 0.3,
                           'crossover_type': 'uniform',
                           'max_iteration_without_improv': None}

probleme_instance = Probleme_Instance.Probleme_Instance(Rcapt, Rcom, k, filepath)
algo_genetique = Algo_Genetique.Genetique(probleme_instance, algorithm_param)

algo_genetique.run()
print("nombre de capteurs placés : ", np.sum(algo_genetique.model.output_dict['variable']))
print("nombre de capteurs qui ne sont pas k_couverts : ", algo_genetique.erreur_compte(algo_genetique.model.output_dict['variable']))