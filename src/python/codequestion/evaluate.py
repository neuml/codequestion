"""
Evaluate module
"""

import argparse
import csv
import os

from scipy.stats import pearsonr, spearmanr
from tqdm import tqdm
from txtai.embeddings import Embeddings
from txtai.scoring import ScoringFactory

from .models import Models
from .tokenizer import Tokenizer


class StackExchange:
    """
    Stack Exchange query-answer dataset.
    """

    def __call__(self, path, method):
        """
        Evaluates a pre-trained model against the Stack Exchange query-answer dataset.

        Args:
            path: path to tests
            method: run method
        """

        # Load model
        embeddings, scoring = self.load(), None

        # Statistics
        mrr = []

        # Build scoring index
        if method in ("bm25", "tfidf", "sif"):
            scoring = ScoringFactory.create(
                {"method": method, "content": True, "terms": True, "k1": 0.1}
            )
            scoring.index(self.stream(embeddings, "Building scoring index"))

        # Run test data
        with open(
            os.path.join(path, "stackexchange", "query.txt"), encoding="utf-8"
        ) as rows:
            for row in rows:
                query, sourceid, source, _ = row.split("|", 3)
                print(query, sourceid, source)

                # Run search
                results = self.search(embeddings, scoring, query)

                # Get row index within results
                index = -1
                for x, result in enumerate(results):
                    if (
                        int(sourceid) == result["sourceid"]
                        and source == result["source"]
                    ):
                        index = x

                # Calculate stats
                calc = 1 / (1 + index) if index != -1 else 0.0
                print(calc)
                mrr.append(calc)

        mrr = sum(mrr) / len(mrr)
        print("Mean Reciprocal Rank = ", mrr)

    def load(self):
        """
        Loads a pre-trained embeddings model

        Returns:
            embeddings
        """

        # Loading embeddings model
        embeddings = Embeddings()
        embeddings.load(Models.modelPath("stackexchange"))

        return embeddings

    def stream(self, embeddings, message):
        """
        Streams content from an embeddings index. This method is a generator and will yield a row at time.

        Args:
            embeddings: embeddings index
            message: progress bar message
        """

        offset, batch = 0, 1000
        with tqdm(total=embeddings.count(), desc=message) as progress:
            for offset in range(0, embeddings.count(), batch):
                for result in embeddings.search(
                    f"select id, text, tags, source, sourceid from txtai limit {batch} offset {offset}"
                ):
                    yield (result["id"], result, None)

                progress.update(batch)

    def search(self, embeddings, scoring, query):
        """
        Executes a search.

        Args:
            embeddings: embeddings instance
            scoring: scoring instance
            query: query to run

        Returns:
            search results
        """

        results = None
        if scoring:
            # Scoring models have data field with source id + source
            results = [result["data"] for result in scoring.search(query, 10)]
        elif embeddings.scoring:
            # Use custom tokenizer for word vector models
            uids = [
                row["id"] for row in embeddings.search(Tokenizer.tokenize(query), 10)
            ]

            # Get source id + source for each result
            results = []
            for uid in uids:
                results.append(
                    embeddings.search(
                        f"select sourceid, source from txtai where id = {uid}"
                    )[0]
                )
        else:
            # Select source id + source with standard similar clause
            results = embeddings.search(
                f"select sourceid, source from txtai where similar('{query}') limit 10"
            )

        return results


class STS:
    """
    STS Benchmark Dataset
    General text similarity

    http://ixa2.si.ehu.es/stswiki/index.php/STSbenchmark
    """

    def __call__(self, path, method):
        """
        Test a list of vector models.

        Args:
            path: path to tests
            method: run method
        """

        # Load embeddings instance - used to calculate similarity
        embeddings = Embeddings()
        embeddings.load(Models.modelPath("stackexchange"))

        # Test model against sts dataset
        self.test(embeddings, path, method)

    def test(self, embeddings, path, method):
        """
        Tests input Embeddings model against STS benchmark data.

        Args:
            embeddings: embeddings instance
            path: path to tests
            method: run method
        """

        # Test file path
        path = os.path.join(
            path, "stsbenchmark", f"sts-{'dev' if method == 'dev' else 'test'}.csv"
        )

        # Read test data
        rows = self.read(path)

        # Calculated scores and ground truth labels
        scores = []
        labels = []

        for row in rows:
            text1, text2 = row[2], row[3]

            # Use custom tokenizer for word vector models
            if embeddings.scoring:
                text1 = Tokenizer.tokenize(text1)
                text2 = Tokenizer.tokenize(text2)

            if text1 and text2:
                score = embeddings.similarity(text1, [text2])[0][1]
                scores.append(score)

                # Ground truth score normalized between 0 - 1
                labels.append(row[1])

        print("Pearson score =", pearsonr(scores, labels))
        print("Spearman score =", spearmanr(scores, labels))

    def read(self, path):
        """
        Reads a STS data file.

        Args:
            path: full path to file

        Returns:
            rows
        """

        with open(path, encoding="utf-8") as f:
            data = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)

            rows = []

            # Column Index-Name: 4-score, 5-string 1, 6-string 2
            for x, row in enumerate(data):
                # Normalize score from 0-5 to 0-1. 1 being most similar.
                score = float(row[4]) / 5.0

                # Store row as id (1 indexed), normalized score, string 1, string 2
                rows.append((x + 1, score, row[5], row[6]))

            return rows


if __name__ == "__main__":
    # Command line parser
    parser = argparse.ArgumentParser(description="Evaluate")
    parser.add_argument(
        "-s", "--source", required=True, help="data source", metavar="SOURCE"
    )
    parser.add_argument(
        "-p", "--path", required=True, help="path to test files", metavar="PATH"
    )
    parser.add_argument("-m", "--method", help="run method", metavar="METHOD")

    # Parse command line arguments
    args = parser.parse_args()

    # Get eval action
    action = STS() if args.source.lower() == "sts" else StackExchange()

    # Run eval action
    action(args.path, args.method)
