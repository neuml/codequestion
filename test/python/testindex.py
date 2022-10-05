"""
Index module tests
"""

import contextlib
import io
import unittest

from codequestion.evaluate import StackExchange, STS
from codequestion.index import Index
from codequestion.search import Search
from codequestion.vectors import Vectors

# pylint: disable=C0411
from utils import Utils


class TestIndex(unittest.TestCase):
    """
    Index tests.
    """

    def testTransformers(self):
        """
        Test transformers-backed index
        """

        # Create embeddings index
        index = Index()
        index(Utils.PATH + "/index.yml", Utils.QUESTIONS)

        # Run tests
        self.runTests()

    def testWordVectors(self):
        """
        Test word vector-backed index
        """

        # Build word vectors
        vectors = Vectors()
        vectors(Utils.QUESTIONS, 300, 3)

        # Create embeddings index
        index = Index()
        index(Utils.PATH + "/index.v1.yml", Utils.QUESTIONS)

        # Run tests
        self.runTests()

    def runTests(self):
        """
        Run index tests.
        """

        self.search()
        self.stackexchange()
        self.sts()

    def search(self):
        """
        Run search test.
        """

        # Test search
        search = Search()
        self.assertIn("machine learning", self.command(lambda: search("machine learning")))

    def stackexchange(self):
        """
        Run stack exchange test.
        """

        action = StackExchange()
        self.assertIn("Mean Reciprocal Rank", self.command(lambda: action(None)))
        self.assertIn("Mean Reciprocal Rank", self.command(lambda: action("bm25")))

    def sts(self):
        """
        Run STS test.
        """

        action = STS()
        self.assertIn("Pearson", self.command(lambda: action(None)))

    def command(self, command):
        """
        Runs a console command.

        Args:
            command: command to run

        Returns:
            command output
        """

        # Run info
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            command()

        return output.getvalue()
