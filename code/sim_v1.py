import numpy as np
import matplotlib.pyplot as plt
import os
from numba import njit
from scipy.signal import convolve

# GRID PARAMETERS 
ntree = 5 # number of tree growth stages
num =12*2  # size, linear dimension s
iterations = 800 # number of iterations to calculate

# INITIALIZE GRID
# grid size enforces 4:3 aspect ratio
arr_shape = (iterations+1, 3*num, 4*num )

arr = np.zeros(arr_shape, dtype='int64')

# place one stage-1 tree in the middle
x, y = round(1.5 *num), round(1.5*num)
arr[0, x, y] = 1

# RULE PARAMETERS
# neighborhoods : sets distance of spatial interaction 
growth_neighborhood = np.array([[1,1,1],[1,0,1],[1,1,1]])
reprod_neighborhood = np.ones((7,7),dtype='int64')
reprod_neighborhood[3,3] = 0 

# vital parameters  
reprod_prob = 0.15
grow_prob = 0.2
mort_prob = 0.01

def iterate(arr):
    out = np.empty_like(arr)

    S_5 = arr > 4  
    N_5 = convolve(S_5, growth_neighborhood, mode='same') 
    R_5 = convolve(S_5, reprod_neighborhood, mode='same')
    
    grow_reproduce(out, arr, N_5, R_5)
    return out

@njit
def grow_reproduce(out, arr, N5, R5):
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            s = arr[i,j]
            u = np.random.rand()
            if s == 0:
                out[i,j] = u < (R5[i,j]/48  *reprod_prob)
            if s == 5:
                out[i,j] = 5 * (u >= mort_prob)     
            if 1 <= s < 4:
                out[i,j] = s +  1 * (u < grow_prob)
            if s == 4:
                out[i,j] = s + (u < grow_prob) * (N5[i,j] < 1)

def simulate(arr):
    for n in range(iterations):
        arr[n+1] = iterate(arr[n])


simulate(arr)

wd = os.path.dirname(__file__)
path = os.path.join(wd,"../data/sim_v1.npy")
path = os.path.normpath(path)
np.save(path, arr)

print("FINISHED. Results saved to:", path,  sep="\n")