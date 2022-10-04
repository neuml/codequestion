"""
Path module
"""

from rich.console import Console


class Path:
    """
    Traverse semantic graphs.
    """

    def __init__(self, embeddings):
        """
        Creates a new path action.

        Args:
            embeddings: embeddings instance
        """

        self.embeddings = embeddings
        self.graph = embeddings.graph

    def __call__(self, start, end):
        """
        Runs a path action.

        Args:
            start: start node id
            end: end node id
        """

        console = Console()

        path = self.graph.showpath(start, end)
        for x, uid in enumerate(path):
            query = f"select question from txtai where id = '{uid}'"
            question = self.embeddings.search(query, 1)[0]["question"]
            console.print(f"{x + 1}. {question} ({uid})")
