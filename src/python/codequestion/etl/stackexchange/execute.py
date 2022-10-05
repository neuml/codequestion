"""
Execute module
"""

import os
import os.path
import sys

from .db2qa import DB2QA
from .decompress import Decompress
from .sift import Sift
from .xml2db import XML2DB


class Execute:
    """
    Main execution method to build a consolidated questions.db file from Stack Exchange Data Dumps.
    """

    # List of sources
    SOURCES = [
        "ai",
        "android",
        "apple",
        "arduino",
        "askubuntu",
        "avp",
        "codereview",
        "cs",
        "datascience",
        "dba",
        "devops",
        "dsp",
        "raspberrypi",
        "reverseengineering",
        "scicomp",
        "serverfault",
        "security",
        "stackoverflow",
        "stats",
        "superuser",
        "unix",
        "vi",
        "wordpress",
    ]

    def __call__(self, path):
        """
        Converts a directory of raw sources to a single output questions database.

        Args:
            path: base directory path
        """

        # Iterates through a directory of raw sources and builds staging databases
        databases = self.process(path)

        # Output database file
        qafile = os.path.join(path, "questions.db")

        # Build consolidated SQLite questions database
        db2qa = DB2QA()
        db2qa(databases, qafile)

    def process(self, path):
        """
        Iterates through each source and converts raw xml to SQLite databases. Returns a list of
        output databases.

        Args:
            path: input directory path with raw source data directories

        Returns:
            paths to output databases
        """

        # Extract filtered content and build source databases to process
        for source in Execute.SOURCES:
            spath = os.path.join(path, source)

            # Extract Posts.xml from 7za file
            decompress = Decompress()
            decompress(spath)

            posts = os.path.join(spath, "Posts.xml")
            filtered = os.path.join(spath, "Filtered.xml")

            # Filter Posts.xml file for matching questions
            sift = Sift()
            sift(posts, filtered)

            dbfile = os.path.join(spath, f"{source}.db")

            # Convert filtered Posts.xml file to SQLite db file
            xml2db = XML2DB()
            xml2db(filtered, dbfile)

        # Get list of all databases to consolidate
        return [
            os.path.join(path, source, f"{source}.db") for source in Execute.SOURCES
        ]


if __name__ == "__main__":
    # Input data directory
    path = sys.argv[1]
    if not os.path.exists(path):
        print("Data directory does not exist, exiting")
        sys.exit()

    # Run ETL process
    execute = Execute()
    execute(path)
