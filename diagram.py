"""
State-diagram renderer for FSM Designer.

The visual twin of the transition table: states are circles, transitions are
labeled directed arrows (with self-loops), the start state has an incoming
arrow from nowhere, and Moore output states are drawn as double circles.

``to_dot`` turns a built state list into Graphviz DOT text (stdlib only).
``render_and_open`` writes that text and, if the Graphviz ``dot`` binary is
available, renders a PNG and opens it. Without ``dot`` it degrades to leaving
the ``.dot`` file behind with a clear message - no runtime pip dependency.
"""

import os
import shutil
import subprocess
import sys


def to_dot(states, machine_type) -> str:
    """Return Graphviz DOT text for the built FSM ``states``.

    ``machine_type`` is ``"moore"`` or ``"mealy"`` and selects how outputs are
    drawn: Moore puts the output in the state (and double-circles output-1
    states), Mealy puts it on the edge as ``input/output``.
    """
    lines = ["digraph FSM {", "    rankdir=LR;", '    node [shape=circle];']

    # Start marker: an invisible point with an arrow into the start state.
    start = states[0].name
    lines.append("    __start [shape=point];")
    lines.append(f"    __start -> {start};")

    # Note: a prefix detector's two outgoing bits always lead to different
    # states (only one bit can extend/overlap the matched prefix), so each
    # state always emits two distinct edges.
    if machine_type == "moore":
        # Node declarations: label "name / output", double-circle output states.
        for s in states:
            shape = "doublecircle" if s.output == 1 else "circle"
            lines.append(f'    {s.name} [shape={shape}, label="{s.name}\\n/{s.output}"];')
        # Edges labeled with the input bit (output lives in the state).
        for s in states:
            lines.append(f'    {s.name} -> {s.nextOn0} [label="0"];')
            lines.append(f'    {s.name} -> {s.nextOn1} [label="1"];')
    else:  # mealy
        # Edges labeled input/output (output lives on the edge).
        for s in states:
            lines.append(f'    {s.name} -> {s.nextOn0} [label="0/{s.outputOn0}"];')
            lines.append(f'    {s.name} -> {s.nextOn1} [label="1/{s.outputOn1}"];')

    lines.append("}")
    return "\n".join(lines) + "\n"


def _open_image(path):
    """Open ``path`` in the OS default viewer (best effort, never raises)."""
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # noqa: S606 - Windows-only, opens default viewer
        elif sys.platform == "darwin":
            subprocess.run(["open", path], check=False)
        else:
            subprocess.run(["xdg-open", path], check=False)
    except OSError as exc:
        print(f"Could not open {path} automatically: {exc}")


def render_and_open(states, machine_type, basename="fsm", open_image=True):
    """Write ``basename.dot`` and, if Graphviz ``dot`` is available, render and
    open ``basename.png``. Returns the PNG path, or ``None`` if ``dot`` is
    missing (the ``.dot`` file is still written either way).
    """
    dot_path = f"{basename}.dot"
    with open(dot_path, "w", encoding="ascii") as f:
        f.write(to_dot(states, machine_type))
    print(f"Wrote DOT source to {dot_path}")

    if shutil.which("dot") is None:
        print("Graphviz 'dot' not found on PATH - install Graphviz to render the diagram "
              "(https://graphviz.org/download/).")
        return None

    png_path = f"{basename}.png"
    subprocess.run(["dot", "-Tpng", dot_path, "-o", png_path], check=True)
    print(f"Rendered diagram to {png_path}")
    if open_image:
        _open_image(png_path)
    return png_path
