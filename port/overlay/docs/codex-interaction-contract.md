# Codex bootcamp interaction contract

Codex has separate intermediate commentary and final-response channels. That host behavior must
not change the bootcamp's question-and-answer rhythm.

## Continue through non-yielding work

- Commentary is a progress update, never a bootcamp turn boundary. Use concise commentary while
  commands or other automatic work run, then continue executing the active skill in the same turn.
- A completed command, successful setup check, generated scenario, written file, checkpoint, status
  report, summary, or phase boundary does not authorize yielding to the bootcamper.
- After any non-yielding step, immediately load and execute the next step. Continue across a run of
  non-yielding steps and across phase files until the active skill reaches its next defined `👉`
  question.
- Do not end a final response with a promise to continue, an invitation such as “tell me when to
  continue,” or any other invented continuation prompt.

## Turn-close audit

Before sending the final response for an active bootcamp turn, verify all of the following:

1. The bootcamper's latest answer has been processed before anything else.
2. Every automatic step following that answer has finished or reached a genuine external blocker.
3. The response ends with exactly one `👉` question copied from the currently active shipped skill
   step. Its answer options, when any, appear directly beneath it.
4. Nothing follows that question and its answer options.

If no `👉` question has been reached, do not send a final response. Continue with the next step,
phase file, or selected module in the same turn. A final response containing only status is a contract violation.

The only exceptions are a genuine blocker that requires user action and a terminal workflow that
the shipped skill explicitly ends without a question. State a blocker as the action required; do
not disguise ordinary automatic work as a blocker.
