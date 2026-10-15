## Exercise 19 — Retrieval Merging and Evidence Selection

**Time: 45 minutes**  
**Suggested implementation: Plain Python.**

### Situation

Two search services return overlapping evidence. The product team asks:

> “Give the answer generator a small, relevant evidence set. Remove duplicates, enforce customer ownership, and avoid letting one document occupy every slot.”

### What is available

You receive an authenticated customer ID and two lists of search results. Each result has a chunk ID, document ID, customer ID, text, and numeric relevance score. Both services use the same score scale; higher is better. Duplicate chunk IDs have identical text, document, and owner, but may have different scores.

### Required behavior

1. Exclude results belonging to other customers and results with empty or whitespace-only text.
2. Combine the two lists and retain one copy per chunk ID, using its highest score.
3. Return at most three chunks in descending score order. Break equal-score ties by chunk ID in ascending alphabetical order.
4. Include no more than two chunks from the same document. Keep considering lower-ranked candidates when a document has already filled its allowance.
5. Return both the selected evidence records and their chunk IDs in matching order.
6. Return all eligible selections if fewer than three fit the rules; return empty collections if none fit. Leave the input lists unchanged.

### Verify your implementation

- A chunk returned by both services appears once with its higher score.
- A highly scored foreign customer's chunk is excluded.
- A blank-text chunk is excluded.
- Given eligible chunks `c1`, `c2`, and `c3` from document A with scores 0.99, 0.98, and 0.97, plus `c4` from document B with score 0.90, the selection is `c1`, `c2`, `c4`.
- Equal scores follow the stated chunk-ID tie rule.
- One empty source and two empty sources are handled correctly; the original inputs remain unchanged.

**Scope:** Search results are already available and scored. This exercise ends at evidence selection; answer generation is a later consumer.

---
