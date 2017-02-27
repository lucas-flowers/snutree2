
py-clean:
	find . -name '*.pyc'       -exec rm --force --recursive {} +
	find . -name '__pycache__' -exec rm --force --recursive {} +

build-clean:
	rm --force --recursive build/
	rm --force --recursive dist/

clean-all: py-clean build-clean

test: py-clean
	nosetests --verbose

pub-test: py-clean
	nosetests --verbose --exclude=private

compile: build-clean py-clean
	pyinstaller __main__.spec


