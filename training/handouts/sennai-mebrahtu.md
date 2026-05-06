# Training handout — sennai-mebrahtu

## Your environment

| field         | value                                           |
|---------------|-------------------------------------------------|
| URL           | https://sennai-mebrahtu.training.gcp.re-cinq.com                                   |
| Repo          | https://github.com/re-cinq/microservices-demo   |
| Your branch   | `attendee/sennai-mebrahtu`                                     |
| Your bug ID   | `search-misses-descriptions` (don't share — see what your neighbours got) |

## What we want from you

A customer just opened a ticket about your URL. The ticket is in
[`BUG_REPORT.md`](https://github.com/re-cinq/microservices-demo/blob/attendee/sennai-mebrahtu/BUG_REPORT.md)
on your branch. Your job today:

1. Reproduce the issue at sennai-mebrahtu.training.gcp.re-cinq.com
2. Use Claude Code to triage it: find the suspected file, understand
   what's wrong, and write an engineer-ready ticket
   (`ENGINEERING_TICKET.md` on your branch) with:
   - exact steps to reproduce
   - suspected service + file
   - severity rationale
3. Fix the bug locally, verify in browser at sennai-mebrahtu.training.gcp.re-cinq.com after deploying
4. Open a PR from a fix branch into `attendee/sennai-mebrahtu`. Auto-merge will
   redeploy your namespace. Verify the fix went live.

## Local workflow

```bash
git clone https://github.com/re-cinq/microservices-demo
cd microservices-demo
git checkout attendee/sennai-mebrahtu
git checkout -b attendee/sennai-mebrahtu-fix
# ... use Claude Code to triage, write ticket, fix ...
git push -u origin attendee/sennai-mebrahtu-fix
gh pr create --base attendee/sennai-mebrahtu --title "fix: <one line>" --body "Closes ticket. See ENGINEERING_TICKET.md."
```

The PR auto-merges on green CI. Watch the GitHub Actions run for the
deploy. Re-test at https://sennai-mebrahtu.training.gcp.re-cinq.com once it's green.
