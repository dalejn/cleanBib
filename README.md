# Instructions

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

7. Open getReferenceGends.ipynb. On line 14, define the genderAPI_key with your [free gender-api account](https://gender-api.com/). Once registered and logged in, [find your 18-character API key at the bottom of this page](https://gender-api.com/en/account/overview#my-api-key)

