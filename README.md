
<a  name="_"></a>
# Genon

1. [ Description ](#desc)  
2. [ Prerequisites](#prereq)  
3. [Generating a utility space for one agent](#oneprof)  
4.1. [Usage](#usage1)  
4.2. [Example](#example1)  
4. [Generating utility spaces for two agent](#twoprof)  
5.1. [Usage](#usage2)  
5.2. [Example](#example2)  
5.3. [Compatibility with Genius](#compat)  
5. [Citation](#Citation)  
6. [Licence & Copyright](#Licence)  

  <a  name="desc"></a>
  ## Description

Genon is a generator of nonlinear preferences for intelligent artificial agents. Nonlinear preferences are matheamtically formulated using nonlinear [utility spaces](https://en.wikipedia.org/wiki/Utility#Utility_function) and can be defined using multidimensional constraints.

A utility space is characterised by 

- *n* issues
- *m* constraints
- A distribution *π* mapping constraints to issues


Issues are the "things" that the agent is reasoning about.

Constraints are the "glue" that the agent is using to structure the issues according to his preferences. We distinguish three types of preferences, modelled using cubic, bell, and conic constraints:

<p align="center">
	<img src="https://github.com/raviq/Genon/blob/master/images/ck.png" width="500">
</p>

The distribution *π* specifies the number of issues involved in one particular constraint. Genon supports three types of distributions:

1.  **Uniform** : All constraints have the same cardinality.
    
2.  **Power-law**: A small fraction of constraints involve most of the issues while the rest of the constraints involve fewer issues.
    
3.  **Random** : The cardinality of a constraint is randomly chosen from *[1,n]*.

The distribution *π* controls the complexity of a preference profile and how it affects the agent's computational abilities in solving any given problem (negotiation, coordination, etc.).

Note that a utility space corresponds to a utility hypergraph where nodes represent the issues and hyperedges represent the constraints:


<p align="center">
	<img src="https://github.com/raviq/Genon/blob/master/images/utspace.png" width="500">
</p>


Theoretical details are found in [citation](#Citation).


<a  name="prereq"></a>
## Prerequisites
- Python2.7
- [pyinterval](https://pyinterval.readthedocs.io/en/latest/)

  <a  name="oneprof"></a>
## Generating a utility space for one agent

  <a  name="usage1"></a>
### Usage

	python2.7 genon.py 
		   NumberofIssues (n)
		   NumberofConstraints (m)
		   ConstraintIssueDistribution (pi) in [complete | random | pl] 
		   ConstraintWeightDistribution in [complete | random | pl] 
		   Competitiveness in [complete | random | pl] 
		   MaxUtilityPerConstraint 
		   CompleteWeight 
		   CompleteCard 
		   NumberOfIterations 
		   ProfileName 
		   ProfileDirectory 
		
  <a  name="Example1"></a>
### Example

```
python2.7 genon.py 2 5 pl random random 100 2 5 100 sample /absolute-path-to-/sample/
```

The output is stored in `/absolute-path-to-/sample/` and contains:

File | Description
------------ | -------------
2-5-pl-random-domain.xml | Domain of the negotiation: issues, types, and bounds
Constraint-Issue_distribution.csv | Distribution **π**
Constraint-Weight_distribution.csv | Weights of the constraints
description_sample.txt | General description of the utility space
figure_sample.png | Hypergraph representation of the utility space
sample.xml | Utility space of the agent


  <a  name="twoprof"></a>
## Generating utility spaces for two agent

In the bilateral case, two self-intersted agents *1* and *2* have two utility spaces *(n, m<sub>1</sub>, π<sub>1</sub> )* and *(n, m<sub>2</sub>, π<sub>2</sub> )*.  When generating such profiles, we can diversify them along the following lines. First, we assume that an agent’s utility space is built using the three types of constraints: linear (hyperplane), bell, or conic. Secondly, it is possible to adjust the complexity of any given utility space by specifying the constraint-issue distribution using the *π* distribution. Such connectivity affects the computational difficuty required to optimise over any given utility space. Utility spaces with randomised sets in particular, render the search for optimal solution more difficult.


#### Competitiveness
Each constraint from agent *1*'s utility space is used to generate a new constraint (in agent *2*'s utility space) having the same utility. The generation is done based on different sampling methods:

- **Zerosum**: disjoint sets. E.g. for 1-dimensional constraints, *c<sub>1</sub>=[0,1]* and *c<sub>2</sub>=[5,8]*.
- **Within**: any constraint of agent *2* is a subset of the original constraint of agent *1*,  with the same utility. E.g. for 1-dimensional constraints, *c<sub>1</sub>=[0,7]* and *c<sub>2</sub>=[1,4]*.
- **Random**: any possible configuration (default mode).

  <a  name="usage2"></a>
### Usage

	python2.7 genon2.py 
		   NumberofIssues 
		   NumberofConstraints 
		   ConstraintIssueDistribution (Pi) in [complete | random | pl] 
		   ConstraintWeightDistribution in [complete | random | pl] 
		   Competitivenss in [complete | random | pl] 
		   MaxUtilityPerConstraint 
		   CompleteWeight 
		   CompleteCard 
		   NumberOfIterations

  <a  name="Example2"></a>
### Example
```
	python2.7 genon2.py 2 5 random random random 100 2 5 100
```

The output will be stored in `scenarios/2-5-random-random-random/` and contains:

File | Description
------------ | -------------
2-5-random-random-domain.xml | Domain of the negotiation: issues, types, and bounds
Constraint-Issue_distribution.csv | Distribution **π**
Constraint-Weight_distribution.csv | Weights of the constraints
description.txt | General description of the utility space
pareto.png | Pareto Frontier (image)
pareto.xml | Pareto Frontier (list of points)
profile-1.xml | Utility space of agent *1*
profile-2.xml | Utility space of agent *2*


  <a  name="compat"></a>
### Compatibility
The generated profiles are compatible with [Genius](http://ii.tudelft.nl/genius/) and were used for the bilateral automated negotiations  of the [ANAC2014](http://www.itolab.nitech.ac.jp/ANAC2014/) competition:

> Aydogan, Reyhan, et al. "A baseline for non-linear bilateral negotiations: the full results of the agents competing in ANAC 2014." (2016): 1-25.

  <a  name="Citation"></a>
## Citation

> Hadfi, Rafik, and Takayuki Ito. "Complex multi-issue negotiation using utility hyper-graphs." _Journal of Advanced Computational Intelligence Vol_ 19.4 (2015).

> Hadfi, Rafik, and Takayuki Ito. "Constraint-Based Preferences via Utility Hyper-Graphs." _MPREF@ AAAI_. 2014.

> Hadfi, Rafik, and Takayuki Ito. "Modeling complex nonlinear utility spaces using utility hyper-graphs." _Modeling Decisions for Artificial Intelligence_. Springer, Cham, 2014.
> 
> Hadfi, Rafik, and Takayuki Ito. "Cognition as a game of complexity." _Proc. 12th International Conference on Cognitive Modeling (ICCM)_. 2013.

  <a  name="Licence"></a>
## Licence & Copyright
This software was developed in the hope that it would be of some use to the agent research community, and is freely available for redistribution and/or modification under the terms of the GNU General Public Licence. It is distributed WITHOUT WARRANTY; without even the implied warranty of merchantability or fitness for a particular purpose. See the [GNU General Public License](https://github.com/raviq/Genon/blob/master/LICENCE.md) for more details. 

Copyright (c) 2015--2018 Rafik Hadfi.
