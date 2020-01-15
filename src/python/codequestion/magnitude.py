"""
Wrapper to load pymagnitude without unused dependencies
"""
#pylint: skip-file

import sys

class AnnoyIndex:
    """
    Empty implementation
    """

class ElmoEmbedder:
    """
    Empty implementation
    """

try:
    import pymagnitude
except ImportError:
    try:
        from annoy import AnnoyIndex
    except ImportError:
        sys.modules["annoy"] = sys.modules[__name__]

    try:
        import torch
    except ImportError:
        sys.modules["pymagnitude.third_party.allennlp.commands.elmo"] = sys.modules[__name__]

    import pymagnitude

# Point this module to pymagnitude
sys.modules[__name__] = sys.modules["pymagnitude"]
