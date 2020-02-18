![Network courtesy Ann Sizemore Blevins](img/repo_pic.png)

# Diversity Statement and Code Notebook

[![DOI](https://zenodo.org/badge/232916183.svg)](https://zenodo.org/badge/latestdoi/232916183)

Motivated from work by [J. D. Dworkin, K. A. Linn, E. G. Teich, P. Zurn, R. T. Shinohara, and D. S. Bassett (2020). bioRxiv. doi: https://doi.org/10.1101/2020.01.03.894378](https://www.biorxiv.org/content/10.1101/2020.01.03.894378v1.full.pdf)

For `.pdf` and `.tex` templates of the statement, see the `/diversityStatement` directory in this repository.

A `.bib` file containing the references used in the statement can be found in `/diversityStatement/bibfile.bib`

## Diversity statement template

> Recent work in neuroscience and other fields has identified a bias in citation practices such that papers from women and other minorities are under-cited relative to the number of such papers in the field [1, 2, 3, 4, 5, 6]. Here we sought to proactively consider choosing references that reflect the diversity of the field in thought, form of contribution, gender, and other factors. We used automatic classification of gender based on the first names of the first and last authors [1], with possible combinations including male/male, male/female, female/male, and female/female. Excluding self-citations to the first and last authors of our current paper, the references contain `A`% male/male, `B`% male/female, `C`% female/male, `D`% female/female, and `E`% unknown categorization. We look forward to future work that could help us to better understand how to support equitable practices in science.

# Instructions

To goal of the coding notebook is to clean your `.bib` file to only contain references that you have cited in your manuscript. This cleaned `.bib` will then be used to generate a data table of full first names that will be used to query the probabilistic gender classifier, [Gender API](https://gender-api.com). Proportions of the predicted gender for first and last author pairs (male/male, male/female, female/male, and female/female) will be calculated. 

1. Obtain a `.bib` file of your manuscript's reference list. You can do this with common reference managers. 

   * [Export `.bib` from Mendeley](https://blog.mendeley.com/2011/10/25/howto-use-mendeley-to-create-citations-using-latex-and-bibtex/)
   * [Export `.bib` from Zotero](https://libguides.mit.edu/ld.php?content_id=34248570)
   * [Export `.bib` from EndNote](https://www.reed.edu/cis/help/LaTeX/EndNote.html)
   * [Export `.bib` from Read Cube Papers](https://support.papersapp.com/support/solutions/articles/30000024634-how-can-i-export-references-from-readcube-papers-)

2. Launch the Binder environment. Please refresh the page if the Binder does not load after 5-10 mins.

    [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/dalejn/cleanBib/master)

3. Open the notebook `cleanBib.ipynb`. Follow the instructions above each code block.

## Input/output

| Input                 | Output                                                                                                                        |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------------|
| `.bib` file(s)**(REQUIRED)**    | `cleanBib.csv`: table of author first names, titles, and .bib keys                                                            |
| `.aux` file (OPTIONAL)| `Authors.csv`: table of author first names, estimated gender classification, and confidence                                   |
| `.tex` file (OPTIONAL)| `yourTexFile_gendercolor.tex`: your `.tex` file modified to compile .pdf with in-line citations colored-coded by gender pairs |

![Color-coded .tex file, Eli Cornblath](img/texColors.png)

# FAQ

* Why do I receive an error when running the code?.
  * The most common errors are due to misformatted .bib files. Errors will usually provide an indication of the line or type of problem in the .bib file. They will require you to manually correct the `.bib` file of formatting errors or incomplete entries. If you cannot resolve an error, please open an `issue` and attach the error pasted into a `.txt` or a screenshot of the error. We will try to help resolve it.
* Will this method work on non-Western names?
  * Yes, the [Gender API supports 177 countries](https://gender-api.com/en/frequently-asked-questions?gclid=Cj0KCQiAmZDxBRDIARIsABnkbYTy9MHmGoR2uBhxEKANbT9B9EFVOSiRzbGeQi7nUn6ODH83s6-RZKwaAjpZEALw_wcB#which-countries-are-supported) but will classify genders with varying confidence. 
* Are self-citations included?
  * We do not include self-citations by default. We define self-citations as those including your first or last author as a co-author.
* What if a reference has only 1 author?
  * We count that author as both the first and last author.
* What about gender-neutral names?
  * We exclude names that cannot be classified with >70% confidence. These are reported in the `Diversity Statement` as "unknown." 
* Should I include the diversity statement references in the gender proportion calculation?
  * Please do not include the diversity statement references. The descriptive statistic of primary interest is of your citation practices.
* What is a `.bib` file?
  * The `.bib` file is a bibliography with tagged entry fields used by LaTeX to format a typesetted manuscript's reference list and its in-line citations. If you are not using LaTeX to write your manuscript, common reference managers that are linked to Microsoft Word or Google Docs also allow you to export `.bib` files (See Instructions, Step 1).
* What is an `.aux` file?
  * The `.aux` file is generated when you compile the `.tex` file to build your manuscript. It is linked to the `.bib` file(s) used to populate your manuscript's reference list and records the citations used.
* I have an idea to advance this project, suggestions about how to improve the notebook, and/or found a bug. Can I contribute?
  * Yes, please open an `issue` or `pull request`. We welcome feedback on any pain points in running this code notebook. If you contribute, please modify the `README.md` to credit yourself in the `Contributors` section in the `pull request`. 

# Other Resources

* [Gender base-rates of neuroscience](https://biaswatchneuro.com/base-rates/neuroscience-base-rates/), based on a poll of SfN attendees from 2014-2018. Categorized by subject area.

* A [list highlighting female neuroscientists](https://anneslist.net/). Categorized by subject area and seniority. 

# References

> [1] J. D. Dworkin, K. A. Linn, E. G. Teich, P. Zurn, R. T. Shinohara, and D. S. Bassett, “The extent and drivers of gender imbalance in neuroscience reference lists,” bioRxiv, 2020.

> [2] D. Maliniak, R. Powers, and B. F. Walter, “The gender citation gap in international relations,” International Organization, vol. 67, no. 4, pp. 889– 922, 2013.

> [3] N. Caplar, S. Tacchella, and S. Birrer, “Quantitative evaluation of gender bias in astronomical publications from citation counts,” Nature Astronomy, vol. 1, no. 6, p. 0141, 2017.

> [4] P. Chakravartty, R. Kuo, V. Grubbs, and C. McIlwain, “# communicationsowhite,” Journal of Communication, vol. 68, no. 2, pp. 254–266, 2018.

> [5] Y. Thiem, K. F. Sealey, A. E. Ferrer, A. M. Trott, and R. Kennison, “Just Ideas? The Status and Future of Publication Ethics in Philosophy: A White Paper,” tech. rep., 2018.

> [6] M. L. Dion, J. L. Sumner, and S. M. Mitchell, “Gendered citation patterns across political science and social science methodology fields,” Political Analysis, vol. 26, no. 3, pp. 312–327, 2018.

# Contributors
(alphabetical)

* Ann Sizemore Blevins
* Eli Cornblath
* Jordan Dworkin
* Jeni Stiso
* Erin Teich
* Dale Zhou

# Changelog

* __2/17/2020__
  * streamlined instructions
  * added repository photo for social media (thanks, Ann!)
  * move instructions into Jupyter notebook
  * added code to automatically remove unused .bib entries instead of needing user to manually remove them (thanks, Eli and Erin!)
  * made removing self-citations default
  * added FAQ
  * added screenshots to instructions
  * added error message to request users remove entries with duplicate IDs. Not automated in case duplicate entry key refers to different references.
  * throw error if entries are incomplete or blank
  * fixed handling of optional middle initial correctly for self-citations
  * added SOS notebook support to put all code and instructions into 1 notebook so users don't have to manually change kernel
  * added optional entry for co-first or co-last authors
  * added optional code block to color-code `.tex` file's citation keys by gender pair classifications
  * added code to search `Crossref` API to automatically complete some incomplete `.bib` entries (thanks, Jeni!)
  * add another self-citation check after manual editing

* __1/19/2020__ 
  * added code to output a column with article titles to make it easier to manually search which bib entries need manual editing
  * added code to output another column that optionally checks for self-citations