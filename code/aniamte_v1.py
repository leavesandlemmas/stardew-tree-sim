import os
import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.animation import FuncAnimation




background_color =np.array([255, 246, 229])/255 # 
tree_color = np.array([2,62,16])/255


def color(arr):
    out = np.empty(arr.shape + (3,))
    stage = arr/5
    for i in range(3):
        out[...,i] = background_color[i]*(1 - stage) + tree_color[i]*stage
    return out

def animate(i):  
    im.set_data(arr_color[i])
    return im

wd = os.path.dirname(__file__)
path = os.path.join(wd,"../data/sim_v1.npy")
path = os.path.normpath(path)
arr = np.load(path)
arr_color = color(arr)


fig , ax =plt.subplots(1,1, figsize=(4,3))

fig.suptitle('Stardew Valley Tree Sim')
im = ax.imshow(arr_color[0])
ax.set_title('Grid')

ani = FuncAnimation(fig, animate,frames=arr.shape[0])
# fig.set_tight_layout(True)
plt.show()
# ani.save("D:/OneDrive/Programming/CellularAutomata/stardewvalley_trees_sim_mahogany.mp4")