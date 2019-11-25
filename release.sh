#!/usr/bin/env bash

python3 setup.py sdist
twine upload dist/* -r pypi
rm -rf dist nboost.egg-info
echo "Waiting for pypi package to update"

for i in $(seq 1 100); do
    printf "  $i%%\r"
    sleep 0.6
done

python3 docker.py
