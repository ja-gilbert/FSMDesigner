"""
Tests for the Mealy sequence-detector builder in ``mealy_machine``.
``build_mealy_fsm`` returns the list of states (without printing); these tests
assert on that returned structure - the transitions and per-edge outputs.
"""
import os
import sys

import pytest

# Make ``import mealy_machine`` work no matter how the suite is launched: the module lives one
# directory up from this test file.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mealy_machine import build_mealy_fsm  # noqa: E402


# The detector for "1011" has 4 states (A..D). Expected transitions and the
# per-edge outputs (outputOn0, outputOn1) for each state, in order.
#   name: (nextOn0, nextOn1, outputOn0, outputOn1)
EXPECTED_1011 = {
    "A": ("A", "B", 0, 0),
    "B": ("C", "B", 0, 0),
    "C": ("A", "D", 0, 0),
    "D": ("C", "B", 0, 1),  # completing "1011" on a 1 emits output 1
}


def test_state_names_and_matched_prefixes():
    states = build_mealy_fsm("1011")
    assert [s.name for s in states] == ["A", "B", "C", "D"]
    # Each state i represents having matched the first i chars of the pattern.
    assert [s.matched for s in states] == ["", "1", "10", "101"]


@pytest.mark.parametrize("name,nextOn0,nextOn1,outputOn0,outputOn1", [
    (name, *vals) for name, vals in EXPECTED_1011.items()
])
def test_transitions_and_outputs_for_1011(name, nextOn0, nextOn1, outputOn0, outputOn1):
    states = {s.name: s for s in build_mealy_fsm("1011")}
    state = states[name]
    assert state.nextOn0 == nextOn0
    assert state.nextOn1 == nextOn1
    assert state.outputOn0 == outputOn0
    assert state.outputOn1 == outputOn1


def test_output_one_only_on_completing_edge():
    # The Mealy detector should emit 1 on exactly one edge: D on input 1.
    states = build_mealy_fsm("1011")
    ones = [(s.name, bit) for s in states for bit, out in
            (("0", s.outputOn0), ("1", s.outputOn1)) if out == 1]
    assert ones == [("D", "1")]


@pytest.mark.parametrize("seq,expected_states", [
    ("1", 1),
    ("11", 2),
    ("1011", 4),
])
def test_state_count_matches_pattern_length(seq, expected_states):
    # A Mealy detector has one state per pattern character (n states).
    assert len(build_mealy_fsm(seq)) == expected_states


def test_single_bit_pattern():
    # "1": one state A; a 1 completes the pattern (output 1), a 0 stays put.
    states = build_mealy_fsm("1")
    assert len(states) == 1
    a = states[0]
    assert a.name == "A"
    assert (a.nextOn0, a.outputOn0) == ("A", 0)
    assert a.outputOn1 == 1


def test_overlapping_pattern():
    # "11" exercises longest_prefix_match: after matching one 1 (state B), another
    # 1 completes the pattern (output 1) while overlapping back into B.
    states = {s.name: s for s in build_mealy_fsm("11")}
    assert states["A"].nextOn1 == "B"
    assert states["B"].nextOn1 == "B"
    assert states["B"].outputOn1 == 1
    # A 0 from either state resets to the start (no progress matched).
    assert states["A"].nextOn0 == "A"
    assert states["B"].nextOn0 == "A"


@pytest.mark.parametrize("bad", ["", "abc", "012", " 10", "10 ", "2"])
def test_rejects_non_binary_seq(bad):
    # The builder validates its own input rather than producing a degenerate machine.
    with pytest.raises(ValueError):
        build_mealy_fsm(bad)
