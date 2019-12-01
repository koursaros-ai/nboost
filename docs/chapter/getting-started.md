### Setting up a Neural Proxy for Elasticsearch in 3 minutes

In this example we will set up a proxy to sit in between the client and Elasticsearch and boost the results!

#### Installing NBoost with tensorflow

If you want to run the example on a GPU, make sure you have Tensorflow 1.14-1.15 (with CUDA) to support the modeling functionality. However, if you want to just run it on a CPU, don't worry about it. For both cases, just run:

```bash
pip install nboost[tf]
```


#### Setting up an Elasticsearch Server
> 🔔 If you already have an Elasticsearch server, you can move on to the next step!

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
The proxy is set up so that there is no need to ever talk to the server directly from here on out. You can send index requests, stats requests, but only the search requests will be altered. For demonstration purposes, we will be indexing [a set of passages about traveling and hotels](https://microsoft.github.io/TREC-2019-Deep-Learning/) through NBoost. You can add the index to your Elasticsearch server by running:
```bash
nboost-tutorial Travel --port 8000 --field passage
```` 

Now let's test it out! Hit the Elasticsearch with:
```bash
curl "http://localhost:8000/travel/_search?pretty&q=passage:vegas&size=2"
```

If the Elasticsearch result has the `_nboost` tag in it, congratulations it's working!

What just happened? You asked for two results from Elasticsearch having to do with "vegas". The proxy intercepted this request, asked the Elasticsearch for 10 results, and the model picked the best two. Magic! 🔮 (statistics)

<p align="center">
<img src="https://github.com/koursaros-ai/nboost/raw/master/.github/travel-tutorial.svg?sanitize=true" alt="success installation of NBoost">
</p>

#### Elastic made easy
To increase the number of parallel proxies, simply increase `--workers`. For a more robust deployment approach, you can distribute the proxy [via Docker Swarm or Kubernetes](#Deploying-a-proxy-via-Docker-Swarm/Kubernetes).

### Deploying a proxy via Docker Swarm/Kubernetes
> 🚧 Swarm yaml/Helm chart under construction...