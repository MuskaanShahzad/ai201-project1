# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:** My library-hold question is the one I expect to be hardest:
the corpus has two separate documents about the library
(`admin_library_holds.txt` and `study_library_hours.txt`), so retrieval could
plausibly pull the wrong one into the top results. The other four questions
each map to exactly one document with no similar competitor, so I'd expect
those to retrieve cleanly.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:** I checked `generate.py`: the model is told, as a system
instruction, to name the filename its answer came from. That's a simple
formatting rule, not something that requires judgment, so I expect it to hold
every time rather than just most of the time — if it fails, that's a real bug
in the prompt or the model ignoring instructions, not bad luck.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:** In Milestone 4 I measured the best distance for all 5 of
my test questions (worst case 0.358) against all 5 `OUT_OF_SCOPE` questions
(best case 0.825) — a gap of nearly 0.47 with nothing in it. Both groups landed
solidly on their own side with room to spare, so I'd expect the gate to catch
all 5 out-of-scope questions, not just 4. I'm keeping "4 of 5" rather than
raising it to "5 of 5" because the gap I measured came from only 5 questions
per side — a wider or oddly-worded out-of-scope question later could still
land closer to the boundary than these five did.

---

## 4. Something about your chunks

No chunk in my corpus is shorter than 100 characters or longer than 600.

**Why this target:** When I indexed `campus_life` in Milestone 1, my 88 chunks
came out averaging 317 characters, ranging from 178 to 549 — comfortably
inside 100–600. These are short, single-paragraph posts, so anything under
100 characters would be too fragmentary to hold a full fact, and anything
over 600 would suggest two unrelated posts got merged into one chunk.



---

## 5. Your choice

For at least 4 of my 5 test questions, the source the system names actually
contains the `expects` phrase — not just any source, the right one.

**Why this target:** This is different from criterion 2 — that one only checks
that a source gets named at all, not whether it's the correct one. I care
about this because a confidently wrong citation is worse than no citation.
Same reasoning as criterion 1: my library question is the one most likely to
cite the wrong document, since the corpus has two library-related files.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
