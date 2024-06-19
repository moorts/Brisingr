import random


def untwist(outputs: list[int]) -> random.Random:
    """Untwist a mersenne twister.

    Given a sequence of (at least) 624 consecutive outputs of a (32-bit) mersenne twister,
    recover the internal state and return a `random.Random` instance that will have the same state
    as the target.

    Args:
        - outputs: list of (32 bit) integers output by the target twister

    Returns:
        - `random.Random` input with same internal state as target
    """
    assert len(outputs) >= 624

    recovered_state =  [untwist_single_value(x) for x in outputs[-624:]]

    # Need to append size of state at the end (for reasons)
    recovered_state.append(624)

    # Stuff required for Random.setstate
    version = 3
    # No idea what this does or why it exists, don't think it matters to us
    gauss_next = None

    # Initialize cracked twister
    mt = random.Random()
    # Set state to recovered state
    mt.setstate((version, tuple(recovered_state), gauss_next))

    return mt


def untwist_single_value(y: int) -> int:
    y ^= (y >> 18)
    y ^= (y << 15) & 0xefc60000

    # Now the good stuff
    partial_y = y
    
    # Unfurl original y 4 bits at a time
    for i in range(4):
        partial_y = (y ^ ((partial_y << 7) & 0x9d2c5680))

    y = partial_y

    # Again need two steps to recover the last value
    partial_y = (y ^ (partial_y >> 11))
    y = (y ^ (partial_y >> 11))

    return y


def randomized_test():
    import os
    # Reference impl of state to output transform
    def twist_single_value(y: int) -> int:
        y ^= (y >> 11)
        y ^= (y << 7) & 0x9d2c5680
        y ^= (y << 15) & 0xefc60000
        y ^= (y >> 18)

        return y

    num_trials = 1000

    for _ in range(num_trials):
        y = int.from_bytes(os.urandom(4))

        out = twist_single_value(y)
        assert y == untwist_single_value(out)


def untwist_test():
    mt = random.Random()

    outputs = [mt.getrandbits(32) for _ in range(2500)]

    other = untwist(outputs)

    for i in range(2000):
        assert mt.getrandbits(32) == other.getrandbits(32)


randomized_test()
untwist_test()
