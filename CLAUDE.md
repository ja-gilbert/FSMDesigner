# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

FSM Designer — an interactive tool for building/simulating finite state machines. Early stage: a
single-file Python CLI with a `unittest` test suite. No external dependencies (stdlib only) and no
build step.

## Run

```bash
python fsm_designer.py
```

The program prompts for a binary string (only `0`/`1`, e.g. `101010`), validates it, then asks
the user to choose **Moore** or **Mealy**. To exercise it non-interactively, pipe input:

```bash
printf '101010\nmoore\n' | python fsm_designer.py
```

## Tests

The input/validation functions are covered by `test/test_fsm_inputs.py` (stdlib `unittest`; it mocks
`builtins.input` with a list of values to exercise the re-prompt loops). Run from the repo root:

```bash
python -m unittest discover -s test -p "test_*.py" -v
```

The test file inserts the repo root onto `sys.path`, so running the file directly
(`python test/test_fsm_inputs.py`) works too.

## Architecture

Everything lives in `fsm_designer.py`, structured as small single-purpose functions composed by
`main()`:

- `get_binary_string()` — re-prompts until a non-empty `0`/`1`-only string is entered.
- `select_machine_type()` — re-prompts until the user picks Moore or Mealy; accepts the word or
  `1`/`2`, returns the canonical `"moore"`/`"mealy"`.
- `main()` — wires the two prompts together, then dispatches to "run the machine".

The dispatch in `main()` is currently a **placeholder** — it just prints a `Running {machine_type}
machine with input: ...` line instead of running anything. This is the intended seam for the next
stage of work: the real Moore/Mealy simulation should be implemented in separate modules (e.g.
`moore.py` / `mealy.py`) and called from `main()`, keeping `fsm_designer.py` as the
input/validation/menu driver. (Moore-machine work is underway on the `feature/moore_machines`
branch.)

## Conventions

- User-facing strings use plain ASCII (e.g. `-`, not `—`) because the program targets the Windows
  console, where non-ASCII punctuation renders as `�`.
