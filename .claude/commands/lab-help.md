---
description: List the workshop branches and what they contain.
---

Print a concise table of the workshop branches and what each one
contains. Source of truth: `WORKSHOP.md` at the repo root. Read that
file and surface a tightened version of the branch table for the
user — branch name, one-line description, when to use it. If
`WORKSHOP.md` doesn't exist, say so and stop (the user is not on a
workshop branch that includes it).

Don't paraphrase loosely; the branch names and one-liners need to be
exact so the user can copy-paste into `git checkout`. After the
table, remind the user how to swap branches mid-lab:

```
git stash push -m "in-progress"
git checkout <branch>
# ... work ...
git checkout -            # return
git stash pop
```
