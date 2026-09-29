from pathlib import Path
import json

import faiss
from sentence_transformers import SentenceTransformer


POLICY_DIR = Path("data/policies")
INDEX_DIR = Path("rag/index")

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class PolicyRetriever:
    """Retrieve relevant sections from the policy knowledge base."""

    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self.chunks = []
        self.index = None

    def load_policies(self):
        """Read policy files and split them into useful text chunks."""

        for policy_file in sorted(POLICY_DIR.glob("*.md")):
            text = policy_file.read_text(encoding="utf-8")

            sections = text.split("\n## ")

            for section in sections:
                section = section.strip()

                if not section:
                    continue

                # Add the heading back after splitting on "## ".
                if not section.startswith("#"):
                    section = "## " + section

                self.chunks.append(
                    {
                        "source": policy_file.name,
                        "text": section,
                    }
                )

        print(f"Loaded {len(self.chunks)} policy chunks.")

    def build_index(self):
        """Create a FAISS index from policy embeddings."""

        texts = [chunk["text"] for chunk in self.chunks]

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        dimension = embeddings.shape[1]

        # Inner product on normalized vectors is cosine similarity.
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)

        INDEX_DIR.mkdir(parents=True, exist_ok=True)

        faiss.write_index(
            self.index,
            str(INDEX_DIR / "policy.index"),
        )

        with open(
            INDEX_DIR / "metadata.json",
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                self.chunks,
                file,
                indent=2,
                ensure_ascii=False,
            )

        print("Policy index created successfully.")

    def search(self, query, top_k=3):
        """Return the most relevant policy sections."""

        if self.index is None:
            raise RuntimeError(
                "Index has not been built. Run build_index() first."
            )

        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
        )

        scores, indices = self.index.search(
            query_embedding,
            top_k,
        )

        results = []

        for score, index in zip(scores[0], indices[0]):
            if index == -1:
                continue

            result = self.chunks[index].copy()
            result["score"] = float(score)

            results.append(result)

        return results


def main():
    retriever = PolicyRetriever()

    retriever.load_policies()
    retriever.build_index()

    test_queries = [
        "The customer was charged twice for the same payment.",
        "A customer sees a failed payment followed by a successful retry.",
        "A customer has several transactions within a few seconds.",
    ]

    print("\nTesting policy retrieval...")
    print("=" * 70)

    for query in test_queries:
        print(f"\nQuery: {query}")

        results = retriever.search(query, top_k=3)

        for rank, result in enumerate(results, start=1):
            print(
                f"\n{rank}. {result['source']} "
                f"(score={result['score']:.3f})"
            )
            print(result["text"][:300])


if __name__ == "__main__":
    main()