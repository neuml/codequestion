# pylint: disable = C0111
from setuptools import setup

with open("README.md", "r") as f:
    DESCRIPTION = f.read()

setup(name="codequestion",
      version="1.0.0",
      author="NeuML",
      description="Ask coding questions directly from the terminal",
      long_description=DESCRIPTION,
      long_description_content_type="text/markdown",
      url="https://github.com/neuml/codequestion",
      project_urls={
          "Documentation": "https://github.com/neuml/codequestion",
          "Issue Tracker": "https://github.com/neuml/codequestion/issues",
          "Source Code": "https://github.com/neuml/codequestion",
      },
      download_url="https://pypi.org/project/codequestion/",
      license="MIT License: http://opensource.org/licenses/MIT",
      packages=["codequestion"],
      package_dir={"": "src/python/"},
      keywords="python search embedding machine-learning",
      python_requires=">=3.5",
      entry_points={
          "console_scripts": [
              "codequestion = codequestion.shell:main",
          ],
      },
      install_requires=[
          "faiss-gpu>=1.6.1",
          "fasttext>=0.9.1",
          "html2text>=2019.9.26",
          "mdv>=1.7.4",
          "numpy>=1.17.4",
          "pymagnitude>=0.1.120",
          "scikit-learn>=0.22.1",
          "scipy>=1.4.1",
          "tqdm==4.40.2"
      ],
      classifiers=[
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 3",
          "Topic :: Software Development",
          "Topic :: Text Processing :: Indexing",
          "Topic :: Utilities"
      ])
