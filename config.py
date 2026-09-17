"""Settings shared by the ingestion path and the query path."""

from pathlib import Path

DOCUMENTS_DIR = Path("documents")
CHROMA_DIR = Path("chroma_db")
COLLECTION_NAME = "professor_reviews"

# 384-dimensional, 256-token input limit. Our longest chunk is 110 tokens, so
# nothing is ever truncated. See the Embedding Model section of README.md.
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Chunks average ~74 tokens, so 8 chunks is only ~600 tokens of context. The
# extra slots give aggregate questions ("who should I take for CSCI135?") a
# chance to see more than one professor.
TOP_K = 8

# Generation model, served by Groq. The planning diagram named
# llama-3.3-70b-versatile, but Groq no longer serves it — the only llama models
# still listed are the prompt-guard safety classifiers. Check what your account
# can reach with:  Groq().models.list()
GROQ_MODEL = "openai/gpt-oss-120b"

# Low but not zero. Grounded answers should follow the retrieved reviews rather
# than paraphrase creatively.
TEMPERATURE = 0.2
