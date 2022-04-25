import subprocess
from pylatexenc.latex2text import LatexNodes2Text
import unicodedata

def checkcites_output(aux_file):
    '''take in aux file for tex document, return list of citation keys
    that are in .bib file but not in document'''

    result = subprocess.run(['texlua', 'checkcites.lua', aux_file[0]], stdout=subprocess.PIPE)
    result = result.stdout.decode('utf-8')
    unused_array_raw = result.split('\n')
    # process array of unused references + other output
    unused_array_final = list()
    for x in unused_array_raw:
        if len(x) > 0: # if line is not empty
            if x[0] == '-':  # and if first character is a '-', it's a citation key
                unused_array_final.append(x[2:]) # truncate '- '
    if "------------------------------------------------------------------------" in unused_array_final:
        return result
    else:
        return unused_array_final


def removeMiddleName(line):
    arr = line.split()
    last = arr.pop()
    n = len(arr)
    if n == 4:
        first, middle = ' '.join(arr[:2]), ' '.join(arr[2:])
    elif n == 3:
        first, middle = arr[0], ' '.join(arr[1:])
    elif n == 2:
        first, middle = arr
    elif n==1:
        return line
    return str(first + ' ' + middle)


def returnFirstName(line):
    arr = line.split()
    n = len(arr)
    if n == 4:
        first, middle = ' '.join(arr[:2]), ' '.join(arr[2:])
    elif n == 3:
        first, middle = arr[0], ' '.join(arr[1:])
    elif n == 2:
        first, middle = arr
    elif n==1:
        return line
    return str(middle)


def convertLatexSpecialChars(latex_text):
    return LatexNodes2Text().latex_to_text(latex_text)


def convertSpecialCharsToUTF8(text):
    data = LatexNodes2Text().latex_to_text(text)
    return unicodedata.normalize('NFD', data).encode('ascii', 'ignore').decode('utf-8')

def namesFromXrefSelfCite(doi, title):
    selfCiteCheck = 0
    # get cross ref data
    authors = ['']
    # first try DOI
    if doi != "":
        works = cr.works(query=title, select=["DOI", "author"], limit=1, filter={'doi': doi})
        if works['message']['total-results'] > 0:
            authors = works['message']['items'][0]['author']

    for i in authors:
        if i != "":
            first = i['given'].replace('.', ' ').split()[0]
            last = i['family'].replace('.', ' ').split()[0]
            authors = removeMiddleName(last + ", " + first)
            if authors in removeMiddleName(yourFirstAuthor) or authors in removeMiddleName(
                    convertSpecialCharsToUTF8(yourFirstAuthor)) or authors in removeMiddleName(
                    yourLastAuthor) or authors in removeMiddleName(convertSpecialCharsToUTF8(yourLastAuthor)):
                selfCiteCheck += 1
    return selfCiteCheck