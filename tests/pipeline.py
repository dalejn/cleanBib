import glob
from habanero import Crossref
import sys
import os
wd = os.getcwd()
print(f'{wd[0:-6]}/utils')
print(f'{wd[0:-6]}/utils')
sys.path.insert(1, f'{wd[0:-6]}/utils')
from preprocessing import *

cr = Crossref()
homedir = '/home/jovyan/'
bib_files = glob.glob(homedir + '*.bib')
paper_aux_file = glob.glob(homedir + '*.aux')
paper_bib_file = 'library_paper.bib'
try:
    tex_file = glob.glob(homedir + "*.tex")[0]
except:
    print('No optional .tex file found.')

yourFirstAuthor = 'LastName, FirstName OptionalMiddleInitial'
yourLastAuthor = 'LastName, FirstName OptionalMiddleInitial'
optionalEqualContributors = ['LastName, FirstName OptionalMiddleInitial', 'LastName, FirstName OptionalMiddleInitial']
checkingPublishedArticle = False

## end of user input
if paper_aux_file:
    find_unused_cites(paper_aux_file)

bib_data = get_bib_data(homedir)
if checkingPublishedArticle:
    FA,LA = get_names_published(homedir, bib_data)
else:
    # find and print duplicates
    get_duplicates(bib_data)
    # get names, remove CDS, find self cites
    FA,LA = get_names(bib_data)