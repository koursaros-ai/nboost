from requests.exceptions import ConnectionError
from paths import RESOURCES
import subprocess
import requests
import time

BUILD = '''
docker pull elasticsearch:7.4.2
docker run -d -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" elasticsearch:7.4.2
'''


def ensure_shakespeare_elasticsearch():
    path = RESOURCES.joinpath('es/build-es-shakespeare.sh').absolute()

    try:
        res = requests.get('http://localhost:9200/shakespeare/_count')
        if res.json()['count'] < 10 ** 5:
            raise RuntimeError
    except ConnectionError:
        subprocess.call(BUILD, shell=True)
        print('Waiting for ES')
        time.sleep(15)
    except RuntimeError:
        subprocess.call(['sh', str(path)])

    print('ES build success')