
TEST = pytest
SETUP = python setup.py

ifeq ($(OS),Windows_NT)
	CC = pyinstaller.exe
	SET_SNUTREE_GUI = set SNUTREE_GUI=1 &&
else
	CC = pyinstaller
	SET_SNUTREE_GUI = SNUTREE_GUI=1
endif

snutree: cli gui

cli:
	$(CC) snutree.spec

gui:
	$(SET_SNUTREE_GUI) $(CC) snutree.spec

dist: clean
	$(SETUP) bdist_wheel
	$(SETUP) sdist

upload-test:
	twine upload -r testpypi dist/*

upload:
	twine upload -r pypi dist/*

readme:
	python docs/readme-generate.py

test-clean: py-clean
	find . -name '*-actual.dot' -exec rm {} +

py-clean:
	find . -name '*.pyc'       -exec rm --force --recursive {} +
	find . -name '__pycache__' -exec rm --force --recursive {} +

build-clean:
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info/

clean: py-clean test-clean build-clean

test:
	$(TEST)

