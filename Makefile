DOCUMENT_NAME = dokumentation
OUTPUT_DIR    = output
ABGABE_DIR    = ../abgabe/


####latexmk

# Build the LaTeX document with latexmk
all: report

# Remove output directory and generated document
clean:
	rm -rf $(OUTPUT_DIR)
	rm -f $(DOCUMENT_NAME).pdf
	rm -f $(DOCUMENT_NAME).synctex.gz

# cleanup tempfiles
cleanup:
	latexmk -c

# Generate PDF output from LaTeX input files
report:
	latexmk


####direct without latexmk

# Build the LaTeX document.
all-legacy: outputdir-legacy report-legacy
#cleanup-legacy

# cleanup tempfiles
cleanup-legacy:
	rm -f $(OUTPUT_DIR)/$(DOCUMENT_NAME).aux $(OUTPUT_DIR)/$(DOCUMENT_NAME).acn $(OUTPUT_DIR)/$(DOCUMENT_NAME).glo $(OUTPUT_DIR)/$(DOCUMENT_NAME).ist $(OUTPUT_DIR)/$(DOCUMENT_NAME).lof $(OUTPUT_DIR)/$(DOCUMENT_NAME).lot $(OUTPUT_DIR)/$(DOCUMENT_NAME).lol $(OUTPUT_DIR)/$(DOCUMENT_NAME).out $(OUTPUT_DIR)/$(DOCUMENT_NAME).toc $(OUTPUT_DIR)/$(DOCUMENT_NAME).alg $(OUTPUT_DIR)/$(DOCUMENT_NAME).glg $(OUTPUT_DIR)/$(DOCUMENT_NAME).gls $(OUTPUT_DIR)/$(DOCUMENT_NAME).acr $(OUTPUT_DIR)/$(DOCUMENT_NAME).blg $(OUTPUT_DIR)/$(DOCUMENT_NAME).bbl $(OUTPUT_DIR)/$(DOCUMENT_NAME).bcf $(OUTPUT_DIR)/$(DOCUMENT_NAME).run.xml

# Remove output directory and generated document
clean-legacy:
	clean

# Create LaTeX output directory.
outputdir-legacy:
	$(shell mkdir $(OUTPUT_DIR) 2>/dev/null)

# Generate PDF output from LaTeX input files.
report-legacy: 
	pdflatex --shell-escape -interaction=errorstopmode -output-directory=$(OUTPUT_DIR) $(DOCUMENT_NAME)
	biber --output-directory $(OUTPUT_DIR) $(DOCUMENT_NAME)
	makeglossaries -d $(OUTPUT_DIR) -q $(DOCUMENT_NAME)
	pdflatex --shell-escape -interaction=errorstopmode -output-directory=$(OUTPUT_DIR) $(DOCUMENT_NAME)
	pdflatex --shell-escape -interaction=errorstopmode -output-directory=$(OUTPUT_DIR) $(DOCUMENT_NAME)
	cp $(OUTPUT_DIR)/$(DOCUMENT_NAME).pdf $(DOCUMENT_NAME).pdf 

# Generate implementation section from jupyter notebook
implementation:
	git submodule init
	git submodule update --recursive --remote
	ipython nbconvert --to markdown othello-studienarbeit-code/othello_game.ipynb --output ../content/implementation/gamelogic.md
	ipython nbconvert --to markdown othello-studienarbeit-code/othello_ai.ipynb --output ../content/implementation/ai.md
	pandoc content/implementation/gamelogic.md -t latex -o content/implementation/gamelogic.tex --listings
	pandoc content/implementation/ai.md -t latex -o content/implementation/ai.tex --listings

