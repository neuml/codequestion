"""
Console module tests
"""

import contextlib
import io
import os
import unittest

from codequestion.console import Console
from codequestion.etl.stackexchange import Execute
from codequestion.index import Index

# pylint: disable=C0411
from utils import Utils


class TestConsole(unittest.TestCase):
    """
    Console tests.
    """

    @classmethod
    def setUpClass(cls):
        """
        Initialize test data.
        """

        os.environ["CODEQUESTION_HOME"] = Utils.STACKEXCHANGE + ".console"

        # Run etl process
        Execute.SOURCES = ["ai"]

        execute = Execute()
        execute(Utils.STACKEXCHANGE)

        # Create embeddings index
        index = Index()
        index(Utils.PATH + "/index.yml", Utils.QUESTIONS)

        cls.console = Console()
        cls.console.preloop()

    def testLimit(self):
        """
        Test .limit command
        """

        self.assertEqual(self.command(".limit 1"), "")

    def testPath(self):
        """
        Test .path command
        """

        self.assertIn("1. ", self.command(".path 0 1"))

    def testSearch(self):
        """
        Test search
        """

        self.assertIn("Question", self.command("ai"))

    def testShow(self):
        """
        Test .show command
        """

        self.assertIn("Question", self.command(".show 0"))

    def testtopics(self):
        """
        Test .topics command
        """

        self.assertNotIn("ERROR", self.command(".topics"))
        self.assertNotIn("ERROR", self.command(".topics ai"))

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
            self.console.onecmd(command)

        return output.getvalue()
