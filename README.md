# Instructions

## Diversity statement

Recent work in neuroscience and other fields has identified a bias in citation practices such that papers from women and other minorities are under-cited relative to the number of such papers in the field [1, 2, 3, 4, 5, 6]. Here we sought to proactively consider choosing references that reflect the diversity of the field in thought, form of contribution, gender, and other factors. We used automatic classification of gender based on the first names of the first and last authors [1], with possible combinations including male/male, male/female, female/male, female/female. Excluding self-citations to the senior authors of our current paper, the references contain X% male/male, Y % male/female, Z% female/male, A% female/female, and B% unknown categorization. We look forward to future work that could help us to better understand how to support equitable practices in science.

See [Dworkin, Linn, Teich, Zurn, Shinohara, Bassett (2020). bioRxiv. doi: https://doi.org/10.1101/2020.01.03.894378](https://www.biorxiv.org/content/10.1101/2020.01.03.894378v1.full.pdf)

For a template diversity statement .pdf and .tex, see the /diversityStatement directory.

## Calculating gender proportions in reference list

## .bib file
1. Check that your .bib file only contains references that you have used in your text. If you are using LaTeX, [use the checkcites function](https://github.com/cereda/checkcites)

If you are not using LaTeX, export your bibliography in .bib format using your reference manager of choice (Mendeley, Zotero, EndNote, etc.)

## Binder

2. Start the Binder environment.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/dalejn/cleanBib/master)

3. Upload your bib file to the Jupyter notebook environment (Upload button top-right). NOTE: after selecting which file to upload, you will need to press the new Upload button that has appeared in the directory interface.

4. Open cleanBib.ipynb (will open in a new tab/window) and run the code. NOTE: co-first or co-senior authors will not be accounted for by the code.

5. Go to the previous tab showing the Jupyter notebook directory files. Check the output called cleanedBib.csv. If there are missing cells under First Author (FA) or Last Author (LA), then check that your .bib file has names for those entries (common causes for blank cells are 'et al.' or 'and Others'). Formatting errors may also be caused by non-standard characters--those names should be  manually inputted. Remove the current version of the .bib file and upload the corrected version. Run the code in cleanBib.ipynb again until satisfied with the output. 

6. Save the output cleanedBib.csv and manually modify as needed. Re-upload modified cleanedBib.csv if needed.

7. Open getReferenceGends.ipynb. In the new window's menu bar, click on Kernel > Change kernel > R

8. On line 14, define the genderAPI_key with your [free gender-api account](https://gender-api.com/). Once registered and logged in, [find your 18-character API key at the bottom of this page](https://gender-api.com/en/account/overview#my-api-key)

9. Run code. The output will provide a frequency count for male-male, male-female, female-male, and female-female. Your reference proportions will be displayed next to expected proportions in the field of neuroscience. Proportion difference relative to expected proportions will be printed.

# References

.bib file containing these references can be found in /diversityStatement/bibfile.bib

[1] J. D. Dworkin, K. A. Linn, E. G. Teich, P. Zurn, R. T. Shinohara, and D. S. Bassett, “The extent and drivers of gender imbalance in neuroscience reference lists,” bioRxiv, 2020.
[2] D. Maliniak, R. Powers, and B. F. Walter, “The gender citation gap in international relations,” International Organization, vol. 67, no. 4, pp. 889– 922, 2013.
[3] N. Caplar, S. Tacchella, and S. Birrer, “Quantitative evaluation of gender bias in astronomical publications from citation counts,” Nature Astronomy, vol. 1, no. 6, p. 0141, 2017.
[4] P. Chakravartty, R. Kuo, V. Grubbs, and C. McIlwain, “# communicationsowhite,” Journal of Communication, vol. 68, no. 2, pp. 254–266, 2018.
[5] Y. Thiem, K. F. Sealey, A. E. Ferrer, A. M. Trott, and R. Kennison, “Just Ideas? The Status and Future of Publication Ethics in Philosophy: A White Paper,” tech. rep., 2018.
[6] M. L. Dion, J. L. Sumner, and S. M. Mitchell, “Gendered citation patterns across political science and social science methodology fields,” Political Analysis, vol. 26, no. 3, pp. 312–327, 2018.