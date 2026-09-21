"""
Settings for The Unofficial Guide.

Everything you're likely to change lives here, at the top, on purpose.
You'll edit THRESHOLD in Milestone 4 and the chunking numbers in Milestone 3.

Anything you set in your .env file wins over the defaults here.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")


# ─── The corpus you're working with ──────────────────────────────────────────
# Change this to switch corpora, or pass --corpus on the command line.
# Options are the folder names inside corpora/. See corpora/README.md.
#
# Milestone 1: picked campus_life on purpose — short, single-sentence posts
# about student life (dining, housing, parking) are the kind of thing people
# would actually ask this system about.

CORPUS = os.getenv("AI201_CORPUS", "campus_life")


# ─── Chunking (Milestone 3) ──────────────────────────────────────────────────
# campus_life posts run ~178-549 characters and are almost always 1-4
# sentences. 400 lets a typical single-fact post stay whole (it's above the
# average of 317) while still giving the longer multi-fact posts — like the
# drop/withdraw deadlines, or the two library systems — room to split into two
# real chunks instead of one that mixes both facts.
#
# 60 characters of overlap is roughly one short sentence: enough that a split
# chunk doesn't start cold, without meaningfully duplicating content across
# posts this short.

CHUNK_SIZE = 400        # characters per chunk
CHUNK_OVERLAP = 60      # characters shared between neighbouring chunks


# ─── Retrieval (Milestone 4) ─────────────────────────────────────────────────

TOP_K = 5               # how many chunks to pull back per question

# The relevance gate. If the best chunk is further away than this, the system
# refuses to answer instead of handing the model thin material.
#
# LOWER IS BETTER: 0.3 is a close match, 0.9 is unrelated.
#
# Milestone 4: measured on campus_life with my 5 questions vs. the 5 in
# OUT_OF_SCOPE. In-corpus best distances: 0.119, 0.358, 0.218, 0.158, 0.245
# (worst case 0.358). Out-of-scope best distances: 0.825, 0.934, 0.886, 0.844,
# 0.891 (best case 0.825). That's a gap from 0.358 to 0.825 with nothing in
# between, so 0.6 — the starter's default — already sits comfortably in the
# middle of it. Keeping it rather than moving it just to have moved it.
THRESHOLD = 0.6


# ─── Models ──────────────────────────────────────────────────────────────────
# Embeddings run on your own machine and cost no API quota.
# Only generation calls out to a service.

# This is the model Chroma bundles, and leaving it alone is the fast path: it
# downloads about 80 MB from Chroma's own CDN and needs nothing else installed.
#
# Setting it to any other name — unit 2's "try a second embedding model"
# stretch option — switches to loading that model from Hugging Face instead,
# which needs `pip install 'sentence-transformers>=3.4,<3.5'` first. store.py
# says so with a real error message rather than a stack trace if you forget.
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
MODEL = os.getenv("AI201_MODEL", "gemini-3.5-flash-lite")


# ─── Rate limiting and quota guards ──────────────────────────────────────────
# You should not need to touch these. They exist so that a runaway loop costs
# you a warning instead of your whole day's allowance.

REQUESTS_PER_MINUTE = 30       # outgoing calls the limiter will allow per minute
SESSION_REQUEST_BUDGET = 300   # stop and warn rather than draining the daily quota
MAX_RETRIES = 4                # on 429 / resource-exhausted, with backoff

CACHE_ENABLED = os.getenv("AI201_CACHE", "1") != "0"
CACHE_DIR = ROOT / ".cache"


# ─── Paths ───────────────────────────────────────────────────────────────────

CORPORA_DIR = ROOT / "corpora"
CHROMA_DIR = ROOT / "chroma_db"
RESULTS_DIR = ROOT / "results"


def corpus_path(name: str | None = None) -> Path:
    """Folder holding the documents for a corpus."""
    return CORPORA_DIR / (name or CORPUS) / "documents"


def collection_name(name: str | None = None, variant: str = "default") -> str:
    """
    Name of the vector-store collection for a corpus.

    `variant` lets you index the same corpus two different ways and query both
    without deleting anything — you'll want that in unit 2 when you compare
    chunking strategies.

    Chroma is fussy about collection names: 3 to 63 characters, starting and
    ending with a letter or digit, and nothing but letters, digits, underscores
    and hyphens in between. If you bring your own corpus and name the folder
    something Chroma won't accept, this cleans it up rather than failing.
    """
    import re

    raw = f"{name or CORPUS}__{variant}"
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "-", raw)
    cleaned = cleaned.strip("_-")          # must start and end alphanumeric
    if not cleaned or not cleaned[0].isalnum():
        cleaned = f"c{cleaned}"
    if not cleaned[-1].isalnum():
        cleaned = f"{cleaned}0"
    return cleaned[:63].rstrip("_-") or "collection"
