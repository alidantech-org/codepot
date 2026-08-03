# Verification rules

A task is complete only when its acceptance criteria are proven.

Required evidence normally includes:

- exact commands run;
- exact results, including counts where available;
- focused tests for changed behavior;
- architecture or conformance tests for boundary changes;
- integration or manual proof for connected workflows;
- documentation paths updated;
- changed-path review confirming no forbidden files changed;
- remaining limitations and follow-up work.

Never write only “tests passed.” Never claim a test that was not run. Documentation-only work must state that runtime tests were not required or not run and must validate links, locations, and repository structure instead.

If verification cannot be completed, leave the task in `blocked` or `review` and explain the missing evidence honestly.
