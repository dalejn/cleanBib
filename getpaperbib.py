# before using, install bibtexparser using shell command `pip install bibtexparser`
# also set paths to:
# paper_aux_file
# bib_file
# paper_bib_file (output)

import numpy as np
import bibtexparser
import subprocess
import os

def checkcites_output(aux_file):
	# take in aux file for tex document, return list of citation keys
	# that are in .bib file but not in document

	result = subprocess.run(['checkcites',aux_file], stdout=subprocess.PIPE)
	result = result.stdout.decode('utf-8')
	unused_array_raw = result.split('\n')
	# process array of unused references + other output 
	unused_array_final = list()
	for x in unused_array_raw:
		if len(x) > 0: # if line is not empty
			if x[0] == '-':  # and if first character is a '-', it's a citation key
				unused_array_final.append(x[2:]) # truncate '- '
	return(unused_array_final)

# for check cites to work, the .bib file must exist in the path specified in the .tex file used to generate the .aux file
homedir = '/path/to/tex/and/bib/files/goes/here'
os.chdir(homedir)
paper_aux_file = 'paper.aux' # name of aux file for paper
bib_file = '../library.bib' # path to full library .bib file, same as one referenced in .tex file
paper_bib_file = 'library_paper.bib' # name of .bib file output
unused_in_paper = checkcites_output(paper_aux_file) # get citations in library not used in paper

with open(bib_file) as bibtex_file:
	bib_data = bibtexparser.load(bibtex_file)

all_library_citations = list(bib_data.entries_dict.keys())
for k in all_library_citations:
	if k in unused_in_paper:
		#bib_data.entries.pop(k)
		del bib_data.entries_dict[k] # remove from entries dictionary if not in paper
in_paper_mask = [x not in unused_in_paper for x in all_library_citations] # get mask of citations in paper
bib_data.entries = [bib_data.entries[x] for x in np.where(in_paper_mask)[0]] # replace entries list with entries only in paper

with open(paper_bib_file, 'w') as bibtex_file:
    bibtexparser.dump(bib_data, bibtex_file)

# remove self-citations (defined as cited papers for which 
# either the first or last author of the citing paper was a co-author) 
# from consideration

# define first author and last author names of citing paper -- will exclude citations of these authors
# beware of latex symbols within author names
citing_authors = np.array(['Author, First', 'Author, Last'])
in_paper_citations = list(bib_data.entries_dict.keys()) # get list of citation keys in paper
# extract author list for every cited paper
cited_authors = [bib_data.entries_dict[x]['author'] for x in in_paper_citations]
# find citing authors in cited author list
# using nested list comprehension, make a citing author -by- citation array of inclusion
self_cite_mask = np.array([[citing_author in authors for authors in cited_authors] for citing_author in citing_authors])
self_cite_mask = np.any(self_cite_mask,axis=0) # collapse across citing authors such that any coauthorship by either citing author -> exclusion

[bib_data.entries[x] for x in np.where(self_cite_mask)[0]] # print self citations
for idx,k in enumerate(in_paper_citations):
	if self_cite_mask[idx]:
		del bib_data.entries_dict[k] # delete citation from dictionary if self citationi
bib_data.entries = [bib_data.entries[x] for x in np.where(np.invert(self_cite_mask))[0]] # replace entries list with entries that aren't self citations

paper_bib_file_excl_sc = os.path.splitext(paper_bib_file)[0] + '_excludeselfcite.bib'

with open(paper_bib_file_excl_sc, 'w') as bibtex_file:
    bibtexparser.dump(bib_data, bibtex_file)


