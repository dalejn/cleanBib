import subprocess
from pylatexenc.latex2text import LatexNodes2Text
import unicodedata
import glob
from pybtex.database.input import bibtex
import os
import csv
from bibtexparser.bparser import BibTexParser
import bibtexparser
import string
from queries import *
import numpy as np

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

def clean_name(name, flag):
    """

    :param name: string author name
            flag: utf or latex
    :return: clean_name
    """
    if flag=='latex':
        clean_name = convertLatexSpecialChars(str(name)[7:-3]).replace(
            "', Protected('", ""
        ).replace(
            "'), '", ""
        )
    elif flag=='utf':
        clean_name = convertSpecialCharsToUTF8(str(name)[7:-3]).replace(
            "', Protected('", ""
        ).replace(
            "'), '", ""
        )
    else:
        raise ValueError

    return clean_name

def removeMiddleName(line):
    """

    :param line: string author name
    :return: the same string, but with the middle name removed
    """
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


def returnMiddletName(line):
    """

    :param line: string author name
    :return: only the middle name
    """
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
    """

    :param latex_text:
    :return:
    """
    return LatexNodes2Text().latex_to_text(latex_text)


def convertSpecialCharsToUTF8(text):
    """

    :param text:
    :return:
    """
    data = LatexNodes2Text().latex_to_text(text)
    return unicodedata.normalize('NFD', data).encode('ascii', 'ignore').decode('utf-8')

def namesFromXrefSelfCite(doi, title):
    """

    :param doi: DOI of published article
    :param title: the title of the same article
    :return: selfCiteCheck: the number of self citations in a published article (indexed by DOI
    """
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


def find_unused_cites(paper_aux_file):
    """

    :param paper_aux_file: path to auxfile
    """
    print(checkcites_output(paper_aux_file))
    unused_in_paper = checkcites_output(paper_aux_file)  # get citations in library not used in paper
    print("Unused citations: ", unused_in_paper.count('=>'))

def get_bib_data(filename, parser="bparser"):
    """

    :param homedir: home directory
           parser: a string telling which parser to use (default is not to use bparser)
    :return: bib_data
    """
    
    if parser == 'bparser':
        bib_data = BibTexParser(common_strings=True, ignore_nonstandard_types=False).parse_file(open(filename))
    else:
        # this one will error if you have duplicates
        parser = bibtex.Parser()
        bib_data = parser.parse_file(filename)

    return bib_data

def get_duplicates(bib_data, filename):
    """
    take bib_data, and get duplicates
    :param homedir: home directory
    :return: bib_data without duplicates
    """

    duplicates = []
    for key in bib_data.entries_dict.keys():
        count = str(bib_data.entries).count("'ID\': \'" + key + "\'")
        if count > 1:
            duplicates.append(key)

            # remove from data
            idx = np.where([x['ID'] == key for x in bib_data.entries])[0]
            # remove first entry, so we keep that one
            idx = idx[1:]
            for i in idx:
                bib_data.entries.remove(bib_data.entries[i])

        # check that we got the duplicate
        if (str(bib_data.entries).count("'ID\': \'" + key + "\'")) > 1:
            raise ValueError("Unable to successfully remove duplicates")

    if len(duplicates) > 0:
        print("\n In your .bib file, we found and removed duplicate entries for the following entries:\n " +
                      ' '.join(map(str, duplicates)) +
              "\n If this is incorrect, please edit your .bib file to give unique identifiers for all unique references. \n")

    if len(duplicates) > 0:
        # write new data to file
        new_bib = filename[:-4] + '_noDuplicates.bib'
        with open(new_bib, 'w') as bibtex_file:
            bibtexparser.dump(bib_data, bibtex_file)

        # reparse
        bib_data = get_bib_data(new_bib, "")
    else:
        bib_data = get_bib_data(filename, "")
    return bib_data


def get_names_published(homedir, bib_data, cr):
    """
    whole pipeline for published papers
    :return: FA,
            LA
    """
    FA = []
    LA = []
    counter = 1
    titleCount = 1  #
    counterNoDOI = list()  # row index (titleCount) of entries with no DOI
    outPath = homedir + 'cleanedBib.csv'

    if os.path.exists(outPath):
        os.remove(outPath)

    with open(outPath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Article', 'FA', 'LA', 'Title', 'SelfCite', 'CitationKey'])

    citedArticleDOI = list()
    citedArticleNoDOI = list()
    allArticles = list()
    for entry in bib_data.entries:
        my_string = entry['cited-references'].split('\n')
        for citedArticle in my_string:
            allArticles.append(citedArticle)
            if citedArticle.partition("DOI ")[-1] == '':
                citedArticleNoDOI.append(citedArticle)
                counterNoDOI.append(titleCount)
            else:
                line = citedArticle.partition("DOI ")[-1].replace("DOI ", "").rstrip(".")
                line = ''.join(c for c in line if c not in '{[}] ')
                if "," in line:
                    line = line.partition(",")[-1]
                citedArticleDOI.append(line)
                with open('citedArticlesDOI.csv', 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile, delimiter=',')
                    writer.writerow([line])
            titleCount += 1

    articleNum = 0
    for doi in citedArticleDOI:
        try:
            FA = namesFromXref(cr, doi, '', 'first')
        except UnboundLocalError:
            sleep(1)
            continue

        try:
            LA = namesFromXref(cr, doi, '', 'last')
        except UnboundLocalError:
            sleep(1)
            continue

        try:
            selfCiteCount = namesFromXrefSelfCite(doi, '')
        except UnboundLocalError:
            sleep(1)
            continue

        with open(outPath, 'a', newline='') as csvfile:
            if selfCiteCount == 0:
                writer = csv.writer(csvfile, delimiter=',')
                getArticleIndex = [i for i, s in enumerate(allArticles) if doi in s]
                writer.writerow([counter, convertSpecialCharsToUTF8(FA), convertSpecialCharsToUTF8(LA),
                                 allArticles[[i for i, s in enumerate(allArticles) if doi in s][0]], '', ''])
                print(str(counter) + ": " + doi)
                counter += 1
            else:
                print(str(articleNum) + ": " + doi + "\t\t\t <-- self-citation")
        articleNum += 1

    if len(citedArticleNoDOI) > 0:
        print()
        for elem in citedArticleNoDOI:
            with open(outPath, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow([counter, '', '', elem, '', ''])
                print(str(counter) + ": " + elem)
            counter += 1
        print()
        raise ValueError("WARNING: No article DOI was provided for the last " + str(
            len(citedArticleNoDOI)) + " listed papers. Please manually search for these articles. IF AND ONLY IF your citing paper's first and last author are not co-authors in the paper that was cited, enter the first name of the first and last authors of the paper that was cited manually. Then, continue to the next code block.")

    return FA, LA


def get_names(homedir, bib_data, yourFirstAuthor, yourLastAuthor, optionalEqualContributors, cr):
    """
    take bib_data, and get lists of first and last names. should also get self cites and CDS cites
    :return: FA
              LA
    """
    counter = 1
    outPath = homedir + 'cleanedBib.csv'

    if os.path.exists(outPath):
        os.remove(outPath)

    with open(outPath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Article', 'FA', 'LA', 'Title', 'SelfCite', 'CitationKey'])

    for key in bib_data.entries.keys():
        diversity_bib_titles = ['The extent and drivers of gender imbalance in neuroscience reference lists',
                                'The gender citation gap in international relations',
                                'Gendered citation patterns in international relations journals',
                                'Quantitative evaluation of gender bias in astronomical publications from citation counts',
                                '\# CommunicationSoWhite',
                                '{Just Ideas? The Status and Future of Publication Ethics in Philosophy: A White Paper}',
                                'Gendered citation patterns across political science and social science methodology fields',
                                'Gender Diversity Statement and Code Notebook v1.0',
                                'Racial and ethnic imbalance in neuroscience reference lists and intersections with gender',
                                'Gender Diversity Statement and Code Notebook v1.1',
                                'Gendered citation practices in the field of communication',
                                'Gender disparity in citations in high- impact journal articles',
                                'Gender Disparity in Citations in High-Impact Journal Articles',
                                'Gender (im)balance in citation practices in cognitive neuroscience',
                                'Gender (Im)balance in Citation Practices in Cognitive Neuroscience',
                                'Name-ethnicity classification from open sources',
                                'Predicting race and ethnicity from the sequence of characters in a name']
        if bib_data.entries[key].fields['title'] in diversity_bib_titles:
            continue

        try:
            author = bib_data.entries[key].persons['author']
        except:
            author = bib_data.entries[key].persons['editor']

        FA = author[0].rich_first_names
        LA = author[-1].rich_first_names
        FA = convertLatexSpecialChars(str(FA)[7:-3]).translate(str.maketrans('', '', string.punctuation)).replace(
            'Protected', "").replace(" ", '')
        LA = convertLatexSpecialChars(str(LA)[7:-3]).translate(str.maketrans('', '', string.punctuation)).replace(
            'Protected', "").replace(" ", '')

        # check if we grabbed a first initial when a full middle name was available
        if (len(FA) == 1):
            mn = author[0].rich_middle_names
            mn = convertLatexSpecialChars(str(mn)[7:-3]).translate(
                str.maketrans('', '', string.punctuation)).replace('Protected', "").replace(" ", '')
            if len(mn) > 1:
                FA = mn
        if (len(LA) == 1):
            mn = author[-1].rich_middle_names
            mn = convertLatexSpecialChars(str(mn)[7:-3]).translate(
                str.maketrans('', '', string.punctuation)).replace('Protected', "").replace(" ", '')
            if len(mn) > 1:
                LA = mn

        # check that we got a name (not an initial) from the bib file, if not try using the title in the crossref API
        try:
            title = bib_data.entries_dict[key].fields['title'].replace(',', '').\
                replace(',', '').replace('{', '').replace('}','')
        except:
            title = ''
        try:
            doi = bib_data.entries_dict[key].fields['doi']
        except:
            doi = ''
        if FA == '' or len(FA.split('.')[0]) <= 1:
            while True:
                try:
                    FA = namesFromXref(cr, doi, title, 'first')
                except UnboundLocalError:
                    sleep(1)
                    continue
                break
        if LA == '' or len(LA.split('.')[0]) <= 1:
            while True:
                try:
                    LA = namesFromXref(cr, doi, title, 'last')
                except UnboundLocalError:
                    sleep(1)
                    continue
                break

        selfCite = self_cites(author, yourFirstAuthor,yourLastAuthor, optionalEqualContributors, FA, LA, counter, key)
        counter += 1
        with open(outPath, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(
                [counter, convertSpecialCharsToUTF8(FA), convertSpecialCharsToUTF8(LA), title, selfCite, key])


def self_cites(author, yourFirstAuthor, yourLastAuthor, optionalEqualContributors, FA, LA, counter, key):
    """
    take author list, and find self citations

    :param author:
    :param yourFirstAuthor:
    :param yourLastAuthor:
    :param optionalEqualContributors:
    :param FA:
    :param LA:
    :return:
    """

    if (yourFirstAuthor == 'LastName, FirstName OptionalMiddleInitial') or (
            yourLastAuthor == 'LastName, FirstName OptionalMiddleInitial'):
        raise ValueError("Please enter your manuscript's first and last author names")

    selfCiteCheck1 = [s for s in author if removeMiddleName(yourLastAuthor) in
                      str(
                          [clean_name(s.rich_last_names, 'latex'),
                           clean_name(s.rich_first_names, 'latex')]
                      ).replace("'", "")]

    selfCiteCheck1a = [s for s in author if removeMiddleName(yourLastAuthor) in
                      str(
                          [clean_name(s.rich_last_names, 'utf'),
                           clean_name(s.rich_first_names, 'utf')]
                      ).replace("'", "")]
    selfCiteCheck1b = [s for s in author if removeMiddleName(yourLastAuthor) in
                       str(
                           [clean_name(s.rich_last_names, 'utf'),
                            LA]).replace("'","")]
    # I was in the process of cleaning all thisup when we stopped
    selfCiteCheck2 = [s for s in author if removeMiddleName(yourFirstAuthor) in
                      str([clean_name(s.rich_last_names, 'utf'),
                           clean_name(s.rich_first_names, 'utf')]
                      ).replace("'", "")]
    selfCiteCheck2a = [s for s in author if removeMiddleName(yourFirstAuthor) in
                       str(
                           [clean_name(s.rich_last_names, 'utf'),
                            clean_name(s.rich_first_names, 'utf')]
                       ).replace("'", "")]
    selfCiteCheck2b = [s for s in author if removeMiddleName(yourFirstAuthor) in
                       str(
                            [clean_name(s.rich_last_names, 'utf'),
                            FA]).replace("'","")]

    nameCount = 0
    if optionalEqualContributors != (
            'LastName, FirstName OptionalMiddleInitial', 'LastName, FirstName OptionalMiddleInitial'):
        for name in optionalEqualContributors:
            selfCiteCheck3 = [s for s in author if removeMiddleName(name) in
                              str( [clean_name(s.rich_last_names, 'utf'),
                           clean_name(s.rich_first_names, 'utf')]
                      ).replace("'", "")]
            selfCiteCheck3a = [s for s in author if removeMiddleName(name) in
                               str(
                                   [clean_name(s.rich_last_names, 'utf'),
                                    clean_name(s.rich_first_names, 'utf')]
                               ).replace("'", "")]
            if len(selfCiteCheck3) > 0:
                nameCount += 1
            if len(selfCiteCheck3a) > 0:
                nameCount += 1
    selfCiteChecks = [selfCiteCheck1, selfCiteCheck1a, selfCiteCheck1b, selfCiteCheck2, selfCiteCheck2a,
                      selfCiteCheck2b]
    if sum([len(check) for check in selfCiteChecks]) + nameCount > 0:
        selfCite = 'Y'
        if len(FA) < 2:
            print(
                str(counter) + ": " + key + "\t\t  <-- self-citation <--  ***NAME MISSING OR POSSIBLY INCOMPLETE***")
        else:
            print(str(counter) + ": " + key + "  <-- self-citation")
    else:
        selfCite = 'N'
        if len(FA) < 2:
            print(str(counter) + ": " + key + "\t\t  <--  ***NAME MISSING OR POSSIBLY INCOMPLETE***")
        else:
            print(str(counter) + ": " + key)

    return selfCite


def bib_check(homedir):
    # Do a final check on the bibliography entries
    authors_full_list = pd.read_csv(homedir + 'cleanedBib.csv')
    skip_selfCites = list(authors_full_list.loc[authors_full_list['SelfCite'] == 'Y']['CitationKey'])

    with open(os.path.join(homedir, 'cleanedBib.csv')) as csvfile:
        names_csv = csv.reader(csvfile)
        names_db = []
        for row in names_csv:
            names_db.append(row)

    incomplete_name_bib_keys = []
    authors_full_list = []
    for row in names_db[1:]:  # Skip the first row, it's just headers
        # Check that the authors' names have at least 2 characters and no periods
        row_id, first_author, last_author, _, self_cite, bib_key = row
        authors_full_list.append(first_author)  # For counting the number of query calls needed
        authors_full_list.append(last_author)
        if len(first_author) < 2 or len(last_author) < 2 or '.' in first_author + last_author:
            if bib_key not in skip_selfCites:
                incomplete_name_bib_keys.append(bib_key)

    if len(incomplete_name_bib_keys) > 0:
        warning_message = "\n STOP: Please revise incomplete full first names or empty cells. Then, re-run step 2. "
        warning_message += "Here are some suggestions to check for with the following citation keys in your .bib file: "
        print(warning_message)
        print(incomplete_name_bib_keys)

    final_warning_message = "\n Only continue if you've run step 2,"
    final_warning_message += " and this code no longer returns error or instructions to revise the .bib file."
    print("\n")
    print(final_warning_message)


