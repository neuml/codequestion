<p align="center">
    <img src="https://raw.githubusercontent.com/neuml/codequestion/master/logo.png"/>
</p>

<h3 align="center">
    <p>Ask coding questions directly from the terminal</p>
</h3>

<p align="center">
    <a href="https://github.com/neuml/codequestion/releases">
        <img src="https://img.shields.io/github/release/neuml/codequestion.svg?style=flat&color=success" alt="Version"/>
    </a>
    <a href="https://github.com/neuml/codequestion/releases">
        <img src="https://img.shields.io/github/release-date/neuml/codequestion.svg?style=flat&color=blue" alt="GitHub Release Date"/>
    </a>
    <a href="https://github.com/neuml/codequestion/issues">
        <img src="https://img.shields.io/github/issues/neuml/codequestion.svg?style=flat&color=success" alt="GitHub issues"/>
    </a>
    <a href="https://github.com/neuml/codequestion">
        <img src="https://img.shields.io/github/last-commit/neuml/codequestion.svg?style=flat&color=blue" alt="GitHub last commit"/>
    </a>
    <a href="https://github.com/neuml/codequestion/actions?query=workflow%3Abuild">
        <img src="https://github.com/neuml/codequestion/workflows/build/badge.svg" alt="Build Status"/>
    </a>
    <a href="https://coveralls.io/github/neuml/codequestion?branch=master">
        <img src="https://img.shields.io/coveralls/github/neuml/codequestion" alt="Coverage Status">
    </a>
</p>

-------------------------------------------------------------------------------------------------------------------------------------------------------

codequestion is a Python application that empowers users to ask coding questions directly from the terminal. Developers often have a web browser window open while they work and run web searches as questions arise. With codequestion, this can be done from a local context.

The default model for codequestion is built off the [Stack Exchange Dumps on archive.org](https://archive.org/details/stackexchange). With the default model, codequestion runs locally, no network connection is required. The model executes similarity queries to find similar questions to the input query.

An example of how codequestion works is shown below:

![demo](https://raw.githubusercontent.com/neuml/codequestion/master/demo.gif)

## Installation
The easiest way to install is via pip and PyPI

```
pip install codequestion
```

Python 3.7+ is supported. Using a Python [virtual environment](https://docs.python.org/3/library/venv.html) is recommended.

codequestion can also be installed directly from GitHub to access the latest, unreleased features.

```
pip install git+https://github.com/neuml/codequestion
```

See [this link](https://neuml.github.io/txtai/install/#environment-specific-prerequisites) to help resolve environment-specific install issues.

## Downloading a model

Once codequestion is installed, a model needs to be downloaded.

```
python -m codequestion.download
```

The model will be stored in ~/.codequestion/

The model can also be manually installed if the machine doesn't have direct internet access. The default model is pulled from the [GitHub release page](https://github.com/neuml/codequestion/releases)

```
unzip cqmodel.zip ~/.codequestion
```

## Running queries

The fastest way to run queries is to start a codequestion shell

```
codequestion
```

A prompt will come up. Queries can be typed directly into the console.

## Tech overview
The following is an overview covering how this project works.

### Processing the raw data dumps
The raw 7z XML dumps from Stack Exchange are processed through a series of steps (see [building a model](#building-a-model)). Only highly scored questions with accepted answers are retrieved for storage in the model. Questions and answers are consolidated into a single SQLite file called questions.db. The schema for questions.db is below.

*questions.db schema*

    Id INTEGER PRIMARY KEY
    Source TEXT
    SourceId INTEGER
    Date DATETIME
    Tags TEXT
    Question TEXT
    QuestionUser TEXT
    Answer TEXT
    AnswerUser TEXT
    Reference TEXT

### Indexing
codequestion builds a sentence embeddings index for questions.db. Each question in the questions.db schema is vectorized with a sentence-transformers model. Once questions.db is converted to a collection of sentence embeddings, the embeddings are normalized and stored in Faiss, which enables fast similarity searches.

### Querying
codequestion tokenizes each query using the same method as during indexing. Those tokens are used to build a sentence embedding. That embedding is queried against the Faiss index to find the most similar questions.

## Building a model
The following steps show how to build a codequestion model using Stack Exchange archives.

_This is not necessary if using the default model from the [GitHub release page](https://github.com/neuml/codequestion/releases)_

1.) Download files from Stack Exchange: https://archive.org/details/stackexchange

2.) Place selected files into a directory structure like shown below (current process requires all these files).

- stackexchange/ai/ai.stackexchange.com.7z
- stackexchange/android/android.stackexchange.com.7z
- stackexchange/apple/apple.stackexchange.com.7z
- stackexchange/arduino/arduino.stackexchange.com.7z
- stackexchange/askubuntu/askubuntu.com.7z
- stackexchange/avp/avp.stackexchange.com.7z
- stackexchange/codereview/codereview.stackexchange.com.7z
- stackexchange/cs/cs.stackexchange.com.7z
- stackexchange/datascience/datascience.stackexchange.com.7z
- stackexchange/dba/dba.stackexchange.com.7z
- stackexchange/devops/devops.stackexchange.com.7z
- stackexchange/dsp/dsp.stackexchange.com.7z
- stackexchange/raspberrypi/raspberrypi.stackexchange.com.7z
- stackexchange/reverseengineering/reverseengineering.stackexchange.com.7z
- stackexchange/scicomp/scicomp.stackexchange.com.7z
- stackexchange/security/security.stackexchange.com.7z
- stackexchange/serverfault/serverfault.com.7z
- stackexchange/stackoverflow/stackoverflow.com-Posts.7z
- stackexchange/stats/stats.stackexchange.com.7z
- stackexchange/superuser/superuser.com.7z
- stackexchange/unix/unix.stackexchange.com.7z
- stackexchange/vi/vi.stackexchange.com.7z
- stackexchange/wordpress/wordpress.stackexchange.com.7z

3.) Run the ETL process

```
python -m codequestion.etl.stackexchange.execute stackexchange
```

This will create the file stackexchange/questions.db

4.) __OPTIONAL:__ Build word vectors - only necessary if using a word vectors model

```
python -m codequestion.vectors stackexchange/questions.db
```

This will create the file ~/.codequestion/vectors/stackexchange-300d.magnitude

5.) Build embeddings index

```
python -m codequestion.index index.yml stackexchange/questions.db
```

The [default index.yml](https://raw.githubusercontent.com/neuml/codequestion/master/config/index.yml) file is found on GitHub. Settings can be changed to customize how the index is built.

After this step, the index is created and all necessary files are ready to query.

## Model accuracy
The following sections show test results for codequestion v2 and codequestion v1 using the latest Stack Exchange dumps. Version 2 uses a sentence-transformers model. Version 1 uses a word vectors model with BM25 weighting. BM25 and TF-IDF are shown to establish a baseline score.

**StackExchange Query**

Models are scored using [Mean Reciprocal Rank (MRR)](https://en.wikipedia.org/wiki/Mean_reciprocal_rank).

| Model               | MRR   |
| ------------------- | :---: |
| all-MiniLM-L6-v2    | 85.0  |
| SE 300d - BM25      | 77.1  |
| BM25                | 67.7  |
| TF-IDF              | 61.7  |

**STS Benchmark**

Models are scored using [Pearson Correlation](https://en.wikipedia.org/wiki/Pearson_correlation_coefficient). Note that the word vectors model is only trained on Stack Exchange data, so it isn't expected to generalize as well against the STS dataset.

| Model            | Supervision   | Dev   | Test  |
| ---------------- | :-----------: | :---: | :---: |
| all-MiniLM-L6-v2 | Train         | 87.0  | 82.7  |
| SE 300d - BM25   | Train         | 74.0  | 67.4  |

## Testing
To reproduce the tests above, you need to download the test data into ~/.codequestion/test

    mkdir -p ~/.codequestion/test/stackexchange
    wget https://raw.githubusercontent.com/neuml/codequestion/master/test/stackexchange/query.txt -P ~/.codequestion/test/stackexchange
    wget http://ixa2.si.ehu.es/stswiki/images/4/48/Stsbenchmark.tar.gz
    tar -C ~/.codequestion/test -xvzf Stsbenchmark.tar.gz
    python -m codequestion.evaluate -s test
