codequestion: Ask coding questions directly from the terminal
======

codequestion is a Python terminal program that allows an user to ask coding questions directly from the terminal. Many developers will have a web browser window open while they develop and run web searches as questions arise. codequestion attempts to make that process faster so you can focus on development.

The default model for codequestion is built off the [Stack Exchange Dumps on archive.org](https://archive.org/details/stackexchange). codequestion runs locally against a pre-trained model using data from Stack Exchange. No network connection is required once installed. The model executes similarity queries to find similar questions to the input query. 

An example of how codequestion works is shown below:

![demo](https://raw.githubusercontent.com/neuml/codequestion/master/demo.gif)

### Installation
The easiest way to install is via pip and PyPI

    pip install codequestion

You can also use Git to clone the repository from GitHub and install it manually:

    git clone https://github.com/neuml/codequestion.git
    cd codequestion
    pip install .

Python 3.5+ is supported

### Downloading a model

Once codequestion is installed, a model needs to be downloaded.

    python -m codequestion.download

The model will be stored in ~/.codequestion/

The model can also be manually installed if the machine doesn't have direct internet access. Pre-trained models are pulled from the [github release page](https://github.com/neuml/codequestion/releases)

    unzip cqmodel.zip ~/.codequestion

It is possible for codequestion to be customized to run against a custom question-answer repository and more will come on that in the future. At this time, only the Stack Exchange model is supported. 

### Running queries

The fastest way to run queries is to start a codequestion shell

    codequestion

A prompt will come up. Queries can be typed directly into the console.

### Technical overview
The full source code for codequestion is available on github. Code is licensed under the MIT license.

    git clone https://github.com/neuml/codequestion.git
    cd codequestion

The following is an overview of how this project works. 

#### Processing the raw data dumps
The raw 7z XML dumps from Stack Exchange are processed through a series of steps. Only highly scored questions with answers are retrieved for storage in the model. Questions and answers are consolidated into a single SQLite file called questions.db. The schema for questions.db is below.

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

#### Indexing
codequestion builds a sentence embeddings index for questions.db. Each question in the questions.db schema is tokenized and resolved to a word embedding. The word embedding model is a custom fastText model built on questions.db. Once each token is converted to word embeddings, a weighted sentence embedding is created. Word embeddings are weighed using a BM25 index over all the tokens in the repository, with one modification. Tags are used to boost the weights of tag tokens.

Once questions.db is converted to a collection of sentence embeddings, they are normalized and stored in faiss, which allows for fast similarity searches.

#### Querying
codequestion tokenizes each query using the same method as during indexing. Those tokens are used to build a sentence embedding. That embedding is queried against the faiss index to find the most similar questions. 

#### Model accuracy
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

### Testing
To reproduce the tests above, you need to download the test data into ~/.codequestion/test

    mkdir -p ~/.codequestion/test/stackexchange
    wget https://raw.githubusercontent.com/neuml/codequestion/master/test/stackexchange/query.txt -P ~/.codequestion/test/stackexchange
    wget http://ixa2.si.ehu.es/stswiki/images/4/48/Stsbenchmark.tar.gz
    tar -C ~/.codequestion/test -xvzf Stsbenchmark.tar.gz
    python -m codequestion.evaluate
