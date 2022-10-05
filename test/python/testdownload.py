"""
Download module tests
"""

import os
import unittest

from codequestion.download import Download

# pylint: disable=C0411
from utils import Utils


class TestDownload(unittest.TestCase):
    """
    Download tests.
    """

    def testDownload(self):
        """
        Test download
        """

        download = Download()
        download(
            "https://github.com/neuml/codequestion/archive/refs/heads/master.zip",
            Utils.PATH,
        )

        # Check archive uncompressed successfully
        self.assertTrue(os.path.exists(Utils.PATH + "/codequestion-master/setup.py"))
