### Setting up NBoost for the Bing Search API

The Bing Search API offers a handy REST service that we can use to get prelimanry results before we rerank with NBoost, or for usage with question answering. We will walk through an example of how to set up a Bing-Powered QA system.

1. Get your [Bing API key](https://azure.microsoft.com/en-us/try/cognitive-services/my-apis/?api=bing-web-search-api).
2. Spin up NBoost and configure it for the Bing API:

     ```bash
        nboost                                  \
            --port 8000                         \
            --uhost api.cognitive.microsoft.com \
            --multiplier 10                     \
            --search_path /bing/v7.0/search     \
            --query_path url.query.q            \
            --topk_path count                   \
            --default_topk 10                   \
            --choices_path body.webPages.value  \
            --cvalues_path snippet              \
            --qa True                           \
            --qa_model PtDistilBertQAModel      
     ```
3. Query NBoost as you would [normally query the Bing API](https://dev.cognitive.microsoft.com/docs/services/f40197291cd14401b93a478716e818bf/operations/56b4447dcf5ff8098cef380d) (replace the API key).
    
   ```bash
   curl -H "Ocp-Apim-Subscription-Key: <BING API KEY>" localhost:8000/bing/v7.0/search?q=how+old+is+obama&count=1&responseFilter=Webpages
   ```
   
   The result will look like this:
   
   ```json

    ```
   
   The `nboost` key signifies that the webpages were reranked. NBoost returns the offsets from the QA Model in the `answerStartPos` and  `answerStopPos` keys.