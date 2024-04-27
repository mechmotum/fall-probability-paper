main.pdf: main.tex references.bib figures/*.png
	pdflatex main.tex
	bibtex main.aux
	pdflatex main.tex
	pdflatex main.tex
figures: src/*.py
	python src/control.py
clearpdf:
	rm paper.pdf
clean:
	(rm -rf *.ps *.log *.dvi *.aux *.*% *.lof *.lop *.lot *.toc *.idx *.ilg *.ind *.bbl *.blg *.cpt *.out)
	rm figures/*.png
