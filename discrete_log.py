import math
from typing import Optional

def baby_step_giant_step(g: int, b: int, p: int, N=None) -> int:
    """
    Solve discrete logarithm problem using babystep-giantstep algorithm.

    Args:
        g: base
        b: right-hand side
        p: order of finite group
        N: order of g (default to p)

    Returns:
        Solution of g^x = b (mod p) for x.
    """
    if not N:
        N = p
    n = 1 + math.isqrt(N)

    # Baby Steps: {e, g, g^2, ..., g^n}
    baby_steps = { pow(g,j,p) : j for j in range(n+1) }

    g_inv = pow(g, -1, p)

    # g^{-n}
    giant_stepper = pow(g_inv, n, p)

    # Giant Steps: {b, b*g^{-n}, b*g^{-2n}, ..., b*g^{-n^2}}
    giant_step = b
    for i in range(n+1):
        if giant_step in baby_steps:
            return i*n + baby_steps[giant_step]
        giant_step = (giant_step * giant_stepper) % p
    
    raise RuntimeError("Reached unreachable code.")

def pohlig_hellman(g: int, b: int, p: int) -> int:
    pass

g = 9704
b = 13896
p = 17389
print(baby_step_giant_step(g,b,p))
