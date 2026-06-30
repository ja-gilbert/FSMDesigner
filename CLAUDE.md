# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

FSM Designer — an interactive tool for building/simulating finite state machines. Early stage: a
Python CLI with a test suite. No external Python dependencies at runtime (stdlib only) and no build
step; `pytest` is the only dev dependency (for tests), listed in `requirements-dev.txt`. Rendering
the state diagram to a PNG additionally uses the Graphviz `dot` **system binary** (optional): if it
is not installed the program still writes the `.dot` source and prints how to install it.

## Run

```bash
python fsm_designer.py
```

The program prompts for a binary string (only `0`/`1`, e.g. `101010`), validates it, then asks
the user to choose **Moore** or **Mealy**. It prints the transition table and then renders the state
diagram: it writes `fsm.dot`, and (if Graphviz `dot` is on PATH) renders `fsm.png` and opens it in
the OS default viewer. To exercise it non-interactively, pipe input:

```bash
printf '101010\nmoore\n' | python fsm_designer.py
```

## Tests

The input/validation functions are covered by `test/test_fsm_inputs.py` (stdlib `unittest`; it mocks
`builtins.input` with a list of values to exercise the re-prompt loops). The Moore/Mealy builders
are covered by `test/test_moore_machine.py` and `test/test_mealy_machine.py` (pytest; they assert on
the state list returned by `build_moore_fsm` / `build_mealy_fsm`). The diagram renderer is covered by
`test/test_diagram.py` (pytest; it asserts on the DOT text from `to_dot`, and has one render smoke
test that is skipped when Graphviz `dot` is absent). Run from the repo root:

```bash
pip install -r requirements-dev.txt   # one-time: installs pytest
python -m pytest -v                   # runs every test (pytest also discovers the unittest suite)
```

The unittest suite can still be run on its own with the stdlib runner:

```bash
python -m unittest discover -s test -p "test_*.py" -v
```

Each test file inserts the repo root onto `sys.path`, so imports work however the suite is launched.

## Architecture

The code is split into small single-purpose modules:

- `fsm_designer.py` — the CLI driver. `get_binary_string()` and `select_machine_type()` handle/
  validate input (re-prompt loops), and `main()` wires them together: it builds the chosen machine,
  prints its table, then renders the diagram.
- `utils.py` — shared helpers: `state_letter` (index → `A`, `B`, … `AA`), `longest_prefix_match`
  (the overlap/"failure" logic that drives transitions), and `validate_binary_seq` (raises
  `ValueError` on empty/non-binary input).
- `moore_machine.py` / `mealy_machine.py` — each exposes `build_*_fsm(seq)` (validates input, returns
  the list of state objects — the pure, tested core), `print_*_table(states)` (the transition-table
  printer), and `generate_*_fsm(seq)` (= build + print).
- `diagram.py` — the state-diagram renderer. `to_dot(states, machine_type)` returns Graphviz DOT text
  (pure, stdlib-only); `render_and_open(states, machine_type, basename="fsm", open_image=True)` writes
  the `.dot`, and if `dot` is on PATH shells out via `subprocess` to render a PNG and opens it,
  degrading gracefully otherwise.

The transition-table and diagram outputs both consume the same `build_*_fsm` state list, so the
builders are the single source of truth for FSM structure.

## Conventions

- User-facing strings use plain ASCII (e.g. `-`, not `—`) because the program targets the Windows
  console, where non-ASCII punctuation renders as `�`.
