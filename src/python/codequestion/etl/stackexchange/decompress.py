"""
Runs a 7zip extract command via an external process.
"""

import shlex
import subprocess

def run(path):
    """
    Runs the 7za extraction.

    Args:
        path: input directory path with 7z files
    """

    # Build the 7za command
    command = "7za e %s/*.7z Posts.xml -y -o%s" % (path, path)
    print(command)

    # Start command
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, universal_newlines=True)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())

    # Call final poll on completion
    process.poll()
