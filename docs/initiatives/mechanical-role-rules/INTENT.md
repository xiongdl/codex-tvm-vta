# Intent: Mechanical Role Rules

## Confirmed intent

Make `.agents/custom/root.md`, `.agents/custom/default.md`, and
`.agents/custom/reviewer.md` mechanically robust. When the request names the
scope and desired outcome clearly, the active role must execute the documented
command sequence without restating, reinterpreting, or asking for redundant
confirmation.

The task branch must be created immediately after the `interview-me` gate is
complete, before Specify, Plan, artifact writes, or implementation writes.

## Out of scope

- Changing `AGENTS.md`.
- Changing the Git workflow implementation.
- Changing project source code or runtime behavior.
