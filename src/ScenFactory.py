##===========================================================================================
## Generator compatible with Genius 2014 scenarios (xml)
## Random Scenario Factory, with modes.
##===========================================================================================

import random
from interval import interval

from scen import Scenario
from geni import generate_interval, geta, getb

def ScenFactory(N, M, P, pType, ProfileID, Weight, MaxUtilityPerConstraint,  CompleteWeight, mode, wType, w_alpha, IssueBounds, path):

	GENERATE_WITH_MODES = (mode != '' and ProfileID == 2)
	rd_dis = False
	TotalUtility = 0
	ctype = 'hyperRectangle'
	min_bound  , max_bound  = IssueBounds[0], IssueBounds[1] # each issue takes value in [a,b]
	alpha = None
	xml_string, xml_string_header, xml_string_footer, bksp = '', '', '', '\n'
	issues_factory = list(range(N))

	xml_string_header += "<?xml version=\"1.0\" encoding=\"utf-8\" ?>"  + bksp
	xml_string_header += "<utility_space type=\"nonlinear\">"  + bksp
	xml_string_header += "  <objective description=\"\" etype=\"objective\" index=\"0\" name=\"root\" type=\"objective\">"  + bksp

	for i in range(1, N+1):
		   xml_string_header += "       <issue etype=\"integer\" index=\"%d\"  name=\"i%d\" type=\"integer\" vtype=\"integer\" lowerbound=\"%d\" upperbound=\"%d\"/>%s" % (i, N-i+1, min_bound, max_bound, bksp)


	ck = [dict] * M # generate M constraints (shapes)
	constraint_issues_assignements = dict()

	constraint_weights_assignements = dict()

	xml_string_header += "    <utility maxutility=\"MAXUTILITYSTRING\">" + bksp
	xml_string_header += "     <ufun type=\"PlainUfun\" weight=\"%d\" aggregation=\"sum\">%s" % (Weight, bksp)


	if GENERATE_WITH_MODES:
		#print '   ID = ', ProfileID
		#print ' mode = ', mode

		pf1 = '%s%s.xml' % (path, 'profile-1')
		sc1 = Scenario(pf1)
		TotalUtility = sc1.get_maxutility()
		cons = sc1.get_constraints()


		for c in cons:
			ConstraintWeigth = cons[c]['utility']
			xml_string +=  "	  <"+ctype+" utility=\""+ ConstraintWeigth +"\">"+ bksp
			for _ in cons[c]:
				if _[:5] == 'index':
					index = int (_[6:])
					membership = cons[c][_][0]
					a, b = cons[c][_][1], cons[c][_][2]	# old intervals

					'''
					in the zerosum case, the complementary of excludes is includes
					TODO: do we remove the a and b? as in ]a,b[
					'''

					if membership == 'EXCLUDES' and mode == 'zerosum':
						membership = 'INCLUDES'   # Invert
						newa, newb = a, b         # keep the intervals
					else:
						src_interval = interval[a, b]
						dest_interval = generate_interval( src_interval, mode )
						newa, newb = geta(dest_interval), getb(dest_interval)		# new intervals

					xml_string += "	      <%s index=\"%d\"  min=\"%d\"  max=\"%d\"/>%s" % ( membership, index, newa, newb, bksp )


			xml_string += "	  </"+ctype+">" + bksp

	else:


		Weights = [0] * M

		# uniform, constraints have the same weight, which is the MaxUtilityPerConstraint
		if wType=='complete':

			for k in range(M):
				Weights[k] = CompleteWeight

		# Gets a random value from [0, MaxUtilityPerConstraint]
		if wType=='random':
			for k in range(M):
				Weights[k] = random.randint(1, MaxUtilityPerConstraint)

		# Power Law, Distributed (few constraints with high weights, most with low weights)
		if wType=='pl':
			Weights = [ MaxUtilityPerConstraint * (k+1) ** -w_alpha for k in range(M)]
			Weights = [ int(w) if w!=0 else 1 for w in  Weights] # convert to int, and make sure weights are non negative

		constraint_weights_assignements[ProfileID] = Weights

		factory = [0]
		tmp = set()
		att = 1
		while factory != [] and len(tmp) != N:

			xml_string = ''
			factory = list(range(N))
			tmp.clear()

			for k in range(M):
				ck[k] = dict()
				ck[k]['utility'] = Weights[k]

				TotalUtility += ck[k]['utility']

				xml_string +=  "	  <"+ctype+" utility=\""+str(ck[k]['utility'])+"\">"+ bksp

				if not isinstance(P, int): # P is a function
					m = P(k)
					constraint_issues_assignements[k] = m
				else:
					m = random.randint(1, P) # pick m random issues from [1,P]

				issues = []
				aux = list(range(N))
				for i in range(m):
					if aux == []:
						break
					elif len(aux)==1:
						rndidx = 0
					else:
						rndidx = random.randint(0, len(aux)-1)
					issue = aux[rndidx]
					issues.append(issue)
					aux.remove(issue)

				for issue in issues:
					if issue in factory:
						factory.remove(issue)

				membership = ['INCLUDES', 'EXCLUDES'][random.randint(0, 1)]

				for issue in issues:
					a = random.randint(min_bound, max_bound)
					b = random.randint(a, max_bound)
					index = issue + 1
					xml_string += "	      <%s index=\"%d\"  min=\"%d\"  max=\"%d\"/>%s" % ( membership, index, a, b, bksp )

				xml_string += "	  </"+ctype+">" + bksp

				for _ in issues:
					tmp.add(_)


	xml_string_footer += "     </ufun>" + bksp
	xml_string_footer += "    </utility>" + bksp
	xml_string_footer += "  </objective>" + bksp
	if rd_dis:
		discount_factor = random.uniform(0, 0.9)
		reservation_value = random.uniform(0.3, 0.6)
		xml_string_footer += "  <discount_factor value=" + str(discount_factor) + " />" + bksp
		xml_string_footer += "  <reservation value="+ str(reservation_value) +" />" + bksp
	xml_string_footer += "</utility_space>"
	xml_string_header = xml_string_header.replace("MAXUTILITYSTRING", "%d" % TotalUtility);
	return [xml_string_header + xml_string + xml_string_footer, constraint_issues_assignements, constraint_weights_assignements]




def generate_domain(N):
	bksp = '\n'
	min_bound  , max_bound  = 0, 9

	template = "<negotiation_template>" + bksp
	template += "<utility_space number_of_issues=\"%d\">" % N  + bksp
	template += "  <objective description=\"\" etype=\"objective\" index=\"0\" name=\"root\" type=\"objective\">"  + bksp

	for i in range(1, N+1):
		template += "       <issue etype=\"integer\" index=\"%d\"  name=\"c1-i%d\" type=\"integer\" vtype=\"integer\" lowerbound=\"%d\" upperbound=\"%d\"/>%s" % (i, N-i+1, min_bound, max_bound, bksp)

	template += "  </objective>" + bksp
	template += "</utility_space>" + bksp
	template += "</negotiation_template>"

	return template



## End
