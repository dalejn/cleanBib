def namesFromXref(doi, title, authorPos):
    '''Use DOI and article titles to query Crossref for author list'''
    if authorPos == 'first':
        idx = 0
    elif authorPos == 'last':
        idx = -1
    # get cross ref data
    authors = ['']
    # first try DOI
    if doi != "":
        works = cr.works(query=title, select=["DOI", "author"], limit=1, filter={'doi': doi})
        if works['message']['total-results'] > 0:
            authors = works['message']['items'][0]['author']
    elif title != '':
        works = cr.works(query=f'title:"{title}"', select=["title", "author"], limit=10)
        cnt = 0
        name = ''
        # check that you grabbed the proper paper
        if works['message']['items'][cnt]['title'][0].lower() == title.lower():
            authors = works['message']['items'][0]['author']

    # check the all fields are available
    if not 'given' in authors[idx]:
        name = ''
    else:
        # trim initials
        name = authors[idx]['given'].replace('.', ' ').split()[0]

    return name


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
