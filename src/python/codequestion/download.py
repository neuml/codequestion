"""
Download module
"""

import os.path
import tempfile
import zipfile

from urllib.request import urlopen

from tqdm import tqdm

from .models import Models

class Download(object):
    """
    Downloads a pre-trained model.
    """

    @staticmethod
    def download(url, dest):
        """
        Downloads a remote file from url and stores at dest.

        Args:
            url: remote url
            dest: destination file path
        """

        with urlopen(url) as response:
            buffer = 16 * 1024
            size = int(response.info()["Content-Length"])

            with tqdm(total=size, unit="B", unit_scale=True, unit_divisor=1024) as pbar:
                with open(dest, "wb") as f:
                    while True:
                        chunk = response.read(buffer)
                        if not chunk:
                            break

                        f.write(chunk)
                        pbar.update(len(chunk))

    @staticmethod
    def run(url):
        """
        Downloads a pre-trained model from url into the local model cache directory.

        Args:
            url: url model path
        """

        # Get base models path
        path = Models.basePath(True)
        dest = os.path.join(tempfile.gettempdir(), os.path.basename(url))

        print("Downloading model from %s to %s" % (url, dest))

        # Download file
        Download.download(url, dest)

        print("Decompressing model to %s" % path)

        # Ensure file was downloaded successfully
        if os.path.exists(dest):
            with zipfile.ZipFile(dest, "r") as z:
                z.extractall(path)

        print("Download complete")

if __name__ == "__main__":
    Download.run("https://github.com/neuml/codequestion/releases/download/v1.1.0/cqmodel.zip")
