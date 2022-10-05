"""
Vectors module
"""

import os
import os.path
import sqlite3
import sys
import tempfile

from tqdm import tqdm
from txtai.vectors import WordVectors

from .models import Models
from .tokenizer import Tokenizer


class RowIterator:
    """
    Iterates over rows in a database query. Allows for multiple iterations.
    """

    def __init__(self, dbfile):
        """
        Initializes RowIterator.

        Args:
            dbfile: path to SQLite file
        """

        # Store database file
        self.dbfile = dbfile

        self.rows = self.stream(self.dbfile)

    def __iter__(self):
        """
        Creates a database query generator.

        Returns:
            generator
        """

        # reset the generator
        self.rows = self.stream(self.dbfile)
        return self

    def __next__(self):
        """
        Gets the next result in the current generator.

        Returns:
            tokens
        """

        result = next(self.rows)
        if result is None:
            raise StopIteration

        return result

    def stream(self, dbfile):
        """
        Connects to SQLite file at dbfile and yields parsed tokens for each row.

        Args:
            dbfile: path to SQLite file
        """

        # Connection to database file
        db = sqlite3.connect(dbfile)
        cur = db.cursor()

        # Get total number of questions
        cur.execute("SELECT count(*) from Questions")
        total = cur.fetchone()[0]

        # Query for iterating over questions.db rows
        cur.execute("SELECT Question, Source, Tags FROM questions")

        for question in tqdm(cur, total=total, desc="Tokenizing input"):
            # Tokenize question, source and tags
            tokens = Tokenizer.tokenize(
                question[0] + " " + question[1] + " " + question[2]
            )

            # Skip documents with no tokens parsed
            if tokens:
                yield tokens

        # Free database resources
        db.close()


class Vectors:
    """
    Methods to build a FastText model.
    """

    def __call__(self, dbfile, size, mincount):
        """
        Converts dbfile into a fastText model using pymagnitude's SQLite output format.

        Args:
            dbfile: input SQLite file
            size: dimensions for fastText model
            mincount: minimum number of times a token must appear in input
        """

        # Stream tokens to temporary file
        tokens = self.tokens(dbfile)

        # Output file path
        path = Models.vectorPath(f"stackexchange-{size}d", True)

        # Build word vectors model
        WordVectors.build(tokens, size, mincount, path)

        # Remove temporary tokens file
        os.remove(tokens)

    def tokens(self, dbfile):
        """
        Iterates over each row in dbfile and writes parsed tokens to a temporary file for processing.

        Args:
            dbfile: SQLite file to read

        Returns:
            path to output file
        """

        tokens = None

        # Stream tokens to temp working file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as output:
            # Save file path
            tokens = output.name

            for row in RowIterator(dbfile):
                output.write(" ".join(row) + "\n")

        return tokens


# pylint: disable=C0103
if __name__ == "__main__":
    # Path to questions.db file
    dbfile = sys.argv[1] if len(sys.argv) > 1 else None
    if not dbfile or not os.path.exists(dbfile):
        print("Path to questions.db file does not exist, exiting")
        sys.exit()

    # Resolve questions.db path and run
    vectors = Vectors()
    vectors(dbfile, 300, 3)
