"""
Vectors module
"""

import os
import os.path
import sqlite3
import tempfile

import fasttext
import fasttext.util

# pylint: disable=E0401,E0611
# Defined at runtime
from .magnitude import converter
from .models import Models
from .tokenizer import Tokenizer

class RowIterator(object):
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
        else:
            return result

    def stream(self, dbfile):
        """
        Connects to SQLite file at dbfile and yields parsed tokens for each row.

        Args:
            dbfile:
        """

        # Connection to database file
        db = sqlite3.connect(dbfile)
        cur = db.cursor()

        cur.execute("SELECT Question, Source, Tags FROM questions")

        count = 0
        for question in cur:
            # Tokenize question, source and tags
            tokens = Tokenizer.tokenize(question[0] + " " + question[1] + " " + question[2])

            count += 1
            if count % 1000 == 0:
                print("Streamed %d documents" % (count))

            # Skip documents with no tokens parsed
            if tokens:
                yield tokens

        print("Iterated over %d total rows" % (count))

        # Free database resources
        db.close()

class Vectors(object):
    """
    Methods to build a FastText model.
    """

    @staticmethod
    def tokens(dbfile):
        """
        Iterates over each row in dbfile and writes parsed tokens to a temporary file for processing.

        Args:
            dbfile: SQLite file to read

        Returns:
            path to output file
        """

        tokens = None

        # Stream tokens to temp working file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as output:
            # Save file path
            tokens = output.name

            for row in RowIterator(dbfile):
                output.write(" ".join(row) + "\n")

        return tokens

    @staticmethod
    def run(dbfile, size, mincount):
        """
        Converts dbfile into a fastText model using pymagnitude's SQLite output format.

        Args:
            dbfile: input SQLite file
            size: dimensions for fastText model
            mincount: minimum number of times a token must appear in input
        """

        # Stream tokens to temporary file
        tokens = Vectors.tokens(dbfile)

        # Train on tokens file using largest dimension size
        model = fasttext.train_unsupervised(tokens, dim=size, minCount=mincount)

        # Remove temporary tokens file
        os.remove(tokens)

        # Output file path
        print("Building %d dimension model" % size)
        path = Models.vectorPath("stackexchange-%dd" %size, True)

        # Output vectors in vec/txt format
        with open(path + ".txt", "w") as output:
            words = model.get_words()
            output.write("%d %d\n" % (len(words), model.get_dimension()))

            for word in words:
                # Skip end of line token
                if word != "</s>":
                    vector = model.get_word_vector(word)
                    data = ""
                    for v in vector:
                        data += " " + str(v)

                    output.write(word + data + "\n")

        # Convert and delete tokens, text vectors
        print("Converting file to magnitude format")
        converter.convert(path + ".txt", path + ".magnitude", subword=True)
        os.remove(path + ".txt")

if __name__ == "__main__":
    # Resolve questions.db path and run
    Vectors.run(os.path.join(Models.modelPath("stackexchange"), "questions.db"), 300, 3)
