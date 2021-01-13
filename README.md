# codequestion: Ask coding questions directly from the terminal

codequestion is a Python application that allows a user to ask coding questions directly from the terminal. Many developers will have a web browser window open while they develop and run web searches as questions arise. codequestion attempts to make that process faster so you can focus on development.

The default model for codequestion is built off the [Stack Exchange Dumps on archive.org](https://archive.org/details/stackexchange). codequestion runs locally against a pre-trained model using data from Stack Exchange. No network connection is required once installed. The model executes similarity queries to find similar questions to the input query. 

An example of how codequestion works is shown below:

![demo](https://raw.githubusercontent.com/neuml/codequestion/master/demo.gif)

## Installation
The easiest way to install is via pip and PyPI

    pip install codequestion

You can also install codequestion directly from GitHub. Using a Python Virtual Environment is recommended.

    pip install git+https://github.com/neuml/codequestion

Python 3.6+ is supported

See [this link](https://github.com/neuml/txtai#installation) to help resolve environment-specific install issues.

## Downloading a model

Once codequestion is installed, a model needs to be downloaded.

    python -m codequestion.download

The model will be stored in ~/.codequestion/

The model can also be manually installed if the machine doesn't have direct internet access. Pre-trained models are pulled from the [GitHub release page](https://github.com/neuml/codequestion/releases)

    unzip cqmodel.zip ~/.codequestion

It is possible for codequestion to be customized to run against a custom question-answer repository and more will come on that in the future. At this time, only the Stack Exchange model is supported. 

## Running queries

The fastest way to run queries is to start a codequestion shell

    codequestion

A prompt will come up. Queries can be typed directly into the console.

## Tech overview
The following is an overview of how this project works. 

### Processing the raw data dumps
The raw 7z XML dumps from Stack Exchange are processed through a series of steps (see [building a model](#building-a-model)). Only highly scored questions with answers are retrieved for storage in the model. Questions and answers are consolidated into a single SQLite file called questions.db. The schema for questions.db is below.

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
codequestion builds a sentence embeddings index for questions.db. Each question in the questions.db schema is tokenized and resolved to word embeddings. The word embedding model is a custom fastText model built on questions.db. Once each token is converted to word embeddings, a weighted sentence embedding is created. Word embeddings are weighed using a BM25 index over all the tokens in the repository, with one important modification. Tags are used to boost the weights of tag tokens.

Once questions.db is converted to a collection of sentence embeddings, they are normalized and stored in Faiss, which allows for fast similarity searches.

### Querying
codequestion tokenizes each query using the same method as during indexing. Those tokens are used to build a sentence embedding. That embedding is queried against the Faiss index to find the most similar questions.

## Building a model
The following steps show how to build a codequestion model using Stack Exchange archives.

_This is not necessary if using the pre-trained models from the [GitHub release page](https://github.com/neuml/codequestion/releases)_

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

```bash
python -m codequestion.etl.stackexchange.execute stackexchange
```

This will create the file ~/.codequestion/models/stackexchange/questions.db

4.) Build word vectors

Currently, the model is using BM25 + fastText for indexing.

```bash
python -m codequestion.vectors
```

This will create the file ~/.codequestion/vectors/stackexchange-300d.magnitude

5.) Build index

```bash
python -m codequestion.index
```

After this step, the index is created and all necessary files are ready to query.

## Model accuracy
The following sections show test results for various word vector/scoring combinations. SE 300d word vectors with BM25 scoring does the best against this dataset. Even with the reduced vocabulary of < 1M Stack Exchange questions, SE 300d - BM25 does reasonably well against the STS Benchmark.

**StackExchange Query**

Models scored using Mean Reciprocal Rank (MRR)

| Model           | MRR   | 
| --------------- | :---: |
| SE 300d - BM25  | 76.3  |
| ParaNMT - BM25  | 67.4  |
| FastText - BM25 | 66.1  |
| BM25            | 49.5  |
| TF-IDF          | 45.9  |

**STS Benchmark**

Models scored using Pearson Correlation

| Model           | Supervision   | Dev   | Test  |
| --------------- | :-----------: | :---: | :---: |
| ParaNMT - BM25  | Train         | 82.6  | 78.1  |
| FastText - BM25 | Train         | 79.8  | 72.7  |
| SE 300d - BM25  | Train         | 77.0  | 69.1  |

## Testing
To reproduce the tests above, you need to download the test data into ~/.codequestion/test

    mkdir -p ~/.codequestion/test/stackexchange
    wget https://raw.githubusercontent.com/neuml/codequestion/master/test/stackexchange/query.txt -P ~/.codequestion/test/stackexchange
    wget http://ixa2.si.ehu.es/stswiki/images/4/48/Stsbenchmark.tar.gz
    tar -C ~/.codequestion/test -xvzf Stsbenchmark.tar.gz
    python -m codequestion.evaluate -s test
