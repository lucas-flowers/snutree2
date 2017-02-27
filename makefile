
py-clean:
	find . -name '*.pyc'       -exec rm --force --recursive {} +
	find . -name '__pycache__' -exec rm --force --recursive {} +

build-clean:
	rm --force --recursive build/
	rm --force --recursive dist/

clean: py-clean build-clean

test: py-clean
	nosetests --verbose --exclude=private

priv-test: py-clean
	nosetests --verbose

snutree: build-clean py-clean
	pyinstaller __main__.spec

