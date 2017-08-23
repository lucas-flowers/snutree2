
CC = pyinstaller
TEST = pytest

snutree: clean
	$(CC) snutree.spec

snutree-onefile: clean
	$(CC) --onefile snutree.spec

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

