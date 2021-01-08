"""
Evaluation methods to measure model performance
"""

import argparse
import csv
import os
import os.path
import re
import sqlite3

from scipy.stats import pearsonr, spearmanr

from txtai.embeddings import Embeddings

from .models import Models
from .tokenizer import Tokenizer

class Command(object):
    """
    Command line parser
    """

    @staticmethod
    def parse():
        """
        Parses command line arguments.
        """

        parser = argparse.ArgumentParser(description="Evaluate")
        parser.add_argument("-s", "--source", required=True, help="data source", metavar="SOURCE")
        parser.add_argument("-m", "--method", help="run method", metavar="METHOD")

        return parser.parse_args()

class StackExchange(object):
    """
    StackExchange query-answer dataset.
    """

    @staticmethod
    def load():
        """
        Loads a questions database and pre-trained embeddings model

        Returns:
            (db, embeddings)
        """

        print("Loading model")

        path = Models.modelPath("stackexchange")
        dbfile = os.path.join(path, "questions.db")

        # Connect to database file
        db = sqlite3.connect(dbfile)

        # Loading embeddings model
        embeddings = Embeddings()
        embeddings.load(path)

        return db, embeddings

    @staticmethod
    def run(args):
        """
        Evaluates a pre-trained model against the StackExchange query-answer dataset.

        Args:
            args: command line arguments
        """

        # Load model
        db, embeddings = StackExchange.load()
        cur = db.cursor()

        # Statistics
        mrr = []

        # Run test data
        with open(Models.testPath("stackexchange", "query.txt")) as rows:
            for row in rows:
                query, sourceid, source, _ = row.split("|", 3)
                print(query, sourceid, source)

                # Lookup internal id for source id/source
                cur.execute("SELECT Id FROM questions WHERE SourceId = ? and Source=?", [sourceid, source])
                uid = cur.fetchone()
                if uid:
                    uid = uid[0]

                    # Get top 10 results
                    if args.method in ("bm25", "tfidf"):
                        sql = "SELECT Id from search WHERE search=? %s LIMIT 10" % ("ORDER BY BM25(search)" if args.method == "bm25" else "")
                        cur.execute(sql, [re.sub(r"[^\w\s]", "", query)])
                        uids = [row[0] for row in cur.fetchall()]
                    else:
                        # Tokenize query and run search against embeddings model
                        query = Tokenizer.tokenize(query)
                        uids = [uid for uid, _ in embeddings.search(query, 10)]

                    # Calculate stats
                    calc = 1 / (1 + uids.index(uid)) if uid in uids else 0.0
                    print(calc)
                    mrr.append(calc)

        mrr = sum(mrr) / len(mrr)
        print("Mean Reciprocal Rank = ", mrr)

        db.close()

class STS(object):
    """
    STS Benchmark Dataset
    General text similarity

    http://ixa2.si.ehu.es/stswiki/index.php/STSbenchmark
    """

    @staticmethod
    def read(path):
        """
        Reads a STS data file.

        Args:
            path: full path to file

        Returns:
            rows
        """

        data = csv.reader(open(path), delimiter="\t", quoting=csv.QUOTE_NONE)

        rows = []

        # Column Index-Name: 4-score, 5-string 1, 6-string 2
        for x, row in enumerate(data):
            # Normalize score from 0-5 to 0-1. 1 being most similar.
            score = float(row[4]) / 5.0

            # Store row as id (1 indexed), normalized score, string 1, string 2
            rows.append((x + 1, score, row[5], row[6]))

        return rows

    @staticmethod
    def train(vector, score):
        """
        Trains an Embeddings model on STS dev + train data.

        Args:
            vector: word vector model path
            score: scoring method (bm25, sif, tfidf or None for averaging)

        Returns:
            trained Embeddings model
        """

        print("Building model")
        embeddings = Embeddings({"path": Models.vectorPath(vector),
                                 "scoring": score,
                                 "pca": 3})

        rows1 = STS.read(Models.testPath("stsbenchmark", "sts-dev.csv"))
        rows2 = STS.read(Models.testPath("stsbenchmark", "sts-train.csv"))

        rows = rows1 + rows2

        documents = []
        for row in rows:
            tokens = Tokenizer.tokenize(row[2] + " " + row[3])

            if tokens:
                documents.append((row[0], tokens, None))
            else:
                print("Skipping all stop word string: ", row)

        # Build scoring index if scoring method provided
        if embeddings.config.get("scoring"):
            embeddings.score(documents)

        # Build embeddings index
        embeddings.index(documents)

        return embeddings

    @staticmethod
    def test(args, embeddings):
        """
        Tests input Embeddings model against STS benchmark data

        Args:
            args: command line arguments
            embeddings: Embeddings model
        """

        print("Testing model")

        # Test file path
        path = Models.testPath("stsbenchmark", "sts-%s.csv" % ("dev" if args.method == "dev" else "test"))

        # Read test data
        rows = STS.read(path)

        # Calculated scores and ground truth labels
        scores = []
        labels = []

        for row in rows:
            tokens1 = Tokenizer.tokenize(row[2])
            tokens2 = Tokenizer.tokenize(row[3])

            if tokens1 and tokens2:
                score = embeddings.similarity(tokens1, [tokens2])[0][1]
                scores.append(score)

                # Ground truth score normalized between 0 - 1
                labels.append(row[1])
            else:
                print("Skipping all stop word string: ", row)

        print("Pearson score =", pearsonr(scores, labels))
        print("Spearman score =", spearmanr(scores, labels))

    @staticmethod
    def run(args):
        """
        Runs multiple combinations of vector and score combinations.

        Args:
            args: command line arguments
        """

        vectors = ["stackexchange-300d.magnitude"]
        scoring = ["bm25"]

        for vector in vectors:
            for score in scoring:
                print("%s - %s" % (vector, score))
                embeddings = STS.train(vector, score)
                STS.test(args, embeddings)

if __name__ == "__main__":
    # Command line parser
    ARGS = Command.parse()

    if ARGS.source.lower() == "sts":
        STS.run(ARGS)
    else:
        StackExchange.run(ARGS)
