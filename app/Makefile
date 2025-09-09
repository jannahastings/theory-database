.PHONY: clean wordclouds diagrams statistics

all: wordclouds statistics diagrams

clean:
	rm -rf static/*.png

venv: venv/touchfile

venv/touchfile: requirements.txt
	test -d venv || virtualenv venv
	. venv/bin/activate; python3 -m pip install -Ur requirements.txt
	touch venv/touchfile

wordclouds:
	python GenerateWordCloud.py

statistics:
	python GenerateTheoryStatistics.py

diagrams:
	python GenerateTheoryDiagram.py