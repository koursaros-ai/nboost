> 🧪 We're looking for beta testers for our <a href='https://answerbot.app'>virtual assistant</a> widget. <a href = 'mailto:jp954@cornell.edu'>Contact us</a> if you're interested in using it on your website.

<p align="center">
<img src="https://github.com/koursaros-ai/nboost/raw/master/.github/banner.svg?sanitize=true" alt="Nboost" width="70%">
</p>

<p align="center">
<a href="https://cloud.drone.io/koursaros-ai/nboost">
    <img src="https://cloud.drone.io/api/badges/koursaros-ai/nboost/status.svg" />
</a>
<a href="https://pypi.org/project/nboost/">
    <img src="https://img.shields.io/pypi/pyversions/nboost.svg" />
</a>
<a href="https://pypi.org/project/nboost/">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/nboost.svg">
</a>
<a href='https://nboost.readthedocs.io/en/latest/'>
    <img src='https://readthedocs.org/projects/nboost/badge/?version=latest' alt='Documentation Status' />
</a>
<a href="https://www.codacy.com/app/koursaros-ai/nboost?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=koursaros-ai/nboost&amp;utm_campaign=Badge_Grade">
    <img src="https://api.codacy.com/project/badge/Grade/a9ce545b9f3846ba954bcd449e090984"/>
</a>
<a href="https://codecov.io/gh/koursaros-ai/neural_rerank">
  <img src="https://codecov.io/gh/koursaros-ai/neural_rerank/branch/master/graph/badge.svg" />
</a>
<a href='https://github.com/koursaros-ai/nboost/blob/master/LICENSE'>
    <img alt="PyPI - License" src="https://img.shields.io/pypi/l/nboost.svg">
</a>
</p>

<p align="center">
  <a href="#what-is-it">Highlights</a> •
  <a href="#overview">Overview</a> •
  <a href="#benchmarks">Benchmarks</a> •
  <a href="#install-nboost">Install</a> •
  <a href="#getting-started">Getting Started</a> •
  <a href="#kubernetes">Kubernetes</a> •
  <a href="https://nboost.readthedocs.io/">Documentation</a> •
  <a href="#tutorials">Tutorials</a> •
  <a href="#contributing">Contributing</a> •
  <a href="./CHANGELOG.md">Release Notes</a> •
  <a href="https://koursaros-ai.github.io/">Blog</a>  
</p>

<h2 align="center">What is it</h2>

⚡**NBoost** is a scalable, search-engine-boosting platform for developing and deploying state-of-the-art models to improve the relevance of search results.

<p align="center">
<img src="https://github.com/koursaros-ai/nboost/raw/master/.github/overview.svg?sanitize=true" width="100%">
</p>

Nboost leverages finetuned models to produce domain-specific neural search engines. The platform can also improve other downstream tasks requiring ranked input, such as question answering.

<a href = 'mailto:jp954@cornell.edu'>Contact us to request domain-specific models or leave feedback</a>

<h2 align="center">Overview</h2>

The workflow of NBoost is relatively simple. Take the graphic above, and imagine that the server in this case is Elasticsearch.

<p align="center">
<img src="https://github.com/koursaros-ai/nboost/raw/master/.github/conventional.svg?sanitize=true" width="80%">
</p>

In a **conventional search request**, the user sends a query to *Elasticsearch* and gets back the results.

<p align="center">
<img src="https://github.com/koursaros-ai/nboost/raw/master/.github/nboost.svg?sanitize=true" width="80%">
</p>

In an **NBoost search request**, the user sends a query to the *model*. Then, the model asks for results from *Elasticsearch* and picks the best ones to return to the user.

<h2 align="center">Benchmarks</h2>

> 🔬 Note that we are evaluating models on differently constructed sets than they were trained on (MS Marco vs TREC-CAR), suggesting the generalizability of these models to many other real world search problems.

<center>

Fine-tuned Models                                                                   | Dependency                                                                   | Eval Set                                                           | Search Boost<a href='#benchmarks'><sup>[1]</sup></a>  | Speed
----------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------ | ----------------------------------------------------- | ----------------------------------
`pt-tinybert-msmarco` (**default**)                                                 | <img alt="PyTorch" src="https://img.shields.io/badge/PyTorch-red"/>          |  <a href ='http://www.msmarco.org/'>bing queries</a>               | **+45%** <sub><sup>(0.26 vs 0.18)</sup></sub>         | ~50ms/query <a href='#footnotes'>
`pt-bert-base-uncased-msmarco`                                                      | <img alt="PyTorch" src="https://img.shields.io/badge/PyTorch-red"/>          | <a href ='http://www.msmarco.org/'>bing queries</a>                | **+62%** <sub><sup>(0.29 vs 0.18)</sup></sub>         | ~300 ms/query<a href='#footnotes'>
`tf-bert-base-uncased-msmarco`<a href='#benchmarks'><sup>[2]</sup></a>              | <img alt="TensorFlow" src="https://img.shields.io/badge/TensorFlow-orange"/> | <a href ='http://www.msmarco.org/'>bing queries</a>                | **+62%** <sub><sup>(0.29 vs 0.18)</sup></sub>         | ~300 ms/query<a href='#footnotes'>
`tf-bert-base-uncased-msmarco`                                                      | <img alt="TensorFlow" src="https://img.shields.io/badge/TensorFlow-orange"/> | <a href ='http://trec-car.cs.unh.edu/'>wiki search</a>             | **+60%** <sub><sup>(0.28 vs 0.18)</sup></sub>         | ~300 ms/query<a href='#footnotes'>
`biobert-base-uncased-msmarco`                                                      | <img alt="TensorFlow" src="https://img.shields.io/badge/TensorFlow-orange"/> | <a href ='https://github.com/naver/biobert-pretrained'>biomed</a>  | **+66%** <sub><sup>(0.17 vs 0.10)</sup></sub>         | ~300 ms/query<a href='#footnotes'>


</center>

**Instructions for reproducing <a href = 'https://nboost.readthedocs.io/en/latest/chapter/benchmarking.html'>here</a>.**

<sub>[1] <a href = 'https://en.wikipedia.org/wiki/Mean_reciprocal_rank'>MRR </a> compared to BM25, the default for Elasticsearch. Reranking top 50.</sub>
<br>
<sub>[2] https://github.com/nyu-dl/dl4marco-bert</sub>

To use one of these fine-tuned models with nboost, run `nboost --model_dir bert-base-uncased-msmarco` for example, and it will download and cache automatically.

Using pre-trained language understanding models, you can boost search relevance metrics by nearly **2x** compared to just text search, with little to no extra configuration. While assessing performance, there is often a tradeoff between model accuracy and speed, so we benchmark both of these factors above. This leaderboard is a work in progress, and we intend on releasing more cutting edge models!

<h2 align="center">Install NBoost</h2>

There are two ways to get NBoost, either as a Docker image or as a PyPi package. **For cloud users, we highly recommend using NBoost via Docker**. 
> 🚸 Depending on your model, you should install the respective Tensorflow or Pytorch dependencies. We package them below.

For installing NBoost, follow the table below.
<center>

Dependency                      | 🐳 Docker                                                 | 📦 Pypi                                           |  <a href="#kubernetes">🐙 Kubernetes</a>
------------------------------- | --------------------------------------------------------- | ------------------------------------------------- | -------------
**Pytorch** (*recommended*)     | <sub><sup>`koursaros/nboost:latest-pt`</sup></sub>        | <sub><sup>`pip install nboost[pt]`</sup></sub>    | <sub><sup>`helm install nboost/nboost --set image.tag=latest-pt`</sup></sub>
**Tensorflow**                  | <sub><sup>`koursaros/nboost:latest-tf`</sup></sub>        | <sub><sup>`pip install nboost[tf]`</sup></sub>    | <sub><sup>`helm install nboost/nboost --set image.tag=latest-tf`</sup></sub>
**All**                         | <sub><sup>`koursaros/nboost:latest-all`</sup></sub>       | <sub><sup>`pip install nboost[all]`</sup></sub>   | <sub><sup>`helm install nboost/nboost --set image.tag=latest-all`</sup></sub>
**-** (*for testing*)           | <sub><sup>`koursaros/nboost:latest-alpine`</sup></sub>    | <sub><sup>`pip install nboost`</sup></sub>        | <sub><sup>`helm install nboost/nboost --set image.tag=latest-alpine`</sup></sub>

</center>

Any way you install it, if you end up reading the following message after `$ nboost --help` or `$ docker run koursaros/nboost --help`, then you are ready to go!

<p align="center">
<img src="https://github.com/koursaros-ai/nboost/raw/master/.github/cli-help.svg?sanitize=true" alt="success installation of NBoost">
</p>


<h2 align="center">Getting Started</h2>

- [The Proxy](#the-proxy)
- [Setting up a Neural Proxy for Elasticsearch in 3 minutes](#Setting-up-a-Neural-Proxy-for-Elasticsearch-in-3-minutes)
  * [Setting up an Elasticsearch Server](#setting-up-an-elasticsearch-server)
  * [Deploying the proxy](#deploying-the-proxy)
  * [Indexing some data](#indexing-some-data)
- [Elastic made easy](#elastic-made-easy)


### 📡The Proxy

<center>
<table>
  <tr>
  <td width="33%">
      <img src="https://github.com/koursaros-ai/nboost/raw/master/.github/rocket.svg?sanitize=true" alt="component overview">
      </td>
  <td>
  <p>The <a href="https://nboost.readthedocs.io/en/latest/api/nboost.proxy.html">Proxy</a> is the core of NBoost. The proxy is essentially a wrapper to enable serving the model. It is able to understand incoming messages from specific search apis (i.e. Elasticsearch). When the proxy receives a message, it increases the amount of results the client is asking for so that the model can rerank a larger set and return the (hopefully) better results.</p>
  <p>For instance, if a client asks for 10 results to do with the query "brown dogs" from Elasticsearch, then the proxy may increase the results request to 100 and filter down the best ten results for the client.</p>
</td>
  </tr>
</table>
</center>

#### 



### Setting up a Neural Proxy for Elasticsearch in 3 minutes

In this example we will set up a proxy to sit in between the client and Elasticsearch and boost the results!

#### Installing NBoost with tensorflow

If you want to run the example on a GPU, make sure you have Tensorflow 1.14-1.15 (with CUDA) to support the modeling functionality. However, if you want to just run it on a CPU, don't worry about it. For both cases, just run:

```bash
pip install nboost[pt]
```


#### Setting up an Elasticsearch Server
> 🔔 If you already have an Elasticsearch server, you can skip this step!

If you don't have Elasticsearch, not to worry! You can set up a local Elasticsearch cluster by using docker. First, get the ES image by running:
```bash
docker pull elasticsearch:7.4.2
```
Once you have the image, you can run an Elasticsearch server via:
```bash
docker run -d -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" elasticsearch:7.4.2
```

#### Deploying the proxy
Now we're ready to deploy our Neural Proxy! It is very simple to do this, run:
```bash
nboost                              \
    --uhost localhost               \
    --uport 9200                    \
    --search_path /.*/_search       \
    --query_path url.query.q        \
    --topk_path url.query.size      \
    --default_topk 10               \
    --choices_path body.hits.hits   \
    --cvalues_path _source.passage
```
> 📢 The `--uhost` and `--uport` should be the same as the Elasticsearch server above! Uhost and uport are short for upstream-host and upstream-port (referring to the upstream server).

If you get this message: `Listening: <host>:<port>`, then we're good to go!

#### Indexing some data
NBoost has a handy indexing tool built in (`nboost-index`). For demonstration purposes,  will be indexing [a set of passages about traveling and hotels](https://microsoft.github.io/TREC-2019-Deep-Learning/) through NBoost. You can add the index to your Elasticsearch server by running:
>  `travel.csv` comes with NBoost
```bash
nboost-index --file travel.csv --index_name travel --delim , --id_col
```` 


Now let's test it out! Hit the Elasticsearch with:
```bash
curl "http://localhost:8000/travel/_search?pretty&q=passage:vegas&size=2"
```

If the Elasticsearch result has the `_nboost` tag in it, congratulations it's working!

<p align="center">
<img src="https://github.com/koursaros-ai/nboost/raw/master/.github/travel-tutorial.svg?sanitize=true" alt="success installation of NBoost">
</p>

#### What just happened?
Let's check out the **NBoost frontend**. Go to your browser and visit [localhost:8000/nboost](http://localhost:8000/nboost).
> If you don't have access to a browser, you can `curl http://localhost:8000/nboost/status` for the same information.

<p align="center">
<img src="https://github.com/koursaros-ai/nboost/raw/master/.github/frontend-example.png">
</p>

The frontend recorded everything that happened:

1. NBoost got a request for **2 search results**. *(average_topk)*
2. NBoost connected to the server at `localhost:9200`.
3. NBoost sent a request for 50 search results to the server. *(topn)* 
4. NBoost received **50 search results** from the server. *(average_choices)*
5. The model picked the best 2 search results and returned them to the client.

#### Elastic made easy
To increase the number of parallel proxies, simply increase `--workers`. For a more robust deployment approach, you can distribute the proxy via Kubernetes (see below).

<h2 align="center">Kubernetes</h2>

<p align="center">
<img src="https://github.com/koursaros-ai/nboost/raw/master/.github/sailboat.svg?sanitize=true" width="100%">
</p>

#### See also
For in-depth query DSL and other search API solutions (such as the Bing API), see the [docs](https://nboost.readthedocs.io/en/latest/chapter/bing-api.html).

### Deploying NBoost via Kubernetes
We can easily deploy NBoost in a Kubernetes cluster using [Helm](https://helm.sh/).

#### Add the NBoost Helm Repo
First we need to register the repo with your Kubernetes cluster.
```bash
helm repo add nboost https://raw.githubusercontent.com/koursaros-ai/nboost/master/charts/
helm repo update
```

#### Deploy some NBoost replicas
Let's try deploying four replicas:
```bash
helm install --name nboost --set replicaCount=4 nboost/nboost
```

All possible `--set` ([values.yaml](https://github.com/koursaros-ai/nboost/blob/master/charts/nboost/values.yaml)) options are listed below:

| Parameter                                    | Description                                      | Default                                                     |
| -------------------------------------------- | ------------------------------------------------ | ----------------------------------------------------------- |
| `replicaCount`                               | Number of replicas to deploy                     | `3`                                                         |
| `image.repository`                           | NBoost Image name                                | `koursaros/nboost`                                          |
| `image.tag`                                  | NBoost Image tag                                 | `latest-pt`                                                 |
| `args.model`                                 | Name of the model class                          | `nil`                                                       |
| `args.model_dir`                             | Name or directory of the finetuned model         | `pt-bert-base-uncased-msmarco`                              |
| `args.qa`                                    | Whether to use the qa plugin                     | `False`                                                     |
| `args.qa_model_dir`                          | Name or directory of the qa model                | `distilbert-base-uncased-distilled-squad`                   |
| `args.model`                                 | Name of the model class                          | `nil`                                                       |
| `args.host`                                  | Hostname of the proxy                            | `0.0.0.0`                                                   |
| `args.port`                                  | Port for the proxy to listen on                  | `8000`                                                      |
| `args.uhost`                                 | Hostname of the upstream search api server       | `elasticsearch-master`                                      |
| `args.uport`                                 | Port of the upstream server                      | `9200`                                                      |
| `args.data_dir`                              | Directory to cache model binary                  | `nil`                                                       |
| `args.max_seq_len`                           | Max combined token length                        | `64`                                                        |
| `args.bufsize`                               | Size of the http buffer in bytes                 | `2048`                                                      |
| `args.batch_size`                            | Batch size for running through rerank model      | `4`                                                         |
| `args.multiplier`                            | Factor to increase results by                    | `5`                                                         |
| `args.workers`                               | Number of threads serving the proxy              | `10`                                                        |
| `args.query_path`                            | Jsonpath in the request to find the query        | `nil`                                                       |
| `args.topk_path`                             | Jsonpath to find the number of requested results | `nil`                                                       |
| `args.choices_path`                          | Jsonpath to find the array of choices to reorder | `nil`                                                       |
| `args.cvalues_path`                          | Jsonpath to find the str values of the choices   | `nil`                                                       |
| `args.cids_path`                             | Jsonpath to find the ids of the choices          | `nil`                                                       |
| `args.search_path`                           | The url path to tag for reranking via nboost     | `nil`                                                       |
| `service.type`                               | Kubernetes Service type                          | `LoadBalancer`                                              |
| `resources`                                  | resource needs and limits to apply to the pod    | `{}`                                                        |
| `nodeSelector`                               | Node labels for pod assignment                   | `{}`                                                        |
| `affinity`                                   | Affinity settings for pod assignment             | `{}`                                                        |
| `tolerations`                                | Toleration labels for pod assignment             | `[]`                                                        |
| `image.pullPolicy`                           | Image pull policy                                | `IfNotPresent`                                              |
| `imagePullSecrets`                           | Docker registry secret names as an array         | `[]` (does not add image pull secrets to deployed pods)     |
| `nameOverride`                               | String to override Chart.name                    | `nil`                                                       |
| `fullnameOverride`                           | String to override Chart.fullname                | `nil`                                                       |
| `serviceAccount.create`                      | Specifies whether a service account is created   | `nil`                                                       |
| `serviceAccount.name`                        | The name of the service account to use. If not set and create is true, a name is generated using the fullname template   | `nil`  |
| `serviceAccount.create`                      | Specifies whether a service account is created   | `nil`                                                       |
| `podSecurityContext.fsGroup`                 | Group ID for the container                       | `nil`                                                       |
| `securityContext.runAsUser`                  | User ID for the container                        | `1001`                                                      |
| `ingress.enabled`                            | Enable ingress resource                          | `false`                                                     |
| `ingress.hostName`                           | Hostname to your installation                    | `nil`                                                       |
| `ingress.path`                               | Path within the url structure                    | `[]`                                                        |
| `ingress.tls`                                | enable ingress with tls                          | `[]`                                                        |
| `ingress.tls.secretName`                     | tls type secret to be used                       | `chart-example-tls`                                         |



<h2 align="center">Documentation</h2>

[![ReadTheDoc](https://readthedocs.org/projects/nboost/badge/?version=latest&style=for-the-badge)](https://nboost.readthedocs.io)

The official NBoost documentation is hosted on [nboost.readthedocs.io](http://nboost.readthedocs.io/). It is automatically built, updated and archived on every new release.

<h2 align="center">Contributing</h2>

Contributions are greatly appreciated! You can make corrections or updates and commit them to NBoost. Here are the steps:

1. Create a new branch, say `fix-nboost-typo-1`
2. Fix/improve the codebase
3. Commit the changes. Note the **commit message must follow [the naming style](./CONTRIBUTING.md#commit-message-naming)**, say `Fix/model-bert: improve the readability and move sections`
4. Make a pull request. Note the **pull request must follow [the naming style](./CONTRIBUTING.md#commit-message-naming)**. It can simply be one of your commit messages, just copy paste it, e.g. `Fix/model-bert: improve the readability and move sections`
5. Submit your pull request and wait for all checks passed (usually 10 minutes)
    - Coding style
    - Commit and PR styles check
    - All unit tests
6. Request reviews from one of the developers from our core team.
7. Merge!

More details can be found in the [contributor guidelines](./CONTRIBUTING.md).

<h2 align="center">Citing NBoost</h2>

If you use NBoost in an academic paper, we would love to be cited. Here are the two ways of citing NBoost:

1.     \footnote{https://github.com/koursaros-ai/nboost}
2. 
    ```latex
    @misc{koursaros2019NBoost,
      title={NBoost: Neural Boosting Search Results},
      author={Thienes, Cole and Pertschuk, Jack},
      howpublished={\url{https://github.com/koursaros-ai/nboost}},
      year={2019}
    }
    ```

<h2 align="center">License</h2>

If you have downloaded a copy of the NBoost binary or source code, please note that the NBoost binary and source code are both licensed under the [Apache License, Version 2.0](./LICENSE).

<sub>
Koursaros AI is excited to bring this open source software to the community.<br>
Copyright (C) 2019. All rights reserved.
</sub>
