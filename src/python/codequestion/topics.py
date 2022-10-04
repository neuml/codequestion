"""
Topics module
"""

from rich.console import Console

from txtai.embeddings import Embeddings


class Topics:
    """
    Query topic models.
    """

    def __init__(self, embeddings):
        """
        Creates a new topics action.

        Args:
            embeddings: embeddings instance
        """

        self.embeddings = embeddings
        self.topics = embeddings.graph.topics

        # Build on-the-fly topics index
        self.topicembed = Embeddings({"path": "sentence-transformers/all-MiniLM-L6-v2"})
        self.topicembed.index((x, topic, None) for x, topic in enumerate(self.topics))

    def __call__(self, query=None):
        """
        Runs a topics action.

        Args:
            query: optional query to filter topics, otherwise top topics are shown
        """

        console = Console()

        topics = list(self.topics.keys())
        if query:
            results = self.topicembed.search(query, 10)
        else:
            results = [(x, 1.0) for x in range(10)]

        for uid, score in results:
            if score >= 0.1:
                topic = topics[uid]
                console.print(f"[bright_green]{topic}[/bright_green]")

                # Print example question
                query = f"select id, question from txtai where similar('{topic}')"
                result = self.embeddings.search(query, 1)[0]
                console.print(f"{result['question']} ({result['id']})\n")
