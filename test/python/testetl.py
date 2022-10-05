"""
ETL module tests
"""

import os
import unittest

from codequestion.etl.stackexchange import Execute

# pylint: disable=C0411
from utils import Utils

class TestETL(unittest.TestCase):
    """
    ETL tests.
    """

    def testETL(self):
        """
        Test ETL
        """

        Execute.SOURCES = ["ai"]

        execute = Execute()
        execute(Utils.STACKEXCHANGE)

        self.assertTrue(os.path.exists(Utils.QUESTIONS))
 