"""
Policy retrieval tool.

Connects the agent to the improved hybrid
policy retrieval system.
"""

from pathlib import Path
import sys


# Add the project root to Python's import path.
PROJECT_ROOT = (
    Path(__file__).resolve().parents[2]
)

sys.path.append(
    str(PROJECT_ROOT)
)


from rag.improved_retriever import (
    ImprovedPolicyRetriever
)


class PolicyTool:
    """Retrieve relevant enterprise policies."""

    def __init__(self):

        self.retriever = (
            ImprovedPolicyRetriever()
        )

    def search_policy(
        self,
        query,
        top_k=3
    ):
        """
        Retrieve the most relevant policies.
        """

        results = self.retriever.search(
            query,
            top_k=top_k
        )

        return results


if __name__ == "__main__":

    tool = PolicyTool()

    results = tool.search_policy(
        "The customer does not recognise "
        "a transaction."
    )

    print("\nPolicy Tool Test")
    print("=" * 60)

    for rank, result in enumerate(
        results,
        start=1
    ):

        print(
            f"{rank}. "
            f"{result['source']} "
            f"(score={result['final_score']:.3f})"
        )