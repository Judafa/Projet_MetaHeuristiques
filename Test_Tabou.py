from Algos import Algo_Tabou

filepath = "instances/captANOR150_7_4.dat"
Rcapt = 1
Rcom = 1
k = 1
nb_iterations = 100
taille_tabou = 3

algo_tabou = Algo_Tabou.Algo_Tabou(Rcapt, Rcom, k, filepath)
algo_tabou.run(taille_tabou, nb_iterations)