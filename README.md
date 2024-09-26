Source repository for the paper:

"Automatic Bicycle Balance Assistance Reduces Probability of Falling at Low
Speeds When Subjected to Handlebar Perturbations" by Marten T. Haitjema, Leila
Alizadehsaravi, Jason K. Moore

View the latest PDF versions here:

https://github.com/mechmotum/fall-probability-paper/blob/gh-pages/main.pdf

# License

The paper content (text, figures, etc.) and the generated paper itself are
licensed under the Creative Commons BY-4.0 license. The computer source code is
licensed under the MIT license. The data is available as public domain with no
copyright restrictions. If you make use of the copyrighted material use a full
citation to the paper to acknowledge the use and list the relevant license(s).

# Author Guide

- Avoid committing binary objects (like pngs). The preference is to generate
  them with a reproducible script.
- Use booktabs for the table formatting
- Use BibLatex with the natbib option and apa settings for variations on
  citations.
- subcaption is available for subfigures
- Use siunitx for units (note the `\kph` custom definition)

## Generating the bib file

There is a shared Zotero collection that is used to generate the bib file using
the Zotero betterbibtex extension. Export the collection with the "Better
BibLaTex" option to get a valid bib file and overwrite the `references.bib`
file with the export to update the bib file.

Link to the collection (need to be in the mechmotum group):

https://www.zotero.org/groups/966974/mechmotum/collections/44NW2M7I

## Build Instructions

Install LaTeX, conda, and make, then:

```
conda env create -f fall-prob-paper-env.yml
conda activate fall-prob-paper
make
```

A Github workflow builds the PDF on each commit to master using this action:
https://github.com/marketplace/actions/github-action-for-latex.
