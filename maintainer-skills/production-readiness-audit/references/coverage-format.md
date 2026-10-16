# Audit coverage format

Use the digest and file entries from `scripts/audit_inventory.py`. The JSON artifact has:

- `snapshot_sha256`: the current inventory digest, covering shipped files and supporting context.
- `files`: one row per shipped path with `path`, `sha256`, `status`, and nonempty `evidence`.
  Status is `reviewed`, `finding`, or `deferred`; deferred rows keep coverage incomplete. Evidence
  describes actual observations and relevant locations, not a claim that a checksum was checked.
- `checks`: one row for each `required_checks` ID with `id`, `status`, and nonempty `evidence`.
  The six core checks require `reviewed` or `finding`; deferred checks keep coverage incomplete.
- `findings`: distinct rows with `id`, `route` (`local` or `parent-bound`), `reason`, owning `source`,
  `evidence`, and `disposition`. File/check rows marked `finding` must name the row's `finding_id`.

Finding dispositions are objects: `{"kind": "filed", "url": "<verified issue URL>"}` or
`{"kind": "duplicate", "url": "<verified matching issue URL>"}`. Pending parent escalation uses
`{"kind": "handoff", "reason": "<what remains and where evidence was handed off>"}`.
Unfinished filing or evidence uses `{"kind": "blocked", "reason": "<specific blocker>"}`.
Local findings cannot use a parent handoff instead of filing. Verify links with the issue tools;
schema validation cannot establish that an external write succeeded.

Additional inherited checks may use `status: "unexpressible"` with an `invariant` (`INV-NNN`) and
evidence. The matching explicit disposition in the actual transformation contract must contain
an `audit_limitations` item with `check` equal to that review ID and a nonempty `reason`, e.g.:

```json
{"check": "INV-158-host-mechanism", "reason": "Describe the unavailable construction and its effect"}
```

The required preservation mechanism or discount justification still applies. A limitation cannot
waive a required semantic review or turn missing runtime evidence into a pass.

Coverage completeness means the observations are accounted for, including confirmed findings and
documented limitations. It does not mean the observations are correct, all issues are resolved,
or runtime behavior passed. Retain structural alerts and blocked dispositions in the final report.
