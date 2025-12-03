FIRST_DIFF_TAG = v3

main.pdf: main.tex references.bib fixlme4 figures/balance-assist-eig-vs-speeds.png figures/torque_angle_perturbation_10.png figures/predicted_fall_probability_6kmh.png
	pdflatex main.tex
	bibtex main
	pdflatex main.tex
	pdflatex main.tex
fixlme4: references.bib
	sed -i 's/Lme4/{lme4}/g' references.bib
iatss:
	mkdir -p iatss/
	cp figures/*.png iatss/
	cp figures/*.jpg iatss/
	cp main.tex iatss/
	sed -i '/^\\author/d' iatss/main.tex
	sed -i 's/^\\section\*{Affli.*//g' iatss/main.tex
	sed -i '/^Department of/d' iatss/main.tex
	sed -i '/^Delft Univers.*/d' iatss/main.tex
	sed -i '/^Delft, The Neth.*/d' iatss/main.tex
	sed -i '/^Correspondenc.*/d' iatss/main.tex
	cp references.bib iatss/references.bib
	sed -i 's/_/\\_/g' iatss/references.bib
	sed -i 's/figures\///g' iatss/main.tex
iatssfirstpage: main.pdf
	pdftk main.pdf cat 1 output main-first-page.pdf
figures/balance-assist-eig-vs-speeds.png: src/control.py
	python src/control.py
figures/torque_angle_perturbation_10.png: src/generate_time_series_imgs.py
	python src/generate_time_series_imgs.py
figures/predicted_fall_probability_6kmh.png: src/statistics.R
	Rscript src/statistics.R
trackchanges:
	git checkout $(FIRST_DIFF_TAG)
	cp main.tex $(FIRST_DIFF_TAG).tex
	sed -i '/^\\author/d' $(FIRST_DIFF_TAG).tex
	sed -i 's/^\\section\*{Affli.*//g' $(FIRST_DIFF_TAG).tex
	sed -i '/^Department of/d' $(FIRST_DIFF_TAG).tex
	sed -i '/^Delft Univers.*/d' $(FIRST_DIFF_TAG).tex
	sed -i '/^Delft, The Neth.*/d' $(FIRST_DIFF_TAG).tex
	sed -i '/^Correspondenc.*/d' $(FIRST_DIFF_TAG).tex
	git checkout master
	sed -i '/^\\author/d' main.tex
	sed -i '/^Department of/d' main.tex
	sed -i '/^Delft Univers.*/d' main.tex
	sed -i '/^Delft, The Neth.*/d' main.tex
	sed -i '/^Correspondenc.*/d' main.tex
	latexdiff $(FIRST_DIFF_TAG).tex main.tex > diff-master_$(FIRST_DIFF_TAG).tex
	rm $(FIRST_DIFF_TAG).tex
	git checkout -- main.tex
	pdflatex -interaction nonstopmode diff-master_$(FIRST_DIFF_TAG).tex
	bibtex diff-master_$(FIRST_DIFF_TAG).aux
	pdflatex -interaction nonstopmode diff-master_$(FIRST_DIFF_TAG).tex
	pdflatex -interaction nonstopmode diff-master_$(FIRST_DIFF_TAG).tex
html: main.tex references.bib
	pandoc -o index.html -s --mathjax="https://cdn.jsdelivr.net/npm/mathjax@4/tex-mml-chtml.js" --bibliography=references.bib --citeproc main.tex
clearpdf:
	rm paper.pdf
clean:
	(rm -rf *.bcf *.fdb_latexmk *synctex.gz *.run.xml *.fls *.ps *.log *.dvi *.aux *.*% *.lof *.lop *.lot *.toc *.idx *.ilg *.ind *.bbl *.blg *.cpt *.out)
	rm figures/balance-assist-eig-vs-speeds.png
	rm figures/bicycle-with-geometry-mass.png
	rm figures/gains-vs-speed.png
	rm figures/pd-simulation.png
	rm figures/predicted_fall_probability_6kmh.png
	rm figures/predicted_fall_probability_10kmh.png
	rm figures/torque_angle*.png
	rm -rf iatss/
	rm -f index.html
	rm -f diff-master_$(FIRST_DIFF_TAG).*
