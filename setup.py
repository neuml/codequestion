# pylint: disable = C0111
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    DESCRIPTION = f.read()

setup(
    name="codequestion",
    version="2.0.0",
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
    license="Apache 2.0: http://www.apache.org/licenses/LICENSE-2.0",
    packages=["codequestion"],
    package_dir={"": "src/python/"},
    keywords="python search embedding machine-learning",
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "codequestion = codequestion.console:main",
        ],
    },
    install_requires=[
        "html2markdown>=0.1.7",
        "rich>=12.0.1",
        "scipy>=1.4.1",
        "tqdm>=4.48.0",
        "txtai[similarity]>=5.0.0",
    ],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
    ],
)
