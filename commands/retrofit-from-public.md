---
description: Compare public payload snapshots and file deduplicated local divergence issues
argument-hint: PUBLIC_REPO=<checkout> DEVELOPMENT_REF=<ref> PUBLIC_REF=<ref>
---

Read and follow `maintainer-skills/retrofit-from-public/SKILL.md` from this repository.

Public checkout: $PUBLIC_REPO
Development snapshot: $DEVELOPMENT_REF
Public snapshot: $PUBLIC_REF

Ask for a missing public checkout, prefixing the question with `👉`. Omitted refs default to
committed HEAD snapshots and must be resolved to exact commits before comparison. Compare and
file findings only; do not apply changes to either working tree.
