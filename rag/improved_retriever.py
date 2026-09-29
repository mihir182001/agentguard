from pathlib import Path
import re
import sys

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from sentence_transformers import SentenceTransformer

from rag.policy_retriever import PolicyRetriever
from rag.policy_metadata import POLICY_METADATA


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class ImprovedPolicyRetriever:
    """
    Retrieve policies using semantic similarity plus
    explicit keyword and phrase signals.
    """

    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)

        self.base_retriever = PolicyRetriever()
        self.base_retriever.load_policies()
        self.base_retriever.build_index()

    @staticmethod
    def normalize_text(text):
        """Normalize text for reliable phrase matching."""

        text = str(text).lower()

        text = re.sub(
            r"[^a-z0-9\s-]",
            " ",
            text
        )

        text = text.replace("-", " ")

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    def keyword_matches(self, query, policy_name):
        """Return policy keywords found in the query."""

        metadata = POLICY_METADATA[policy_name]

        query = self.normalize_text(query)

        matches = []

        for keyword in metadata["keywords"]:
            keyword = self.normalize_text(keyword)

            if keyword and keyword in query:
                matches.append(keyword)

        return matches

    def keyword_score(self, query, policy_name):
        """Score explicit keyword evidence."""

        matches = self.keyword_matches(
            query,
            policy_name
        )

        if not matches:
            return 0.0

        if len(matches) == 1:
            return 0.70

        if len(matches) == 2:
            return 0.85

        return 1.0

    def exact_match_score(self, query, policy_name):
        """Give extra weight to exact multi-word phrases."""

        matches = self.keyword_matches(
            query,
            policy_name
        )

        phrase_matches = [
            match
            for match in matches
            if len(match.split()) >= 2
        ]

        if not phrase_matches:
            return 0.0

        if len(phrase_matches) == 1:
            return 0.80

        return 1.0

    def rerank(self, query, results):
        """Combine semantic similarity with policy signals."""

        policy_scores = {}

        for result in results:

            policy_name = result["source"]
            semantic_score = result["score"]

            if (
                policy_name not in policy_scores
                or semantic_score
                > policy_scores[policy_name]["semantic"]
            ):
                policy_scores[policy_name] = {
                    "semantic": semantic_score,
                    "text": result.get("text", "")
                }

        reranked = []

        for policy_name, scores in policy_scores.items():

            keyword_score = self.keyword_score(
                query,
                policy_name
            )

            exact_score = self.exact_match_score(
                query,
                policy_name
            )

            final_score = (
                0.60 * scores["semantic"]
                + 0.20 * keyword_score
                + 0.20 * exact_score
            )

            matches = self.keyword_matches(
                query,
                policy_name
            )

            reranked.append(
                {
                    "source": policy_name,
                    "text": scores["text"],
                    "semantic_score": scores["semantic"],
                    "keyword_score": keyword_score,
                    "exact_match_score": exact_score,
                    "matched_keywords": matches,
                    "final_score": final_score,
                }
            )

        reranked.sort(
            key=lambda item: item["final_score"],
            reverse=True
        )

        return reranked

    def search(self, query, top_k=3):
        """Retrieve and rerank policy candidates."""

        candidates = self.base_retriever.search(
            query,
            top_k=20
        )

        reranked = self.rerank(
            query,
            candidates
        )

        return reranked[:top_k]


def main():
    retriever = ImprovedPolicyRetriever()

    test_queries = [
        "The customer does not recognise a transaction in Mumbai.",
        "The customer made a payment using a foreign currency.",
        "The customer was charged twice for the same payment.",
        "Several payments happened within a few seconds.",
        "The customer is requesting a refund.",
        "The customer has a large transaction.",
    ]

    print("\nImproved Policy Retriever")
    print("=" * 75)

    for query in test_queries:

        print(f"\nQuery: {query}")

        results = retriever.search(
            query,
            top_k=3
        )

        for rank, result in enumerate(
            results,
            start=1
        ):

            print(
                f"{rank}. {result['source']} "
                f"(final={result['final_score']:.3f}, "
                f"semantic={result['semantic_score']:.3f}, "
                f"keyword={result['keyword_score']:.3f}, "
                f"exact={result['exact_match_score']:.3f}, "
                f"matches={result['matched_keywords']})"
            )


if __name__ == "__main__":
    main()