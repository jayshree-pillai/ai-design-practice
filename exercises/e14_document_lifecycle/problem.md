## Exercise 14 — Document Ingestion, Replacement, and Deletion

**Time: 45 minutes**  
**Suggested implementation: Python with in-memory document and search stores.**

### Situation

A RAG assistant accepts customer documents. The product team asks:

> “Users must be able to upload, replace, and delete their documents. Search must reflect the latest successful change. A failed update must not destroy the working version.”

### What is available

An upload supplies a customer ID, document name, and plain text. A mocked preparation step either returns searchable text or raises an error. For this exercise, search is a case-insensitive substring search over that text, with one search entry per document.

### Required behavior

1. A successful upload returns a document ID and makes the document searchable for its owner.
2. Replacing a document keeps its ID. On success, only its new text is searchable.
3. If replacement preparation fails, the previous document and searchable text remain intact.
4. Deletion removes the document from search. Deleting an unknown or already deleted ID is harmless.
5. Search returns only the requesting customer's documents. Attempts to replace or delete an existing document owned by someone else are rejected.
6. Replacing an unknown document ID returns an error. Failed initial ingestion creates no searchable entry.
7. Every change returns a clear success or failure outcome.

### Verify your implementation

- Upload “refunds are available” and find it by searching for “refunds.”
- Replace it with “exchanges are available”: the old term no longer finds it, while “exchanges” does.
- Force a replacement failure and confirm the last successful content remains searchable.
- Delete it and confirm it disappears from search; repeat the deletion safely.
- A second customer cannot search, replace, or delete the first customer's document.
- Failed initial ingestion leaves no searchable document behind.

**Scope:** Synchronous changes, plain text, one current version per document, and sequential operations. Real parsing, embeddings, and version history are outside this attempt.

---
