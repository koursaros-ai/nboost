from requests.exceptions import ConnectionError
import subprocess
import requests
import time

BUILD = '''
docker pull elasticsearch:7.4.2
docker run -d -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" elasticsearch:7.4.2
'''

INDEX = '''
curl -X PUT "{host}:{port}/shakespeare?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
    "speaker": {"type": "keyword"},
    "play_name": {"type": "keyword"},
    "line_id": {"type": "integer"},
    "speech_number": {"type": "integer"}
    }
  }
}
'
curl -O https://download.elastic.co/demos/kibana/gettingstarted/7.x/shakespeare.json
curl -H 'Content-Type: application/x-ndjson' -XPOST '{host}:{port}/shakespeare/_bulk?pretty' --data-binary @shakespeare.json
curl -X GET "{host}:{port}/_cat/indices?v&pretty"
rm shakespeare.json
'''


def ensure_shakespeare_elasticsearch(host: str = 'localhost', port: int = 9200):
    """Makes sure there is a shakespeare index on the given ES host"""

    try:
        res = requests.get('http://%s:%s/shakespeare/_count' % (host, port))
        # if index does not exist, it will default raise exception
        if res.json().get('count', 0) < 10 ** 5:
            raise RuntimeError
    except ConnectionError:
        if host in ('localhost', '127.0.0.1', '::1'):
            subprocess.call(BUILD, shell=True)
            print('Waiting for ES')
            time.sleep(15)
        else:
            raise ConnectionError('Please set up ES at %s:%s' % (host, port))
    except RuntimeError:
        subprocess.call(INDEX.format(host=host, port=port), shell=True)

    print('ES build success')