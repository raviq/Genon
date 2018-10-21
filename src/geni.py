# overlap interval generation

import os
import time
import random
import matplotlib.pyplot as plt
from interval import interval
import numpy as np

# Intervals complementary/sampling

def complementary(interv):
	a, b = interv[0]
	if a == 0 and b == 9:	return interval[0, 9]    # assumption : complementary of [0,9] is [0,9]
	if b == 9 and a > 0:	return interval[0, a-1]
	if a == 0 and b < 9:	return interval[b+1, 9]
	return interval( [0, a-1], [b+1, 9] )

def sample_from_one_interval(i):
	return random.randint(i[0][0], i[0][1])

def sample_interval_from_interval(i):
	ci_l = list(i.components)

	random_component = ci_l[random.randint(0, len(ci_l)-1 )]

	j = 0
	for k in range(len(ci_l)):
		if ci_l[k][0][0] == ci_l[k][0][1]:
			j += 1
	if j == len(ci_l):
		if random_component[0][0]==0:
			return interval[0,1]
		if random_component[0][0]==9:
			return interval[8,9]

		return random_component

	if len(ci_l) == 1 and random_component[0][0] == random_component[0][1]:
		return random_component

	while random_component[0][0] == random_component[0][1]:
		# print random_component
		random_component = ci_l[random.randint(0, len(ci_l)-1 )]

	a = sample_from_one_interval(random_component)
	b = sample_from_one_interval(random_component)
	while b <= a:
		a = sample_from_one_interval(random_component)
		b = sample_from_one_interval(random_component)

	return interval[a, b]

def random_interval():
	a = random.randint(0,9)
	b = random.randint(0,9)
	while b <= a:
		a = random.randint(0,9)
		b = random.randint(0,9)
	return interval[a, b]

def poisseq(n, lambd):
    tmpdegs = np.zeros(n)
    while np.any(tmpdegs == 0):
        inds = np.where(tmpdegs == 0)[0]
        tmpdegs[inds] = np.random.poisson(lambd, len(inds))
    return (tmpdegs)

def geta(i): return i[0][0]
def getb(i): return i[0][1]

def leni(i):
	if i == interval():  	return 0
	if i[0][1] == i[0][0]:	return 1
	return i[0][1]-i[0][0]+1

def plot_intervals(src_interval, dest_interval, d):
	fig = plt.figure(1, figsize=(8, 8))
	ia = geta(src_interval)
	ib = getb(src_interval)
	where = 0.1
	plt.hlines(where, ia, ib, 'b', lw=5, label='$P_1=[%d, %d]$' % (ia, ib))
	plt.vlines(ia, where-0.01, where+0.01, 'b', lw=2)
	plt.vlines(ib, where-0.01, where+0.01, 'b', lw=2)

	ida = geta(dest_interval)
	idb = getb(dest_interval)
	where += 0.1

	plt.hlines(where, ida, idb, 'r', lw=5, label='$P_2=[%d, %d]$' % (ida, idb))
	plt.vlines(ida, where-0.01, where+0.01, 'r', lw=2)
	plt.vlines(idb, where-0.01, where+0.01, 'r', lw=2)

	intersection = src_interval & dest_interval
	where += 0.1
	if intersection != interval():
		intersa, intersb = geta(intersection), getb(intersection)
		plt.hlines(where, intersa, intersb, 'g', lw=5, label='$P_1 \cap P_2=[%d, %d],\ l=%d$' % (intersa, intersb, leni(intersection) ))
		plt.vlines(intersa, where-0.01, where+0.01, 'g', lw=2)
		plt.vlines(intersb, where-0.01, where+0.01, 'g', lw=2)

	union = src_interval | dest_interval
	where += 0.1
	if union != interval():
		uintersa, uintersb = geta(union), getb(union)
		plt.hlines(where, uintersa, uintersb, 'm', lw=5, label='$P_1 \cup P_2=[%d, %d],\ l=%d$' % (uintersa, uintersb, leni(union)))
		plt.vlines(uintersa, where-0.01, where+0.01, 'm', lw=2)
		plt.vlines(uintersb, where-0.01, where+0.01, 'm', lw=2)

	J = leni(intersection) / (leni(union) * 1.)

	if False:
		new = src_interval / dest_interval
		where += 0.1
		newa, newb = geta(new), getb(new)
		plt.hlines(where, newa, newb , 'm', lw=5, label='$P_1/P_2=[%f, %f]$' % (newa, newb))
		plt.vlines(newa, where-0.01, where+0.01, 'm', lw=2)
		plt.vlines(newb, where-0.01, where+0.01, 'm', lw=2)

	ax = plt.gca()
	plt.ylim(0, where+0.3)
	plt.xlim(-1, 10)
	plt.xticks(xrange(10))
	plt.xlabel('i')
	plt.grid()
	plt.legend()
	plt.title('$%s,\ J(P_1, P_2)=%.3f$' % (d, J))
	plt.show()
	cwd = os.path.dirname(os.path.realpath(__file__))
	fname = '%s/Jaccard/j_%s.png' % (cwd, time.time())
	fig.savefig(fname)
	plt.close()

# ------------------------------------------------------------------------
# competitiveness and overlap
# 0 : no overlap (zero-sum)
#    ... Jaccard index
# 1 : complete overlap same, or contained
# ------------------------------------------------------------------------

def overlap(interv_src, delta = 'zerosum'):
	if delta == 'zerosum':
		ci = complementary(interv_src)
		return sample_interval_from_interval(ci)   # complementary (0-sum)
	if delta == 'within':

		if geta(interv_src)==getb(interv_src): # [x,x]
			return interv_src

		return sample_interval_from_interval(interv_src) # within
	if delta == 'random':
		return sample_interval_from_interval(interval[0, 9]) # random
	else:
		print ('arg error')
		exit()

# ------------------------------------------------------------------------
# Final function to generate interval from src_interval given a mode.
# mode : within, zerosum and random
# ------------------------------------------------------------------------

def generate_interval( src_interval, mode='within' ):
	if mode ==  'zerosum':
		# avoid the case where A=[0,9] so that we can create B in the 0-sum case.
		while src_interval == interval[0,9]:
			src_interval = random_interval()

	return overlap(src_interval, delta = mode)

# Demo

def example_of_j_plot():
	ch = ['within', 'zerosum', 'random']
	d = ch[random.randint(0, 2)]
	src_interval = random_interval()
	dest_interval = overlap(src_interval, delta = d)
	plot_intervals(src_interval, dest_interval, d)
	print ('\ndone.\n')

	exit()

if __name__ == '__main__':
	example_of_j_plot()


# End
