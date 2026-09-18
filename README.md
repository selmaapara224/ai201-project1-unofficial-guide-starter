# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---
---

## Environment Setup Note

This project runs on an Intel (x86_64) Mac, which constrains the dependency
versions in `requirements.txt`. The stock file did not install; three pins were
added to fix it.

**The failure.** `pip install -r requirements.txt` aborted with:

    ERROR: Could not find a version that satisfies the requirement torch>=1.11.0
           (from sentence-transformers) (from versions: none)

`from versions: none` means no compatible wheel exists at all — this is a
platform gap, not a version conflict. `sentence-transformers` requires PyTorch,
and PyTorch ended macOS x86_64 support at **torch 2.2.2**, which shipped wheels
only for Python 3.8–3.12. Everything from torch 2.3.0 onward is arm64-only. The
environment was on Python 3.13, so no installable torch existed.

**The fix, and what it cascaded into.**

1. Installed Python 3.12.10 (the last 3.12 with an official macOS installer) and
   rebuilt the virtual environment on it.
2. Pinned `torch==2.2.2`, the final Intel-Mac release.
3. Pinned `numpy<2`. torch 2.2.2 was compiled against the NumPy 1.x C ABI, so
   NumPy 2 caused `RuntimeError: Numpy is not available` at embedding time.
4. Pinned `scipy<1.18`. scipy 1.18 requires `numpy>=2.0.0`, so pinning NumPy
   alone left the dependency set inconsistent.

**Resulting versions:** Python 3.12.10, torch 2.2.2, numpy 1.26.4,
scipy 1.17.1, transformers 4.57.6, chromadb 1.5.9, sentence-transformers 3.4.1.

Verified with a clean-room install from the pinned `requirements.txt`:
`pip check` reports no broken requirements, and `all-MiniLM-L6-v2` produces
384-dimensional embeddings that store and query correctly through Chroma.

**A second near-miss: the query interface.** Milestone 5 needs Gradio, and the
stock `requirements.txt` suggested `gradio>=6.9.0`. That resolves to gradio
6.27.0, which requires `huggingface_hub>=1.16` — a major-version jump from the
installed 0.36.2. `sentence-transformers` 3.4.1 declares no upper bound on the
hub, so pip would have performed that upgrade without complaint, moving a
pinned, working package across an API boundary it was never tested against.
Nothing would have failed at install time; it would have failed at embedding
time, which is the same late-surfacing pattern as the NumPy 2 ABI problem above.

`pip install --dry-run` exposed the planned upgrade before anything touched the
environment. Constraining the hub rather than accepting the newest Gradio:

    pip install "gradio" "huggingface_hub<1.0" "numpy<2"

resolves to **gradio 6.17.3**, which leaves torch, numpy, transformers,
sentence-transformers, and huggingface_hub untouched, adding only pandas 3.0.5
and the FastAPI/Starlette server stack. Both constraints are pinned in
`requirements.txt` so a fresh install reproduces the working set instead of
re-triggering the conflict. Installing a bare `gradio` will undo this.

**Re-verified after installing:** `pip check` reports no broken requirements;
numpy 1.26.4, torch 2.2.2, and huggingface_hub 0.36.2 are unchanged;
`retrieve.py` still returns scored matches from Chroma; and `python app.py`
serves HTTP 200 on port 7860.

**Portability.** These pins remain valid on Apple Silicon, since torch 2.2.2
also ships arm64 wheels. The binding constraint for any machine is Python ≤ 3.12.

---

## Domain

The domain will be student reviews of Computer Science professors at Howard University. Many students hear about different professors that other students love or ones they hated, but they may not always know the specifics of what was endured in those professor's classes. For some professors with horrible reviews, their classes are unavoidable, and a student may be able to prepare in some way, even if it's just mentally. For other professors with great reviews, a student may be advised to choose that one over another. It is helpful to have this information quickly accessible while actively registering for classes, instead of having to comb through lots of reviews individually.


---

## Document Sources

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 |RateMyProf|Reviews on Prof Jeremy Blackstone| /Users/selmaapara/CodePath/ai201-project1-unofficial-guide-starter/documents/Professor Jeremy Blackstone.txt |
| 2 |LRateMyProf |LReviews on Prof Anietie Andy |/Users/selmaapara/CodePath/ai201-project1-unofficial-guide-starter/documents/Professor Anietie Andy.txt |
| 3 |RateMyProf |Reviews on Prof. Linwei Niu |/Users/selmaapara/CodePath/ai201-project1-unofficial-guide-starter/documents/Professor Linwei Niu.txt |
| 4 |RateMyProf |Reviews on Prof. Jiang Li |/Users/selmaapara/CodePath/ai201-project1-unofficial-guide-starter/documents/Professor Jiang Li.txt |
| 5 |RateMyProf |Reviews on Prof. Andre Campbell |/Users/selmaapara/CodePath/ai201-project1-unofficial-guide-starter/documents/Professor Andre Campbell.txt |
| 6 |RateMyProf |Reviews on Prof. Todd Shurn |/Users/selmaapara/CodePath/ai201-project1-unofficial-guide-starter/documents/Professor Todd Shurn.txt |
| 7 |RateMyProf |Reviews on Prof. Legand Burge |/Users/selmaapara/CodePath/ai201-project1-unofficial-guide-starter/documents/Professor Legand Burge.txt |
| 8 |RateMyProf |Reviews on Prof. Mikayla Orange| /Users/selmaapara/CodePath/ai201-project1-unofficial-guide-starter/documents/Professor Mikayla Orange|
| 9 |RateMyProf |Reviews on Prof. Anamika Rupa|'/Users/selmaapara/CodePath/ai201-project1-unofficial-guide-starter/documents/Professor Anamika Rupa.txt' |
| 10 |RateMyProf |Reviews on Prof. Ashish Adhikari |/Users/selmaapara/CodePath/ai201-project1-unofficial-guide-starter/documents/Professor Ashish Adhikari.txt |

---

## Chunking Strategy


Chunk size: Instead of by characters, the chunks will be split by empty space, making every review its own chunk.

Overlap: There will be no overlap.

Reasoning: Each review includes the Professor's name, the course the student had them for, and different specific information each student stated. Chunking by review allows for the requested information to always be attached to the specific Professor the information is being requested about. For example, if a query is about the homework load for Professor Blackstone, the user would not want a response that relates to a different professor that also has a review about. homework. 


Final chunk count: 63

---

## Sample Chunks

<!-- Paste 5 representative chunks from your document collection after running your ingestion pipeline.
     For each chunk, note which source document it came from.
     These must be actual text — not screenshots. -->

| # | Source document | Chunk text |
|---|----------------|------------|
| 1 |Professor Anamika Rupa Reviews |Professor Anamika Rupa — CSCI120 — Quality 2/5, Difficulty 1/5:
Reads off of slides, doesn't teach much. Quizzes/exams replicate slides tho, so just memorize them if needed. Lectures are short but boring. |
| 2 |Professor Anamika Rupa Reviews|Professor Anamika Rupa — CSCI120 — Quality 1/5, Difficulty 5/5: Not a good professor, doesn't know what she is doing! Too much homework for 2 credit class and its honestly not even that good. Take another professor if possible |
| 3 |Professor Anamika Rupa Reviews |Professor Anamika Rupa — CSCI453 — Quality 1/5, Difficulty 5/5:
This professor is bad with communication, she doesn't really teach in class! Had so many problems this semester and tried to talk to her about it but no response! Uses chatgpt, slides and so much work load! Doesn't understand simple questions. |
| 4 |Professor Anamika Rupa Reviews |Professor Anamika Rupa — CSCI453 — Quality 1/5, Difficulty 5/5:
This professor is the worst i have taken so far, idk why she is even a PhD candidate ! Like using chat in class to explain stuff! So many slides and she doesn't even know what she teaching, so much codio and quizzes on top of that midterm and final! She is the worst |
| 5 |Professor Anamika Rupa Reviews |Professor Anamika Rupa — CSCI120 — Quality 2/5, Difficulty 2/5:
She was new when I had her, and for the most part it seemed like she didn't know what she was doing. It was an easy class, but I can't really say that I learned anything from her. She was very lenient with her grading though. Also, for a class called exploring computer science, we didn't really learn much about computer science. |

---

## Embedding Model

Embedding model: The embedding model I am using is all-MiniLM-L6-v2. It has a 256-token window, and the maximum amount of tokens out of all of my chunks is 110, so my documents fit within its limitation. 

Top-k: I am using 8, because of the nature of my chunks. My first test query asks about CSCI135 specifically, but also mentions a grade. There is a possibility that a chunk about a professor that teaches a different course will be retrieved, due to other parts of the chunk making it relate closely to those chunks that contain information about CSCI135. Having a higher top-k, 8, allows for the LLM to be sent more chunks, having a higher probability of generating a more-fit answer, instead of leaving out chunks that may have had the specific answer needed in them.

Production tradeoff reflection: If I were to deploy this project for real users, I would still not use a different embedding model, simply because of the size of the reviews. More token allowance would not be needed, because the reviews would never go over the current 256-token window of all-MiniLM-L6-v2, due to RateMyProfessor having a character limit on their website in the first place.
---

## Retrieval Test Results


**Query 1:**
What professor should I take for CSCI135 if I want an A?

Top returned chunks:
-[0.582] Professor Jiang Li — CSCI450 — Quality 1/5, Difficulty 5/5:
     He is most likely going to be the only professor that you can take but if there are other options take them. He is the most inconsiderate professor yo...
-[0.573] Professor Jeremy Blackstone — CSCI135 — Quality 5/5, Difficulty 1/5:
     Take this class if you want an A. Professor Blackstone is a great teacher especially if you're new to coding. Records his lectures and is very lenient...
-[0.563] Professor Jeremy Blackstone — CSCI135 — Quality 5/5, Difficulty 4/5:
     One of the best teachers I've had in my life, and if he taught Computer Science II (CSCSI136) I definitely would want to have him as my professor agai...

Relevance explanation: The two relevant chunks are the second and third ones. The first chunk refers to a professor that does not teach CSCI135 and has horrible reviews. Even though his reviews say nothing about earning an A, the data is skewed due to him having the most reviews out of all of the professors. This is why the metadata that includes the course number is important, so the LLM can ignore that first, unrelated chunk.

---

**Query 2:**
How often does Professor Andy assign labs?

Top returned chunks:
-[0.560] Professor Anietie Andy — CSCI136 — Quality 5/5, Difficulty 2/5:
     Andy is an excellent professor. His lectures and tests are clear and connected. Weekly lab and sometimes homework, but it's all from the lecture. He e...
-[0.426] Professor Jeremy Blackstone — CSCI135 — Quality 5/5, Difficulty 3/5:
     10/10 would recommend! He's super understanding about late work and his office hours are really flexible. He really wants his students to do well and ...
-[0.389] Professor Jiang Li — CSCI201 — Quality 3/5, Difficulty 5/5:
     this class is hard and the homework/projects require a lot of time. dr li's lectures are boring but he's helpful especially if you go to office hours....

Relevance explanation: Chunks for three different professors returned, but the one with the most relevance was returned first. This is a very decent retreival.

---

**Query 3:**
Which professors don't teach the material and expect you to learn it alone?
Top returned chunks:
-[0.532] Professor Jiang Li — CSCI450 — Quality 1/5, Difficulty 5/5:
     He is most likely going to be the only professor that you can take but if there are other options take them. He is the most inconsiderate professor yo...
-[0.495] Professor Linwei Niu — CSCI201 — Quality 3/5, Difficulty 3/5:
     He doesn't really teach, just reads off of Google Slides for every single one of his classes. Extremely monotone, which will bore you after listening ...
-[0.472] Professor Jiang Li — CSCI201 — Quality 1/5, Difficulty 5/5:
     One of the worst professors I've ever had. He doesn't teach/explain anything in depth, when asked to clarify he won't b/c we should just get it and it...

Relevance explanation: These retreivals are perfectly relevant. They reflect how a student in the department would answer if asked the same question in person. However, the 5th chunk that was retreived refers to a professor who is desrcibed as 'Excellent at explaining", which is the opposite of what's being asked. This is not surpising, though, because the word "explaining" is directly in the chunk, which is related to "teach" in the query.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction: 

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

How source attribution is surfaced in the response: See rule 4.

---

## Example Responses

<!-- Provide at least 2 grounded responses (query + response + source attribution)
     and 1 out-of-scope query showing your system's refusal.
     All entries must be text — not screenshots. -->

**Grounded response 1**

Query:

Response:

Source attribution:

---

**Grounded response 2**

Query:

Response:

Source attribution:

---

**Out-of-scope query**

Query: Who won the world series?

System response (refusal): The reviews I have don’t cover that. They only discuss students’ opinions of Howard University computer‑science professors, their teaching styles, course difficulty, and grading.

---

## Query Interface

<!-- Describe your query interface: what are the input fields, what does the output look like?
     Then provide a complete sample interaction transcript showing a real exchange. -->

**Input fields:**

**Output format:**

---

**Sample Interaction Transcript**

<!-- Show a complete query → response exchange as it actually appears in your interface.
     Must be text — not a screenshot. -->

> **User:** 

> **System:** 

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI: I gave Claude my pipeline diagram and chunking strategy.
- *What it produced: It produced code to implement chunking, that included attaching metadata to my chunks.
- *What I changed or overrode: It added code to print chunks for testing, but it was only 2 chunks and only the first 90 characters of each. I edited the code to print 5 chunks and to print the entire chunk instead of just a portion.
**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*


Loom demo Video:

<div style="position: relative; padding-bottom: 62.5%; height: 0;"><iframe src="https://www.loom.com/embed/f4f9bf7ef0214c01895cca078986fa50" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe></div>


<div style="position: relative; padding-bottom: 62.5%; height: 0;"><iframe src="https://www.loom.com/embed/321aaafe53814a5bb598fe7e470400b9" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe></div>