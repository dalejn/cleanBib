![Network courtesy Ann Sizemore Blevins](img/repo_pic.png)

# Diversity Statement and Code Notebook

Motivated from work by [J. D. Dworkin, K. A. Linn, E. G. Teich, P. Zurn, R. T. Shinohara, and D. S. Bassett (2020). bioRxiv. doi: https://doi.org/10.1101/2020.01.03.894378](https://www.biorxiv.org/content/10.1101/2020.01.03.894378v1.full.pdf)

For `.pdf` and `.tex` templates of the statement, see the `/diversityStatement` directory in this repository.

A `.bib` file containing the references used in the statement can be found in `/diversityStatement/bibfile.bib`

## Diversity statement template

> Recent work in neuroscience and other fields has identified a bias in citation practices such that papers from women and other minorities are under-cited relative to the number of such papers in the field [1, 2, 3, 4, 5, 6]. Here we sought to proactively consider choosing references that reflect the diversity of the field in thought, form of contribution, gender, and other factors. We used automatic classification of gender based on the first names of the first and last authors [1], with possible combinations including male/male, male/female, female/male, and female/female. Excluding self-citations to the first and last authors of our current paper, the references contain `A`% male/male, `B`% male/female, `C`% female/male, `D`% female/female, and `E`% unknown categorization. We look forward to future work that could help us to better understand how to support equitable practices in science.

# Instructions

## Binder

1. Launch the Binder environment. Please refresh the page if the Binder does not load after 5-10 mins.

    [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/dalejn/cleanBib/master)

2. Open the notebook `cleanBib.ipynb`. Follow the instructions above each code block and run them one by one.

    NOTE: if your author lists are not complete (e.g. your bibliography entry truncates the author list with 'et al.' or 'and Others', then you will need to manually edit the bibliography entry to include all author names). Also note that co-first or co-senior authors will not be accounted for by the code.

# FAQ

* Why do I receive an error when running the code?.
  * The most common errors are due to misformatted .bib files. Errors will usually provide an indication of the line or type of problem in the .bib file. If you cannot resolve an error, please open an `issue` and attach the error pasted into a `.txt` or a screenshot of the error. We will try to help resolve it.
* Will this method work on non-Western names?
  * Yes, the [Gender API supports 177 countries](https://gender-api.com/en/frequently-asked-questions?gclid=Cj0KCQiAmZDxBRDIARIsABnkbYTy9MHmGoR2uBhxEKANbT9B9EFVOSiRzbGeQi7nUn6ODH83s6-RZKwaAjpZEALw_wcB#which-countries-are-supported). 
* Are self-citations included?
  * We do not include self-citations by default. We define self-citations as those including your first or last author as a co-author.
* What if a reference has only 1 author?
  * We count that author as both the first and last author.
* What about gender-neutral names?
  * We exclude names that cannot be classified with >70% confidence. These are reported in the `Diversity Statement` as "unknown." 
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
* Erin Teich
* Dale Zhou

# Changelog

2/14/2020 - streamlined instructions, added repository photo for social media, move instructions into Jupyter notebook, added code to automatically remove unused .bib entries instead of needing user to manually remove them, made removing self-citations default, added FAQ, added screenshots to instructions, added error message to request users remove entries with duplicate IDs, throw error if entries are incomplete or blank, handle optional middle initial correctly for self-citations, added SOS notebook support to put all code and instructions into 1 notebook so users don't have to manually change kernel. 

1/19/2020 - added code to output a column with article titles to make it easier to manually search which bib entries need manual editing. Also added code to output another column that optionally checks for self-citations.