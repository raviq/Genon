import numpy as np
import matplotlib.pyplot as plt   
from scipy import random
import pylab
import numpy
import os

#==========================================================================================
# Method to take two equally-sized lists and return just the elements which lie 
# on the Pareto frontier, sorted into order. Default behaviour is to find the 
# maximum for both X and Y, but the option is available to specify maxX = False
# or maxY = False to find the minimum for either or both of the parameters.
#==========================================================================================

def pareto_frontier(Xs, Ys, maxX = True, maxY = True):
# Sort the list in either ascending or descending order of X
    myList = sorted([[Xs[i], Ys[i]] for i in range(len(Xs))], reverse=maxX)
# Start the Pareto frontier with the first value in the sorted list
    p_front = [myList[0]]    
    # Loop through the sorted list
    for pair in myList[1:]:
        if maxY: 
            if pair[1] >= p_front[-1][1]:    # Look for higher values of Y ...
                p_front.append(pair)         # ... and add them to the Pareto frontier
        else:
            if pair[1] <= p_front[-1][1]:    # Look for lower values of Y ...
                p_front.append(pair)         # ... and add them to the Pareto frontier
# Turn resulting pairs back into a list of Xs and Ys
    p_frontX = [pair[0] for pair in p_front]
    p_frontY = [pair[1] for pair in p_front]
    return p_frontX, p_frontY


def get_pareto(u1, u2, fname='pareto', cwd='', show=False, verbose=False):
    fig = plt.figure(1, figsize=(8, 8))
    
    n = len(u1)  # number of bids

    if verbose:
        print 'input 1'
        print ' u1 = ', ''.join([ '  %.4f' % _ for _ in u1])
        print ' u2 = ', ''.join([ '  %.4f' % _ for _ in u2])
    
    Ua, Ub = np.array(u1), np.array(u2)

    p_front = pareto_frontier(Ub, Ua, maxX = True, maxY = True) 
    
    npf = len(p_front[0])

    tmp = ''    
    if verbose:
        print '\nu1, u2'
    for k in xrange(npf):
        
        tmp += '%f, %f\n' % (p_front[1][k], p_front[0][k])
        
        if verbose:
            print '%f, %f' % (p_front[1][k], p_front[0][k])
    
    pf_file = open(fname, "w")
    pf_file.write(tmp)
    pf_file.close()


    # Plot a scatter graph of all results
    plt.scatter(Ua, Ub, marker='+', c='b')
    
    # Then plot the Pareto frontier on top
    plt.plot(p_front[1], p_front[0], 'r^-')
    plt.draw()
    # print n as exponent
    #s = '%.0e' % n
    #ns = '10 ** %d' % int(s[s.index('+')+1:])
    plt.title("Utilities and Pareto Frontier (#PF=%d)" % npf , fontsize=14)
    plt.ylabel("$u_2$", fontsize=20)
    plt.xlabel("$u_1$", fontsize=20)
    plt.xticks(np.arange(0., 1.1, .1))
    plt.yticks(np.arange(0., 1.1, .1))

    pylab.xlim([-.02, 1.02])
    pylab.ylim([-.02, 1.02])
    plt.grid(True)
    
    fig.savefig('%s/%s' % (cwd, 'pareto'))
    if show:
        plt.show()

if __name__ == '__main__':
    pass

