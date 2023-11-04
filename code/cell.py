import math
import numpy as np 
from scipy.signal import convolve
from numba import vectorize, njit 
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# PARAMETERS
grow_chance = 0.2
mort_chance = 0.01
reproduce_chance = 0.15

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



@vectorize('int64(int64,int64, int64[:])')
def growth(y, n5, r):
    s, t = to_tuple(y)

    u = np.random.rand()
    if y == 0:
        # reproduces? 
        rs = r.sum()
        r_cdf = np.cumsum(r/rs)
        yes = u < rs/48 * reproduce_chance
        if yes:
            v = np.random.rand()
            return from_tuple(1, np.argmax(v < r_cdf))
        return y
    
    
    if u < mort_chance:
        return 0

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
        R = np.array([convolve(arr == from_tuple(5,n), moore, mode='same') for n in range(nt) ]) 
        out[...] = growth(out, N5, R)
    return out  

def generate(iterations, arr0):
    arr = np.empty((iterations + 1, ) + arr0.shape,dtype='int64')
    arr[0] = arr0
    for i in range(iterations):
        N5 = convolve(arr[i] >  from_tuple(4, 0), moore, mode='same')

        arr[i+1] = growth(arr[i], N5)
    return arr 


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
arr0 = 1* (np.random.rand(3*size,4*size) < 0.3) + 1*(np.random.rand(3*size,4*size) < 0.3)
# arr1 = simulate(5, arr0)
iterations = 50
arr = generate(iterations, arr0)


fig , ax =plt.subplots(1,2, figsize=(12,4))

fig.suptitle('Stardew Valley Tree Sim')
im = ax[0].imshow(plot(arr[0],cols))


ts = np.arange(iterations+1)
pops = np.empty((iterations+1,2*5 + 1))
for i in range(2*5+1):
    pops[:,i] = np.sum(arr == i,axis=(1,2))


popsize = np.empty((iterations+1,3))
for i in range(2):
    popsize[:,i+1] = pops[:, 2*(1 + np.arange(5)) + i - 1].sum(axis=1)
popsize[:,0] = popsize[:,1] + popsize[:,2]
cs = ['k'] + list(cols)
lines = [ax[1].plot(ts[0], popsize[0,i], color=cs[i])[0] for i in range(3)] 


def animate(i):
    imdata = plot(arr[i], cols)
    im.set_data(imdata)
    for j in range(3):
        lines[j].set_data(ts[:i],popsize[:i,j])
    ax[1].set_ylim(-1,1.1*popsize[i,0]+10)
    ax[1].set_xlim(0,ts[i]+1)
    return im, lines

ax[0].set_title('Grid')
ax[1].set_ylabel('Popsize')
ax[1].set_xlabel('Time (days)')
ani = FuncAnimation(fig, animate,frames=arr.shape[0])
# fig.set_tight_layout(True)
plt.show()

# fig, ax = plt.subplots(1, 3)

# ax[0].imshow(plot(arr1))
# ax[1].imshow(arr1 >= 9, cmap = 'Reds')

# N = convolve(arr1 >= 9, moore, 'same')
 
# ax[2].imshow(0.2*(arr1 == from_tuple(4,0))*(N < 1), cmap = 'Blues')



# fig,ax =plt.subplots()
# ss = np.array([np.sum(N == i) for i in range(10)])

# ns = np.arange(10)
# ax.plot(ns,ss/ss.sum(),'-o')
# ax.plot(ns,binom.pmf(ns,9,grow_chance),'-o')


# print( np.sum(arr1 >= 9)/(64*48))
# print(ss)
# plt.show()