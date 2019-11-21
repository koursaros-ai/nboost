python3 setup.py sdist
twine upload dist/* -r pypi
rm -rf dist nboost.egg-info
python3 docker.py
