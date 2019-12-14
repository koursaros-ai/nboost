### Data Structures

There are three main data structures in NBoost, and they are all dictionaries: the request, response, and config.

#### Request
```json
{
  "method": "(str) the http method",
  "version": "(str) the http version",
  "headers": "(dict) the dictionary of http headers",
  "url":  { 
    "scheme": "(str) URL scheme specifier",
    "netloc": "(str) network location part",
    "path": "(str) hierarchical path",
    "params": "(str) parameters for last path element",
    "query": "(dict) query parameters",
    "fragment": "(str) fragment identifier"
  },
  "body": {
    "nboost": "(dict) Configures NBoost at runtime. The same as the config.",
    "...other keys": "(dict) the rest of the body to send to the upstream server (e.g. Elasticsearch)"
  }
}
```

The url is in the form of `scheme://netloc/path;parameters?query#fragment`, but is decomposed into a dictionary, as noted above.

#### Response
```json
{
  "status": "(int) the status code of the response message",
  "headers": "(dict) the dictionary of http headers",
  "body": {
    "nboost": "(dict) NBoost specific metadata, plugin data, etc..."
  }
}
```

#### Config

```json
{
  "delim": "(str) the deliminator to concatenate multiple queries into a single query",
  "query_path": "(str) the jsonpath in the request to find the query",
  "topk_path": "(str) the jsonpath to find the number of requested results",
  "choices_path":  "(str) the jsonpath to find the array of choices to reorder",
  "cvalues_path": "(str) the jsonpath to find the string values of the choices",
  "cids_path": "(str) the jsonpath to find the ids of the choices (for benchmarking)",
  "capture_path": "(str) the route to capture for reranking search results",
  "default_topk": "(int) the default number of results to return if the topk_path is not found"
}
```

Depending on value of the `key` switch that you use when you run NBoost on the cli, it will use a configuration in the CONFIG_MAP.

For example, the default Elasticsearch configuration is:
```json
{
    "query_path": "(body.query.match) | (body.query.term.*) | ($.url.query.q)",
    "topk_path": "(body.size) | (url.query.size)",
    "cvalues_path": "$.body.hits.hits[*]._source.*",
    "true_cids_path": "$.body.nboost.cids",
    "cids_path": "$.body.hits.hits[*]._id",
    "choices_path": "$.body.hits.hits",
    "capture_path": "/.*/_search",
    "default_topk": 10
  }
```
