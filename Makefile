.SUFFIXES: .py .yaml .md .xml
test:
	python -m unittest fgcz_maxquant_wrapper
clean:
	-rm -fv *.pyc
