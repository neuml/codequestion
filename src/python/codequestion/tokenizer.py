"""
Tokenizer module
"""

import re
import string


class Tokenizer:
    """
    Text tokenization methods
    """

    # Use standard python punctuation chars but allow tokens to end in # (to allow c#, f#) and + to allow (c++ g++)
    PUNCTUATION = string.punctuation.replace("#", "").replace("+", "")

    # fmt: off
    # English Stop Word List (Standard stop words used by Apache Lucene)
    STOP_WORDS = {"a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if", "in", "into", "is", "it",
                  "no", "not", "of", "on", "or", "such", "that", "the", "their", "then", "there", "these",
                  "they", "this", "to", "was", "will", "with"}
    # fmt: on

    @staticmethod
    def tokenize(text):
        """
        Tokenizes input text into a list of tokens. Filters tokens that match a specific pattern and removes stop words.

        Args:
            text: input text

        Returns:
            list of tokens
        """

        # Convert to all lowercase, split on whitespace, strip punctuation
        tokens = [token.strip(Tokenizer.PUNCTUATION) for token in text.lower().split()]

        # Filter tokens that are numbers or a valid string at least 2 characters long. Remove stop words.
        # Assume tokens already are uncased (all lowercase)
        return [
            token
            for token in tokens
            if (re.match(r"^[#*+\-.0-9:@_a-z]{2,}$", token) or token.isdigit())
            and token not in Tokenizer.STOP_WORDS
        ]
