"""Default nboost-indexer command line arguments"""

from pathlib import Path

verbose = False
file = Path('.')
index_name = 'nboost'
host = '0.0.0.0'
port = 9200
delim = '\t'
shards = 5
indexer = 'ESIndexer'
id_col = False
