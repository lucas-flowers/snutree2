
CC = pyinstaller
TEST = pytest
SETUP = python setup.py

snutree: cli gui

cli:
	$(CC) snutree.spec

gui:
	SNUTREE_GUI=1 $(CC) snutree.spec

dist: clean
	$(SETUP) bdist_wheel
	$(SETUP) sdist

upload-test:
	twine upload -r testpypi dist/*

upload:
	twine upload -r pypi dist/*

readme:
	python generate-readme.py

test-clean:
	find . -name '*-actual.dot' -exec rm {} +

py-clean:
	find . -name '*.pyc'       -exec rm --force --recursive {} +
	find . -name '__pycache__' -exec rm --force --recursive {} +

build-clean:
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info/

clean: py-clean test-clean build-clean

test: py-clean
	$(TEST)

