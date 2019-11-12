<p align="center">
<img src="https://github.com/koursaros-ai/nboost/raw/master/.github/banner.png?raw=true" alt="Nboost">
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
  <a href="#highlights">Highlights</a> •
  <a href="#overview">Overview</a> •
  <a href="#install-nboost">Install</a> •
  <a href="#getting-started">Getting Started</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#tutorial">Tutorial</a> •
  <a href="#contributing">Contributing</a> •
  <a href="./CHANGELOG.md">Release Notes</a> •
  <a href="https://koursaros-ai.github.io/Live-Fact-Checking-Algorithms-in-the-Era-of-Fake-News/">Blog</a>  
</p>

<h2 align="center">What is it</h2>

⚡**NBoost** is a scalable, search-api-boosting proxy for developing and deploying SOTA models to improve the relevance of search results.
 
Nboost leverages finetuned models to produce domain-specific neural search engines. The platform can also improve other downstream tasks requiring ranked input, such as question answering.

<h2 align="center">Overview</h2>
**This project is currently undergoing rapid release cycles and the core package is not ready for distribution**


<h2 align="center">Install NBoost</h2>

There are two ways to get NBoost, either as a Docker image or as a PyPi package. **For cloud users, we highly recommend using NBoost via Docker**. 
> 🚸 Tensorflow, and Pytorch are not part of the "barebone" NBoost installation. Depending on your model, you may have to install them in advance.

For installing NBoost, follow the table below.

Dependency      | 🐳 Docker                             | 📦 pypi
--------------- | ------------------------------------- | --------------------------
**None**        | `koursaros/nboost:latest-alpine`      | `pip install nboost`
**Pytorch**     | `koursaros/nboost:latest-torch`       | `pip install nboost[torch]`      
**Tensorflow**  | `koursaros/nboost:latest-tf`          | `pip install nboost[tf]`
**All**         | `koursaros/nboost:latest-all`         | `pip install nboost[all]` 


Any way you install it, if you end up reading the following message after `$ nboost --help` or `$ docker run koursaros/nboost --help`, then you are ready to go!

<p align="center">
<img src="https://github.com/koursaros-ai/nboost/raw/master/.github/cli-help.svg?sanitize=true" alt="success installation of NBoost">
</p>


<h2 align="center">Getting Started</h2>

- [Preliminaries](#-preliminaries)
  * [📡The Proxy](#microservice)
- [Setting up a Neural Proxy for Elasticsearch in 3 minutes](#Setting-up-a-Neural-Proxy-for-Elasticsearch-in-1-minute)
- [Elastic made easy](#elastic-made-easy)
- [Deploying a distributed proxy via Docker Swarm/Kubernetes](#deploying-a-flow-via-docker-swarmkubernetes)
- [‍Take-home messages](#-take-home-messages)


### Preliminaries

Before we start, let me first introduce the most important concept, the **Proxy**.

#### 📡The Proxy

The proxy object is the core of NBoost. It has four components: the **model**, **server**, **db**, and **codex**. The only role of the proxy is to manage these four components.

- [**Model**](http://nboost.readthedocs.io/en/latest/chapter/component.html#model): ranking search results before sending to the client, and training on feedback;
- [**Server**](http://nboost.readthedocs.io/en/latest/chapter/component.html#server): receiving incoming client requests and passing them to the other components;
- [**Db**](http://nboost.readthedocs.io/en/latest/chapter/component.html#db): storing past searches in order to learn from client feedback, also logging/benchmarking;
- [**Codex**](http://nboost.readthedocs.io/en/latest/chapter/component.html#codex): translating incoming messages from specific search apis (i.e. Elasticsearch);


### Setting up a Neural Proxy for Elasticsearch in 3 minutes

In this example we will set up a proxy to sit in between the client and Elasticsearch and boost the results!

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

#### Indexing some data
For demonstration purposes, we will be indexing [a set of passages about open-source software](https://microsoft.github.io/TREC-2019-Deep-Learning/). You can add the index to your Elasticsearch server by running:
```bash
nboost-tutorial opensource --es_host localhost --es_port 9200
```` 
> 📢 If your server is not on your local machine, change the `--host` and `--port` switches accordingly.

#### Deploying the proxy
Now we're ready to deploy our Neural Proxy! It is very simple to do this, simply run:
```bash
nboost --ext_host localhost --ext_port 9200
```
> The `--ext_host` and `--ext_port` should be the same as the Elasticsearch server above!

If you get this message: `LISTENING: <host>:<port>`, then we're good to go.

Now let's test it out! Hit the proxy with:
```bash
curl "http://localhost:8000/opensource/_search?q=passage:what%20is%20mozilla%20firefox&pretty&size=2"
```

If the Elasticsearch result has the `_nboost` tag in it, congratulations it's working!
<p align="center">
<img src="https://github.com/koursaros-ai/nboost/raw/master/.github/cli-help.svg?sanitize=true" alt="success installation of NBoost">
</p>

### Elastic made easy
To increase the number of parallel proxies, simply increase `--workers`:
> 🚧 Under construction.

### Deploying a proxy via Docker Swarm/Kubernetes
> 🚧 Under construction.


### Take-home messages

Let's make a short recap of what we have learned. 

- NBoost is *result-boosting-proxy*, there are four fundamental components: model, server, db and codex.
- One can increase the number of concurrent proxies with `--workers` or by deploying more containers.
- NBoost can be deployed using an orchestration engine to coordinate load-balancing. It supports Kubernetes, Docker Swarm,  or built-in multi-process/thread solution. 


<h2 align="center">Documentation</h2>

[![ReadTheDoc](https://readthedocs.org/projects/nboost/badge/?version=latest&style=for-the-badge)](https://nboost.readthedocs.io)

The official NBoost documentation is hosted on [nboost.readthedocs.io](http://nboost.readthedocs.io/). It is automatically built, updated and archived on every new release.

<h2 align="center">Tutorial</h2>

> 🚧 Under construction.

<h2 align="center">Benchmark</h2>

We have setup `/benchmarks` to track the network/model latency over different NBoost versions.


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