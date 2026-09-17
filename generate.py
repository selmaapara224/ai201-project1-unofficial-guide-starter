"""Stage 5 — grounded generation. Runs per question, after retrieval.

    python generate.py "How often does Professor Andy assign labs?"
"""

import os
import sys

from dotenv import load_dotenv
from groq import Groq

from config import GROQ_MODEL, TEMPERATURE, TOP_K
from retrieve import retrieve

load_dotenv()

# The retrieved set is deliberately wider than most questions need (TOP_K = 8),
# so the first instruction is to discard what does not apply. Without it the
# model tries to use all eight reviews and starts attributing one professor's
# policies to another.
SYSTEM_PROMPT = """You answer questions about Computer Science professors at Howard \
University using only student reviews retrieved from Rate My Professors.

Rules:
1. Use ONLY the reviews provided below. Never add facts from your own knowledge \
about these professors, their courses, or the university.
2. Ignore reviews that do not address the question. The reviews are selected by \
similarity search, so several are usually irrelevant. Do not force them in.
3. If the reviews do not contain the answer, say so plainly: "The reviews I have \
don't cover that." Then state what they do cover, if anything is close. Do not guess.
4. Cite every claim with the professor's name and course in plain parentheses, \
like (Blackstone, CSCI135). A claim without a citation is not allowed. Use no \
other citation format — no bracketed markers, no review numbers, no footnotes, \
no line references.
5. Reviews often disagree about the same professor. When they do, report the \
disagreement instead of averaging it away or picking a side — say how many \
reviews take each position.
6. One review is one student's opinion. Do not present a single review as a \
general fact; write "one student said" rather than "students say".
7. Never invent ratings, averages, or counts. Only use the Quality and Difficulty \
numbers shown in the reviews.

Be concise. Two to four sentences is usually enough."""


_client = None


def _get_client():
    """Create the Groq client once, and fail with a useful message if unconfigured."""
    global _client

    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key or api_key.startswith("<"):
            raise RuntimeError(
                "GROQ_API_KEY is not set. Copy .env.example to .env and add your key "
                "from https://console.groq.com"
            )
        _client = Groq(api_key=api_key)

    return _client


def format_context(results):
    """Render retrieved chunks as a numbered block for the prompt.

    Each review keeps its header line, so the professor, course, and ratings the
    model is told to cite are visible in the text it reads.
    """
    blocks = []
    for i, r in enumerate(results, 1):
        blocks.append(f"[Review {i}] (source: {r['source']})\n{r['text']}")
    return "\n\n".join(blocks)


def answer(question, top_k=TOP_K, course=None, min_quality=None):
    """Retrieve, then generate a grounded answer.

    Returns a dict with the `answer` text, the `results` it was based on, and the
    `model` used, so the caller can show its sources.
    """
    results = retrieve(question, top_k=top_k, course=course, min_quality=min_quality)

    if not results:
        return {
            "answer": "No reviews matched that filter, so I have nothing to answer from.",
            "results": [],
            "model": GROQ_MODEL,
        }

    user_message = f"Reviews:\n\n{format_context(results)}\n\nQuestion: {question}"

    response = _get_client().chat.completions.create(
        model=GROQ_MODEL,
        temperature=TEMPERATURE,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    return {
        "answer": response.choices[0].message.content.strip(),
        "results": results,
        "model": GROQ_MODEL,
    }


if __name__ == "__main__":
    if len(sys.argv) > 1:
        questions = [" ".join(sys.argv[1:])]
    else:
        questions = [
            "What professor should I take for CSCI135 if I want an A?",
            "How often does Professor Andy assign labs?",
            "What do students say about Professor Jiang Li's grading?",
            "Which professor teaches CSCI999?",
        ]

    for question in questions:
        result = answer(question)
        print(f"\nQ: {question}")
        print(f"A: {result['answer']}")
        print(f"   sources: {', '.join(sorted({r['source'] for r in result['results']}))}")
