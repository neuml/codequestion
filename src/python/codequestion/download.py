"""
Download module
"""

import os.path
import tempfile
import zipfile

from urllib.request import urlopen

from tqdm import tqdm

from .models import Models


class Download:
    """
    Downloads a pre-trained model.
    """

    def __call__(self, url, path=None):
        """
        Downloads a pre-trained model from url into the local model cache directory.

        Args:
            url: url model path
        """

        # Get base models path
        path = path if path else Models.basePath(True)
        dest = os.path.join(tempfile.gettempdir(), os.path.basename(url))

        print(f"Downloading model from {url} to {dest}")

        # Download file
        self.download(url, dest)

        print(f"Decompressing model to {path}")

        # Ensure file was downloaded successfully
        if os.path.exists(dest):
            with zipfile.ZipFile(dest, "r") as z:
                z.extractall(path)

        print("Download complete")

    def download(self, url, dest):
        """
        Downloads a remote file from url and stores at dest.

        Args:
            url: remote url
            dest: destination file path
        """

        with urlopen(url) as response:
            buffer = 16 * 1024
            headers = response.info()
            size = int(headers["Content-Length"]) if "Content-Length" in headers else -1

            with tqdm(total=size, unit="B", unit_scale=True, unit_divisor=1024) as pbar:
                with open(dest, "wb") as f:
                    while True:
                        chunk = response.read(buffer)
                        if not chunk:
                            break

                        f.write(chunk)
                        pbar.update(len(chunk))


if __name__ == "__main__":
    download = Download()
    download(
        "https://github.com/neuml/codequestion/releases/download/v2.0.0/cqmodel.zip"
    )
