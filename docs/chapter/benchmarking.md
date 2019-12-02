### Benchmarking NBoost

NBoost comes with out-of-the-box 📦 functionality to benchmark the speed and accuracy of NBoost. If you tell NBoost which documents should be returned by a query, it will calculate how much better (or worse) the model is at ranking search results than the search api.

This is made possible by sending the correct document ids with either the `?nboost=` query parameter (comma delimited) or `"nboost"` key in the query json body (as an array). 

#### Index the background corpus

For demonstration, we will be indexing the [TREC CAR dataset](http://trec-car.cs.unh.edu/). Download the necessary `paragraphs.tsv` from [this link](https://storage.googleapis.com/koursaros/trec-car/paragraphs.tsv) and extract it. 

Use the `nboost-index` utility to send the data to your Elasticsearch:

```shell script
nboost-index --file paragraphs.tsv --name trec_car --host <Elasticsearch host>
```
> ☕ The corpus is composed of 30 million paragraphs, so go grab a coffee while it finishes indexing...

#### Start the Proxy

Start the NBoost proxy using one of the main methods:

1. `nboost --uport 9200`
2. `docker run koursaros/nboost:latest-tf --uport 9200`
3. `helm install --name nboost --set uport=9200 nboost/nboost`

#### Benchmark on the test set

Download the `queries.tsv` from [this link](https://storage.googleapis.com/koursaros/trec-car/queries.tsv). This tsv has queries matched with relevant paragraph ids (comma delimited). Let's send the queries with the matched paragraph ids to Elasticsearch with the `?nboost=` parameter:

```python
import requests, csv

with open('queries.tsv') as file:
    for query, cids in csv.reader(file, delimiter='\t'):
        params = dict(q='passage:' + query, nboost=cids)
        requests.post('http://localhost:8000/trec_car', params=params)
```

That's it! This just sends `http://localhost:8000/trec_car?nboost=id1,id2,id3...&q=passage:query` for every query.

Now check out the frontend at [localhost:8000/nboost](http://localhost:8000/nboost)!

You should find the model latency and calculated MRR for Elasticsearch vs NBoost. Here's our output:

(frontend picture)

Even though this model was finetuned on [a different dataset](http://www.msmarco.org/), it was generalizable enough to increase Elasticsearch search relevancy by **70%**!  
