main.pdf: main.tex references.bib figures/balance-assist-eig-vs-speeds.png figures/torque_angle_perturbation_10.png figures/predicted_fall_probability_6kmh.png
	pdflatex main.tex
	biber main
	pdflatex main.tex
	pdflatex main.tex
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
