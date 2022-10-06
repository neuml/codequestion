# pylint: disable = C0111
from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    # Remove GitHub dark mode images
    DESCRIPTION = "".join([line for line in f if "gh-dark-mode-only" not in line])

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
    license="Apache 2.0: http://www.apache.org/licenses/LICENSE-2.0",
    packages=find_packages(where="src/python"),
    package_dir={"": "src/python"},
    keywords="search embedding machine-learning nlp",
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
        "txtai[graph]>=5.0.0",
    ],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
    ],
)
