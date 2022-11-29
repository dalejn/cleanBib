import numpy as np
import pandas as pd
import pickle
import tqdm as tqdm
import preprocessing
import re
import string
from ethnicolr import pred_fl_reg_name
from urllib.parse import quote
from urllib.request import urlopen
import json
import matplotlib.pyplot as plt
import seaborn as sns

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


def get_gender_base(homedir):
    """
    for unknown gender, fill with base rates
    you will never / can't run this (that file is too big to share)
    """

    with open(homedir + 'data/gender_base' + '.pkl', 'rb') as f:
        gender_base = pickle.load(f)

    return gender_base


def get_pred_demos(authors, homedir, bibfile, gender_key, font='Palatino', method='florida'):
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
    # skip self-citations
    authors_full_list = pd.read_csv(homedir + 'cleanedBib.csv')
    skip_selfCites = list(authors_full_list.loc[authors_full_list['SelfCite'] == 'Y']['CitationKey'])
    # skip citation diversity statement papers
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
    # save base gender rates
    gender_base = get_gender_base(homedir)
    # make a dictionary of names so we don't query the same thing twice
    full_name_data = {}
    first_name_data = {}
    n_gen_queries = 0
    n_race_queries = 0
    for paper in tqdm.tqdm(bibfile.entries, total=len(bibfile.entries)):
        if paper in skip_selfCites:
            continue
        if bibfile.entries[paper].fields['title'] in diversity_bib_titles:
            continue
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


        fa_fname = preprocessing.convertLatexSpecialChars(str(fa_fname.encode("ascii", errors="ignore").decode())).translate(
            str.maketrans('', '', re.sub('\-', '', string.punctuation))).replace('Protected', "").replace(" ", '')
        fa_lname = preprocessing.convertLatexSpecialChars(str(fa_lname.encode("ascii", errors="ignore").decode())).translate(
            str.maketrans('', '', re.sub('\-', '', string.punctuation))).replace('Protected', "").replace(" ", '')
        la_fname = preprocessing.convertLatexSpecialChars(str(la_fname.encode("ascii", errors="ignore").decode())).translate(
            str.maketrans('', '', re.sub('\-', '', string.punctuation))).replace('Protected', "").replace(" ", '')
        la_lname = preprocessing.convertLatexSpecialChars(str(la_lname.encode("ascii", errors="ignore").decode())).translate(
            str.maketrans('', '', re.sub('\-', '', string.punctuation))).replace('Protected', "").replace(" ", '')

        # double check for self cites again
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

        if (fa_lname, fa_fname) in full_name_data:
            fa_race = full_name_data[(fa_lname, fa_fname)]
        else:
            names = [{'lname': fa_lname, 'fname': fa_fname}]
            fa_df = pd.DataFrame(names, columns=['fname', 'lname'])
            odf = pred_fl_reg_name(fa_df, 'lname', 'fname')
            n_race_queries = n_race_queries + 1
            fa_race = [odf['nh_white'], odf['asian'], odf['hispanic'], odf['nh_black']]
            full_name_data[(fa_lname, fa_fname)] = fa_race

        if (la_lname, la_fname) in full_name_data:
            la_race = full_name_data[(la_lname, la_fname)]
        else:
            names = [{'lname': la_lname, 'fname': la_fname}]
            la_df = pd.DataFrame(names, columns=['fname', 'lname'])
            odf = pred_fl_reg_name(la_df, 'lname', 'fname')
            n_race_queries = n_race_queries + 1
            la_race = [odf['nh_white'], odf['asian'], odf['hispanic'], odf['nh_black']]
            full_name_data[(la_lname, la_fname)] = la_race

        if fa_fname in first_name_data:
            fa_gender, fa_g = first_name_data[fa_fname]
        else:
            fa_gender, fa_g = gen_api_query(gender_key, fa_fname, gb)
            n_gen_queries = n_gen_queries + 1
            first_name_data[fa_fname] = (fa_gender, fa_g)

        if la_fname in first_name_data:
            la_gender, la_g = first_name_data[la_fname]
        else:
            la_gender, la_g = gen_api_query(gender_key, la_fname, gb)
            n_gen_queries= n_gen_queries + 1
            first_name_data[la_fname] = (la_gender, la_g)

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

    # report queries
    print(f"Queried gender api {n_gen_queries} times out of {len(bibfile.entries)*2} entries")
    print(f"Queried race/ethnicity api {n_race_queries} times out of {len(bibfile.entries)*2} entries")

    mm, wm, mw, ww = np.mean(gender, axis=0) * 100
    WW, aw, wa, aa = np.mean(race, axis=0) * 100

    return mm, wm, mw, ww, WW, aw, wa, aa, citation_matrix, paper_df

def gen_api_query(gender_key, name, gb):
    url = "https://gender-api.com/get?key=" + gender_key + "&name=%s" % (quote(name))
    response = urlopen(url)
    decoded = response.read().decode('utf-8')
    gender = json.loads(decoded)
    if gender['gender'] == 'female':
        g = [0, gender['accuracy'] / 100.]
    if gender['gender'] == 'male':
        g = [gender['accuracy'] / 100., 0]
    if gender['gender'] == 'unknown':
        g = gb[:2]
    return gender, g

def print_statements(mm, wm, mw, ww, WW, aw, wa, aa):
    statement = ("Recent work in several fields of science has identified a bias in citation practices such that papers from women and other minority scholars "
    "are under-cited relative to the number of such papers in the field (1-9). Here we sought to proactively consider choosing references that reflect the "
    "diversity of the field in thought, form of contribution, gender, race, ethnicity, and other factors. First, we obtained the predicted gender of the first "
    "and last author of each reference by using databases that store the probability of a first name being carried by a woman (5, 10). By this measure "
    "and excluding self-citations to the first and last authors of our current paper), our references contain ww% woman(first)/woman(last), "
    "MW% man/woman, WM% woman/man, and MM% man/man. This method is limited in that a) names, pronouns, and social media profiles used to construct the "
    "databases may not, in every case, be indicative of gender identity and b) it cannot account for intersex, non-binary, or transgender people. "
    "Second, we obtained predicted racial/ethnic category of the first and last author of each reference by databases that store the probability of a "
    "first and last name being carried by an author of color (11, 12). By this measure (and excluding self-citations), our references contain AA% author of "
    "color (first)/author of color(last), WA% white author/author of color, AW% author of color/white author, and WW% white author/white author. This method "
    "is limited in that a) names and Florida Voter Data to make the predictions may not be indicative of racial/ethnic identity, and b) "
    "it cannot account for Indigenous and mixed-race authors, or those who may face differential biases due to the ambiguous racialization or ethnicization of their names. "
    "We look forward to future work that could help us to better understand how to support equitable practices in science.")

    statement = statement.replace('MM', str(np.around(mm, 2)))
    statement = statement.replace('WM', str(np.around(wm, 2)))
    statement = statement.replace('MW', str(np.around(mw, 2)))
    statement = statement.replace('ww', str(np.around(ww, 2)))
    statement = statement.replace('WW', np.array2string(WW.values[0], formatter={'float_kind':lambda x: "%.2f" % x}))
    statement = statement.replace('AW', np.array2string(aw.values[0], formatter={'float_kind':lambda x: "%.2f" % x}))
    statement = statement.replace('WA', np.array2string(wa.values[0], formatter={'float_kind':lambda x: "%.2f" % x}))
    statement = statement.replace('AA', str(np.around(aa, 2)))

    statementLatex = ("Recent work in several fields of science has identified a bias in citation practices such that papers from women and other minority scholars "
    "are under-cited relative to the number of such papers in the field \cite{mitchell2013gendered,dion2018gendered,caplar2017quantitative, maliniak2013gender, Dworkin2020.01.03.894378, bertolero2021racial, wang2021gendered, chatterjee2021gender, fulvio2021imbalance}. Here we sought to proactively consider choosing references that reflect the "
    "diversity of the field in thought, form of contribution, gender, race, ethnicity, and other factors. First, we obtained the predicted gender of the first "
    "and last author of each reference by using databases that store the probability of a first name being carried by a woman \cite{Dworkin2020.01.03.894378,zhou_dale_2020_3672110}. By this measure "
    "(and excluding self-citations to the first and last authors of our current paper), our references contain ww\% woman(first)/woman(last), "
    "MW\% man/woman, WM\% woman/man, and MM\% man/man. This method is limited in that a) names, pronouns, and social media profiles used to construct the "
    "databases may not, in every case, be indicative of gender identity and b) it cannot account for intersex, non-binary, or transgender people. "
    "Second, we obtained predicted racial/ethnic category of the first and last author of each reference by databases that store the probability of a "
    "first and last name being carried by an author of color \cite{ambekar2009name, sood2018predicting}. By this measure (and excluding self-citations), our references contain AA\% author of "
    "color (first)/author of color(last), WA\% white author/author of color, AW\% author of color/white author, and WW\% white author/white author. This method "
    "is limited in that a) names and Florida Voter Data to make the predictions may not be indicative of racial/ethnic identity, and b) "
    "it cannot account for Indigenous and mixed-race authors, or those who may face differential biases due to the ambiguous racialization or ethnicization of their names. "
    "We look forward to future work that could help us to better understand how to support equitable practices in science.")

    statementLatex = statementLatex.replace('MM', str(np.around(mm, 2)))
    statementLatex = statementLatex.replace('WM', str(np.around(wm, 2)))
    statementLatex = statementLatex.replace('MW', str(np.around(mw, 2)))
    statementLatex = statementLatex.replace('ww', str(np.around(ww, 2)))
    statementLatex = statementLatex.replace('WW', np.array2string(WW.values[0], formatter={'float_kind':lambda x: "%.2f" % x}))
    statementLatex = statementLatex.replace('AW', np.array2string(aw.values[0], formatter={'float_kind':lambda x: "%.2f" % x}))
    statementLatex = statementLatex.replace('WA', np.array2string(wa.values[0], formatter={'float_kind':lambda x: "%.2f" % x}))
    statementLatex = statementLatex.replace('AA', str(np.around(aa, 2)))

    return statement, statementLatex

def plot_heatmaps(citation_matrix, homedir):
    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    names = ['white_m','api_m','hispanic_m','black_m','white_w','api_w','hispanic_w','black_w']
    plt.close()
    sns.set(style='white')
    fig, axes = plt.subplots(ncols=2,nrows=1,figsize=(7.5,4))
    axes = axes.flatten()
    plt.sca(axes[0])
    heat = sns.heatmap(np.around((citation_matrix/citation_matrix.sum())*100,2),annot=True,ax=axes[0],annot_kws={"size": 8},cmap=cmap,vmax=1,vmin=0)
    axes[0].set_ylabel('first author',labelpad=0)  
    heat.set_yticklabels(names,rotation=0)
    axes[0].set_xlabel('last author',labelpad=1)  
    heat.set_xticklabels(names,rotation=90) 
    heat.set_title('percentage of citations')  

    citation_matrix_sum = citation_matrix / np.sum(citation_matrix) 

    expected = np.load('/%s/data/expected_matrix_florida.npy'%(homedir))
    expected = expected/np.sum(expected)

    percent_overunder = np.ceil( ((citation_matrix_sum - expected) / expected)*100)
    plt.sca(axes[1])
    heat = sns.heatmap(np.around(percent_overunder,2),annot=True,ax=axes[1],fmt='g',annot_kws={"size": 8},vmax=50,vmin=-50,cmap=cmap)
    axes[1].set_ylabel('',labelpad=0)  
    heat.set_yticklabels('')
    axes[1].set_xlabel('last author',labelpad=1)  
    heat.set_xticklabels(names,rotation=90) 
    heat.set_title('percentage over/under-citations')
    plt.tight_layout()

    plt.savefig('/home/jovyan/race_gender_citations.pdf')

def plot_histograms():
    # Plot a histogram #
    names = pd.read_csv('/home/jovyan/predictions.csv')
    total_citations = names.CitationKey.nunique()
    names.GendCat = names.GendCat.str.replace('female', 'W', regex=False)
    names.GendCat = names.GendCat.str.replace('male', 'M', regex=False)
    names.GendCat = names.GendCat.str.replace('unknown', 'U', regex=False)
    gend_cats = names['GendCat'].dropna().unique()  # get a vector of all the gender categories in your paper

    # Create a data frame that will be used to plot the histogram. This will have the gender category (e.g., WW, MM) in the first column and the percentage (e.g., number of WW citations divided by total number of citations * 100) in the second column #
    dat_for_plot = names.groupby('GendCat').size().reset_index()
    all_cats = ['MU', 'WW', 'UM', 'MW', 'WM', 'UW', 'MM']
    empty_dat_for_plot = pd.DataFrame(0, index=np.arange(7), columns=['GendCat', 0])
    empty_dat_for_plot['GendCat'] = all_cats
    set(dat_for_plot['GendCat']).intersection(empty_dat_for_plot['GendCat'])
    for i in set(dat_for_plot['GendCat']).intersection(empty_dat_for_plot['GendCat']):
        empty_dat_for_plot.loc[empty_dat_for_plot['GendCat'] == i, 0] = dat_for_plot.loc[dat_for_plot['GendCat']== i, 0].values
    dat_for_plot = empty_dat_for_plot
    dat_for_plot.rename(columns={0:'count'}, inplace=True)
    dat_for_plot = dat_for_plot.assign(percentage=dat_for_plot['count']/total_citations*100)

    # Create a data frame with only the WW, MW, WM, MM categories and their base rates - to plot percent citations relative to benchmarks
    dat_for_baserate_plot = dat_for_plot.loc[(dat_for_plot.GendCat == 'WW') |
                                             (dat_for_plot.GendCat == 'MW') |
                                             (dat_for_plot.GendCat == 'WM') |
                                             (dat_for_plot.GendCat == 'MM'),:]
    # MM,MW,WM,WW
    # 58.4% for man/man, 9.4% for man/woman, 25.5% for woman/man, and 6.7% for woman/woman
    baserate = [6.7, 9.4, 25.5, 58.4]
    dat_for_baserate_plot['baserate'] = baserate
    dat_for_baserate_plot = dat_for_baserate_plot.assign(citation_rel_to_baserate=
                                                         dat_for_baserate_plot.percentage - dat_for_baserate_plot.baserate
                                                         )

    # plot
    plt.figure()
    sns.barplot(data=dat_for_plot, x='GendCat', y='count', order=np.flip(gend_cats))
    plt.xlabel('Predicted gender category')
    plt.ylabel('Number of papers')
    plt.tight_layout()

    plt.figure()
    sns.barplot(data=dat_for_baserate_plot, x='GendCat', y='citation_rel_to_baserate', order=['WW','WM','MW','MM'])
    plt.xlabel('Predicted gender category')
    plt.ylabel('% of citations relative to benchmarks')
    plt.tight_layout()


def check_genderAPI_balance(genderAPI_key, homedir):
    authors_full_list = pd.read_csv(homedir + 'cleanedBib.csv')
    authors_full_list = authors_full_list.loc[authors_full_list['SelfCite'] == 'N']

    url = "https://gender-api.com/get-stats?key=" + genderAPI_key
    response = urlopen(url)
    decoded = response.read().decode('utf-8')
    decoded_json = json.loads(decoded)
    print('Remaining credits: %s'%decoded_json["remaining_requests"])
    print('This should use (at most) %d credits, '%(authors_full_list.FA.nunique() + authors_full_list.LA.nunique()) + \
            'saving you approx %d'%((authors_full_list.FA.count() + authors_full_list.LA.count())-
                                (authors_full_list.FA.nunique() + authors_full_list.LA.nunique())) + \
          ' credit(s) by storing queries.')


def colorful_latex(paper_df, homedir, tex_file):
    cite_gender = paper_df[1::2]
    cite_gender.GendCat = cite_gender.GendCat.str.replace('female', 'W', regex=False)
    cite_gender.GendCat = cite_gender.GendCat.str.replace('male', 'M', regex=False)
    cite_gender.GendCat = cite_gender.GendCat.str.replace('unknown', 'U', regex=False)
    cite_gender.index = cite_gender.CitationKey
    cite_gender['Color'] = '' # what color to make each gender category
    colors = {'MM':'red','MW':'blue','WW':'green','WM':'magenta','UU':'black',
    'MU':'black','UM':'black','UW':'black','WU':'black'}
    for idx in cite_gender.index: # loop through each citation key and set color
        cite_gender.loc[idx,'Color'] = colors[cite_gender.loc[idx,'GendCat']]

    fin = open(homedir+tex_file)
    texdoc=fin.readlines()
    with open(homedir+tex_file[:-4]+'_gendercolor.tex','w') as fout:
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
                l = ['\\textcolor{' + colors[k] + '}{'+k+'}' for k in colors.keys()]
                fout.write('\tKey: '+ ', '.join(l)+'.\n')


