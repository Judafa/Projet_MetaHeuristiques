from Algos import Algo_Simplex
import numpy as np
#
# c = np.array([6, 4])
# C = np.array([[-3, 2], [3, 2], [1, 0]])
# b = np.array([4, 16, 3])
#
# s = Algo_Simplex.Algo_Simplex(c, b, C, "min")
# print(s.run_algo())

e = 0
for i in range(0,10000000):
    e += (-1)**i * 1 / (2*i+1)
print(4*e)