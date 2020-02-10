# this script takes an author list 
# and colors citations in a text document according to the
# genders of their first and last authors

import numpy as np
import re
import pandas as pd

homedir = '/Users/Eli/Dropbox/Cornblath_Bassett_Projects/NeuroPathCluster/'
tex_file = 'neuropathcluster_v5_blue'

cite_gender = pd.read_csv('Authors.csv') # output of getReferenceGends.ipynb
cite_gender.index = cite_gender.CitationKey
cite_gender['Color'] = '' # what color to make each gender category
colors = {'MM':'red','MW':'blue','WW':'green','WM':'magenta','UU':'black',
'MU':'black','UM':'black','UW':'black','WU':'black'}
for idx in cite_gender.index: # loop through each citation key and set color
	cite_gender.loc[idx,'Color'] = colors[cite_gender.loc[idx,'GendCat']]
cite_gender.loc[cite_gender.index[cite_gender.SelfCite=='Y'],'Color'] = 'black' # make self citations black

fin = open(homedir+tex_file+'.tex')
texdoc=fin.readlines()
with open(homedir+tex_file+'_gendercolor.tex','w') as fout:
	for i in range(len(texdoc)):
		s = texdoc[i]
		cite_instances = re.findall('\\\\cite\{.*?\}',s)
		cite_keys = re.findall('\\\\cite\{(.*?)\}',s)
		cite_keys = [x.split(',') for x in cite_keys]
		cite_keys_sub = [['\\textcolor{' + cite_gender.loc[x.strip(),'Color'] + '}{\\cite{'+x.strip()+'}}' for x in cite_instance] for cite_instance in cite_keys]
		cite_keys_sub = ['\\textsuperscript{,}'.join(x) for x in cite_keys_sub]
		for idx,cite_instance in enumerate(cite_instances):
			s = s.replace(cite_instances[idx],cite_keys_sub[idx])
		fout.write(s)
		# place color key after abstract
		if '\\section*{Introduction}\n' in s:			
			l = ['\t\\textcolor{' + colors[k] + '}{'+k+'}' for k in colors.keys()]
			fout.write(','.join(l)+'\n')