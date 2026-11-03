# Reflection — Post-Evaluation

**Evaluation date:** 2026-10-09  
**Score received:** 52/120 — Not Yet Certified  
**Resubmission date:** 2026-11-03

---

## What the evaluation found

The evaluator confirmed the core RAG pipeline works end-to-end and that the
spec-first artefacts (spec.md, plan.md, tasks.md), data provenance note, and
CLAUDE.md context engineering are in place. The main findings were internal
consistency failures: claims in the write-up did not match the actual code.

Specific inconsistencies caught:

| Claim in write-up | Actual in code |
|-------------------|----------------|
| 42 chunks | 69 chunks (40 endpoints + 29 note sections) |
| 38 endpoints | 40 endpoint operations |
| Top 5 chunks retrieved | N_RESULTS = 3 in config.py |
| Model: Claude claude-opus-4-5 | GPT-4o-mini via Portkey gateway |
| MAX_QUERY_LENGTH = 500 guard in query.py | Guard was absent |
| test_query.py with restructured tests | No test file in package |

---

## Root cause

The write-up was drafted at a different point in the development timeline
than the final submitted code. Two specific changes were made late and not
propagated back to the documentation:

1. **Model switch:** gpt-4o-mini was substituted for claude-opus-4-5 late
   in development to reduce latency via the Portkey gateway. The slide,
   app.py sidebar, and failure_analysis.md were not updated at the same time.

2. **N_RESULTS reduction:** N_RESULTS was reduced from 5 to 3 to reduce
   token cost. The failure_analysis.md and pitch_slide.md still referenced
   the old value.

3. **Test file:** test_query.py was described in the AI output review as a
   planned correction, but the file itself was not included in the submitted
   package zip.

4. **MAX_QUERY_LENGTH guard:** This was described as a correction in the
   AI output review but was not actually added to src/query.py before
   submission.

---

## What was fixed for resubmission

1. **Added `MAX_QUERY_LENGTH = 500` guard** to `src/query.py` — the guard
   now truncates queries over 500 characters and emits a warning.

2. **Created `tests/test_query.py`** — deterministic tests for ingest count
   (asserts 69 chunks), retrieval source correctness, and the query length
   constant. Tests run without an LLM key.

3. **Fixed all numbers** in docs to match the code:
   - `docs/ai_output_review.md`: 42 → 69 chunks
   - `docs/pitch_slide.md`: top 5 → top 3, claude-opus-4-5 → GPT-4o-mini,
     38 → 40 endpoints
   - `docs/failure_analysis.md`: N=5 → N=3, N_RESULTS increase 5→8 changed
     to 3→6
   - `docs/data_provenance.md`: 38 → 40 endpoints throughout
   - `README.md`: ~38 → 40 endpoints

4. **Fixed `src/app.py` sidebar** — now correctly labels the model as
   "GPT-4o-mini via Portkey gateway".

5. **Added `src/retrieve_only.py`** — runs the retrieval step for all five
   failure inputs and prints the top 3 chunks, with no gateway key required.

6. **Added `docs/reflection.md`** (this file).

---

## What I learned from the evaluation

The integrity check process revealed a category of error that code review
alone does not catch: **documentation drift**. When the code changes late
in development, every place that describes the code must be updated at the
same time. The fix for future projects is to treat the numbers in the
write-up (chunk count, N_RESULTS, model name) as constants that come from
a single source — ideally read programmatically from config.py — so a code
change automatically invalidates the claim.

The test-file omission was a packaging error: the file was described and
planned but not actually written before the package zip was created. The
fix was to write the test file before zipping, and to check the
submission checklist against the actual zip contents, not the project folder.
