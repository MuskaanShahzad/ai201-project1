# The Unofficial Guide

<!-- Replace this line with your name and which corpus you picked. -->

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->

## Chunking Strategy

**Chunk size:** 400 characters
**Overlap:** 60 characters

`campus_life` is 88 short posts, ~178–549 characters each, almost always
1–4 sentences (average 317). The starter's fixed 800-character window never
touched them — 88 documents in, 88 chunks out, because nothing reaches 800.
That's not wrong, but a few posts pack two separate facts into one file
(`admin_withdrawal_deadline.txt` covers both the drop deadline and the
withdrawal deadline; several course-review posts cover both the class format
and a separate piece of advice), and one fixed chunk hides that.

I replaced the fixed window with a sentence-aware splitter
(`chunker.py::split_documents`): it groups whole sentences up to 400
characters and never cuts mid-sentence, so a short single-fact post still
comes out as one chunk, but a longer or multi-fact post gets a real chance to
split at a sentence boundary. 60 characters of overlap (roughly one short
sentence) carries the last sentence of a chunk into the next one, so a split
chunk doesn't start cold.

Re-indexing with this changed 88 chunks into **100 chunks, averaging 282
characters (94–398)**. 12 documents split — mostly course reviews, where the
splitter cleanly separated the class-format/workload sentences from the
one-line "advice" sentence at the end. Worth noting: the two-fact deadline doc
I expected to split (`admin_withdrawal_deadline.txt`, 342 characters) actually
stayed as one chunk — it's under 400 characters even with both facts in it, so
there was nothing to split. I decided that's fine rather than lowering the
chunk size further: at 342 characters it's still well inside a reasonable
chunk size, and the two facts are closely related (both are deadlines on the
same topic), unlike the course reviews where the advice sentence is a genuinely
separate thought from the format description.

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** — source: `course_cs_210.txt#0` — produced by: `chunker.py::split_documents`

```
CS 210 Data Structures

I'm a junior and I've done this twice now. Format is lecture with weekly labs; slides go up after class, not before. Assessment: two midterms and a final, all drawn from lecture material rather than the textbook. Midterms are curved, the final is not. Expect 8 to 10 hours a week outside class.
```

**Chunk 2** — source: `course_cs_210.txt#1` — produced by: `chunker.py::split_documents`

```
Expect 8 to 10 hours a week outside class. The one piece of advice: do the labs even though they're only 10% — the exams reuse the lab problems.
```

**Chunk 3** — source: `housing_morrow_house.txt#0` — produced by: `chunker.py::split_documents`

```
Morrow House — what it's actually like

Just finished a year in this building. Built 1954, partially renovated 2008. Rooms are singles and doubles, hall bathrooms. The good: cheapest housing tier by about $900 a year, and the singles are real singles. The bad: known damp problem on the ground floor; two rooms were taken offline in 2024. Laundry costs $1.50 wash, $1.25 dry, coin or card.
```

**Chunk 4** — source: `admin_withdrawal_deadline.txt#0` — produced by: `chunker.py::split_documents`

```
On the withdrawal deadline

Withdrawal is a different thing from dropping and has a different date. Dropping ends at week six. Withdrawal runs to week ten, requires an adviser signature, and puts a W on the transcript that doesn't affect GPA. The two dates appear on different pages of the registrar's site and this catches people every year.
```

**Chunk 5** — source: `dining_the_ridgeway_cafe_followup.txt#0` — produced by: `chunker.py::split_documents`

```
Re: The Ridgeway Café

Adding to what people have said about The Ridgeway Café. The wait figure of 10 to 15 minutes at 12:30 matches what I've seen. If you're trying to eat between classes, go before 11:45 and it's a different building entirely. Also worth saying: seating is tight; about 40 seats for a building of 900. Nobody tells you this at orientation.
```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:** How long does your student account, including campus wifi access, stay active after you graduate?

**Answer:**

```
Your student account stays active for six months after you graduate.

Source: admin_wifi_and_accounts.txt
```

**Top-k:** 5 (kept the starter's default)

I ran `python app.py retrieve "..."` on 3 of my 5 questions before touching
anything. Every one of them retrieved the correct chunk in position #1, with
a large margin to position #2 (e.g. 0.119 vs. 0.563 for the library question),
so there was no case where the right answer was getting buried further down
and needed a bigger `top_k` to surface. I kept it at 5 rather than lowering it,
since the grounding instruction already ignores irrelevant chunks in the
retrieved set (see below) — a smaller `top_k` would save nothing and risks
losing the right chunk on a harder question.

**My relevance cutoff:** 0.6 (kept the starter's default)

I ran retrieval on all 5 of my test questions and the 5 `OUT_OF_SCOPE`
questions and recorded the best (lowest) distance for each. The in-corpus
questions topped out at 0.358; the out-of-scope questions bottomed out at
0.825. That's a gap of nearly 0.47 with nothing in it, so almost any cutoff
between 0.36 and 0.82 would work — 0.6 sits comfortably in the middle of that
gap, so I kept it rather than moving it for the sake of moving it.

I also checked `GROUNDING_INSTRUCTION` in `generate.py` with `--show-prompt`:
even when 4 of the 5 retrieved chunks were irrelevant noise (course workload
numbers, a shuttle schedule), the model still picked out only the correct
chunk and cited it — so I didn't tighten the instruction further.

| Question | In corpus? | Best distance |
|---|---|---|
| How long does it take for a hold on a checked-out library book to become available? | Yes | 0.119 |
| By what week must you withdraw from a course, as opposed to just dropping it? | Yes | 0.358 |
| How do I file a grade appeal, and how many days do I have after my grade is posted? | Yes | 0.218 |
| How much does an official transcript cost, and how long does it take to arrive electronically? | Yes | 0.158 |
| How long does your student account, including campus wifi access, stay active after you graduate? | Yes | 0.245 |
| What is the capital of Mongolia? | No | 0.825 |
| How do I change the oil in a diesel engine? | No | 0.934 |
| Who won the 1994 World Cup? | No | 0.886 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.844 |
| How do I write a for loop in Rust? | No | 0.891 |

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.**

**2.**

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
