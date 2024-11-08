from typing import Callable, Self
from Crypto.Util.Padding import unpad

def xor(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])

def oracle() -> tuple[bool, int]:
    raise Exception("Oracle not implemented")

def padding_oracle_attack(oracle: Callable[[bytes], bool], ct: bytes, block_size: int):
    num_blocks = len(ct) // block_size

    assert num_blocks >= 2
    assert len(ct) % block_size == 0

    blocks = [ct[i*block_size:(i+1)*block_size] for i in range(num_blocks)]

    pt = b""
    decrypted_blocks = 0

    for c0, c1 in zip(blocks, blocks[1:]):
        print(f"[Status] Decrypting block {decrypted_blocks+1}.")
        print("[Status] Progress: 0/16, Plaintext: ", end="\r", flush=True)

        pt_block = b""

        for byte in range(1, block_size + 1):
            for candidate in range(256):
                # if byte == 1 and candidate == c0[-1]:
                #    continue
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
                    print(pad_value)
                    pt_block = bytes([pad_value ^ candidate]) + pt_block

                    print(f"[Status] Progress: {len(pt_block)}/16, Plaintext: {xor(pt_block, c0[-byte:])}", end="\r", flush=True)
                    break
            else:
                print("WTF")
        print(f"[Status] Progress: 16/16, Plaintext: {xor(pt_block, c0)}")
        print(xor(pt_block, c0))

        pt += xor(pt_block, c0)
        decrypted_blocks += 1
    return pt


class PaddingOracleAttack:
    def __init__(self, oracle, ct: bytes, block_size: int, pt_alphabet=None):
        """Initialize the attack.

        Args:
        - oracle: 
        - ct: Ciphertext. ct = IV || ciphertext
        """
        self.oracle = oracle
        self.block_size = block_size

        self.num_blocks = len(ct) // self.block_size

        assert self.num_blocks >= 2
        assert len(ct) % self.block_size == 0

        self.blocks = [
            ct[i*self.block_size : (i+1)*self.block_size]
            for i in range(self.num_blocks)
        ]

        self.ct = ct
        self.pt = b""

        self.current_block = 1

        self.pt_alphabet = pt_alphabet
        
        # Initialize telemetry.
        self.oracle_calls = 0
        self.decrypted_bytes = 0
        self.decrypted_blocks = 0

    def decrypt(self) -> bytes:
        """Execute the attack.
        """

        for i in range(self.num_blocks - 1):
            self.log(f"Begin decrypting block {i}.")
            self.pt += self.decrypt_block(i)
            self.log("")
            self.current_block += 1

        return unpad(self.pt, self.block_size)

    def decrypt_block(self, i) -> bytes:
        """Decrypts plaintext block i."""
        self.IV = self.blocks[i]
        self.C = self.blocks[i+1]

        # DEC(k, iv=self.IV, ct=self.C)
        decrypted = b""
        # Plaintext block
        pt_block = b""
        
        # Start with last byte of block.
        self.byte = self.block_size - 1

        self.pad_value = 1

        while self.byte >= 0:
            prefix = self.IV[:self.byte]
            padding = bytes([self.pad_value for _ in range(len(decrypted))])
            suffix = xor(decrypted, padding)

            for candidate in self.get_candidate_bytes():
                IV_prime = prefix + bytes([candidate]) + suffix

                is_valid_padding, queries = self.oracle(IV_prime + self.C)

                self.oracle_calls += queries

                if is_valid_padding:
                    # Found valid candidate byte.
                    if self.byte == self.block_size - 1:
                        fake_pt_value = self.resolve_first_byte(candidate)
                        decrypted_byte = fake_pt_value ^ candidate

                        # But we actually know more here. Do this later.
                    else:
                        decrypted_byte = self.pad_value ^ candidate

                    decrypted = bytes([decrypted_byte]) + decrypted
                    pt_block = bytes([decrypted_byte ^ self.IV[self.byte]]) + pt_block

                    self.log(f"Plaintext: {pt_block}", end="\r")

                    self.pad_value += 1
                    self.byte -= 1
                    break
            else:
                self.log(f"No valid candidate for byte {self.byte}.")
                return pt_block

        return pt_block
                    


    def resolve_first_byte(self, candidate):
        """The first decrypted byte (last byte of a block)
        needs special treatment.
        """

        for i in range(2, self.block_size):
            prefix = self.IV[:-i]

            suffix = self.IV[1-i:-1] + bytes([candidate])

            IV_prime = prefix + bytes([self.IV[-i] ^ 1]) + suffix

            is_valid_padding, queries = self.oracle(IV_prime + self.C)

            self.oracle_calls += queries

            if is_valid_padding:
                # Found first byte that is not part of the padding.
                return i - 1

        # I think this is unreachable.
        return self.block_size

    def get_candidate_bytes(self):
        """Compute possible bytes.

        Recall that:
            pt[byte] = candidate ^ byte ^ IV[byte]
        """
        if not self.pt_alphabet:
            return [x for x in range(256)]

        pt_alphabet = self.pt_alphabet

        if self.current_block == self.num_blocks - 1:
            # Last block can contain padding.
            pt_alphabet += bytes([i for i in range(self.block_size)])

        candidate_bytes = []

        for x in range(256):
            if x ^ self.pad_value ^ self.IV[self.byte] in pt_alphabet:
                candidate_bytes.append(x)

        return candidate_bytes

    def log(self, msg, end="\n"):
        print(f"[Attack] {msg}", end=end)

