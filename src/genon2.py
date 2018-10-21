############################################################
## Generates two profiles
## @author: Rafik HADFI, <rafik.hadfi@gmail.com>
############################################################

import os
import sys
import math
import time
import random
import matplotlib.pyplot as plt
from interval import interval
from xml.parsers.expat import ExpatError
from xml.dom import minidom
import numpy as np

from ScenFactory import ScenFactory as sf
from ScenFactory import generate_domain
from pareto import get_pareto


# recursively loads a component node, prints the content. Returns if iptr
def recompoload(compo, verbose):	
    if verbose:
        print ('Component', compo.getAttribute('name'), '(', compo.getAttribute('description'),')')
    
    for child in compo.childNodes:
        if (child.nodeType != child.TEXT_NODE):
            if child.tagName == 'iptr':
                if child.nodeType==child.ELEMENT_NODE:
                        if verbose:
                            print (' iptr =', child.firstChild.nodeValue)
            else: # component
                recompoload(child, verbose)

def H(p):
    s = 0.
    for _ in p:
        if _ == 0:
            continue
        else:
            s -= _ * math.log(_)
    return s
    
class Scenario(object):
	def __init__(self, fname = None, fpath = None,  verbose = False):
		
		self.cons = dict()
		self.issues = dict()
		self.index_issue = dict()
		
		try:
			self.filename, self.path = fname, fpath
			if verbose:
				print 'self.filename = ', self.filename
				print '    self.path = ', self.path		
					
			xmldoc = minidom.parse(os.path.join(self.path, self.filename))
		except ExpatError as e:
			print "XML : Error (line %d): %d" % (e.lineno, e.code)
			print "XML : Offset: %d" % (e.offset)
			raise e
		except IOError as e:
			print ' self.filename = ', self.filename
			#print '         path_ = ', path_
			raise e, "IO : I/O Error %d: %s" % (e.errno, e.strerror)
		else:
			self.docelem = xmldoc.documentElement
			
		for p in self.docelem.getElementsByTagName('utility'):
			self.maxutility = int(p.getAttribute('maxutility'))

		for p in self.docelem.getElementsByTagName('objective'):
			for issue in p.getElementsByTagName('issue'):
				name = issue.getAttribute('name')
				self.issues[name] = dict()
				self.issues[name] = {
					'index' : issue.getAttribute('index'),
					'type'  : issue.getAttribute('type'),
					'etype' : issue.getAttribute('etype'),
					'vtype' : issue.getAttribute('vtype'),
					'lowerbound' : issue.getAttribute('lowerbound'),
					'upperbound' : issue.getAttribute('upperbound')	 }
				index = int(self.issues[name]['index'])
				self.index_issue[index] = str(name)
						
		if verbose:			
			for p in self.docelem.getElementsByTagName('ufun'):
				print '  ufun            type : ', p.getAttribute('type')
				print '                weight : ', p.getAttribute('weight')
				print '           aggregation : ', p.getAttribute('aggregation'), '\n_______________________________________________________\n'
			
		k = 1
		for p in self.docelem.getElementsByTagName('ufun'):
			for cube in p.getElementsByTagName('hyperRectangle'):
				self.cons['hc_%d' % k] = dict()
				self.cons['hc_%d' % k]['utility'] = cube.getAttribute('utility')
				for x in cube.childNodes:
					if (x.nodeType != x.TEXT_NODE):
						self.cons['hc_%d' % k]['index=%s' % x.getAttribute('index')] = [str(x.nodeName),  int(x.getAttribute('min')), int(x.getAttribute('max')) ]
				k += 1

	def get_constraints(self):
		return self.cons


	def get_issue_names(self):
		return [str(_) for _ in self.issues.keys()]

	def get_rand_contract(self, N):
		x = dict()
		for issue_name in self.issues.keys():		
			x[str(issue_name)] = random.randint(0, 9)
		return x

	def get_maxutility(self):
		return self.maxutility
		
	# x is the contract, indexed by index, not by the issue name ! the mapping needs to be established using self.issues
	def get_utility(self, x, verbose=False):
		u = 0
		for c in self.cons:
			if verbose: print '\n', c, '_________________________________________________________________________'
			inclusion = []
			exclusion = []
			for i in self.cons[c]:
					
				if i[:5] == 'index':
					memebership = self.cons[c][i][0]
					interv = self.cons[c][i][1:3]
					index = int(i[6:])
					issue_name = self.index_issue[index]
					issue_value = x[issue_name]					
					
					if verbose: print '\t  name=%s  value=%s   index=%d    type=%s  interval=%s' % ( issue_name, issue_value, index, memebership, interv  )

					if memebership == 'INCLUDES':
						b = issue_value >= interv[0] and issue_value <= interv[1]
						inclusion.append( b )
						
					if memebership == 'EXCLUDES':
						b = issue_value < interv[0] or issue_value > interv[1]
						
						exclusion.append( b )
							
					if verbose: print '\t   ', interv, memebership, issue_value, ' = ', b
					
				else:
					utility = int(self.cons[c][i])

			if verbose:
				print '\t\t\t\t\t\t exclusion = ', exclusion
				print '\t\t\t\t\t\t all(exclusion) ?', any(exclusion)
				print '\t\t\t\t\t\t inclusion = ', inclusion
				print '\t\t\t\t\t\t all(inclusion) ?', all(inclusion) 

			
			if exclusion != []:
				if any(exclusion):
					u += utility
					if verbose:
						print 'adding ', utility
			
			if inclusion != []:
				if all(inclusion):
					u += utility	
					if verbose:
						print 'adding ', utility
		
		
		return u


#====================================================================================================
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
	for k in xrange(len(ci_l)):
		if ci_l[k][0][0] == ci_l[k][0][1]:
			j += 1
	#print '>>>>>>>> ', j
	if j == len(ci_l):
		print 'returning ', random_component
		
		if random_component[0][0]==0:
			return interval[0,1]
		if random_component[0][0]==9:
			return interval[8,9]
		
		return random_component

	if len(ci_l)==1 and random_component[0][0] == random_component[0][1]:
		return random_component

	while random_component[0][0] == random_component[0][1]:
		#print random_component
		random_component = ci_l[random.randint(0, len(ci_l)-1 )]
	
	a = sample_from_one_interval(random_component)
	b = sample_from_one_interval(random_component)
	while b <= a:
		a = sample_from_one_interval(random_component)
		b = sample_from_one_interval(random_component)
		#print a,b, '\t\t', random_component
	
	
	#print '\t\t >', a, ' \t ',b
	
	
	return interval[a, b]

def random_interval():
	a = random.randint(0,9)
	b = random.randint(0,9)	
	while b <= a:
		a = random.randint(0,9)
		b = random.randint(0,9)
	return interval[a, b]

	
#====================================================================================================

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

#__________________________________________________________________________________________
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

#__________________________________________________________________________________________
'''
	competitiveness and overlap	
	0 : no overlap (zero-sum)
		... Jaccard index
	1 : complete overlap same, or contained
'''

def overlap(interv_src, delta = 'zerosum'):
	if delta == 'zerosum':
		ci = complementary(interv_src)
		return sample_interval_from_interval(ci)   # complementary (0-sum)
	if delta == 'within':
		return sample_interval_from_interval(interv_src) # within
	if delta == 'random':
		return sample_interval_from_interval(interval[0, 9]) # random
	else:
		print 'arg error'
		exit()
# Demo
def example_of_J_plot():
	ch = ['within', 'zerosum', 'random']
	d = ch[random.randint(0, 2)]
	src_interval = random_interval()
	dest_interval = overlap(src_interval, delta = d)
	plot_intervals(src_interval, dest_interval, d)
	print '\ndone.\n'

	exit()

'''
Final function to generate interval from src_interval given a mode.
	mode :	within
		zerosum
		random
'''


def generate_interval( src_interval, mode='within' ):
	if mode ==  'zerosum':	
		# avoid the case where A=[0,9] so that we can create B in the 0-sum case.
		while src_interval == interval[0,9]:
			src_interval = random_interval()		

	return overlap(src_interval, delta = mode)	


#__________________________________________________________________________________________

if __name__== "__main__":

	if False: # Demo

		src_interval = random_interval()

		mode_ = 'within'

		dest_interval = generate_interval( src_interval, mode=mode_)
	
		J = leni(src_interval & dest_interval) / (leni(src_interval | dest_interval) * 1.)
		
		print J
			
		plot_intervals(src_interval, dest_interval, mode_)

		exit()


	args = "\n\t\tNumberofIssues \n\t\tNumberofConstraints \n\t\tConstraintIssueDistribution (Pi) in [complete | random | pl] \n\t\tConstraintWeightDistribution in [complete | random | pl] \n\t\tCompetitivenss in [complete | random | pl] \n\t\tMaxUtilityPerConstraint \n\t\tCompleteWeight \n\t\tCompleteCard \n\t\tNumberOfIterations\n" + \
	"\nAbout Competitiveness:\n" + \
	" Competitiveness: Each constraint from profile 1 is used to generate a new constraint (in profile 2) with the same utility.\n"+\
	" The generation is done based on different sampling methods:\n"+\
	" - zerosum: disjoint sets \n"+\
	" 	E.g. For 1-dimensional constraints, c1=[0,1] and c2=[5,8]\n"+\
	" - within: any constraint of player 2 is a subset of the original constraint of agent 1, with the same utility.	\n"+\
	"	E.g. For 1-dimensional constraints, c1=[0,7] and c2=[1,4]\n"+\
	" - random: any possible configuration (old default mode)" + \
	"\n\nExample:   python genon2.py 2 5 random random random 100 2 5 100"


	usage  = "\npython genon2.py " + args
	
	if len(sys.argv) == 10:

		IN_ONE_FILE_WITH_ENTROPY = False
				
		IssueBoundA, IssueBoundB = 0, 9
		N, M, pType, wType, mode, MaxUtilityPerConstraint, CompleteWeight, CompleteCard, niter = int(sys.argv[1]), \
		int(sys.argv[2]) , sys.argv[3] , sys.argv[4], sys.argv[5], \
		int(sys.argv[6]), int(sys.argv[7]), int(sys.argv[8]), int(sys.argv[9])
		cwd = os.path.dirname(os.path.realpath(__file__))	

		#==============================================================================================================		
		w_alpha  = random.uniform(0.1, 2) if wType == 'pl' else None
		if wType == 'pl':
			w_info = '\n\t\t\t\t   alpha   =  %f' % w_alpha
		elif wType == 'complete':
			w_info = '\n\t\t\t CompleteWeight    =  %d (<= MaxUtilityPerConstraint)' % CompleteWeight # assigned to all constraints, if complete
			if CompleteWeight > MaxUtilityPerConstraint:
				print ' \'CompleteWeight\' must be <= MaxUtilityPerConstraint=%d' % MaxUtilityPerConstraint
				exit()
			
		else:
			w_info = ''
		#==============================================================================================================	
		pi_alpha  = random.uniform(0.1, 2) if pType == 'pl' else None
		if pType == 'pl':
			pi_info = '\n\t\t\t\t   alpha   =  %f' % pi_alpha
		elif pType == 'complete':
			pi_info = '\n\t\t\t   CompleteCard    =  %d   (<= n)' % CompleteCard # assigned to all constraints, if complete
			
			if CompleteCard > N:
				print 'For Complete pi distribution, \'CompleteCard\' must be <= n' % N
				exit()
		else:
			pi_info = ''
		#==============================================================================================================		
		desc =  '   Number of issues                n       =  %d \n' \
			'   Number of constraints           m       =  %d \n' \
			'   Constraint-Issue distribution   pi      =  %s   %s \n' \
			'   Constraint-Weight distribution  w       =  %s   %s \n' \
			'                   Competitiveness Mode    =  %s \n' \
			'                Max Utility per Constraint =  %d \n' \
			'                               #iter PF    =  %d \n' % (N, M, pType, pi_info, wType, w_info, mode, MaxUtilityPerConstraint, niter)
		
		print desc
		
		verbose = False
		Competitiveness = 1
		Weight      = 1

		number_iterations =  niter   # For the pareto frontier

		GENERATION_WITH_MODES = True

		def pFunction(k):

			if pType=='complete':
				result = CompleteCard

			if pType=='random':
				result = random.randint(1, N) # pick m random issues from [1,N]


			if pType=='pl':
				# Power Law
				alpha  = pi_alpha
				PL = [N * ( _ + 1 ) ** -alpha for _ in range(M)]
				i = int(PL[k])  # make sure all constraints have at least 1 issue (no 0 issues!)
				result = 1 if i==0 else i
				#-- print ' p( c_k =', k,') = ', result
				if result > N:
				    print 'Error, return value must be <= ', N
				    sys.exit()
				if k > M or 0 > k:
				    print 'Error, k value must be in [ 0, ', M, ']'
				    sys.exit()

			return result

		profile_directory = cwd + '/scenarios/%d-%d-%s-%s-%s/' % (N, M, pType, wType, mode)		
		
		# Profile directory	
		if not os.path.exists(profile_directory):
			os.makedirs(profile_directory)

		#--- write the description to a file ---------------------------------- {
		scenario_description_file = cwd + '/scenarios/%d-%d-%s-%s-%s/description.txt' % (N, M, pType, wType, mode)		
		scenario_description = open(scenario_description_file, "w")
		scenario_description.write('\n Utility hypergraph description:\n\n'+desc)
		scenario_description.close()
		#------------------------------------------------------------------ }

		# Generate the domain template (issues list)	
		if True:
			domain_ = '%d-%d-%s-%s-domain' % (N, M, pType, wType)
		else:
			domain_='S-1NIKFRT-1-domain'
		
		
		domain_filename = '%s%s.xml' % (profile_directory, domain_)
		domain_file = open(domain_filename, "w")


		dom = generate_domain(N)
		
		domain_file.write(dom)
		domain_file.close()
		print 'Domain (%s) saved.' % domain_filename
			
		# Profiles		
		for profile_id in [1, 2]:

			res = sf(N, M, pFunction, pType, profile_id, Weight, MaxUtilityPerConstraint, CompleteWeight, mode, wType, w_alpha, [IssueBoundA, IssueBoundB],  profile_directory)
			profile_ = 'profile-%s' % profile_id
			
			#if profile_id == 2:
			#	print res[0]
			#	exit()
			
			# XML	
			profile_filename = '%s%s.xml' % (profile_directory, profile_)			
			profile_file = open(profile_filename, "w")
			profile_file.write(res[0])
			profile_file.close()
			print 'profile (%s) saved.' % profile_filename
			
			if profile_id==1: # Generative profile (basis one)
				# cons-issue distribution ---------------------------------------------------
				tmp =  'Constraint, Number of Issues\n'
				r_ = res[1]
				degrees = []
				for _ in r_:
					tmp += '%d, %d\n' % (_, r_[_])
					degrees.append(r_[_])
					
				dsum = sum(degrees) * 1.
				degrees = [_/dsum for _ in degrees]
	
				#h = H(degrees)	
				#tmp += '\n ,,,H , %f' % h
			
				consissues_ = 'Constraint-Issue_distribution'
				cons_issues_filename = '%s%s.csv' % (profile_directory, consissues_)
				cons_issues_file = open(cons_issues_filename, "w")		
				cons_issues_file.write(tmp)
				cons_issues_file.close()
				print '%s saved.' % consissues_

				# cons-weight distribution ---------------------------------------------
				tmp =  'Constraint, Weight\n'
				r_ = res[2][profile_id]
				
				degrees = []
				for k in xrange(M):
					tmp += '%d, %d\n' % (k, r_[k])
					
				consweights_ = 'Constraint-Weight_distribution'
				cons_weights_filename = '%s%s.csv' % (profile_directory, consweights_)
				cons_weights_file = open(cons_weights_filename, "w")		
				cons_weights_file.write(tmp)
				cons_weights_file.close()
				print '%s saved.' % consweights_
				
				if IN_ONE_FILE_WITH_ENTROPY: # ------------------------------------------------
					distrib_ = 'Distributions'
					cons_distr_filename = '%s%s.csv' % (profile_directory, distrib_)
					cons_distr_file = open(cons_distr_filename, "w")		
					
					tmp = 'constraint k, pi(k), w(k)\n'
					for k, pik, wk  in zip(xrange(M), res[1],res[2][profile_id]):
						tmp += '%d, %d, %d\n' % (k, res[1][pik], res[2][profile_id][k])
				
					
					cons_distr_file.write(tmp)
					cons_distr_file.close()
					print ' %s saved.' % consweights_
					

		
		# Pareto Evaluate random contract
		
		pf1 = '%s%s.xml' % (profile_directory, 'profile-1')
		pf2 = '%s%s.xml' % (profile_directory, 'profile-2')
				
		sc1 = Scenario(pf1)
		sc2 = Scenario(pf2)
		
		PF = [None] * number_iterations
		
		dtotal = 0
		history = dict()
		
		
		start_t = time.time()
		for k in xrange(number_iterations):
			x = sc1.get_rand_contract(N)
			# The key is simly the values
			contract_string = ''.join(map(str, x.values())) 
			if contract_string in history:
				# already checked, no need to recheck it..
				continue
			else:
				# add it
				history[contract_string] = 1
			u1 = sc1.get_utility(x)
			u2 = sc2.get_utility(x)
			PF[k] = [u1, u2, x]

		dt = time.time() - start_t
		print 'PF:\n      Sampling duration = %f' % dt

		# remove 'None'
		PF = [_ for _ in PF if _ != None]

		# update with number of checked bids		
		number_of_checked_bids = len(PF)
							
		print ' Number of checked bids = %d' % number_of_checked_bids
		print '                  niter = %d' % niter

		maxu1 = sc1.get_maxutility() * 1.
		maxu2 = sc2.get_maxutility() * 1.
	
		if verbose:
			print '________________________________________________'
			print 'maxutility 1 =  ',  maxu1
			print 'maxutility 2 =  ', maxu2, '\n'
		
		for k in xrange(number_of_checked_bids):
			
			maxa = PF[k][0]/maxu1
			maxb = PF[k][1]/maxu2

			if verbose:
				print ' %d / %d  =  %f  \t  %d / %d  =  %f' % (PF[k][0], maxu1, maxa, PF[k][1], maxu2, maxb)
			
			#if maxa > 1:  maxa = 1
			#if maxb > 1:  maxb = 1
				
			PF[k] = [maxa, maxb, PF[k][2]]
			
	#		print '  %d / %d = %f    and    %d / %d = %f' % (PF[k][0], maxu1, maxa,  PF[k][1], maxu2, maxb)
		
		if verbose:
			print 'All bids_____________________________________________'

		U1 = []
		U2 = []
		for k in xrange(number_of_checked_bids):
			U1.append(PF[k][0])
			U2.append(PF[k][1])
		
		#for k in xrange(number_of_checked_bids):
		#	print '  b%d   %f    %f  ' % (k+1, U1[k], U2[k])
			
		if verbose: print '____________________________________________________'			
		
		if False:
			pf_ = 'pareto_%d-%d-%s' % (N, M, pType)
		pf_ = 'pareto'
			
		pf_filename = '%s%s.xml' % (profile_directory, pf_)

		get_pareto(U1, U2, pf_filename, profile_directory)

		
		# Generate the domain template (issues list)	

		
		print '\n'
	else:
		print 'usage: ', usage

	