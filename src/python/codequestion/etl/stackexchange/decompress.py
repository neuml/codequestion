"""
Decompress module
"""

import shlex
import shutil
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

        # Check for 7za, default to 7z
        binary = "7za" if shutil.which("7za") else "7z"

        # Build command
        path = path.replace("\\", "/")
        command = f"{binary} e {path}/*.7z Posts.xml -y -o{path}"
        print(command)

        # Start command
        with subprocess.Popen(
            shlex.split(command), stdout=subprocess.PIPE, universal_newlines=True
        ) as process:
            while True:
                output = process.stdout.readline()
                if output == "" and process.poll() is not None:
                    break
                if output:
                    print(output.strip())

            # Call final poll on completion
            process.poll()
