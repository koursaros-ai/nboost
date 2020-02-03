
"""Default command line arguments."""

from nboost.helpers import ListOrCommaDelimitedString
from nboost import PKG_PATH

host = '0.0.0.0'
port = 8000
uhost = '0.0.0.0'
uport = 9200
ussl = False
backlog = 100
verbose = False
query_delim = '. '
lr = 10e-3
max_seq_len = 64
bufsize = 2048
batch_size = 4
topn = 50
workers = 10
data_dir = PKG_PATH.joinpath('.cache')
no_rerank = False
model = ''
model_dir = 'pt-tinybert-msmarco'
qa = False
qa_model = ''
qa_model_dir = 'distilbert-base-uncased-distilled-squad'
qa_threshold = 0
max_query_length = 64
filter_results = False
query_prep = 'lambda query: query'
debug = False
db_file = data_dir.joinpath('nboost.db')
rerank_cids = ListOrCommaDelimitedString()
prerank = False

# by default, nboost is configured for elasticsearch
search_route = '/<index>/_search'
frontend_route = '/nboost'
status_route = '/status'
query_path = '(body.query.match) | (body.query.term.*) | (url.query.q)'
topk_path = '(body.size) | (url.query.size)'
default_topk = 10
choices_path = 'body.hits.hits'
cvalues_path = '_source.*'
cids_path = '_id'

