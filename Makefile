default:
	echo "Hello"

q:
	bin/celery3 -A sheetsite.queue worker  -l info

sdist:
	rm -rf dist
	cp README.md README
	python3 setup.py sdist
	cd dist && mkdir tmp && cd tmp && tar xzvf ../sheet*.tar.gz && cd sheet*[0-9] && ./setup.py build
	python3 setup.py sdist upload
	rm -rf dist
	rm README MANIFEST

