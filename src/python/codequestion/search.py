"""
Search module
"""

import os
import os.path
import re

import html2markdown

from rich.console import Console
from rich.markdown import Markdown
from txtai.embeddings import Embeddings

from .models import Models
from .tokenizer import Tokenizer


class Search:
    """
    Search an embeddings index.
    """

    def __init__(self):
        """
        Creates a new search action.
        """

        # Load embeddings index
        self.embeddings = self.load()
        self.console = Console()

    def __call__(self, query=None, limit=1, uid=None):
        """
        Runs a search action.

        Args:
            query: query string
            limit: number of results to return
            uid: id to show
        """

        # Query prefix
        prefix = "select id, score, questionuser, question, tags, date, answeruser, object answer, reference from txtai where"

        if uid is not None:
            # ID query
            query = f"{prefix} id = '{uid}'"
        elif self.embeddings.scoring:
            # Use custom tokenizer for word vector models
            query = Tokenizer.tokenize(query)

            # Run search and build id query
            result = self.embeddings.search(query, 1)[0] if query else {}
            query = f"""
                select id, {result.get('score')} score, questionuser, question, tags, date, answeruser, object answer, reference
                from txtai
                where id = '{result.get('id')}'
            """
        else:
            # Default similar clause query
            query = f"{prefix} similar('{query}')"

        # Render results
        for result in self.embeddings.search(query, limit):
            # Show result
            self.result(result, limit)

        self.console.print()

    def load(self):
        """
        Loads an embeddings model.

        Returns:
            embeddings
        """

        path = Models.modelPath("stackexchange")

        if os.path.isfile(os.path.join(path, "config")):
            print(f"Loading model from {path}")
            embeddings = Embeddings()
            embeddings.load(path)
        else:
            print("ERROR: loading model: ensure model is installed")
            print(
                "ERROR: Pre-trained model can be installed by running python -m codequestion.download"
            )
            raise FileNotFoundError(f"Unable to load codequestion model from {path}")

        return embeddings

    def result(self, result, limit):
        """
        Renders a result row.

        Args:
            result: result row
            limit: number of results
        """

        # If score is empty, this a direct query
        score = result["score"]
        score = score if score is not None else 1.0

        self.console.print(
            f"[bright_green]Question (by {result['questionuser']}): {result['question']} [{score:4f}][/bright_green]",
            highlight=False,
        )
        self.console.print(f"Id: {result['id']}", highlight=False)
        self.console.print(f"Last Activity: {result['date']}", highlight=False)
        self.console.print(f"Tags: {result['tags']}")
        self.console.print(f"Answer (by {result['answeruser']}):\n", highlight=False)
        self.console.print(self.markdown(result["answer"]))
        self.console.print(f"\nReference: {result['reference']}")

        # Print results divider
        if limit > 1:
            self.console.rule()

    def markdown(self, text):
        """
        Converts html text to markdown.

        Args:
            text: html text

        Returns:
            text as markdown
        """

        # Remove rel attributes as they are not supported by html2markdown
        text = re.sub(r' rel=".+?">', ">", text)

        # Convert html to markdown
        text = html2markdown.convert(text)

        # Decode [<>&] characters
        text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")

        # Wrap as Rich Markdown
        return Markdown(text)
