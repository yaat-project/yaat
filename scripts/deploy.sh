python setup.py sdist
twine upload dist/* --username $PYPI_USER --password $PYPI_SECRET
