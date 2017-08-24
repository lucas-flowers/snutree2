
CC = pyinstaller
TEST = pytest
SETUP = python setup.py

snutree: clean
	$(CC) snutree.spec

snutree-onefile: clean
	$(CC) --onefile snutree.spec

dist: clean
	$(SETUP) bdist_wheel
	$(SETUP) sdist

upload-test:
	twine upload -r testpypi dist/*

upload:
	twine upload -r pypi dist/*

readme:
	python readme.py

test-clean:
	find . -name '*-actual.dot' -exec rm {} +

py-clean:
	find . -name '*.pyc'       -exec rm --force --recursive {} +
	find . -name '__pycache__' -exec rm --force --recursive {} +

build-clean:
	rm --force --recursive build/
	rm --force --recursive dist/

clean: py-clean test-clean build-clean

test: py-clean
	$(TEST)

