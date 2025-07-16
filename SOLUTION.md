### 1. Assumptions
- The webhook payloads from Azure DevOps are delivered in near real-time, but duplicate deliveries and missing/out-of-order events are possible (based on the provided sample_payloads.json).
- The authoritative timestamp for state changes is System.ChangedDate in the payload, not the time the webhook was received.
- Work items can move between states multiple times (e.g., Active → Resolved → Active), so we must store full state transition history.
- Only state transitions (System.State changes) are important for analytics; other field changes are ignored.
- SQLite is acceptable for this test, but in production a more robust database (e.g., PostgreSQL) would be used.

### 2. What I’d Do Differently With More Time
- Signature Validation: Validate webhook signatures from Azure DevOps to ensure requests are authentic.
- Idempotency Keying: Add deduplication logic using webhook event IDs to handle retries and avoid double-processing.
- Retry Queue: Implement retry logic for transient database errors or processing failures.
- Concurrency Handling: Add transactional locking or use upserts to avoid race conditions on high webhook volume.
- Tests: Write unit and integration tests covering duplicate payloads, missing intermediate events, and out-of-order delivery.
- Analytics Queries: Optimize "time in state" calculations for reporting use cases with a large number of work items.

### 3. Questions I’d Ask in a Real Scenario
- Should we persist all work item updates (even if there’s no state change) or only System.State transitions?
- Should deletes and rollbacks (if a work item is deleted in DevOps) be reflected in this mirror service?
- Is it acceptable to rely on System.ChangedDate as the canonical timestamp, or should we use the webhook delivery timestamp for some use cases?
- How critical is data consistency if webhooks are missed entirely (e.g., due to a temporary outage)? Should we build a sync job to backfill missing transitions?


---

# Summary of Solution
- Implemented POST /webhook/workitem/updated to receive state change events.
- Stored work item metadata and full state transition history in SQLite.
- Implemented analytics endpoints:
   - GET /workitems/{id} for details and history.
   - GET /workitems/{id}/time-in-state to calculate time spent in each state.
- Deduplicated payloads using (work_item_id, from_state, to_state, changed_at).