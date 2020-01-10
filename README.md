# Instructions

## .bib file
Check that your .bib file only contains references that you have used in your text. If you are using LaTeX, use the checkcites function: https://github.com/cereda/checkcites

If you are not using LaTeX, export your bibliography in .bib format using your reference manager of choice (Mendeley, Zotero, EndNote, etc.)

## Binder
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/dalejn/cleanBib/master)
Start the Binder environment.

Upload your bib file to the Jupyter notebook environment (Upload button top-right). NOTE: after selecting which file to upload, you will need to press the new Upload button that has appeared in the directory interface.

Open cleanBib.ipynb (will open in a new tab/window) and run the code. NOTE: co-first or co-senior authors will not be accounted for by the code.

Go to the previous tab showing the Jupyter notebook directory files. Check the output called cleanedBib.csv. If there are missing cells under First Author (FA) or Last Author (LA), then check that your .bib file has names for those entries (common causes for blank cells are 'et al.' or 'and Others'). Formatting errors may also be caused by non-standard characters--those names should be  manually inputted. Remove the current version of the .bib file and upload the corrected version. Run the code in cleanBib.ipynb again until satisfied with the output. 

Save the output cleanedBib.csv and manually modify as needed.