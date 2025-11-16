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
	cp references-iatss-bibtex.bib iatss/references.bib
	sed -i 's/doi = {\(.*\)},/note = {doi:~{\1}},/g' iatss/references.bib
	sed -i 's/_/\\_/g' iatss/references.bib
	sed -i 's/figures\///g' iatss/main.tex
	sed -i 's/citep/cite/g' iatss/main.tex
	sed -i 's/citet/cite/g' iatss/main.tex
	sed -i 's/Citet/cite/g' iatss/main.tex
	sed -i 's/\\printbibliography/\\bibliographystyle{unsrt}\n\\bibliography{references}/g' iatss/main.tex
	sed -i '/biblatex/d' iatss/main.tex
	sed -i '/addbibresource/d' iatss/main.tex
figures/balance-assist-eig-vs-speeds.png: src/control.py
	python src/control.py
figures/torque_angle_perturbation_10.png: src/generate_time_series_imgs.py
	python src/generate_time_series_imgs.py
figures/predicted_fall_probability_6kmh.png: src/statistics.R
	Rscript src/statistics.R
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
