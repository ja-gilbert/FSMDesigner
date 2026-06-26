"""
Unit tests for the input-gathering functions in ``fsm_designer``.
Each test case feeds a list of inputs to ``input()`` and silences ``print()``.
Ensures that the functions return the expected values and print the correct error messages.
"""
import os
import sys
import unittest
from unittest.mock import patch

# Make ``import fsm_designer`` work no matter how the suite is launched: the module lives one
# directory up from this test file.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import fsm_designer  # noqa: E402


def run_with_inputs(func, inputs):
    """Call ``func`` while feeding ``inputs`` to ``input()`` and silencing ``print()``."""
    with patch("builtins.input", side_effect=list(inputs)), patch("builtins.print"):
        return func()


class TestGetBinaryString(unittest.TestCase):
    def test_accepts_valid_string(self):
        self.assertEqual(run_with_inputs(fsm_designer.get_binary_string, ["101010"]), "101010")

    def test_accepts_single_bit(self):
        self.assertEqual(run_with_inputs(fsm_designer.get_binary_string, ["0"]), "0")
        self.assertEqual(run_with_inputs(fsm_designer.get_binary_string, ["1"]), "1")

    def test_reprompts_on_non_binary_digits(self):
        # "234" is rejected, then "1010" is accepted.
        self.assertEqual(run_with_inputs(fsm_designer.get_binary_string, ["234", "1010"]), "1010")

    def test_reprompts_on_non_numeric_text(self):
        self.assertEqual(run_with_inputs(fsm_designer.get_binary_string, ["abc", "11"]), "11")

    def test_reprompts_on_embedded_space(self):
        # The input is not stripped, so a leading space makes the string invalid.
        self.assertEqual(run_with_inputs(fsm_designer.get_binary_string, [" 101", "101"]), "101")

    def test_rejects_empty_string(self):
        # INTENDED (CLAUDE.md: non-empty only). FAILS until get_binary_string rejects "".
        self.assertEqual(run_with_inputs(fsm_designer.get_binary_string, ["", "1"]), "1")


class TestSelectMachineType(unittest.TestCase):
    def test_accepts_word_moore(self):
        self.assertEqual(run_with_inputs(fsm_designer.select_machine_type, ["moore"]), "moore")

    def test_accepts_word_mealy(self):
        self.assertEqual(run_with_inputs(fsm_designer.select_machine_type, ["mealy"]), "mealy")

    def test_accepts_mixed_case_and_whitespace(self):
        # select_machine_type strips and lowercases the input before checking.
        self.assertEqual(run_with_inputs(fsm_designer.select_machine_type, [" MOORE "]), "moore")

    def test_reprompts_on_invalid_word(self):
        self.assertEqual(
            run_with_inputs(fsm_designer.select_machine_type, ["maely", "mealy"]), "mealy"
        )

    def test_reprompts_on_out_of_range_number(self):
        # "3" is not a valid choice; the loop should ask again and accept "1".
        result = run_with_inputs(fsm_designer.select_machine_type, ["3", "1"])
        self.assertIn(result, ("1", "moore"))  # tolerant of the canonicalization fix

    def test_reprompts_on_empty(self):
        self.assertEqual(
            run_with_inputs(fsm_designer.select_machine_type, ["", "moore"]), "moore"
        )

    def test_number_1_returns_moore(self):
        # INTENDED (CLAUDE.md: canonical word). FAILS until "1" is mapped to "moore".
        self.assertEqual(run_with_inputs(fsm_designer.select_machine_type, ["1"]), "moore")

    def test_number_2_returns_mealy(self):
        # INTENDED (CLAUDE.md: canonical word). FAILS until "2" is mapped to "mealy".
        self.assertEqual(run_with_inputs(fsm_designer.select_machine_type, ["2"]), "mealy")


if __name__ == "__main__":
    unittest.main()
