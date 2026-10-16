# Codex model selection

The authoritative bootcamp comparison, stage table and switch/confirmation procedure are in
`../skills/bootcamp-onboarding/ground-rules.md` → "Best-value model/effort prompt". Graduation uses
that same procedure. This document supplies only the host-control and model-role adaptation;
never replace the procedure with an optional "when helpful" suggestion.

The bootcamp compares the stage's model and effort recommendation at each eligible boundary. It cannot make
that change itself. In the Codex desktop app or IDE, tell the bootcamper to use the visible model
and reasoning controls. In the Codex CLI, describe the intent without inventing a command.

## Resolving the table's model roles

Resolve `balanced` to one available general-purpose Codex model and `high-capability` to one
available model the current host reliably describes as suited to complex reasoning/coding.
Use current host-provided model descriptions or current official OpenAI documentation, never
training-data model rankings. Reuse the current configured model when it satisfies the role.
Do not present multiple candidates or add a model-selection question outside the pinned procedure.

If available alternatives or their capabilities cannot be verified, retain the configured model
and disclose that the role comparison is unavailable. Never invent an alternative, ordering,
price or claim that the current model is inadequate. A role label is not an observed model ID.
Resolve effort to the table's target only when the selected model/host supports it; otherwise
name the unavailable target, retain the current supported setting and continue without blocking.
The fallback does not add a host-configuration gate or silently claim a match.

Read model and effort independently from reliable current context or explicit user reports of
actual selected values; neither a recommendation nor a bare confirmation proves a hidden value.
The ground-rules procedure owns per-dial fallback and every answer branch, not this document.

In the desktop app or IDE, use the controls actually exposed by that interface. In an unknown
interface or CLI, describe the intended setting and use only a control verified for that client;
do not assume Claude commands or invent a separate effort command. Changing a host setting is
always the user's action, never a plugin write.

Official references checked for the host-control boundary (2026-10-15):
[Codex CLI](https://learn.chatgpt.com/docs/codex/cli) documents model/reasoning selection.
This reference does not establish the current task's settings or account-specific model access.
