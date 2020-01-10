### Setting up NBoost for the Bing Search API

The Bing Search API offers a handy REST service that we can use to get preliminary results before we rerank with NBoost, or for usage with question answering. We will walk through an example of how to set up a Bing-Powered QA system.

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
        --topn 20                           \
        --search_path /bing/v7.0/search     \
        --query_path url.query.q            \
        --topk_path url.query.count         \
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
    from pprint import pprint
    
    response = requests.get(
        url='http://localhost:8000/bing/v7.0/search',
        headers={'Ocp-Apim-Subscription-Key': '<BING API KEY>'},
        params={'q': 'how old is obama', 'responseFilter': 'Webpages'},
        json={
            'nboost': {
                'uhost': 'api.cognitive.microsoft.com',
                'uport': 443,
                'ussl': True,
                'topn': 20,
                'query_path': 'url.query.q',
                'topk_path': 'url.query.count',
                'default_topk': 10,
                'choices_path': 'body.webPages.value',
                'cvalues_path': 'snippet'
            }
        }
    )
    
    pprint(response.json())
   ```
   
3. Via query params.

    On the command line, let's run:
    ```bash
   nboost --search_path /bing/v7.0/search --qa True --qa_model PtDistilBertQAModel
   ```

   In a python script, we can run:
    ```python
    import requests
    from pprint import pprint
    
    response = requests.get(
       url='http://localhost:8000/bing/v7.0/search',
       headers={'Ocp-Apim-Subscription-Key': '<BING API KEY>'},
       params={
           'q': 'how old is obama',
           'responseFilter': 'Webpages',
           'uhost': 'api.cognitive.microsoft.com',
           'uport': 443,
           'ussl': True,
           'topn': 20,
           'query_path': 'url.query.q',
           'topk_path': 'url.query.count',
           'default_topk': 10,
           'choices_path': 'body.webPages.value',
           'cvalues_path': 'snippet'
       }
   )
   
   pprint(response.json())
   ```
   
No matter how we query, the json response will look like this:

```json
{"_type": "SearchResponse",
 "nboost": {"answer_start_pos": 145,
            "answer_stop_pos": 157,
            "answer_text": "Born in 1961"},
 "queryContext": {"originalQuery": "how old is obama"},
 "webPages": {"totalEstimatedMatches": 81800000,
              "value": [{"about": [{"name": "Barack Obama"}],
                         "dateLastCrawled": "2020-01-06T13:40:00.0000000Z",
                         "displayUrl": "https://www.myagecalculator.com/how-old-is-barack-obama",
                         "id": "https://api.cognitive.microsoft.com/api/v7/#WebPages.9",
                         "isFamilyFriendly": true,
                         "isNavigational": false,
                         "language": "en",
                         "name": "How old is Barack Obama? - MyAgeCalculator",
                         "snippet": "Barack Obama is a prominent American "
                                    "politician, a Democrat and the 44th "
                                    "President of the United States who served "
                                    "two terms, from 2009 to 2017. Born in "
                                    "1961 in Hawaii, Obama spent some parts of "
                                    "his childhood in the continental US and "
                                    "in Indonesia.",
                         "url": "https://www.myagecalculator.com/how-old-is-barack-obama"},
                        {"about": [{"name": "Family of Barack Obama"}],
    ...

```
   
The `nboost` key signifies that the webpages were reranked. NBoost returns the `answer_text`, and the offsets from the QA Model in the `answer_start_pos` and  `answer_stop_pos` keys.