"""Build the vector index for The Unofficial Guide.

Runs once, offline. Stages: ingest -> chunk -> embed + store.
Only stage 1 (ingest) is implemented so far.
"""

import re

import chromadb
from sentence_transformers import SentenceTransformer

from config import CHROMA_DIR, COLLECTION_NAME, DOCUMENTS_DIR, EMBEDDING_MODEL

# Reviews are separated by one or more blank lines. Each review is a header line
# followed by the student's comment, e.g.
#   Professor Jiang Li — CSCI201 — Quality 2/5, Difficulty 5/5:
#   Spends time going through concepts but expects too much from students...
REVIEW_SEPARATOR = re.compile(r"\n\s*\n")

HEADER = re.compile(
    r"^Professor\s+(?P<professor>.+?)\s*—\s*(?P<course>.+?)\s*—\s*"
    r"Quality\s*(?P<quality>\d)/5,\s*Difficulty\s*(?P<difficulty>\d)/5:?\s*$"
)


def ingest(documents_dir=DOCUMENTS_DIR):
    """Read every .txt file in documents_dir into one raw string per file.

    Returns a list of (source, text) tuples, sorted by filename. `source` is the
    filename without its extension (e.g. "Professor Jiang Li Reviews") and is
    carried through the pipeline so generated answers can cite their document.

    Raises FileNotFoundError if the directory is missing or holds no .txt files.
    """
    if not documents_dir.is_dir():
        raise FileNotFoundError(f"No such directory: {documents_dir.resolve()}")

    paths = sorted(documents_dir.glob("*.txt"))
    if not paths:
        raise FileNotFoundError(f"No .txt files found in {documents_dir.resolve()}")

    records = []
    for path in paths:
        # encoding is explicit because the reviews contain em dashes (U+2014) in
        # their header lines; relying on the platform default risks mojibake.
        text = path.read_text(encoding="utf-8").strip()

        if not text:
            print(f"  skipped (empty): {path.name}")
            continue

        records.append((path.stem, text))

    return records


def chunk_text(text):
    """Split one document's raw text into chunks, one chunk per review.

    Reviews are already self-contained units averaging ~300 characters, so the
    chunk boundary is the blank line between them rather than a fixed character
    count. Overlap is zero: consecutive reviews are written by different students
    about different semesters, so no idea spans a boundary for overlap to rescue.

    The header line stays attached to its comment. It is the only carrier of the
    professor name and course code, and without it a short chunk like
    "Hard but good" embeds to nothing and cannot be attributed.
    """
    chunks = []
    for block in REVIEW_SEPARATOR.split(text):
        block = block.strip()
        if block:
            chunks.append(block)
    return chunks


def parse_header(chunk):
    """Pull {professor, course, quality, difficulty} out of a chunk's header line.

    Returns an empty dict if the first line is not a well-formed header, so a
    malformed review still gets indexed on its text rather than being dropped.
    Quality and difficulty are ints so Chroma can filter on them numerically.
    """
    match = HEADER.match(chunk.splitlines()[0])
    if not match:
        return {}

    fields = match.groupdict()
    return {
        "professor": fields["professor"].strip(),
        "course": fields["course"].strip(),
        "quality": int(fields["quality"]),
        "difficulty": int(fields["difficulty"]),
    }


def build_chunks(records):
    """Turn ingest() output into flat chunk records ready for embedding.

    Each record is a dict with a stable `id`, the chunk `text`, and the metadata
    Chroma will store alongside it. IDs are derived from the source filename and
    the chunk's position, so they stay identical across runs.
    """
    built = []
    for source, text in records:
        for i, chunk in enumerate(chunk_text(text)):
            metadata = parse_header(chunk)
            if not metadata:
                print(f"  warning: unparsed header in {source} chunk {i}")

            built.append({"id": f"{source}::{i}", "text": chunk, "source": source, **metadata})
    return built


def embed_and_store(chunks):
    """Embed every chunk and write it to the persistent Chroma collection.

    The collection is dropped and rebuilt on each run so that edits and
    deletions in documents/ are reflected, rather than accumulating stale rows.

    Embeddings are computed here with sentence-transformers and passed to Chroma
    explicitly, instead of letting Chroma call its own default embedding model.
    That keeps one model responsible for both sides of the pipeline — the same
    model must embed the query at retrieval time or the vectors aren't comparable.
    """
    model = SentenceTransformer(EMBEDDING_MODEL)
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=False)

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    if COLLECTION_NAME in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION_NAME)

    # all-MiniLM-L6-v2 already L2-normalizes its output, so cosine and euclidean
    # produce the same ranking. Cosine is set explicitly anyway so the distances
    # Chroma returns are cosine distances, and 1 - distance is a real similarity.
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    collection.add(
        ids=[chunk["id"] for chunk in chunks],
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=[
            {k: v for k, v in chunk.items() if k not in ("id", "text")} for chunk in chunks
        ],
    )

    return collection, embeddings.shape[1]


if __name__ == "__main__":
    records = ingest()
    chunks = build_chunks(records)

    print(f"Ingested {len(records)} file(s) from {DOCUMENTS_DIR}/")
    print(f"Built {len(chunks)} chunks\n")

    print(f"{'source':38} {'chunks':>6} {'chars':>7}  avg")
    print("-" * 70)
    for source, text in records:
        sizes = [len(c) for c in chunk_text(text)]
        print(f"{source:38} {len(sizes):>6} {len(text):>7}  {sum(sizes) // len(sizes):>4}")
    print("-" * 70)

    sizes = [len(c["text"]) for c in chunks]
    print(f"{'total':38} {len(chunks):>6} {sum(sizes):>7}  {sum(sizes) // len(sizes):>4}")
    print(f"\nchunk chars: min {min(sizes)}, max {max(sizes)}")
    unparsed = [c for c in chunks if "professor" not in c]
    print(f"chunks missing metadata: {len(unparsed)}")

    print("\nfirst 5 chunks:")
    for chunk in chunks[:5]:
        print(f"\n  id:       {chunk['id']}")
        print(f"  metadata: {  {k: v for k, v in chunk.items() if k not in ('id', 'text')} }")
        print(f"  text:     {chunk['text']}")

    print(f"\nEmbedding with {EMBEDDING_MODEL} and writing to {CHROMA_DIR}/ ...")
    collection, dims = embed_and_store(chunks)
    print(f"Stored {collection.count()} chunks, {dims} dimensions each")
    print(f"Collection '{COLLECTION_NAME}' is ready — query it with retrieve.py")
