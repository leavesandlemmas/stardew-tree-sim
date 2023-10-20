from webbrowser import get
import numpy as np
import matplotlib.pyplot as plt


def get_transition_matrix(stages):
    A = np.zeros((stages,stages))
    for i in range(stages - 1):
        A[i+1,i] = 0.2
        A[i,i] = 0.8
    A[-1,-1] = 1.
    return A


def iterate(num, transition_matrix):
    A = transition_matrix.copy()
    prob = np.empty((num, transition_matrix.shape[0]))
    prob[0,0] = 1.
    prob[0,1:] =0.

    for n in range(num-2):
        
        prob[n+1] = A[:,0]
        np.dot(transition_matrix, A, out= A) 
         

    prob[-1] = A[:,0]
    return prob

def calculate_pmf(num, transition_matrix):
    pmf = np.empty(num)
    for k in range(num):
        pmf[k] =  transition_matrix[-1,:-1] @  np.linalg.matrix_power(transition_matrix[:-1,:-1],k-1)[:,0] if k > 0 else 0.0
    return pmf

def calculate_stats(pmf,cmf):
    out = dict()

    out['mean'] = sum( n * p for n, p in enumerate(pmf))
    out['variance'] = sum((n - out['mean'])**2 * p for n, p in enumerate(pmf))
    out['median'] = np.argmax(cmf >= 0.5 )
    
    out['std'] = np.sqrt(out['variance'])
    return out 

At = get_transition_matrix(5)
print(At)
days = np.arange(2*28)
prob = iterate(days.shape[0], At)
pmf = calculate_pmf(days.shape[0], At)
stats = calculate_stats(pmf, prob[:,-1])
print(stats)

fig, axes = plt.subplots(1,2,figsize=(4*2,3),sharex='row')
fig.suptitle('Growing times')
ax = axes[0]
for n in range(5):
    ax.plot(days,100*prob[:,n], label="$s={}$".format(n))


ax.axvline(28,color='black',ls='--')

ax.set_ylabel('Probability (%)')
    


ax = axes[1]

ax.plot(days, 100*pmf,label='pmf')
# ax.plot(100*np.gradient(prob[:,-1],1),label='pmf')

ax.axvline(stats['mean'],label='mean',ls='--',color='C1')

ax.axvline(stats['median'],label='median',ls='--',color='C3')


for ax in axes:
    ax.legend()
    ax.set_xlabel('Day')

fig.set_tight_layout(True)
plt.show()