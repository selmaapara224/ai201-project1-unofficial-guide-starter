# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

The domain will be student reviews of Computer Science professors at Howard University. Many students hear about different professors that other students love or ones they hated, but they may not always know the specifics of what was endured in those professor's classes. For some professors with horrible reviews, their classes are unavoidable, and a student may be able to prepare in some way, even if it's just mentally. For other professors with great reviews, a student may be advised to choose that one over another. It is helpful to have this information quickly accessible while actively registering for classes, instead of having to comb through lots of reviews individually.

---

## Documents


| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 |RateMyProf|Reviews on Prof Jeremy Blackstone| https://www.ratemyprofessors.com/professor/2640220 |
| 2 |LRateMyProf |LReviews on Prof Anietie Andy |https://www.ratemyprofessors.com/professor/3048123 |
| 3 |RateMyProf |Reviews on Prof. Linwei Niu |https://www.ratemyprofessors.com/professor/2719629 |
| 4 |RateMyProf |Reviews on Prof. Jiang Li |https://www.ratemyprofessors.com/professor/2323879 |
| 5 |RateMyProf |Reviews on Prof. Andre Campbell |https://www.ratemyprofessors.com/professor/2837871 |
| 6 |RateMyProf |Reviews on Prof. Todd Shurn |https://www.ratemyprofessors.com/professor/2208362 |
| 7 |RateMyProf |Reviews on Prof. Legand Burge |https://www.ratemyprofessors.com/professor/286894 |
| 8 |RateMyProf |Reviews on Prof. Mikayla Orange| https://www.ratemyprofessors.com/professor/3045892|
| 9 |RateMyProf |Reviews on Prof. Anamika Rupa|https://www.ratemyprofessors.com/professor/2976470 |
| 10 |RateMyProf |Reviews on Prof. Ashish Adhikari |https://www.ratemyprofessors.com/professor/2751478 |

---

## Chunking Strategy



Chunk size: Instead of by characters, the chunks will be split by empty space, making every review its own chunk.

Overlap: There will be no overlap.

Reasoning: Each review includes the Professor's name, the course the student had them for, and different specific information each student stated. Chunking by review allows for the requested information to always be attached to the specific Professor the information is being requested about. For example, if a query is about the homework load for Professor Blackstone, the user would not want a response that relates to a different professor that also has a review about. homework. 

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

Embedding model: The embedding model I am using is all-MiniLM-L6-v2. It has a 256-token window, and the maximum amount of tokens out of all of my chunks is 110, so my documents fit within its limitation. 

Top-k: I am using 8, because of the nature of my chunks. My first test query asks about CSCI135 specifically, but also mentions a grade. There is a possibility that a chunk about a professor that teaches a different course will be retrieved, due to other parts of the chunk making it relate closely to those chunks that contain information about CSCI135. Having a higher top-k, 8, allows for the LLM to be sent more chunks, having a higher probability of generating a more-fit answer, instead of leaving out chunks that may have had the specific answer needed in them.

Production tradeoff reflection: If I were to deploy this project for real users, I would still not use a different embedding model, simply because of the size of the reviews. More token allowance would not be needed, because the reviews would never go over the current 256-token window of all-MiniLM-L6-v2, due to RateMyProfessor having a character limit on their website in the first place.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 |What Professor should I take for CSCI135 if I want an A? |Professor Jeremy Blackstone |
| 2 |How often does Professor Andy give lab assignments? |Weekly|
| 3 |What do students say about Professor Jiang Li's lecturing style? |fast,boring |
| 4 |Which professors don't teach the material and expect you to learn it alone? |Professor Jiang Li, Professor Linwei Niu |
| 5 |Who is a good professor for CSCI 999? |No information to answer |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Anomalies in the reviews can cause a challenge. One student gave a raving review about Professor Jiang Li, while the rest of the reviews are horrible. There is also one bad review for Professor Jeremy Blackstone, while the rest are raving. This is less of an issue for the scope of this project though, but would definitley be an issue for a student seeking information if the project was deployed.

2. Colloquialisms, slang, and abbreviations within reviews can cause an issue. A query can mention "homework" and the most fitting review could say "hw" and not be retrieved.

---

## Architecture

/documents/App of AI Project 1 Pipeline.jpg



## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->
Milestone 1 — Collecting Documents: I asked Claude the best way to format my documents for the information I wanted to retreive.

Milestone 2 — Writing Spec: I asked Claude to explain certain concepts that I needed a deeper understanding of to properly write my spec.

Milestone 3 — Ingestion and chunking: I will ask Claude to review the format of my documents, and ask it to implement ingestion. I will then give Claude my Chunking Strategy and ask it to implement chunk_text(), ensuring it also saves the metadata I need saved.

Milestone 4 — Embedding and retrieval: I will ask claude to implement my embedding and retrieval ensuring to prioritize maintaining the important metadata, ensuring retreival errors don't affect generation too much.

Milestone 5 — Generation and interface: I will ask Claude to reccomend ways to ensure my system prompt results in the generation of grounded answers, as it relates to my particular domain. I will also ask it to generate the code for this section.
