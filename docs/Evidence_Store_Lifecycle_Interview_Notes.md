# Evidence Store Lifecycle: Interview Notes

CAR Conversational Agent — five questions and answers covering evidence storage, index rebuilds, document updates and deletion, checkpoint recovery, and historical evaluation.

**Document registry:** We maintained an authoritative document record independently of the search index. It tracked the document ID, current version or content hash, availability status, original file location, and ownership/access information. Rebuilding the search index did not erase this registry.

## 1. How are the checkpoint, evidence store and search index connected?

They are connected through IDs, but each stores different information.

**The search index stores searchable document chunks.** For example, the Semantic specialist searches an index and retrieves chunk `C21` from document `D9`, version `1`, along with its text and source metadata.

**The evidence store preserves the content used to answer the question.** We save that retrieved passage as evidence record `E17`. That record contains:

- The full passage text.
- Document ID `D9` and version `1`.
- Original chunk ID `C21` and the source index.
- Citation details identifying the source.

**The checkpoint stores the workflow state and evidence references.** For example, checkpoint `CP42` in Cosmos contains the conversation’s resolved scope, workflow progress and reference to `E17`. It does not duplicate the full passage in every checkpoint.

When the specialist or final-answer step needs the passage, application code reads `E17` from the evidence store and supplies its text to that step.

When reopening the conversation, the application loads `CP42`, finds its reference to `E17`, and checks whether that evidence is still available and eligible for reuse using the document registry and current permissions. Valid evidence is loaded; invalid evidence triggers fresh retrieval when the question needs it.

For historical evaluation, we follow the same checkpoint-to-evidence references to inspect exactly what the original execution used. We do not search the current index and assume its results match the original evidence.

That is why rebuilding the index and changing `C21` does not break the historical connection: `CP42` still points to `E17`, which holds the saved passage. If `E17`’s content has been deleted, the reference is explicitly unavailable.

## 2. What happens when the index is rebuilt or a document changes?

If a rebuild generates new chunk IDs, the old IDs may no longer resolve in the search index. We therefore saved the passage itself in the evidence store.

For example:

1. **Before rebuilding:** Checkpoint `CP42` references evidence `E17`. `E17` contains the full passage, document `D9`, version `1`, and original chunk ID `C21`.
2. **After rebuilding:** The same passage might appear under chunk ID `C88`. The old `C21` no longer exists in the index.
3. **When opening the old answer or evaluating it:** The application loads `E17` from the evidence store and reads its saved passage. It does not need to find `C21` in the rebuilt index. The old chunk ID remains provenance: where the evidence originally came from.

The citation therefore resolves through `evidence_id`, rather than directly querying the live index using the old chunk ID.

**A document content update followed our delete-old-version approach.** Once the replacement was indexed and ready, we made the new version active, marked the old version superseded, and applied the removal and refresh process described in Question 3. The old evidence content was removed, affected findings were marked `needs_refresh`, and current answers retrieved new evidence. We did not map old chunk IDs to new ones or silently replace the passage inside `E17`.

If the evidence store held only `chunk_id`, without the passage or a retained version capable of supplying it, the reference would break. Fresh retrieval could support a new answer, but could not reconstruct the original evidence exactly.

## 3. What happened when a user deleted or updated an uploaded document?

We treated an update as removing the old version and adding a new version. The changes happened in three places:

**Search index:**

I deleted every chunk belonging to that document and version, using their indexed keys. I did not wipe the entire uploaded-documents index. For an update, I indexed the replacement under its new document version. The document registry identified which version was active; deleted or superseded versions were blocked from reuse.

**Evidence store:**

I found every evidence record associated with the old document version. I removed its stored passage and retained its evidence ID with an unavailable status, so existing references could be recognized as invalid.

For example, `E17` previously contained text from document `D9`, version `1`, chunk `C21`. After removal, requesting `E17` returned “source unavailable.” It did not silently return a passage from version `2`.

I also marked findings, summaries and generated narratives derived from that evidence as `needs_refresh`, including generated reports searchable through another index. Cached answers, where present, followed the same invalidation rule. Citations indicated “Source removed” or “Source updated.”

**Checkpoints and the next chat turn:**

The historical checkpoint still contained its original evidence references—for example, `CP42` still referenced `E17`.

When restoring that checkpoint, application code checked its evidence IDs. Finding `E17` unavailable triggered a refresh path. The orchestrator excluded the affected findings and summary content from its working context, retrieved from current permitted sources, regenerated the affected answer and reran validation.

The refreshed work was recorded under a new execution and new checkpoints within the same conversation. `CP42` retained its original reference to `E17`; we did not rewrite it to pretend the original answer had used replacement evidence. If no supporting source remained, the answer reported that limitation.

**Cleanup reliability:**

The registry status blocked reuse before physical cleanup completed. A durable, retryable cleanup job removed the old indexed chunks and evidence content, and periodic checks caught missed cleanup. Evidence reads checked document status, version and current permissions while that work ran.

**Historical evaluation:**

Because the old evidence text had been removed, its grounding checks were marked “not evaluable: evidence unavailable.” Other checks could still run where records were sufficient. The refreshed execution was evaluated separately as a new run.

## 4. What happened when the conversation resumed from an affected checkpoint?

When the user continued the conversation, application code loaded the saved checkpoint—for example, `CP42`, which referenced evidence `E17`.

**First, it checked whether that evidence could still be used.** It checked the evidence record’s availability, the source document’s status and version in the registry, and the user’s current permissions. Loading a checkpoint did not automatically make its contents valid.

**If `E17` was unavailable or superseded, its dependent findings were marked `needs_refresh`.** Those findings were excluded from the next prompt. We also removed affected earlier-answer text from the model’s input and rebuilt any contaminated summary from the remaining valid context. Otherwise, the deleted fact could re-enter through memory even after its evidence was removed.

**If the new question needed that finding, the orchestrator routed back to retrieval.** It searched current permitted sources, saved replacement evidence under a new ID such as `E18`, regenerated the affected answer and reran validation. Unaffected findings could still be reused after their checks passed. If the question did not need the invalid finding, we did not regenerate it unnecessarily.

The refreshed work was recorded under a new execution and new checkpoints within the same conversation. `CP42` retained its original reference to `E17`; we did not rewrite it to pretend the original answer had used `E18`.

If no supporting evidence remained, the answer explicitly stated that the information could no longer be verified. Any historical copied content covered by the deletion policy was separately purged or redacted.

## 5. How did evaluation work when the evidence was stale or deleted?

Evaluation started with the original execution’s trace and logged checkpoint references. I loaded that execution’s checkpoint—for example, `CP42`—and followed its evidence reference to `E17`. I used the historical checkpoint, because the conversation’s latest state could already contain later answers and different evidence.

**If the original evidence remained available and was permitted for evaluation**, I compared the original answer against that saved passage or SQL result. I checked whether its figures, periods, explanations and citations were supported. A later source update did not automatically make the earlier answer incorrectly grounded; answering correctly against today’s information was a separate assessment. Under our delete-old-version approach, however, evidence whose content had been removed followed the unavailable-evidence case below.

**If `E17`’s content had been deleted**, its ID and unavailable-status marker were insufficient to verify the answer. I marked the affected grounding checks **`not_evaluable`**, with the reason **`evidence_unavailable`**. I did not retrieve a new passage and treat it as the evidence the original model had seen.

Other checks continued where sufficient records remained—for example, latency, tool errors and call-limit compliance from the execution telemetry. Routing could be assessed if the original request and handoffs were available.

**I reported evaluation coverage separately from quality scores.** For example, if eight of ten selected turns retained all required evidence, full grounding-evaluation coverage was 80%. Quality scores covered the evaluable turns; the two incomplete turns counted as neither passes nor failures.

If we retrieved fresh evidence `E18` and generated a replacement answer, that belonged to a new execution with new checkpoints. I evaluated that run separately, preserving the distinction between the original answer and the refreshed answer.
