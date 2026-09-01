# FSM Designer

A finite state machine (FSM) designer - give it a binary pattern and it builds the sequence
detector that recognises it, prints the transition table, and draws the state diagram.

> 🚧 Early work in progress.

## Features

- Builds a **Moore** or **Mealy** sequence detector for any binary pattern.
- Handles **overlapping matches** - after a hit, the machine falls back to the longest prefix of the
  pattern that is still matched, so `11` fires on every `1` after the first in `1111`.
- Prints the **transition table** for the machine it built.
- Renders the **state diagram** with Graphviz (`fsm.dot` + `fsm.png`) and opens the image.

## Requirements

- Python 3 - no runtime dependencies, stdlib only.
- [Graphviz](https://graphviz.org/download/) *(optional)* - the `dot` system binary, for PNG
  rendering. Without it the program still writes `fsm.dot` and tells you how to install Graphviz.

## Getting Started

```bash
python fsm_designer.py
```

It prompts for a binary string (only `0`/`1`), then for the machine type. To run it
non-interactively, pipe the answers in:

```bash
printf '1101\nmoore\n' | python fsm_designer.py
```

```
Transition Table (Moore)
-----------------------------------------------------
State   W=0 -> Next     W=1 -> Next     Z
-----------------------------------------------------
A       A               B               0
B       A               C               0
C       D               C               0
D       A               E               0
E       A               C               1
Wrote DOT source to fsm.dot
Rendered diagram to fsm.png
```

State `A` is the start state (nothing matched yet) and `E` is the accepting state (all of `1101`
matched). In the Moore table `Z` is the output of the state itself; the Mealy table instead shows
`Z(0 1)` - the output emitted on input `0` and on input `1`.

## Tests

`pytest` is the only dev dependency. Run from the repo root:

```bash
pip install -r requirements-dev.txt   # one-time
python -m pytest -v
```

| Test file | Covers |
| --- | --- |
| `test/test_fsm_inputs.py` | Input prompts and validation (stdlib `unittest`) |
| `test/test_moore_machine.py`, `test/test_mealy_machine.py` | Hand-checked machines from the builders |
| `test/test_diagram.py` | The DOT text, plus a render smoke test (skipped without Graphviz) |
| `test/test_reference_model.py` | Both builders vs. a brute-force reference model - exhaustively for every pattern up to 4 bits against every input stream up to 10 bits, and on seeded random streams for every pattern up to 8 bits |

## Project Layout

| File | Role |
| --- | --- |
| `fsm_designer.py` | CLI entry point: prompts, then builds, prints and renders |
| `utils.py` | Shared helpers: state naming, prefix-overlap logic, input validation |
| `moore_machine.py` / `mealy_machine.py` | Build the state list and print the transition table |
| `diagram.py` | Turns a state list into Graphviz DOT, renders and opens the PNG |

The transition table and the diagram are both generated from the same `build_*_fsm` state list, so
the builders are the single source of truth for FSM structure.

## License

[MIT](LICENSE)
