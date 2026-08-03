# Implementing a task

Use this loop:

```text
read
→ inspect
→ confirm task readiness and ownership
→ make the smallest coherent change
→ run focused validation
→ inspect the diff
→ update documentation and evidence
→ move to review
```

Keep implementation and tests aligned. Do not postpone safety checks, public exports, or documentation until an unrelated cleanup pass. When new evidence invalidates the task design, stop and return the task to planning rather than forcing the implementation through.
