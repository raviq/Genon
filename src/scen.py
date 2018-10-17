#
#
#

import os
import sys
import math
import time
import random
import matplotlib.pyplot as plt
from interval import interval
from xml.parsers.expat import ExpatError
from xml.dom import minidom
from xml.dom.minidom import parse
import collections
from collections import defaultdict, OrderedDict

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
		
	'''
	x is the contract, indexed by index, not by the issue name ! the mapping needs to be established using self.issues
	'''
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

# End