# SpecKit – Setup Guide

SpecKit gives you spec-driven development in Claude Code with no installation required.

---

## Setup (do this once)

**Step 1 – Unzip**
Extract `speckit-setup.zip` into your project root folder.
You should see a `speckit-setup` folder appear next to your project files.

**Step 2 – Open a terminal in your project root**
```
cd C:\your-project
```

**Step 3 – Run the script**
```powershell
.\speckit-setup\install-speckit.ps1
```

You should see all files confirmed with `OK`.

**Step 4 – Open Claude Code in your project folder**
Make sure Claude Code is opened at the project root (not inside `speckit-setup`).

**Step 5 – Verify the commands are available**
Open the Claude Code chat panel and type `/speckit` in the message input at the bottom — you should see all five commands appear in the autocomplete list. Do NOT type it in the VS Code search bar or file explorer.

---

## Manual Installation (if the script does not work)

Copy these folders from inside `speckit-setup` into your **project root**:

```
your-project\
├── .claude\
│   └── commands\        <- copy this folder
│       ├── speckit.constitution.md
│       ├── speckit.specify.md
│       ├── speckit.plan.md
│       ├── speckit.tasks.md
│       └── speckit.implement.md
└── .specify\
    └── memory\          <- create this empty folder
```

> **Note:** Folders starting with `.` may be hidden in File Explorer.
> Enable "Show hidden items" under the View menu to see them.

---

## Questions?

Contact your instructor.
