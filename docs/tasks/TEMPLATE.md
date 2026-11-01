# {{ID}}: {{TITLE}}

- **Phase:** 
- **Owner:** (subagent name, or main)
- **Depends on:** 
- **Reviewer:** (physics-reviewer / security-reviewer / main)

## Goal
One or two sentences on what this task produces and why.

## Interface / contract
Exact function signatures, inputs, outputs, file formats. Copy from the frozen
interface files; don't paraphrase.

```python
def example(arg: type) -> type:
    """What it does."""
```

## Context to read
- `docs/interfaces/...`
- Sample files: `tests/fixtures/...`

## Constraints
- Language, libraries allowed, performance and memory limits
- Where code goes: `folder/file`
- Where tests go: `tests/folder/`

## Acceptance criteria
- [ ] Matches the interface exactly
- [ ] Tests listed below exist and pass via `bash scripts/run-tests.sh`
- [ ] No TODO-LIT / TODO-DECIDE values invented

## Tests that must pass
- `tests/...::test_...`

## Out of scope
What the subagent must NOT touch.

## Report (filled in by the subagent)
- Files changed:
- Tests run and results:
- Assumptions:
- Open questions:
