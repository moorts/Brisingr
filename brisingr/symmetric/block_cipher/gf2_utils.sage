def is_power_of_two(x):
    return (x & (x - 1)) == 0 and x != 0


def lift_bytes(field, x: bytes):
    return field.from_integer(int.from_bytes(x))
