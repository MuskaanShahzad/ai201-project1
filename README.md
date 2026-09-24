# The Unofficial Guide

Muskaan Shahzad — corpus: `campus_life`

# Unit 1

## What This Does

This is a question-answering system for `campus_life` — 88 short, real-student
posts about the parts of college nobody puts in the official handbook: drop
and withdrawal deadlines, library holds, transcript costs, wifi/account
expiration, grade appeals, dining hall wait times, dorm reviews, and course
workload. Ask it something like "how much does an official transcript cost?"
or "what's Morrow House actually like?" and it retrieves the specific post(s)
that cover it, answers using only that text, and names the file it came from.
If you ask something the corpus doesn't cover — like a question about a
different school, or something totally unrelated — it says so instead of
guessing.

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

**1.** For criteria 4 and 5, I asked Claude to help me turn my ideas into
properly worded acceptance criteria. It asked me what would make a chunk feel
wrong, and what would bug me most if the system got wrong — I answered in a
few words each ("shouldn't cut mid-sentence," "wrong source cited is worse
than no source"), and Claude helped shape those into numbered criteria with
real targets (100–600 characters; 4 of 5 correct source citations). I picked
the actual numbers, and Claude ran the criteria self-check against all five
to confirm each one was testable from the sentence alone.

**2.** For Milestone 3, I asked Claude to write the chunking function. It
guessed `admin_withdrawal_deadline.txt` (two deadlines in one file) would
split into two chunks and built the size/overlap numbers around that. When we
ran it, that file didn't split — it fit in one 343-character chunk anyway.
Instead, 12 course-review files split, separating the class info from a
one-line piece of advice. I corrected the README to say what actually
happened instead of the original guess.



# Unit 2

## Run Log

Evidence file: [`results/run_2026-09-23_2009_before.md`](results/run_2026-09-23_2009_before.md)
(produced by `run_eval.py --label before`, 3 real runs per question, caching off).

Criteria 1, 3, and 4 are measured against things that don't change between
runs — which chunks retrieval returns, and how long those chunks are — so the
same number legitimately appears in all three run columns. Criteria 2 and 5
depend on what the model writes, so those are the ones that could actually
move.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. No chunk shorter than 100 or longer than 600 characters | 100–600 | 94–398 | 94–398 | 94–398 | MISSED |
| 5. Named source actually contains the `expects` phrase | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |

### Real output, per criterion

**Criterion 1** — produced by `store.py::search`. For every one of the 5
questions, one of the 5 retrieved chunks contains the exact `expects` phrase.
Example, for "How long does it take for a hold on a checked-out library book
to become available?" (`expects: "two to three days"`):

```
"On the library holds

You can place a hold on a checked-out book and it usually arrives in two to
three days. What isn't advertised: the interlibrary system covers eleven
other institutions and requests through it take about a week but almost
never fail."
```
— from `admin_library_holds.txt`, distance 0.1187 (well under the 0.6 gate).

**Criterion 2** — produced by `generate.py::answer_from_chunks`. Every one of
the 15 answers (5 questions × 3 runs) named a source. Example, run 2 of the
transcript question:

```
Official transcripts cost $8 and take three business days electronically (admin_transcript_requests.txt).
```

**Criterion 3** — produced by `run_eval.py::check_out_of_scope` and
`gate.py::check`. All 5 `OUT_OF_SCOPE` questions were refused before ever
reaching the model:

```
refused  (best distance 0.825)  What is the capital of Mongolia?
refused  (best distance 0.934)  How do I change the oil in a diesel engine?
refused  (best distance 0.886)  Who won the 1994 World Cup?
refused  (best distance 0.844)  What is the recommended dosage of ibuprofen for a headache?
refused  (best distance 0.891)  How do I write a for loop in Rust?
-> gate refused 5 of 5
```

**Criterion 4** — produced by `chunker.py::describe`, run against the current
`campus_life` index:

```
100 chunks, 282 characters on average (shortest 94, longest 398), produced by chunker.py::split_documents
```

The two shortest chunks, both under the 100-character floor:

```
 94  dining_verrill_street_grill.txt#1  ->  'Hours are 11:00am to 1:00am daily during term. Costs declining balance, or cash after 11:00pm.'
 98  housing_tamsin_court.txt#1  ->  'Laundry costs in-unit washer-dryer. On noise: quiet, structurally concrete floors between units.'
```

**Criterion 5** — produced by `generate.py::answer_from_chunks` (the citation)
cross-checked against `store.py::search` (the chunk it should have cited).
Example, the withdrawal question cites the one document that actually
contains "week ten":

```
Withdrawal runs to week ten, whereas dropping ends at week six (*admin_withdrawal_deadline.txt*).
```

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
