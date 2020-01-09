### Setting up NBoost for Elasticsearch

In this example we will set up a proxy to sit in between the client and Elasticsearch and boost the results!

#### Preliminaries

1. Install NBoost for Pytorch.
    ```bash
    pip install nboost[pt]
    ```
2. Set up an Elasticsearch Server
    > 🔔 If you already have an Elasticsearch server, you can skip this step!

    If you don't have Elasticsearch, not to worry! You can set up a local Elasticsearch cluster by using docker. First, get the ES image by running:
    ```bash
    docker pull elasticsearch:7.4.2
    ```
    Once you have the image, you can run an Elasticsearch server via:
    ```bash
    docker run -d -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" elasticsearch:7.4.2
    ```

3. Index some data

    NBoost has a handy indexing tool built in (`nboost-index`). For demonstration purposes,  will be indexing [a set of passages about traveling and hotels](https://microsoft.github.io/TREC-2019-Deep-Learning/). You can add the index to your Elasticsearch server by running:
    >  `travel.csv` comes with NBoost
    ```bash
    nboost-index --file travel.csv --name travel --delim ,
    ```` 

#### Deploying the proxy
Now we're ready to deploy our Neural Proxy! There are three ways to configure NBoost.
1. Via command line.
    
    On the command line, we can run:
    ```bash
    nboost                              \
        --uhost localhost               \
        --uport 9200                    \
        --search_path /.*/_search       \
        --query_path url.query.q        \
        --topk_path url.query.size      \
        --default_topk 10               \
        --topn 50                       \
        --choices_path body.hits.hits   \
        --cvalues_path _source.passage
    ```
    > 📢 The `--uhost` and `--uport` should be the same as the Elasticsearch server above! Uhost and uport are short for upstream-host and upstream-port (referring to the upstream server).

    Now let's test it out! Hit the Elasticsearch with:
    ```bash
    curl "http://localhost:8000/travel/_search?pretty&q=passage:vegas&size=2"
    ```
    
2. Via json.

    On the command line, let's run:
    ```bash
   nboost --search_path /.*/_search
   ```
   
   In a python script, we can run:
    ```python
    import requests
    
    requests.get(
       url='http://localhost:8000/travel/_search',
       json={
           'nboost': {
               'uhost': 'localhost',
               'uport': 9200,
               'query_path': 'body.query.match.passage',
               'topk_path': 'body.size',
               'default_topk': 10,
               'topn': 50,
               'choices_path': 'body.hits.hits',
               'cvalues_path': '_source.passage'
           },
           'query': {
               'match': {'passage': 'I want a vegas hotel with a pool'},
               'size': 2
           }
       }
   )
   ```
3. Via query params.
    On the command line, let's run:
    ```bash
   nboost --search_path /.*/_search
   ```
   
      In a python script, we can run:
    ```python
   import requests
    
   requests.get(
       url='http://localhost:8000/travel/_search',
       params={
           'uhost': 'localhost',
           'uport': 9200,
           'query_path': 'url.query.q',
           'topk_path': 'url.query.size',
           'default_topk': 10,
           'topn': 50,
           'choices_path': 'body.hits.hits',
           'cvalues_path': '_source.passage',
           'q': 'passage:I want a vegas hotel with a pool',
           'size': 2
       }
   )
   ```

No matter how we configure NBoost, if the Elasticsearch result has the `nboost` tag in it, congratulations it's working!
    
<p align="center">
<img src="https://github.com/koursaros-ai/nboost/raw/master/.github/travel-tutorial.svg?sanitize=true" alt="success installation of NBoost">
</p>


#### What just happened?
Let's check out the **NBoost frontend**. Go to your browser and visit [localhost:8000/nboost](http://localhost:8000/nboost).
> If you don't have access to a browser, you can `curl http://localhost:8000/nboost/status` for the same information.

<p align="center">
<img src="https://github.com/koursaros-ai/nboost/raw/master/.github/frontend-tutorial.png">
</p>

The frontend recorded everything that happened:

1. NBoost got a request for **2 search results**.
2. NBoost sent a request for **50 search results** to the server.
3. The model picked the best 2 search results. *(300 ms)*
4. NBoost returned the search results to the client.
