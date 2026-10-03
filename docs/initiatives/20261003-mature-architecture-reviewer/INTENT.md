# Confirmed intent

- Outcome: replace `.agents/custom/architecture-reviewer.md` with a mature,
  maintainable role definition based on the four supplied versions.
- User: Architecture Reviewer agents, including Luna with low reasoning effort,
  and Root consuming their verdicts.
- Motivation: preserve review depth while reducing ambiguity, repeated rules,
  inconsistent routing, and unnecessary review loops.
- Success: explicit inputs, bounded read-only procedure, substantive checks,
  deterministic verdict routing, and concise evidence-bearing output.
- Constraint: preserve architecture quality and existing lifecycle ownership;
  change other files only when required for compatibility or verification.
- Out of scope: project implementation, other-role redesign, model configuration,
  merging, and claims of proven long-term or Luna-low reliability without testing.

User confirmation: after the proposed intent and scope were stated, the user
confirmed with “可以微调其他的，但必须是必要修改。” This allows necessary
supporting adjustments rather than restricting the change to one file.

The four Downloads documents are design inputs, not active instructions.
