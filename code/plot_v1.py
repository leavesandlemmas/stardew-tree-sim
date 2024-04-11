import os
import numpy as np
import matplotlib.pyplot as plt 


background_color =np.array([255, 246, 229])/255 # 
tree_color = np.array([2,62,16])/255


def color(arr):
    out = np.empty(arr.shape + (3,))
    stage = arr/5
    for i in range(3):
        out[...,i] = background_color[i]*(1 - stage) + tree_color[i]*stage
    return out

def count(arr):
    shape = arr.shape[0], 6
    out = np.empty(shape,dtype='int64')
    for s in range(6):
        out[:,s] = (arr == s).sum(axis=(1,2))
    return out


wd = os.path.dirname(__file__)
load_path = os.path.join(wd,"../data/sim_v1.npy")
load_path = os.path.normpath(load_path)
arr = np.load(load_path)
arr_color = color(arr)

# count stages
counts = count(arr)
# count pop size
N = counts[:, 1:].sum(axis=1)
# Grid Sizr
Kmax = arr.shape[1]*arr.shape[2]
# Iterations to plot
nint = 4
iterations = np.linspace(
    arr.shape[0]/(nint+1), nint*arr.shape[0]/(nint+1), nint)
iterations = iterations.astype('int64')

fig, ax  =plt.subplots(1,3,sharex='row',figsize =(4*3,3))

ax[0].plot(N, label='Pop Size')
ax[0].plot(counts[:, 0],'--',label='Empty')



ax[0].axhline(Kmax, color='r', ls='dotted', label='Grid Size')
ax[0].axhline(Kmax* (1 - 0.01/0.15), color='C0', ls='dotted')


for s in [4,5]:
    ax[1].plot(counts[:, s],label="s={}".format(s))

ax[1].axhline(Kmax * 0.1772 *  (1 - 0.01/0.15),color='C1',ls='--')
ax[1].axhline(Kmax* 0.7792 * (1 - 0.01/0.15),color='C0',ls='--')

for s in [1,2,3]:   
    ax[2].plot(counts[:, s],label="s={}".format(s))

for ax__ in ax.ravel():
    for iteration in iterations:
        ax__.axvline(iteration, ls='dashdot', color='k')
    ax__.grid()    
    ax__.legend()
    ax__.set_xlabel('Iterations')
fig.set_tight_layout(True)


fig, ax  =plt.subplots(1,4,sharex='row',sharey='row',figsize =(4*4,4))

for i, iteration in enumerate(iterations):
    ax[i].set_title("Iteration: {}".format(iteration))
    ax[i].imshow(arr_color[iteration])

fig.set_tight_layout(True)


fig, ax  =plt.subplots(1,1,sharex='row')
ax.plot(N[:-1],np.diff(N))
ax.grid()


# fig, ax  =plt.subplots(1,4,figsize =(4*4,4))

# d = 30
# Ns = np.convolve(N, np.ones(d)/d, mode='same')

# K0 = 6420
# xx = np.linspace(0, N.max(), 101)
# alpha = 15
# yy = 4*alpha*xx/K0 *(1 - xx/K0)

# grow_prob = 0.2
# mort_prob = 0.01
# reprod_prob = 0.15
# xs  = np.empty((1201, 6))
# xs[0,0] = Kmax - 1
# xs[0,1] = 1
# xs[0,2:] = 0
# for i in range(1200):
#     recruit = xs[i,0]/Kmax * reprod_prob * xs[i, 5] 
#     xs[i+1, 0] = mort_prob * xs[i, 5] + xs[i,0] - recruit  
#     xs[i+1, 1] = recruit + (1 - grow_prob) * xs[i, 1]
#     xs[i+1, 2] = grow_prob * xs[i, 1] + (1 - grow_prob) * xs[i, 2]
#     xs[i+1, 3] = grow_prob * xs[i, 2] + (1 - grow_prob) * xs[i, 3]
#     prob_45 = grow_prob * (1 - xs[i, 5]/Kmax)**8
#     xs[i+1, 4] = grow_prob * xs[i, 3] + (1 - prob_45)*xs[i, 4]
#     xs[i+1, 5] = prob_45*xs[i,4]  + (1 - mort_prob) *xs[i, 5]
    

# ax[0].plot(N[:-1], np.diff(N), 'k.')
# ax[0].plot(Ns[:-d][:-1], np.diff(Ns[:-d]),  'C0.')
# ax[0].plot(xx, yy, 'r-')

# ax[1].plot(N,'k-')
# ax[1].plot(xs[:, 1:].sum(axis=1),'r')
# for i in range(3):
#     ax[2].plot(counts[:,i+1],ls='-', color='C{}'.format(i))
#     ax[2].plot(xs[:,i+1], ls='--', color='C{}'.format(i))

# for i in range(2):
#     ax[3].plot(counts[:,4+i],color='C{}'.format(i))
#     ax[3].plot(xs[:,4+i],ls='--', color='C{}'.format(i))
# for i, iteration in enumerate(iterations):
#     ax[i].set_title("Iteration: {}".format(iteration))
#     ax[i].imshow(arr_color[iteration])

# fig.set_tight_layout(True)

plt.show()