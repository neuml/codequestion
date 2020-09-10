"""
Indexing module
"""

import os.path
import sqlite3

from txtai.embeddings import Embeddings

from .models import Models
from .tokenizer import Tokenizer

class Index(object):
    """
    Methods to build a new sentence embeddings index.
    """

    @staticmethod
    def stream(dbfile):
        """
        Streams questions from a questions.db file. This method is a generator and will yield a row at time.

        Args:
            dbfile: input SQLite file
        """

        # Connection to database file
        db = sqlite3.connect(dbfile)
        cur = db.cursor()

        cur.execute("SELECT Id, Question, Source, Tags FROM questions")

        count = 0
        for question in cur:
            # Tokenize question, source and tags
            tokens = Tokenizer.tokenize(question[1] + " " + question[2] + " " + question[3])

            document = (question[0], tokens, question[3])

            count += 1
            if count % 1000 == 0:
                print("Streamed %d documents" % (count), end="\r")

            # Skip documents with no tokens parsed
            if tokens:
                yield document

        print("Iterated over %d total rows" % (count))

        # Free database resources
        db.close()

    @staticmethod
    def embeddings(dbfile):
        """
        Builds a sentence embeddings index.

        Args:
            dbfile: input SQLite file

        Returns:
            embeddings index
        """

        embeddings = Embeddings({"path": Models.vectorPath("stackexchange-300d.magnitude"),
                                 "storevectors": True,
                                 "scoring": "bm25",
                                 "pca": 3,
                                 "quantize": True})

        # Build scoring index if scoring method provided
        if embeddings.config.get("scoring"):
            embeddings.score(Index.stream(dbfile))

        # Build embeddings index
        embeddings.index(Index.stream(dbfile))

        return embeddings

    @staticmethod
    def run():
        """
        Executes an index run.
        """

        path = Models.modelPath("stackexchange")
        dbfile = os.path.join(path, "questions.db")

        print("Building new model")
        embeddings = Index.embeddings(dbfile)
        embeddings.save(path)

if __name__ == "__main__":
    Index.run()
