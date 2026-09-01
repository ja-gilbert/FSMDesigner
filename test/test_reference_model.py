"""
Reference-model tests for the Moore and Mealy sequence-detector builders.

The builder tests pin down a few hand-checked machines. These tests instead
check every machine the builders can produce (up to a fixed pattern length)
against an independent, brute-force definition of a sequence detector:

    after consuming bit t, the output is 1  <=>  the input so far ends with the pattern

That definition allows overlapping matches (pattern "11" fires on every 1 after
the first in "1111"), which is exactly what the prefix-fallback transitions in
``utils.longest_prefix_match`` are supposed to implement. If the builders and
the brute-force model ever disagree, the failing pattern and stream are shown.

Two layers:
  * exhaustive - every pattern up to EXHAUSTIVE_PATTERN_LEN bits against every
    input stream up to EXHAUSTIVE_STREAM_LEN bits (no randomness at all);
  * randomized - every pattern up to MAX_PATTERN_LEN bits against seeded
    streams built from the pattern, its prefixes, near-misses, and noise, so
    overlaps and partial matches actually occur.
"""
import itertools
import os
import random
import sys

import pytest

# Make top-level imports work no matter how the suite is launched: the modules
# live one directory up from this test file.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mealy_machine import build_mealy_fsm  # noqa: E402
from moore_machine import build_moore_fsm  # noqa: E402

EXHAUSTIVE_PATTERN_LEN = 4   # 2 + 4 + 8 + 16 = 30 patterns
EXHAUSTIVE_STREAM_LEN = 10   # every stream of 1..10 bits = 2046 streams per pattern
MAX_PATTERN_LEN = 8          # 2 + 4 + ... + 256 = 510 patterns
STREAMS_PER_PATTERN = 20
STREAM_LEN = 64


# ---------------------------------------------------------------------------
# Reference model and simulators
# ---------------------------------------------------------------------------

def all_patterns(max_len):
    """Every binary pattern of length 1..max_len, shortest first."""
    for n in range(1, max_len + 1):
        for bits in itertools.product("01", repeat=n):
            yield "".join(bits)


def reference_outputs(pattern, stream):
    """Brute force: output 1 at every position where the stream so far ends with the pattern."""
    return [1 if stream[: t + 1].endswith(pattern) else 0 for t in range(len(stream))]


def run_moore(states, stream):
    """Feed ``stream`` through a built Moore machine; return the output after each bit."""
    by_name = {s.name: s for s in states}
    state = states[0]
    outputs = []
    for bit in stream:
        state = by_name[state.nextOn0 if bit == "0" else state.nextOn1]
        outputs.append(state.output)
    return outputs


def run_mealy(states, stream):
    """Feed ``stream`` through a built Mealy machine; return the output emitted on each bit."""
    by_name = {s.name: s for s in states}
    state = states[0]
    outputs = []
    for bit in stream:
        if bit == "0":
            outputs.append(state.outputOn0)
            state = by_name[state.nextOn0]
        else:
            outputs.append(state.outputOn1)
            state = by_name[state.nextOn1]
    return outputs


MACHINES = [
    pytest.param(build_moore_fsm, run_moore, id="moore"),
    pytest.param(build_mealy_fsm, run_mealy, id="mealy"),
]


def build_stream(pattern, rng, length):
    """A stream that deliberately contains the pattern, its prefixes, near-misses, and noise."""
    parts = []
    total = 0
    while total < length:
        roll = rng.random()
        if roll < 0.4:
            part = pattern
        elif roll < 0.6:
            part = pattern[: rng.randint(1, len(pattern))]          # partial match
        elif roll < 0.7:
            i = rng.randrange(len(pattern))                          # one bit flipped
            part = pattern[:i] + ("1" if pattern[i] == "0" else "0") + pattern[i + 1:]
        else:
            part = "".join(rng.choice("01") for _ in range(rng.randint(1, 4)))
        parts.append(part)
        total += len(part)
    return "".join(parts)[:length]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("build, run", MACHINES)
@pytest.mark.parametrize("pattern", list(all_patterns(MAX_PATTERN_LEN)))
def test_every_transition_targets_an_existing_state(build, run, pattern):
    # Structural sanity: the machine is closed (no dangling next-state names) and
    # the start state is the empty-prefix state.
    states = build(pattern)
    names = {s.name for s in states}
    assert states[0].matched == ""
    for s in states:
        assert s.nextOn0 in names, f"{pattern}: {s.name} --0--> {s.nextOn0} is not a state"
        assert s.nextOn1 in names, f"{pattern}: {s.name} --1--> {s.nextOn1} is not a state"


@pytest.mark.parametrize("build, run", MACHINES)
@pytest.mark.parametrize("pattern", list(all_patterns(EXHAUSTIVE_PATTERN_LEN)))
def test_matches_reference_model_exhaustively(build, run, pattern):
    states = build(pattern)
    for length in range(1, EXHAUSTIVE_STREAM_LEN + 1):
        for bits in itertools.product("01", repeat=length):
            stream = "".join(bits)
            assert run(states, stream) == reference_outputs(pattern, stream), (
                f"pattern={pattern} stream={stream}"
            )


@pytest.mark.parametrize("build, run", MACHINES)
@pytest.mark.parametrize("pattern", list(all_patterns(MAX_PATTERN_LEN)))
def test_matches_reference_model_on_random_streams(build, run, pattern):
    # Seed from the pattern so each case is reproducible on its own.
    rng = random.Random(pattern)
    states = build(pattern)
    for _ in range(STREAMS_PER_PATTERN):
        stream = build_stream(pattern, rng, STREAM_LEN)
        assert run(states, stream) == reference_outputs(pattern, stream), (
            f"pattern={pattern} stream={stream}"
        )
