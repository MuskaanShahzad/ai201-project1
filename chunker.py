"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


import re

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_SPLIT.split(text.strip()) if s.strip()]


def split_documents(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    Sentence-aware chunking for campus_life: short, single-paragraph posts.

    campus_life's posts run ~178-549 characters, almost always 1-4 sentences,
    and a fixed 800-character window never touches them (88 docs -> 88 chunks).
    But a few posts pack two separate facts together (admin_withdrawal_deadline
    covers both the drop deadline and the withdrawal deadline; admin_library_
    holds covers both an in-house hold and an interlibrary request) — those
    deserve a chance to split, without ever cutting a sentence in half.

    So instead of a character window, this groups whole sentences until the
    next one would push the chunk past `chunk_size`, then starts a new chunk.
    A short post that never reaches `chunk_size` just comes out as one chunk,
    same as the fallback — the difference only shows up on the longer or
    multi-fact posts.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    chunks: list[Chunk] = []
    for doc in documents:
        sentences = _split_sentences(doc.text)
        if not sentences:
            continue

        groups: list[list[str]] = []
        current: list[str] = []
        current_len = 0

        for sentence in sentences:
            if current and current_len + len(sentence) + 1 > chunk_size:
                groups.append(current)
                # Carry trailing sentences forward so the next chunk doesn't
                # start cold — but only whole sentences, up to `overlap` chars.
                carried: list[str] = []
                carried_len = 0
                for s in reversed(current):
                    if carried_len + len(s) > overlap:
                        break
                    carried.insert(0, s)
                    carried_len += len(s) + 1
                current, current_len = carried, carried_len

            current.append(sentence)
            current_len += len(sentence) + 1

        if current:
            groups.append(current)

        for i, group in enumerate(groups):
            chunks.append(
                Chunk(
                    text=" ".join(group),
                    source=doc.source,
                    index=i,
                    produced_by="chunker.py::split_documents",
                )
            )

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
