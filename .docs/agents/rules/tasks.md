# Task rules

Implementation begins only from a task under `.docs/tasks`.

An AI may implement a task only when:

- its status is `ready`, `claimed`, or `in_progress` for that agent;
- dependencies are complete;
- no conflicting task owns overlapping files;
- allowed and forbidden paths are explicit;
- architecture questions are resolved;
- acceptance criteria and validation commands are concrete.

Before editing, record or confirm task ownership. One task has one active owner.

Do not:

- choose a random unchecked item and start coding;
- expand scope because nearby code looks untidy;
- mark a task complete because files were created;
- change acceptance criteria after implementation to match the result;
- implement a blocked or draft task;
- bundle unrelated tasks into one change.

Task status and evidence are updated as part of the work, not as an afterthought.
