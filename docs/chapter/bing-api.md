### Setting up NBoost for the Bing Search API

The Bing Search API offers a handy REST service that we can use to get prelimanry results before we rerank with NBoost, or for usage with question answering. We will walk through an example of how to set up a Bing-Powered QA system.

#### Preliminaries
1. Get your [Bing API key](https://azure.microsoft.com/en-us/try/cognitive-services/my-apis/?api=bing-web-search-api).
2. Check out the [Bing DSL docs](https://dev.cognitive.microsoft.com/docs/services/f40197291cd14401b93a478716e818bf/operations/56b4447dcf5ff8098cef380d) for background on how to normally use the API.

#### Deploying the Proxy
Just like the Elasticsearch tutorial, we will go through the three ways to configure NBoost.
1. Via Command Line:

     On the command line, let's run:
    ```bash
    nboost                                  \
        --uhost api.cognitive.microsoft.com \
        --uport 443                         \
        --ussl True                         \
        --topn 50                           \
        --search_path /bing/v7.0/search     \
        --query_path url.query.q            \
        --topk_path count                   \
        --default_topk 10                   \
        --choices_path body.webPages.value  \
        --cvalues_path snippet              \
        --qa True                           \
        --qa_model PtDistilBertQAModel      
    ```
    Then we can query NBoost.
    
    ```bash
    curl -H "Ocp-Apim-Subscription-Key: <BING API KEY>" localhost:8000/bing/v7.0/search?q=how+old+is+obama&count=1&responseFilter=Webpages
    ```
   
2. Via json.

    On the command line, let's run:
    ```bash
   nboost --search_path /bing/v7.0/search --qa True --qa_model PtDistilBertQAModel
   ```
   
   In a python script, we can run:
    ```python
    import requests
    
    requests.get(
       url='http://localhost:8000/travel/_search',
       params={'q': 'how old is obama'},
       json={
           'nboost': {
               'uhost': 'api.cognitive.microsoft.com',
               'uport': 443,
               'topn': 50,
               'query_path': 'url.query.q',
               'topk_path': 'count',
               'default_topk': 10,
               'choices_path': 'body.webPages.value',
               'cvalues_path': 'snippet'
           }
       }
   )
   ```
   
3. Via query params.

    On the command line, let's run:
    ```bash
   nboost --search_path /bing/v7.0/search --qa True --qa_model PtDistilBertQAModel
   ```

   In a python script, we can run:
    ```python
    import requests
    
    requests.get(
       url='http://localhost:8000/travel/_search',
       params={
           'q': 'how old is obama',
           'uhost': 'api.cognitive.microsoft.com',
           'uport': 443,
           'topn': 50,
           'query_path': 'url.query.q',
           'topk_path': 'count',
           'default_topk': 10,
           'choices_path': 'body.webPages.value',
           'cvalues_path': 'snippet'
       }
   )
   
No matter how we query, the json response will look like this:

```json

```
   
The `nboost` key signifies that the webpages were reranked. NBoost returns the `answer_text`, and the offsets from the QA Model in the `answer_start_pos` and  `answer_stop_pos` keys.