"""
Decompress module
"""

import shlex
import subprocess


class Decompress:
    """
    Runs a 7zip extract command via an external process.
    """

    def __call__(self, path):
        """
        Runs the 7za extraction.

        Args:
            path: input directory path with 7z files
        """

        # Build the 7za command
        command = f"7za e {path}/*.7z Posts.xml -y -o{path}"
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
