def namesFromXref(cr, doi, title, authorPos):
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


def gender_base(homedir):
	"""
	for unknown gender, fill with base rates
	you will never / can't run this (that file is too big to share)
	"""
	main_df = pd.read_csv('/%s/data/NewArticleData2019.csv'%(homedir),header=0)


	gender_base = {}
	for year in np.unique(main_df.PY.values):
		ydf = main_df[main_df.PY==year].AG
		fa = np.array([x[0] for x in ydf.values])
		la = np.array([x[1] for x in ydf.values])

		fa_m = len(fa[fa=='M'])/ len(fa[fa!='U'])
		fa_w = len(fa[fa=='W'])/ len(fa[fa!='U'])

		la_m = len(la[fa=='M'])/ len(la[la!='U'])
		la_w = len(la[fa=='W'])/ len(la[la!='U'])

		gender_base[year] = [fa_m,fa_w,la_m,la_w]

	gender_base[2020] = [fa_m,fa_w,la_m,la_w]

	with open(homedir + '/data/gender_base' + '.pkl', 'wb') as f:
		pickle.dump(gender_base, f, pickle.HIGHEST_PROTOCOL)


def get_pred_demos(authors):
    """

    :param authors:
    :return:
    """
    authors = authors.split(' ')
    print('first author is %s %s ' % (authors[1], authors[0]))
    print('last author is %s %s ' % (authors[3], authors[2]))
    print("we don't count these, but check the predictions file to ensure your names did not slip through!")

    citation_matrix = np.zeros((8, 8))

    print('looping through your references, predicting gender and race')

    columns = ['CitationKey', 'Author', 'Gender', 'W', 'A', 'GendCat']
    paper_df = pd.DataFrame(columns=columns)

    gender = []
    race = []

    idx = 0
    for paper in tqdm.tqdm(bibfile.entries, total=len(bibfile.entries)):
        if 'author' not in bibfile.entries[paper].persons.keys():
            continue  # some editorials have no authors
        if 'year' not in bibfile.entries[paper].fields.keys():
            year = 2020
        else:
            year = int(bibfile.entries[paper].fields['year'])

        if year not in gender_base.keys():
            gb = gender_base[1995]
        else:
            gb = gender_base[year]

        fa = bibfile.entries[paper].persons['author'][0]
        try:
            fa_fname = fa.first_names[0]
        except:
            fa_fname = fa.last_names[0]  # for people like Plato
        fa_lname = fa.last_names[0]

        la = bibfile.entries[paper].persons['author'][-1]
        try:
            la_fname = la.first_names[0]
        except:
            la_fname = la.last_names[0]  # for people like Plato
        la_lname = la.last_names[0]

        if fa_fname.lower().strip() == authors[1].lower().strip():
            if fa_lname.lower().strip() == authors[0].lower().strip():
                continue

        if fa_fname.lower().strip() == authors[3].lower().strip():
            if fa_lname.lower().strip() == authors[2].lower().strip():
                continue

        if la_fname.lower().strip() == authors[1].lower().strip():
            if la_lname.lower().strip() == authors[0].lower().strip():
                continue

        if la_fname.lower().strip() == authors[3].lower().strip():
            if la_lname.lower().strip() == authors[2].lower().strip():
                continue

        fa_fname = convertLatexSpecialChars(str(fa_fname.encode("ascii", errors="ignore").decode())).translate(
            str.maketrans('', '', re.sub('\-', '', string.punctuation))).replace('Protected', "").replace(" ", '')
        fa_lname = convertLatexSpecialChars(str(fa_lname.encode("ascii", errors="ignore").decode())).translate(
            str.maketrans('', '', re.sub('\-', '', string.punctuation))).replace('Protected', "").replace(" ", '')
        la_fname = convertLatexSpecialChars(str(la_fname.encode("ascii", errors="ignore").decode())).translate(
            str.maketrans('', '', re.sub('\-', '', string.punctuation))).replace('Protected', "").replace(" ", '')
        la_lname = convertLatexSpecialChars(str(la_lname.encode("ascii", errors="ignore").decode())).translate(
            str.maketrans('', '', re.sub('\-', '', string.punctuation))).replace('Protected', "").replace(" ", '')

        names = [{'lname': fa_lname, 'fname': fa_fname}]
        fa_df = pd.DataFrame(names, columns=['fname', 'lname'])
        asian, hispanic, black, white = pred_fl_reg_name(fa_df, 'lname', 'fname').values[0][-4:]
        fa_race = [white, asian, hispanic, black]

        names = [{'lname': la_lname, 'fname': la_fname}]
        la_df = pd.DataFrame(names, columns=['fname', 'lname'])
        asian, hispanic, black, white = pred_fl_reg_name(la_df, 'lname', 'fname').values[0][-4:]
        la_race = [white, asian, hispanic, black]

        url = "https://gender-api.com/get?key=" + gender_key + "&name=%s" % (quote(fa_fname))
        response = urlopen(url)
        decoded = response.read().decode('utf-8')
        fa_gender = json.loads(decoded)
        if fa_gender['gender'] == 'female':
            fa_g = [0, fa_gender['accuracy'] / 100.]
        if fa_gender['gender'] == 'male':
            fa_g = [fa_gender['accuracy'] / 100., 0]
        if fa_gender['gender'] == 'unknown':
            fa_g = gb[:2]

        url = "https://gender-api.com/get?key=" + gender_key + "&name=%s" % (quote(la_fname))
        response = urlopen(url)
        decoded = response.read().decode('utf-8')
        la_gender = json.loads(decoded)
        if la_gender['gender'] == 'female':
            la_g = [0, la_gender['accuracy'] / 100.]

        if la_gender['gender'] == 'male':
            la_g = [la_gender['accuracy'] / 100., 0]

        if la_gender['gender'] == 'unknown':
            la_g = gb[2:]

        fa_data = np.array(
            [paper, '%s,%s' % (fa_fname, fa_lname), '%s,%s' % (fa_gender['gender'], fa_gender['accuracy']), fa_race[0],
             np.sum(fa_race[1:]), '']).reshape(1, 6)
        paper_df = paper_df.append(pd.DataFrame(fa_data, columns=columns), ignore_index=True)
        la_data = np.array(
            [paper, '%s,%s' % (la_fname, la_lname), '%s,%s' % (la_gender['gender'], la_gender['accuracy']), la_race[0],
             np.sum(la_race[1:]), '%s%s' % (fa_gender['gender'], la_gender['gender'])]).reshape(1, 6)
        paper_df = paper_df.append(pd.DataFrame(la_data, columns=columns), ignore_index=True)

        mm = fa_g[0] * la_g[0]
        wm = fa_g[1] * la_g[0]
        mw = fa_g[0] * la_g[1]
        ww = fa_g[1] * la_g[1]
        mm, wm, mw, ww = [mm, wm, mw, ww] / np.sum([mm, wm, mw, ww])

        gender.append([mm, wm, mw, ww])

        ww = fa_race[0] * la_race[0]
        aw = np.sum(fa_race[1:]) * la_race[0]
        wa = fa_race[0] * np.sum(la_race[1:])
        aa = np.sum(fa_race[1:]) * np.sum(la_race[1:])

        race.append([ww, aw, wa, aa])

        paper_matrix = np.zeros((2, 8))
        paper_matrix[0] = np.outer(fa_g, fa_race).flatten()
        paper_matrix[1] = np.outer(la_g, la_race).flatten()

        paper_matrix = np.outer(paper_matrix[0], paper_matrix[1])

        citation_matrix = citation_matrix + paper_matrix
        idx = idx + 1

    mm, wm, mw, ww = np.mean(gender, axis=0) * 100
    WW, aw, wa, aa = np.mean(race, axis=0) * 100

    return mm, wm, mw, ww, WW, aw, wa,aa

def print_statements(mm, wm, mw, ww, WW, aw, wa,aa):
    statement = "Recent work in several fields of science has identified a bias in citation practices such that papers from women and other minority scholars \
    are under-cited relative to the number of such papers in the field (1-9). Here we sought to proactively consider choosing references that reflect the \
    diversity of the field in thought, form of contribution, gender, race, ethnicity, and other factors. First, we obtained the predicted gender of the first \
    and last author of each reference by using databases that store the probability of a first name being carried by a woman (5, 10). By this measure \
    (and excluding self-citations to the first and last authors of our current paper), our references contain ww% woman(first)/woman(last), \
    MW% man/woman, WM% woman/man, and MM% man/man. This method is limited in that a) names, pronouns, and social media profiles used to construct the \
    databases may not, in every case, be indicative of gender identity and b) it cannot account for intersex, non-binary, or transgender people. \
    Second, we obtained predicted racial/ethnic category of the first and last author of each reference by databases that store the probability of a \
    first and last name being carried by an author of color (11, 12). By this measure (and excluding self-citations), our references contain AA% author of \
    color (first)/author of color(last), WA% white author/author of color, AW% author of color/white author, and WW% white author/white author. This method \
    is limited in that a) names and Florida Voter Data to make the predictions may not be indicative of racial/ethnic identity, and b) \
    it cannot account for Indigenous and mixed-race authors, or those who may face differential biases due to the ambiguous racialization or ethnicization of their names.  \
    We look forward to future work that could help us to better understand how to support equitable practices in science."

    statement = statement.replace('MM', str(np.around(mm, 2)))
    statement = statement.replace('WM', str(np.around(wm, 2)))
    statement = statement.replace('MW', str(np.around(mw, 2)))
    statement = statement.replace('ww', str(np.around(ww, 2)))
    statement = statement.replace('WW', str(np.around(WW, 2)))
    statement = statement.replace('AW', str(np.around(aw, 2)))
    statement = statement.replace('WA', str(np.around(wa, 2)))
    statement = statement.replace('AA', str(np.around(aa, 2)))

    statementLatex = "Recent work in several fields of science has identified a bias in citation practices such that papers from women and other minority scholars \
    are under-cited relative to the number of such papers in the field \cite{mitchell2013gendered,dion2018gendered,caplar2017quantitative, maliniak2013gender, Dworkin2020.01.03.894378, bertolero2021racial, wang2021gendered, chatterjee2021gender, fulvio2021imbalance}. Here we sought to proactively consider choosing references that reflect the\
    diversity of the field in thought, form of contribution, gender, race, ethnicity, and other factors. First, we obtained the predicted gender of the first \
    and last author of each reference by using databases that store the probability of a first name being carried by a woman \cite{Dworkin2020.01.03.894378,zhou_dale_2020_3672110}. By this measure \
    (and excluding self-citations to the first and last authors of our current paper), our references contain ww\% woman(first)/woman(last), \
    MW\% man/woman, WM\% woman/man, and MM\% man/man. This method is limited in that a) names, pronouns, and social media profiles used to construct the \
    databases may not, in every case, be indicative of gender identity and b) it cannot account for intersex, non-binary, or transgender people. \
    Second, we obtained predicted racial/ethnic category of the first and last author of each reference by databases that store the probability of a \
    first and last name being carried by an author of color \cite{ambekar2009name, sood2018predicting}. By this measure (and excluding self-citations), our references contain AA\% author of \
    color (first)/author of color(last), WA\% white author/author of color, AW\% author of color/white author, and WW\% white author/white author. This method \
    is limited in that a) names and Florida Voter Data to make the predictions may not be indicative of racial/ethnic identity, and b) \
    it cannot account for Indigenous and mixed-race authors, or those who may face differential biases due to the ambiguous racialization or ethnicization of their names.  \
    We look forward to future work that could help us to better understand how to support equitable practices in science."

    statementLatex = statementLatex.replace('MM', str(np.around(mm, 2)))
    statementLatex = statementLatex.replace('WM', str(np.around(wm, 2)))
    statementLatex = statementLatex.replace('MW', str(np.around(mw, 2)))
    statementLatex = statementLatex.replace('ww', str(np.around(ww, 2)))
    statementLatex = statementLatex.replace('WW', str(np.around(WW, 2)))
    statementLatex = statementLatex.replace('AW', str(np.around(aw, 2)))
    statementLatex = statementLatex.replace('WA', str(np.around(wa, 2)))
    statementLatex = statementLatex.replace('AA', str(np.around(aa, 2)))

    return statement, statementLatex

