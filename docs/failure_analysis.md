# Failure Analysis

Five specific inputs that break the prototype, with root causes.

---

## Failure 1 — Query about batch operations

**Input:** `"How do I create multiple orders at once?"`

**Expected:** "There is no batch order creation endpoint. You must create orders individually."

**Actual output:** The system retrieves the `POST /orders` endpoint (single order creation)
and the LLM answers:
> "To create an order, use POST /api/v1/orders... [proceeds to describe single-order creation]"

The LLM does not tell the developer that batch creation is not supported.

**Root cause:** The corpus has no batch endpoint. The retrieval correctly surfaces the closest
match (single order creation), but the LLM then answers as if this satisfies the question.
The CLAUDE.md instruction to "admit when no matching endpoint exists" fires only when there
is *no* similar content retrieved — not when there is a *related but different* endpoint.

**Fix needed:** Add explicit negative examples to the corpus or add a CLAUDE.md instruction
to compare the retrieved endpoint against the exact question intent before answering.

---

## Failure 2 — Query about rate limits on a specific endpoint

**Input:** `"What is the rate limit for calling the payment endpoint?"`

**Expected:** "Standard rate limit is 100 requests per 60 seconds per customer token,
as documented in error-handling.md. There is no separate per-endpoint rate limit."

**Actual output:** The retrieval sometimes surfaces the payment service YAML (which has no
rate limit information) and sometimes surfaces error-handling.md. When it retrieves the YAML,
the LLM says:
> "I couldn't find rate limit information specific to the Payment Service endpoint in the
> retrieved documentation."

This is technically accurate but unhelpful — the answer exists in the notes doc, just not
in the retrieved chunks.

**Root cause:** "Rate limit" and "payment endpoint" are semantically distant in the embedding
space. The retrieval query has to choose between the payment endpoint chunk (high path
similarity) and the error-handling notes chunk (has rate limit content). With N=5 results,
only 2 out of 5 test runs retrieved the rate-limiting section.

**Fix needed:** Increase N_RESULTS from 5 to 8 for queries containing "rate limit". Or add
rate limit information directly to each endpoint's YAML spec (the right fix architecturally).

---

## Failure 3 — Multi-step workflow query

**Input:** `"Walk me through the complete checkout flow — every endpoint I need to call in order."`

**Expected:** A numbered list: cart → inventory reserve → checkout trigger → order created →
payment processed → shipment created → confirmation email.

**Actual output:** The retrieval surfaces 5 chunks from various services but none of them
describe the full flow. The architecture-overview.md section "Happy-Path Order Flow" is the
right source but it ranks below individual endpoint chunks because it uses narrative language
rather than the keyword "checkout".

The LLM constructs a partial answer from the retrieved endpoint chunks but misses the inventory
reservation step and the Notification Service email trigger.

**Root cause:** Multi-step workflow questions need the architecture overview document, but
it loses to individual endpoint chunks in relevance ranking because the question contains
endpoint keywords (`checkout`, `order`, `payment`) that match those chunks more precisely.

**Fix needed:** Store the full order flow section as a dedicated chunk with explicit keyword
tagging. Or implement a hybrid search that also matches on structural notes when the question
contains words like "flow", "sequence", "order of operations".

---

## Failure 4 — Query using internal service jargon

**Input:** `"How do I call the payment capture API?"` (instead of "process a payment")

**Expected:** Return `POST /api/v1/payments` with full details.

**Actual output:** The retrieval returns the payment service chunks, but the LLM answers:
> "I found the payment processing endpoint... POST /api/v1/payments... [correct answer]"

However, in 2 out of 5 test runs, the retrieval surfaced the inventory reservation endpoint
first because "capture" semantically overlaps with "reserve" in the embedding space.

**Root cause:** "Capture" is a payment-domain term meaning "charge the card". The
all-MiniLM-L6-v2 model has seen this term in many contexts (photography, data capture,
inventory capture) and its embedding is not tightly coupled to payment processing.
The inventory reservation endpoint uses language like "reserve" and "capture" stock.

**Fix needed:** Add synonyms to each endpoint chunk. For the payment endpoint, include
"capture", "charge", "debit" in the description. This is a domain vocabulary coverage problem.

---

## Failure 5 — Query about a non-existent service

**Input:** `"Which endpoint handles subscription management?"` (subscriptions do not exist)

**Expected:** "There is no subscription management service or endpoint in the current documentation."

**Actual output:**
> "Based on the retrieved documentation, the closest match for subscription management
> would be the Notification Service, which handles recurring notifications, or the
> Analytics Service for subscription metrics..."

The LLM hallucinates a plausible-sounding mapping from subscription → notification,
which is wrong. No such relationship exists in the corpus.

**Root cause:** When no close match is retrieved, the LLM is instructed (by CLAUDE.md) to
"state the closest match" — but it treats "notification" as semantically close to
"subscription" and bridges the gap with reasoning rather than citing a document.

**Fix needed:** Set a minimum relevance score threshold. If all retrieved chunks score below
0.4 similarity, return a fixed response: "No matching endpoint found in the current
documentation" rather than passing low-confidence chunks to the LLM.
