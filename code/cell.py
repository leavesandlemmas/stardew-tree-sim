import numpy as np 
from scipy.signal import convolve
from numba import vectorize, njit 
import matplotlib.pyplot as plt 
from scipy.stats import binom

# PARAMETERS
grow_chance = 0.2
mort_chance = 0.01


# number of types
nt = 2 

@njit
def from_tuple(s,t):
    return nt*s + t  - 1

@njit
def to_tuple(y):
    s = (y - 1) // nt + 1 # stage 
    t = (y - 1) % nt # type
    return s, t  

moore = np.ones((3,3), dtype='int64')
# moore[1,1] = 0 

moore_big = np.ones((5,5), dtype='int64')
# moore_big[3,3] = 0 


von_neumann = np.zeros((3,3),dtype='int64')
for i in range(3):
    for j in range(3):
        von_neumann[i,j] = ( (i - 1)**2 + (j - 1)**2 <= 1)



@vectorize('int64(int64,int64)')
def growth(y, n5):
    s, t = to_tuple(y)

    if s == 0:
        return y
    
    u = np.random.rand()
    if u < mort_chance:
        return 1

    if 1 <= s < 4:
        return from_tuple(s + (u < grow_chance) , t)
    if s == 4:
        # grow if stage 4 and no stage 5 neighbors 
        return from_tuple(s + (u < grow_chance) * (n5 == 0), t)

    return y

def iterate(arr):
    N5 = convolve(arr >  from_tuple(4, 0), moore)
    return growth(arr, N5)


def simulate(iterations, arr):
    out = arr.copy()
    for _ in range(iterations):
        N5 = convolve(out >  from_tuple(4, 0), moore, mode='same')
        out[...] = growth(out, N5)
    return out  
 
cols = np.array([[2,62,16], [200*0.75,30*0.75,80*0.75]])/255
    
def plot(arr, cols=cols):
    bgc =np.array([255, 246, 229])/255

    s, t = to_tuple(arr)

    out = np.empty(arr.shape + (3,))
    for i in range(3):
        uu = s/5
        out[...,i] = bgc[i]*(1- uu) + cols[t,i]*uu
    return out

size = 12
arr0 = np.ones((3*size,4*size), dtype='int64')
arr1 = simulate(5, arr0)

fig, ax = plt.subplots(1, 3)

ax[0].imshow(plot(arr1))
ax[1].imshow(arr1 >= 9, cmap = 'Reds')

N = convolve(arr1 >= 9, moore, 'same')
 
ax[2].imshow(0.2*(arr1 == from_tuple(4,0))*(N < 1), cmap = 'Blues')



fig,ax =plt.subplots()
ss = np.array([np.sum(N == i) for i in range(10)])

ns = np.arange(10)
ax.plot(ns,ss/ss.sum(),'-o')
ax.plot(ns,binom.pmf(ns,9,grow_chance),'-o')


print( np.sum(arr1 >= 9)/(64*48))
print(ss)
plt.show()