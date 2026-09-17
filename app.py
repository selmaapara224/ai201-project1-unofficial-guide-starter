"""The Unofficial Guide — query interface.

    python app.py

Requires an index. Run `python build_index.py` first.
"""

import gradio as gr

from config import GROQ_MODEL, TOP_K
from generate import answer
from retrieve import list_courses

ANY_COURSE = "All courses"

QUALITY_FILTERS = {
    "Any rating": None,
    "Quality 3+": 3,
    "Quality 4+": 4,
    "Quality 5 only": 5,
}


def ask(question, course, quality_label, top_k):
    """Handle one submission. Returns (answer markdown, sources markdown)."""
    if not question or not question.strip():
        return "Ask a question to get started.", ""

    result = answer(
        question.strip(),
        top_k=int(top_k),
        course=None if course == ANY_COURSE else course,
        min_quality=QUALITY_FILTERS.get(quality_label),
    )

    if not result["results"]:
        return result["answer"], ""

    count = len(result["results"])
    lines = [
        f"**{count} review{'' if count == 1 else 's'} retrieved** "
        f"— model: `{result['model']}`\n"
    ]
    for i, r in enumerate(result["results"], 1):
        header, *body = r["text"].splitlines()
        lines.append(
            f"**{i}. {r['professor']} — {r['course']}** "
            f"· Quality {r['quality']}/5 · Difficulty {r['difficulty']}/5 "
            f"· similarity {r['similarity']:.3f}  \n"
            f"{' '.join(body)}\n"
        )

    return result["answer"], "\n".join(lines)


with gr.Blocks(title="The Unofficial Guide") as demo:
    gr.Markdown(
        "# The Unofficial Guide\n"
        "Ask about Computer Science professors at Howard University. Answers come "
        "only from student reviews collected from Rate My Professors — if the "
        "reviews don't cover your question, the system says so instead of guessing."
    )

    with gr.Row():
        question = gr.Textbox(
            label="Your question",
            placeholder="How often does Professor Andy assign labs?",
            lines=2,
            scale=4,
        )
        submit = gr.Button("Ask", variant="primary", scale=1)

    with gr.Accordion("Filters", open=False):
        gr.Markdown(
            "Course codes barely differentiate in vector space — CSCI135 and CSCI136 "
            "embed at 0.977 similarity — so filtering by course is more reliable than "
            "naming it in the question."
        )
        with gr.Row():
            course = gr.Dropdown(
                choices=[ANY_COURSE] + list_courses(),
                value=ANY_COURSE,
                label="Course",
            )
            quality = gr.Dropdown(
                choices=list(QUALITY_FILTERS),
                value="Any rating",
                label="Minimum quality rating",
            )
            top_k = gr.Slider(1, 20, value=TOP_K, step=1, label="Reviews to retrieve (top-k)")

    answer_box = gr.Markdown(label="Answer")

    with gr.Accordion("Retrieved reviews", open=False):
        sources_box = gr.Markdown()

    gr.Examples(
        examples=[
            ["What professor should I take for CSCI135 if I want an A?"],
            ["How often does Professor Andy assign labs?"],
            ["What do students say about Professor Jiang Li's grading?"],
            ["Which professors don't teach the material and expect you to learn it alone?"],
            ["Is Professor Blackstone good for someone new to coding?"],
        ],
        inputs=[question],
    )

    inputs = [question, course, quality, top_k]
    outputs = [answer_box, sources_box]
    submit.click(ask, inputs=inputs, outputs=outputs)
    question.submit(ask, inputs=inputs, outputs=outputs)


if __name__ == "__main__":
    print(f"Serving with {GROQ_MODEL}. Press Ctrl+C to stop.")
    demo.launch()
