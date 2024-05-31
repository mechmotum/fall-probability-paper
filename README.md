- Don't commit binary objects (like pngs) yet, maybe we can set this up to
  build everything.
- Use booktabs for the table formatting
- Use natbib for variations on citations
- subcaption is available for subfigures
- Use siunitx for units (note the kph custom definition)
- Jason has a zotero folder with the references and auto generates the bib
  file from it. Don't edit the bib file manually (until possibly the very end
  of writing).

Uses this action to build the PDF: https://github.com/marketplace/actions/github-action-for-latex

View the latest PDF:

https://github.com/mechmotum/fall-probability-paper/blob/gh-pages/main.pdf

# Generating the bib file

Install Zotero and betterbibtex. Using this collection:

https://www.zotero.org/groups/966974/mechmotum/collections/44NW2M7I

export the bib file with betterbitex.

# Build Instructions

Install LaTeX, conda, and make, then:

```
conda env create -f fall-prob-paper-env.yml
conda activate fall-prob-paper
make figures
make
```
