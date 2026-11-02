# Nuclear@Home — Claude Code environment

A ready-made Claude Code project for building **Nuclear@Home**, a BOINC volunteer
computing project that simulates radiation damage in fusion materials and estimates
how much tritium gets trapped in reactor walls.

This folder contains the project rules, the main agent's brief, 11 specialist
subagents, draft interface specs, a task-card system, safety hooks, and a reference
PPD implementation with tests. It contains no simulation code yet: Claude Code builds
that with you, phase by phase.

## What's inside

```
nuclear-at-home/
├── CLAUDE.md                     Rules every agent follows
├── PROMPT.md                     The main agent's full brief
├── README.md                     This file
├── .claude/
│   ├── settings.json             Permissions + frozen-interface hook
│   └── agents/                   11 subagents (builders + reviewers)
├── docs/
│   ├── interfaces/               Draft contracts (freeze in Phase 2)
│   └── tasks/                    TEMPLATE.md, TRACKER.md, example card
├── scripts/
│   ├── guard_frozen.py           Blocks edits to FROZEN interface files
│   ├── run-tests.sh              Runs the test suite
│   └── new-task.sh               Creates a numbered task card
├── stats/ppd.py                  Reference credit/PPD math
├── tests/stats/test_ppd.py       Tests for it
└── server/ client/ validator/ viewer/ analysis/   (empty, built in later phases)
```

## Setup (about 5 minutes)

1. **Install Claude Code** if you haven't: see https://code.claude.com/docs
2. **Unzip** this folder somewhere, then open a terminal in it.
3. **Make it a git repo** (required: builder subagents work in isolated git worktrees):
   ```bash
   git init
   git add .
   git commit -m "Nuclear@Home Claude Code environment"
   ```
4. **Check the tests run:**
   ```bash
   bash scripts/run-tests.sh
   ```
5. **Start Claude Code** in the folder:
   ```bash
   claude
   ```
   Accept the workspace trust prompt so the project hooks and subagents load.
6. **Kick off the project** by typing:
   ```
   Read PROMPT.md and CLAUDE.md, then begin Phase 1.
   ```

## The agent team

| Subagent | Model | Can edit? | Job |
|---|---|---|---|
| `wu-template-writer` | sonnet | yes (worktree) | LAMMPS templates, sample WUs, samplers |
| `client-helper` | sonnet | yes (worktree) | LAMMPS input logic, job.xml, LAMMPS build, output parsing |
| `validator-check-writer` | sonnet | yes (worktree) | Individual validator checks |
| `stats-builder` | sonnet | yes (worktree) | Stats SQL, credit/PPD/badges, XML export, API |
| `viewer-builder` | sonnet | yes (worktree) | Three.js viewer, dashboard UI |
| `analysis-builder` | sonnet | yes (worktree) | Defect counting, clusters, plots |
| `test-writer` | haiku | yes | Mock data, unit and load tests |
| `docs-writer` | haiku | yes | Volunteer FAQ, guides, explainers |
| `lit-researcher` | sonnet | no (writes notes only) | Finds papers, potentials, benchmarks |
| `physics-reviewer` | opus | no | Reviews physics, validation, credit |
| `security-reviewer` | opus | no | Reviews server, signing, privacy |

The main session (you + Claude Code) is the main agent. It plans, freezes interfaces,
writes task cards, delegates, reviews, and merges.

## Using it day to day

- **Delegate by name:** `Use stats-builder for docs/tasks/T-012.md`
- **Guarantee a specific agent:** type `@` and pick it, e.g. `@"viewer-builder (agent)" do T-020`
- **Run in parallel:** `Run T-010, T-011 and T-020 in parallel with their subagents`
- **Build then review:** `Have validator-check-writer do T-030, then physics-reviewer review it`
- **See what's running and on which model:** `/tasks`
- **New task card:** `bash scripts/new-task.sh "Energy conservation check"`

## Frozen interfaces

Files in `docs/interfaces/` start as **DRAFT**. In Phase 2 the main agent finalizes
them, you approve, and you freeze each one outside Claude Code:

```bash
# set the file's status line to FROZEN, then:
sha256sum docs/interfaces/<file> >> docs/interfaces/FROZEN.sha256
git commit -am "Freeze <file>"
```

The hook in `scripts/guard_frozen.py` then blocks agent Edit/Write on frozen files, and
after every agent Bash command it re-checks all frozen files against the manifest. The
test suite runs the same check, which catches changes arriving through merges. To change a
frozen file, set its status back to DRAFT, delete its manifest line, and commit.

## Things only you should do

- Fill in every `TODO-LIT` placeholder from real papers
- Approve physics settings, validator thresholds, and credit calibration
- Keep the BOINC code-signing key offline (never in this repo)
- Review anything before it's published or announced

## Cost tip

Every subagent uses your Claude usage limits. Most builders run on Sonnet or Haiku;
only the two reviewers use Opus. Change any agent's `model:` line to adjust.
