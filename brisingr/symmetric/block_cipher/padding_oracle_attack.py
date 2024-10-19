from typing import Callable


def xor(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])

def oracle() -> bool:
    raise Exception("Oracle not implemented")

def padding_oracle_attack(oracle: Callable[[bytes], bool], ct: bytes, block_size: int):
    num_blocks = len(ct) // block_size

    assert num_blocks >= 2
    assert len(ct) % block_size == 0

    blocks = [ct[i*block_size:(i+1)*block_size] for i in range(num_blocks)]

    pt = b""

    for c0, c1 in zip(blocks, blocks[1:]):
        pt_block = b""

        for byte in range(1, block_size + 1):
            for candidate in range(256):
                padding = bytes([len(pt_block) + 1] * len(pt_block))
                c0_prime = c0[:-byte] + bytes([candidate]) + xor(pt_block, padding)

                if oracle(c0_prime + c1):
                    pad_value = len(pt_block) + 1
                    # Found candidate that produces valid padding
                    if byte == 1:
                        # Calculate length of padding
                        for i in range(2, 16):
                            start = c0_prime[:-i]
                            c0_prime = start + bytes([c0[-i] ^ 1]) + c0_prime[1-i:]
                            if oracle(c0_prime + c1):
                                # Byte 16 - i is not part of the padding
                                pad_value = i - 1
                                break
                    pt_block = bytes([pad_value ^ candidate]) + pt_block
                    break
        pt += pt_block
    return pt
