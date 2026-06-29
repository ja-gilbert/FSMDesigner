def validate_binary_seq(seq):
    """Raise ValueError unless 'seq' is a non-empty string of only 0s and 1s."""
    if not seq or not all(bit in "01" for bit in seq):
        raise ValueError("seq must be a non-empty binary string (only 0s and 1s).")


def state_letter(i):
    """Convert an index to a state letter (A, B, C, etc.)."""
    name = ""
    while i >= 0:
        name = chr(ord('A') + (i % 26)) + name
        i = i // 26 - 1
    return name
    
def longest_prefix_match(pattern, str_val):
    """Find the longest prefix of 'pattern' that matches a suffix of 'str_val'."""
    max_len = min(len(pattern), len(str_val))
    for i in range(max_len, 0, -1):
        if str_val[-i:] == pattern[:i]:
            return i
    return 0