# FSM Designer

A command-line finite state machine (FSM) designer for binary sequence detectors. Give it a bit
pattern such as `1101` and it builds the Moore or Mealy machine that recognises that pattern in a
stream of bits, prints the transition table, and draws the state diagram with Graphviz.

## Features

- Builds a **Moore** or **Mealy** sequence detector for any binary pattern.
- Handles **overlapping matches** - after a hit the machine falls back to the longest prefix of the
  pattern that is still matched, so a `11` detector fires on every `1` after the first in `1111`.
- Prints the **transition table** for the machine it built.
- Renders the **state diagram** with Graphviz (`fsm.dot` + `fsm.png`) and opens the image.
- Standard library only - no runtime dependencies.

## Requirements

- Python 3.
- [Graphviz](https://graphviz.org/download/) *(optional)* - the `dot` command, for rendering the
  PNG. Without it the program still writes `fsm.dot` and prints how to install Graphviz.

## Usage

```bash
python fsm_designer.py
```

The program asks two questions:

1. **Binary string** - the pattern to detect, using only `0` and `1` (e.g. `101010`). Anything
   else is rejected and the prompt repeats.
2. **Machine type** - `1` / `moore` or `2` / `mealy` (case-insensitive).

It then prints the transition table, writes `fsm.dot` to the current directory and, if Graphviz is
installed, renders `fsm.png` and opens it in your default image viewer.

To run it non-interactively, pipe the answers in:

```bash
printf '1101\nmoore\n' | python fsm_designer.py
```

### Example: Moore detector for `1101`

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

`W` is the input bit and `Z` is the output. State `A` is the start state (nothing matched yet) and
each later state means one more bit of the pattern has been matched, so `E` means all of `1101`
has been seen. In a Moore machine the output belongs to the state, so the table has a single `Z`
column and only `E` outputs `1`.

### Example: Mealy detector for `1101`

```
Transition Table (Mealy)
-----------------------------------------------------
State   W=0 -> Next     W=1 -> Next     Z(0 1)
-----------------------------------------------------
A       A               B               0 0
B       A               C               0 0
C       D               C               0 0
D       A               B               0 1
```

In a Mealy machine the output belongs to the transition, so the table shows `Z(0 1)` - the output
emitted on input `0` and on input `1`. The Mealy version needs one state fewer: the final `1` seen
from state `D` emits the `1` on the edge itself instead of entering a separate accepting state.

### The state diagram

`fsm.png` is the visual twin of the table: states are circles, transitions are labelled arrows
(including self-loops), and an arrow from nowhere marks the start state. For Moore machines each
state is labelled `name / output` and output-`1` states are drawn as double circles; for Mealy
machines each edge is labelled `input/output`.

## How it works

Both machines are built the same way. State `i` means "the last `i` bits seen are the first `i`
bits of the pattern". For each state and each input bit, the builder appends the bit to the matched
prefix and finds the longest prefix of the pattern that is a suffix of the result - that length is
the next state. This is the same overlap ("failure") logic used by string-matching algorithms, and
it is what makes overlapping matches work without special cases.

## Tests

`pytest` is the only development dependency. Run from the repo root:

```bash
pip install -r requirements-dev.txt   # one-time
python -m pytest -v
```

| Test file | Covers |
| --- | --- |
| `test/test_fsm_inputs.py` | Input prompts and validation (stdlib `unittest`) |
| `test/test_moore_machine.py`, `test/test_mealy_machine.py` | Hand-checked machines from the builders |
| `test/test_diagram.py` | The DOT text, plus a render smoke test (skipped without Graphviz) |
| `test/test_reference_model.py` | Both builders against a brute-force reference model - exhaustively for every pattern up to 4 bits against every input stream up to 10 bits, and on seeded random streams for every pattern up to 8 bits |

## Project layout

| File | Role |
| --- | --- |
| `fsm_designer.py` | CLI entry point: prompts, then builds, prints and renders |
| `utils.py` | Shared helpers: state naming, prefix-overlap logic, input validation |
| `moore_machine.py` / `mealy_machine.py` | Build the state list and print the transition table |
| `diagram.py` | Turns a state list into Graphviz DOT, renders and opens the PNG |
| `test/` | Test suite (see above) |

The transition table and the diagram are both generated from the same `build_*_fsm` state list, so
the builders are the single source of truth for FSM structure. The generated `fsm.dot` and
`fsm.png` are git-ignored.

## License

[MIT](LICENSE)
