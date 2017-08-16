
CC = pyinstaller
TEST = pytest

snutree: clean
	$(CC) snutree.spec

snutree-onefile: clean
	$(CC) --onefile snutree.spec

py-clean:
	find . -name '*.pyc'       -exec rm --force --recursive {} +
	find . -name '__pycache__' -exec rm --force --recursive {} +

build-clean:
	rm --force --recursive build/
	rm --force --recursive dist/

clean: py-clean build-clean

test: py-clean
	$(TEST) -k 'not private'

priv-test: py-clean
	$(TEST)

