"""
Tests for the state-diagram renderer in ``diagram``.

``to_dot`` is pure (returns Graphviz DOT text) so it is asserted directly with
no Graphviz binary needed. The render smoke test is skipped when ``dot`` is not
installed, and passes ``open_image=False`` so it never pops a viewer window.
"""
import os
import shutil
import sys

import pytest

# Make top-level imports work no matter how the suite is launched: the modules
# live one directory up from this test file.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from diagram import render_and_open, to_dot  # noqa: E402
from mealy_machine import build_mealy_fsm  # noqa: E402
from moore_machine import build_moore_fsm  # noqa: E402


def test_moore_dot_has_start_accept_and_self_loop():
    dot = to_dot(build_moore_fsm("1011"), "moore")
    assert "digraph FSM {" in dot
    # Start marker points at the first state.
    assert "__start [shape=point];" in dot
    assert "__start -> A;" in dot
    # The accept state (E, output 1) is drawn as a double circle.
    assert 'E [shape=doublecircle' in dot
    # A on input 0 stays in A (self-loop).
    assert 'A -> A [label="0"];' in dot


def test_moore_emits_both_bit_edges_per_state():
    # Each state has exactly one "0" edge and one "1" edge.
    dot = to_dot(build_moore_fsm("1"), "moore")
    assert 'A -> A [label="0"];' in dot
    assert 'A -> B [label="1"];' in dot
    assert 'B -> A [label="0"];' in dot
    assert 'B -> B [label="1"];' in dot


def test_mealy_dot_labels_output_on_edge_and_has_no_doublecircle():
    dot = to_dot(build_mealy_fsm("1011"), "mealy")
    # Mealy puts output on the completing edge: D on 1 emits 1.
    assert 'D -> B [label="1/1"];' in dot
    # No state is an accept state in a Mealy machine.
    assert "doublecircle" not in dot


@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz 'dot' not installed")
def test_render_writes_png(tmp_path):
    states = build_moore_fsm("1011")
    basename = str(tmp_path / "fsm")
    png = render_and_open(states, "moore", basename=basename, open_image=False)
    assert png is not None
    assert os.path.exists(png)
    assert os.path.exists(basename + ".dot")
