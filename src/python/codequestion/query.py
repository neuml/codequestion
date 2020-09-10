"""
Query module
"""

import argparse
import os
import os.path
import sqlite3

import html2text
import mdv

from txtai.embeddings import Embeddings

from .models import Models
from .tokenizer import Tokenizer

class Query(object):
    """
    Methods to query an embeddings index.
    """

    @staticmethod
    def escape(text):
        """
        Escapes text to work around issues with mdv double escaping characters.

        Args:
            text: input text

        Returns:
            escaped text
        """

        text = text.replace("<", "¿")
        text = text.replace(">", "Ñ")
        text = text.replace("&", "ž")

        return text

    @staticmethod
    def unescape(text):
        """
        Un-escapes text to work around issues with mdv double escaping characters.

        Args:
            text: input text

        Returns:
            unescaped text
        """

        text = text.replace("¿", "<")
        text = text.replace("Ñ", ">")
        text = text.replace("ž", "&")

        return text

    @staticmethod
    def render(text, html=True, tab_length=0):
        """
        Renders input text to formatted text ready to send to the terminal.

        Args:
            text: input html text

        Returns:
            text formatted for print to terminal
        """

        if html:
            # Convert HTML
            parser = html2text.HTML2Text()
            parser.body_width = 0
            text = parser.handle(text)

            text = Query.escape(text)

        text = mdv.main(text, theme="592.2129", c_theme="953.3567", cols=180, tab_length=tab_length)

        if html:
            text = Query.unescape(text)

        return text.strip()

    @staticmethod
    def match(query, tags, question):
        """
        Analyzses a query match to determine if it will be accepted as a match.

        Args:
            query: query tokens
            tags: all tags
            question: matching question

        Return:
            True if query is accepted as a match, False otherwise
        """

        # Flatten question object to string for searching
        question = Tokenizer.tokenize(question[0] + " " + question[1] + " " + question[2])

        match = True
        for token in query:
            # Look for tag tokens and require all those tag tokens to be in the matching question
            if token in tags and token not in question:
                match = False
                break

        return match

    @staticmethod
    def load():
        """
        Loads an embeddings model and questions.db database.

        Returns:
            (embeddings, db handle)
        """

        path = Models.modelPath("stackexchange")
        dbfile = os.path.join(path, "questions.db")

        if os.path.isfile(os.path.join(path, "config")):
            print("Loading model from %s" % path)
            embeddings = Embeddings()
            embeddings.load(path)
        else:
            print("ERROR: loading model: ensure model is installed")
            print("ERROR: Pre-trained model can be installed by running python -m codequestion.download")
            raise FileNotFoundError("Unable to load codequestion model from %s" % path)

        # Connect to database file
        db = sqlite3.connect(dbfile)

        return (embeddings, db)

    @staticmethod
    def query(embeddings, db, query):
        """
        Executes a query against the embeddings model.

        Args:
            embeddings: embeddings model
            db: open SQLite database
            query: query string
        """

        cur = db.cursor()

        query = Tokenizer.tokenize(query)
        print("Query: ", query)

        accepted = 0
        for uid, score in embeddings.search(query, 10):
            cur.execute("SELECT QuestionUser, Question, Tags, AnswerUser, Answer, Reference FROM questions WHERE id = ?", [uid])

            question = cur.fetchone()
            match = Query.match(query, embeddings.scoring.tags, question)
            if match or score >= 0.9:
                print(Query.render("#Question (by %s): %s [%.4f]" % (question[0], question[1], score), html=False))
                print("Tags: %s" % question[2])
                print("Answer (by %s):\n%s" % (question[3], Query.render(question[4], 2)))
                print("\nReference: %s" % question[5])

                accepted += 1
                if match or accepted >= 2:
                    break

                print()

    @staticmethod
    def close(db):
        """
        Closes a SQLite database database.

        Args:
            db: open database
        """

        # Free database resources
        db.close()

    @staticmethod
    def args():
        """
        Parses command line arguments.

        Returns:
            command line arguments
        """

        parser = argparse.ArgumentParser(description="codequestion query")

        parser.add_argument("-l", "--lang", help="Sets default language")
        parser.add_argument("-q", "--query", required=True, help="Query to execute")

        return parser.parse_args()

    @staticmethod
    def run():
        """
        Executes a query against a codequestion index.
        """

        # Parse command line arguments
        args = Query.args()

        # Build query
        query = "%s %s" % (args.lang, args.query) if args.lang else args.query

        # Load model
        embeddings, db = Query.load()

        # Query the database
        Query.query(embeddings, db, query)

        # Free resources
        Query.close(db)

if __name__ == "__main__":
    Query.run()
