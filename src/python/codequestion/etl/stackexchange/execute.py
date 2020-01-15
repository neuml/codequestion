"""
Main execution method to build a consolidates questions.db file from Stack Exchange Data Dumps.
"""

import os
import os.path
import sys

from . import db2qa
from . import decompress
from . import sift
from . import xml2db

# List of sources
SOURCES = ["ai", "android", "apple", "arduino", "askubuntu", "avp", "codereview", "cs", "datascience", "dba", "devops",
           "dsp", "raspberrypi", "reverseengineering", "scicomp", "serverfault", "security", "stackoverflow", "stats",
           "superuser", "unix", "vi", "wordpress"]

def process(path):
    """
    Iterates through each source and converts raw xml to SQLite databases. Returns a list of
    output databases.

    Args:
        path: input directory path with raw source data directories

    Returns:
        paths to output databases
    """

    # Extract filtered content and build source databases to process
    for source in SOURCES:
        spath = os.path.join(path, source)

        # Extract Posts.xml from 7za file
        decompress.run(spath)

        posts = os.path.join(spath, "Posts.xml")
        filtered = os.path.join(spath, "Filtered.xml")

        # Filter Posts.xml file for matching questions
        sift.run(posts, filtered)

        dbfile = os.path.join(spath, "%s.db" % source)

        # Convert filtered Posts.xml file to SQLite db file
        xml2db.run(filtered, dbfile)

    # Get list of all databases to consolidate
    return [os.path.join(path, source, "%s.db" % source) for source in SOURCES]

def run():
    """
    Converts a directory of raw sources to a single output questions database.
    """

    # Input data directory
    path = sys.argv[1]
    if not os.path.exists(path):
        print("Data directory does not exist, exiting")
        return

    # Iterates through a directory of raw sources and builds staging databases
    databases = process(path)

    # Output directory - create if it doesn't exist
    output = os.path.join(os.path.expanduser("~"), ".codequestion", "models", "stackexchange")
    os.makedirs(output, exist_ok=True)

    # Output database file
    qafile = os.path.join(output, "questions.db")

    # Build consolidated SQLite questions database
    db2qa.run(databases, qafile)

if __name__ == "__main__":
    run()
