# Exercise 2 — OOP: External Company API
**Time:** 40 minutes

## Problem

An external REST API returns companies.

Each company contains:

- `id`
- `name`
- `industry`
- `rating`

Build a client that:

1. Calls the external API
2. Uses an HTTP timeout
3. Raises an appropriate error for a non-200 response
4. Converts returned JSON records into `Company` objects
5. Removes duplicate companies based on company ID
6. Returns only companies above a requested rating threshold
7. Sorts final results from highest rating to lowest

## Important

Do **not** begin by copying a pre-defined class structure.

Start from the paragraph and derive the program yourself.

## Concepts to practice

- Domain objects / dataclasses
- API client objects
- `requests`
- Timeouts
- HTTP status handling
- JSON → Python objects
- Deduplication
- Filtering
- Sorting

---
