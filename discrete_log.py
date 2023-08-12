import math
from typing import Optional

def baby_step_giant_step(g: int, h: int, p: int, N=None) -> int:
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
    giant_step = h
    for i in range(n+1):
        if giant_step in baby_steps:
            return i*n + baby_steps[giant_step]
        giant_step = (giant_step * giant_stepper) % p
    
    raise RuntimeError("Reached unreachable code.")

def prime_power_pohlig_hellman(g: int, h: int, p: int, q: int, e: int) -> int:
    """
    Solve discrete logarithm problem for element with order q^e, q prime

    g^x = h (mod p) and g^(q^e) = 1 (mod p)
    """
    solution = 0

    order = pow(q, e)

    assert((p-1) % order == 0)

    g_inv = pow(g, -1, p)
    g_order_q = pow(g, pow(q, e-1, order), p)

    q_to_the_i = 1

    # rhs = (h*g^(-x_0-x_1q-...-x_{i-1}q^{i-1}))^{q^{e-i-1}}
    rhs = h
    for i in range(e):
        x_i = baby_step_giant_step(g_order_q, pow(rhs, pow(q, e-i-1, order), p), p, N=q)
        rhs = (rhs * pow(g_inv, x_i*q_to_the_i, p)) % p
        solution = (solution + x_i*q_to_the_i) % order
        q_to_the_i = (q_to_the_i * q) % order

    assert(pow(g, solution, p) == h)
    return solution

def solve_congruence_system(rhs, moduli):
    """Solve a system of congruences by the chinese remainder theorem

    Find x so that for each 0 <= i < len(rhs):
    x = rhs[i] (mod moduli[i])

    Args:
        rhs: List of right-hand sides of the congruences
        moduli: Moduli for each of the congruences
    Returns:
        Solution to the system
    """
    solution = rhs[0]
    increment = moduli[0]
    for (current_rhs, modulus) in zip(rhs[1:], moduli[1:]):
        while solution % modulus != current_rhs:
            solution += increment
        increment *= modulus
    return solution % increment


def pohlig_hellman(g: int, h: int, p: int) -> int:
    pass

g = 9704
h = 13896
p = 17389
#print(baby_step_giant_step(g,h,p))
print(prime_power_pohlig_hellman(5448, 6909, 11251, 5, 4))
print(solve_congruence_system([2,3,4], [3,7,16]))
