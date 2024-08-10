main.pdf: main.tex references.bib figures/balance-assist-eig-vs-speeds.png
	pdflatex main.tex
	bibtex main.aux
	pdflatex main.tex
	pdflatex main.tex
figures/balance-assist-eig-vs-speeds.png: src/control.py src/generate_time_series_imgs.py
	python src/control.py
	python src/generate_time_series_imgs.py
clearpdf:
	rm paper.pdf
clean:
	(rm -rf *.ps *.log *.dvi *.aux *.*% *.lof *.lop *.lot *.toc *.idx *.ilg *.ind *.bbl *.blg *.cpt *.out)
	rm figures/balance-assist-controllers-eig-vs-speeds.png
	rm figures/bicycle-geometry-mass.png
	rm figures/gains-vs-speed.png
	rm figures/pd-simulation.png
	rm figures/perturbation*.png
	rm figures/uncontrolled-eig-vs-speeds.png
