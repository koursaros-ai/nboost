### Setting up a Neural Proxy for Elasticsearch in 3 minutes

In this example we will set up a proxy to sit in between the client and Elasticsearch and boost the results!

#### Installing NBoost with tensorflow

If you want to run the example on a GPU, make sure you have Tensorflow 1.14-1.15 (with CUDA) to support the modeling functionality. However, if you want to just run it on a CPU, don't worry about it. For both cases, just run:

```bash
pip install nboost[tf]
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
Now we're ready to deploy our Neural Proxy! It is very simple to do this, simply run:
```bash
nboost --uport 9200
```
> 📢 The `--uhost` and `--uport` should be the same as the Elasticsearch server above! Uhost and uport are short for upstream-host and upstream-port (referring to the upstream server).

If you get this message: `Listening: <host>:<port>`, then we're good to go!

#### Indexing some data
NBoost has a handy indexing tool built in (`nboost-index`). For demonstration purposes,  will be indexing [a set of passages about traveling and hotels](https://microsoft.github.io/TREC-2019-Deep-Learning/) through NBoost. You can add the index to your Elasticsearch server by running:
>  `travel.csv` comes with NBoost
```bash
nboost-index --file travel.csv --name travel --delim ,
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
<img src="https://github.com/koursaros-ai/nboost/raw/master/.github/frontend-tutorial.png">
</p>

The frontend recorded everything that happened:

1. NBoost got a request for **2 search results**. *(0.32 ms)*
2. NBoost connected to the server. *(0.13 ms)*
3. NBoost sent a request for 10 search results to the server. *(0.12 ms)* 
4. NBoost received **10 search results** from the server. *(120.33 ms)*
5. The model picked the best 2 search results. *(300 ms)*
6. NBoost returned the search results to the client. *(0.10 ms)* 

#### Elastic made easy
To increase the number of parallel proxies, simply increase `--workers`. For a more robust deployment approach, you can distribute the proxy via Kubernetes (see below).

<h2 align="center">Kubernetes</h2>

<p align="center">
<img src="https://github.com/koursaros-ai/nboost/raw/master/.github/sailboat.svg?sanitize=true" width="100%">
</p>

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

| Parameter                                    | Description                                      | Default                                                 |
| -------------------------------------------- | ------------------------------------------------ | ------------------------------------------------------- |
| `replicaCount`                               | Number of replicas to deploy                     | `3`                                                     |
| `image.repository`                           | NBoost Image name                                | `koursaros/nboost`                                      |
| `image.tag`                                  | NBoost Image tag                                 | `latest-tf`                                             |
| `args.model_dir`                             | Name or directory of the finetuned model         | `bert-base-uncased-msmarco`                             |
| `args.model`                                 | Model Class                                      | `BertModel`                                             |
| `args.host`                                  | Hostname of the proxy                            | `0.0.0.0`                                               |
| `args.port`                                  | Port for the proxy to listen on                  | `8000`                                                  |
| `args.uhost`                                 | Hostname of the upstream search api server       | `elasticsearch-master`                                  |
| `args.uport`                                 | Port of the upstream server                      | `9200`                                                  |
| `args.data_dir`                              | Directory to cache model binary                  | `nil`                                                   |
| `args.max_seq_len`                           | Max combined token length                        | `64`                                                    |
| `args.bufsize`                               | Size of the http buffer in bytes                 | `2048`                                                  |
| `args.batch_size`                            | Batch size for running through rerank model      | `4`                                                     |
| `args.multiplier`                            | Factor to increase results by                    | `5`                                                     |
| `args.workers`                               | Number of threads serving the proxy              | `10`                                                    |
| `args.codex`                                 | Codex Class                                      | `ESCodex`                                               |
| `service.type`                               | Kubernetes Service type                          | `LoadBalancer`                                          |
| `resources`                                  | resource needs and limits to apply to the pod    | `{}`                                                    |
| `nodeSelector`                               | Node labels for pod assignment                   | `{}`                                                    |
| `affinity`                                   | Affinity settings for pod assignment             | `{}`                                                    |
| `tolerations`                                | Toleration labels for pod assignment             | `[]`                                                    |
| `image.pullPolicy`                           | Image pull policy                                | `IfNotPresent`                                          |
| `imagePullSecrets`                           | Docker registry secret names as an array         | `[]` (does not add image pull secrets to deployed pods) |
| `nameOverride`                               | String to override Chart.name                    | `nil`                                                   |
| `fullnameOverride`                           | String to override Chart.fullname                | `nil`                                                   |
| `serviceAccount.create`                      | Specifies whether a service account is created   | `nil`                                                   |
| `serviceAccount.name`                        | The name of the service account to use. If not set and create is true, a name is generated using the fullname template   | `nil`  |
| `serviceAccount.create`                      | Specifies whether a service account is created   | `nil`                                                   |
| `podSecurityContext.fsGroup`                 | Group ID for the container                       | `nil`                                                   |
| `securityContext.runAsUser`                  | User ID for the container                        | `1001`                                                  |
| `ingress.enabled`                            | Enable ingress resource                          | `false`                                                 |
| `ingress.hostName`                           | Hostname to your installation                    | `nil`                                                   |
| `ingress.path`                               | Path within the url structure                    | `[]`                                                    |
| `ingress.tls`                                | enable ingress with tls                          | `[]`                                                    |
| `ingress.tls.secretName`                     | tls type secret to be used                       | `chart-example-tls`                                     |

