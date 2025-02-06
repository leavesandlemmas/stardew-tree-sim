import numpy as np

def simulate(n0, steps, gridsize, theta=0.2, beta=0.15, mu=0.01):
    out = np.empty((steps +1,6), int)
    out[0] = n0 
    for i in range(steps):
        prob_empty_size = out[i,0]/gridsize
        x10 = np.random.binomial(out[i,5], beta*prob_empty_size)
        x12 = np.random.binomial(out[i,1], theta)
        x23 = np.random.binomial(out[i,2], theta)
        x34 = np.random.binomial(out[i,3], theta)
        
        prob_no_5 = (1 - out[i,5]/gridsize)**8
        x45 = np.random.binomial(out[i,3], theta * prob_no_5)
        x50 = np.random.binomial(out[i,5], mu)

        out[i+1,0] = out[i,0] + x50 - x10 
        out[i+1,1] = out[i,1] + x10 - x12
        out[i+1,2] = out[i,2] + x12 - x23 
        out[i+1,3] = out[i,3] + x23 - x34
        out[i+1,4] = out[i,4] + x34 - x45
        out[i+1,5] = out[i,5] + x45 - x50

    return out
        

