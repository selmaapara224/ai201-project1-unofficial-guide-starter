"""Stage 4 — retrieval. Runs per question, against the index build_index.py wrote.

Imported by the query interface; run directly to spot-check queries from the
command line:

    python retrieve.py "How often does Professor Andy assign labs?"
"""

import sys

import chromadb
from chromadb.errors import NotFoundError
from sentence_transformers import SentenceTransformer

from config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL, TOP_K

_model = None
_collection = None


def _load(reopen=False):
    """Open the model and collection once, then reuse them.

    Loading the model takes a couple of seconds, so a long-lived interface should
    not pay that cost on every question.

    `reopen=True` discards the cached collection handle and fetches a fresh one.
    A handle is bound to a specific collection UUID, so running build_index.py
    (which drops and recreates the collection) invalidates any handle a running
    app is holding. The model is never reloaded — it does not go stale.
    """
    global _model, _collection

    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)

    if _collection is None or reopen:
        if not CHROMA_DIR.exists():
            raise FileNotFoundError(
                f"No index at {CHROMA_DIR.resolve()}. Run: python build_index.py"
            )
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = client.get_collection(COLLECTION_NAME)

    return _model, _collection


def retrieve(question, top_k=TOP_K, course=None, min_quality=None):
    """Return the top_k chunks most similar to `question`, best match first.

    The question is embedded with the same model used at build time — vectors
    from different models are not comparable, so this must not drift.

    `course` and `min_quality` filter on metadata before the similarity search.
    Use them for questions the embeddings cannot answer on their own: course
    codes barely differentiate in vector space (CSCI135 and CSCI136 embed at
    0.977 similarity) and the model cannot compare ratings numerically.

    Each result is a dict with `text`, `similarity` (0-1, higher is closer),
    and the chunk's stored metadata.
    """
    model, collection = _load()

    conditions = []
    if course is not None:
        conditions.append({"course": course})
    if min_quality is not None:
        conditions.append({"quality": {"$gte": min_quality}})

    where = None
    if len(conditions) == 1:
        where = conditions[0]
    elif conditions:
        where = {"$and": conditions}

    query_embedding = model.encode([question]).tolist()

    try:
        response = collection.query(
            query_embeddings=query_embedding, n_results=top_k, where=where
        )
    except NotFoundError:
        # The index was rebuilt since this handle was opened. Reopen and retry
        # once, so a running interface survives `python build_index.py` instead
        # of failing every query until it is restarted.
        _, collection = _load(reopen=True)
        response = collection.query(
            query_embeddings=query_embedding, n_results=top_k, where=where
        )

    results = []
    for text, metadata, distance in zip(
        response["documents"][0], response["metadatas"][0], response["distances"][0]
    ):
        # The collection uses cosine space, so distance runs 0 (identical) to 2
        # (opposite) and similarity is its complement.
        results.append({"text": text, "similarity": 1 - distance, **metadata})

    return results


def list_courses():
    """Every course code present in the index, sorted. Populates the UI filter."""
    _, collection = _load()
    stored = collection.get(include=["metadatas"])
    return sorted({m["course"] for m in stored["metadatas"] if "course" in m})


def format_results(results):
    """Render results as text for the README's Retrieval Test Results section."""
    if not results:
        return "  (no chunks matched)"

    lines = []
    for i, r in enumerate(results, 1):
        header = r["text"].splitlines()[0]
        body = " ".join(r["text"].splitlines()[1:])
        lines.append(f"  {i}. [{r['similarity']:.3f}] {header}")
        lines.append(f"     {body[:150]}{'...' if len(body) > 150 else ''}")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        questions = [" ".join(sys.argv[1:])]
    else:
        questions = [
            "What professor should I take for CSCI135 if I want an A?",
            "How often does Professor Andy assign labs?",
            "Which professors don't teach the material and expect you to learn it alone?",
        ]

    for question in questions:
        print(f"\nQ: {question}")
        print(format_results(retrieve(question)))
