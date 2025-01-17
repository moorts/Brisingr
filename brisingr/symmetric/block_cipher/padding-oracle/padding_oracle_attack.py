from typing import Callable, Self
from Crypto.Util.Padding import unpad

def xor(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])

def oracle() -> tuple[bool, int]:
    raise Exception("Oracle not implemented")


class PaddingOracleAttack:
    def __init__(self, oracle, block_size: int, pt_alphabet=None):
        """Initialize the attack.

        Args:
        - oracle: 
        - ct: Ciphertext. ct = IV || ciphertext
        """
        self.oracle = oracle
        self.block_size = block_size

        self.pt = b""

        # Store DEC(k, self.blocks[i])
        self.decrypted_blocks = []

        self.current_block = 1

        self.pt_alphabet = pt_alphabet
        
        # Initialize telemetry.
        self.oracle_calls = 0
        self.decrypted_bytes = 0

    def decrypt(self, ct: bytes) -> bytes:
        """Execute the attack."""
        assert len(ct) % self.block_size == 0

        num_blocks = len(ct) // self.block_size
        assert num_blocks >= 2 # IV is required.

        blocks = [
            ct[i*self.block_size : (i+1)*self.block_size]
            for i in range(num_blocks)
        ]

        block_idx = 0
        for (IV, ct) in zip(blocks, blocks[1:]):
            final_block = block_idx == num_blocks - 1

            self.log(f"Begin decrypting block {block_idx}.")
            self.pt += self.decrypt_block(IV, ct, final_block=final_block)
            self.log("")
            block_idx += 1

        return unpad(self.pt, self.block_size)

    def encrypt(self, pt: bytes) -> bytes:
        """Encrypt an arbitrary plaintext."""
        assert len(pt) % self.block_size == 0

        num_blocks = len(pt) // self.block_size
        blocks = [
            pt[i:i+self.block_size]
            for i in range(0, len(pt), self.block_size)
        ]

        # Goes from back to front.
        # Final block
        ct = b"\xff" * self.block_size
        dummy_iv = b"\x00" * self.block_size

        for block in blocks[::-1]:
            ct_block = ct[:self.block_size]
            dec = self.decrypt_block(dummy_iv, ct_block)

            ct = xor(block, dec) + ct

        return ct


    def decrypt_block(self, iv, block, final_block=False) -> bytes:
        """Decrypts plaintext block i."""
        self.IV = iv
        self.C = block

        # DEC(k, ct=self.C)
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

            for candidate in self.get_candidate_bytes(final_block):
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

        self.decrypted_blocks.append(decrypted)

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

    def get_candidate_bytes(self, final_block: bool):
        """Compute possible bytes.

        Recall that:
            pt[byte] = candidate ^ byte ^ IV[byte]
        """
        if not self.pt_alphabet:
            return [x for x in range(256)]

        pt_alphabet = self.pt_alphabet

        if final_block:
            # Last block can contain padding.
            pt_alphabet += bytes([i for i in range(self.block_size)])

        candidate_bytes = []

        for x in range(256):
            if x ^ self.pad_value ^ self.IV[self.byte] in pt_alphabet:
                candidate_bytes.append(x)

        return candidate_bytes

    def log(self, msg, end="\n"):
        print(f"[Attack] {msg}", end=end)

