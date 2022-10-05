"""
Index module
"""

import os.path
import sqlite3
import sys

from tqdm import tqdm
from txtai.app import Application
from txtai.embeddings import Embeddings

from .models import Models
from .tokenizer import Tokenizer


class Index:
    """
    Builds a new embeddings index.
    """

    def __call__(self, config, dbfile):
        """
        Builds and saves an embeddings index.

        Args:
            config: input configuration file
            dbfile: input SQLite file
        """

        embeddings = self.build(config, dbfile)
        embeddings.save(Models.modelPath("stackexchange"))

    def build(self, config, dbfile):
        """
        Builds an embeddings index.

        Args:
            config: input configuration file
            dbfile: input SQLite file

        Returns:
            embeddings index
        """

        # Configure embeddings index
        config = Application.read(config)

        # Resolve full path to vectors file, if necessary
        if config.get("scoring"):
            config["path"] = os.path.join(Models.vectorPath(config["path"]))

        # Create embeddings index
        embeddings = Embeddings(config)

        # Build scoring index, if scoring method provided
        if embeddings.scoring:
            embeddings.score(self.stream(dbfile, embeddings, "Building scoring index"))

        # Build embeddings index
        embeddings.index(self.stream(dbfile, embeddings, "Building embeddings index"))

        return embeddings

    def stream(self, dbfile, embeddings, message):
        """
        Streams questions from a questions.db file. This method is a generator and will yield a row at time.

        Args:
            dbfile: input SQLite file
            embeddings: embeddings instance
            message: progress bar message
        """

        # Connection to database file
        db = sqlite3.connect(dbfile)
        db.row_factory = sqlite3.Row
        cur = db.cursor()

        # Get total number of questions
        cur.execute("SELECT count(*) from Questions")
        total = cur.fetchone()[0]

        # Query for iterating over questions.db rows
        cur.execute(
            "SELECT Id, Source, SourceId, Date, Tags, Question, QuestionUser, Answer, AnswerUser, Reference FROM Questions"
        )

        for row in tqdm(cur, total=total, desc=message):
            # Transform all keys to lowercase
            row = {k.lower(): row[k] for k in row.keys()}

            # Store answer as object
            row["object"] = row.pop("answer")

            # Build text and yield (id, text, tags) tuple
            row["text"] = row["question"] + " " + row["source"] + " " + row["tags"]

            # Use custom tokenizer for word vector models
            if embeddings.scoring:
                row["text"] = Tokenizer.tokenize(row["text"])

            # Yield document
            yield (row["id"], row, row["tags"])

        # Free database resources
        db.close()


# pylint: disable=C0103
if __name__ == "__main__":
    # Path to index configuration file
    config = sys.argv[1] if len(sys.argv) > 1 else None
    if not config or not os.path.exists(config):
        print("Path to index configuration file does not exist, exiting")
        sys.exit()

    # Path to questions.db file
    dbfile = sys.argv[2] if len(sys.argv) > 1 else None
    if not dbfile or not os.path.exists(dbfile):
        print("Path to questions.db file does not exist, exiting")
        sys.exit()

    # Build index
    index = Index()
    index(config, dbfile)
