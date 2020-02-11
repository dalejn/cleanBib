# before using, install bibtexparser using shell command `pip install bibtexparser`
# also set paths to:
# paper_aux_file
# bib_file
# paper_bib_file (output)
## MODIFIED BY EGT 2-10-2020 for multiple bib file inputs, non-standard bib entries,
## "=>" style of checkcites, and POSSIBLY NON-ORDERED DICTS (python < 3.6, dicts are non-ordered)
## also \bibliographystyle{apsrev4-2} needed in tex file to prevent "aip41Control" from being a checkcites bib entry somehow.
import numpy as np
import bibtexparser
from bibtexparser.bparser import BibTexParser
import subprocess
import os, copy

# for check cites to work, the .bib file must exist in the path specified in the .tex file used to generate the .aux file
homedir = '/Users/eteich/Bassett/arratia_collab/papers/xtal_repo'
paper_aux_file = 'draft.aux' # name of aux file for paper
bib_files = ['bibliography/dsb_mat.bib','bibliography/misc.bib'] # path to full library .bib file, same as one referenced in .tex file
paper_bib_file = 'clean_draft_eli.bib' # name of .bib file output

## NEEDS PYTHON 3.6+,
## if python < 3.5, this has to be backported:
## https://stackoverflow.com/questions/40590192/getting-an-error-attributeerror-module-object-has-no-attribute-run-while
def subprocess_run(*popenargs, **kwargs):
    input = kwargs.pop("input", None)
    check = kwargs.pop("handle", False)

    if input is not None:
        if 'stdin' in kwargs:
            raise ValueError('stdin and input arguments may not both be used.')
        kwargs['stdin'] = subprocess.PIPE

    process = subprocess.Popen(*popenargs, **kwargs)
    try:
        stdout, stderr = process.communicate(input)
    except:
        process.kill()
        process.wait()
        raise
    retcode = process.poll()
    if check and retcode:
        raise subprocess.CalledProcessError(
            retcode, process.args, output=stdout, stderr=stderr)
    return retcode, stdout, stderr

def checkcites_output(aux_file):
    # take in aux file for tex document, return list of citation keys
    # that are in .bib file but not in document

    try:
        result = subprocess.run(['checkcites',aux_file], stdout=subprocess.PIPE)
        result = result.stdout.decode('utf-8')
    except AttributeError:
        retcode, stdout, stderr = subprocess_run(['checkcites',aux_file], stdout=subprocess.PIPE)
        result = stdout.decode('utf-8')
    unused_array_raw = result.split('\n')
    # process array of unused references + other output
    unused_array_final = list()
    for x in unused_array_raw:
        if len(x) > 0: # if line is not empty
            if x[0] == '=':  # and if first character is a '=', it's a citation key
                unused_array_final.append(x[3:]) # truncate '=> '
    return(unused_array_final)

os.chdir(homedir)
unused_in_paper = checkcites_output(paper_aux_file) # get citations in library not used in paper
print("Unused citations: ", len(unused_in_paper))

parser = BibTexParser()
parser.ignore_nonstandard_types = False

bib_data = None
for bib_file in bib_files:
    with open(bib_file) as bibtex_file:
        if bib_data is None:
            bib_data = bibtexparser.load(bibtex_file)
        else:
            bib_data_extra = bibtexparser.load(bibtex_file, parser)
            bib_data.entries_dict.update(bib_data_extra.entries_dict)
            bib_data.entries.extend(bib_data_extra.entries)

all_library_citations = list(bib_data.entries_dict.keys())
print("All citations: ", len(all_library_citations))

for k in all_library_citations:
    if k in unused_in_paper:
        del bib_data.entries_dict[k] # remove from entries dictionary if not in paper

#in_paper_mask = [x not in unused_in_paper for x in all_library_citations] # get mask of citations in paper
in_paper_mask = [bib_data.entries[x]['ID'] not in unused_in_paper for x in range(len(bib_data.entries))]
bib_data.entries = [bib_data.entries[x] for x in np.where(in_paper_mask)[0]] # replace entries list with entries only in paper

with open(paper_bib_file, 'w') as bibtex_file:
    bibtexparser.dump(bib_data, bibtex_file)

# remove self-citations (defined as cited papers for which
# either the first or last author of the citing paper was a co-author)
# from consideration

# define first author and last author names of citing paper -- will exclude citations of these authors
# beware of latex symbols within author names
citing_authors = np.array(['Teich, Erin G.', 'Bassett, Danielle S.'])
#in_paper_citations = list(bib_data.entries_dict.keys())
in_paper_citations = [bib_data.entries[x]['ID'] for x in range(len(bib_data.entries))] # get list of citation keys in paper

# extract author list for every cited paper
cited_authors = [bib_data.entries_dict[x]['author'] for x in in_paper_citations]
# find citing authors in cited author list
# using nested list comprehension, make a citing author -by- citation array of inclusion
self_cite_mask = np.array([[citing_author in authors for authors in cited_authors] for citing_author in citing_authors])
self_cite_mask = np.any(self_cite_mask,axis=0) # collapse across citing authors such that any coauthorship by either citing author -> exclusion

print("Self-citations: ", [bib_data.entries[x]['ID'] for x in np.where(self_cite_mask)[0]]) # print self citations
for idx,k in enumerate(in_paper_citations):
    if self_cite_mask[idx]:
        del bib_data.entries_dict[k] # delete citation from dictionary if self citationi
bib_data.entries = [bib_data.entries[x] for x in np.where(np.invert(self_cite_mask))[0]] # replace entries list with entries that aren't self citations

paper_bib_file_excl_sc = os.path.splitext(paper_bib_file)[0] + '_noselfcite.bib'

with open(paper_bib_file_excl_sc, 'w') as bibtex_file:
    bibtexparser.dump(bib_data, bibtex_file)
