

p = 10000
v = 1
for n in range(1, p//2):
    v *= (1 - 1/(p+1))

print(v)