## Exercise 17 — Bounded Knowledge-Source Crawling

**Time: 45 minutes**  
**Suggested implementation: Python with mocked pages and an in-memory index.**

### Situation

A company wants to refresh a small knowledge collection. The product team asks:

> “Start from this page and follow approved links. Avoid cycles and repeated work. Stop at the page budget, and update the index only when content changes.”

### What is available

The request supplies a start URL, an explicit set of allowed URLs, and a positive page budget. Mock fetching returns page text and a list of outgoing URLs, or raises an error. URLs are already normalized.

Use a tiny fixture: the start page links to A, B, A again, and an unapproved page. A links back to the start and to B. B links to a permitted broken page that raises an error and another approved healthy page, C.

### Required behavior

1. Fetch only URLs present in the allowed set. An unapproved start URL is rejected.
2. Fetch each URL at most once per run, including URLs reached through cycles or duplicate links.
3. Stop when there are no more reachable approved pages or the page budget is reached. Every distinct fetch attempt, including a failed one, consumes one budget slot.
4. Successfully fetched new pages become searchable entries in the in-memory index.
5. Across runs, unchanged text causes no index write. Changed text replaces the previous entry for that URL.
6. A failed fetch is reported, leaves any existing indexed content intact, and does not prevent other permitted pages from being processed.
7. Return a summary of attempted URLs, failures, and entries added, updated, or unchanged.

### Verify your implementation

- Cycles and duplicate links cause no repeated fetch within a run.
- The unapproved page is never fetched.
- A budget of two results in only two distinct fetch attempts when enough permitted pages are reachable.
- Arrange a run with enough budget where the broken page fails while a healthy page is still pending; confirm the healthy page is then processed.
- An unchanged second run performs no index writes; changing one page updates one entry.
- A fetch failure on a later run preserves that page's previously indexed content.

**Scope:** Sequential fetching, any consistent traversal order, already extracted links, and exact text comparison for changes. Fetch failures receive no retry in this problem.

---
