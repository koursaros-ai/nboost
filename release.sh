python3 setup.py sdist
twine upload dist/* -r pypi
rm -rf dist nboost.egg-info
echo "Waiting for pypi package to update"
sleep 15
python3 docker.py
