import argparse
import hashlib
import hmac
from hashlib import pbkdf2_hmac
import struct
import base58
from ecdsa import SigningKey, SECP256k1
from ecdsa.util import number_to_string

def derive_bip39_seed(mnemonic: str, passphrase: str = "") -> str:
    """
    Derive a 512-bit seed from a BIP-39 mnemonic phrase and optional passphrase.

    Args:
        mnemonic (str): The 24-word mnemonic phrase.
        passphrase (str): Optional passphrase (default is "").

    Returns:
        str: The derived 512-bit seed as a hexadecimal string.
    """
    # Ensure the mnemonic and passphrase are valid strings
    if not isinstance(mnemonic, str) or not mnemonic:
        raise ValueError("Mnemonic must be a non-empty string.")

    if not isinstance(passphrase, str):
        raise ValueError("Passphrase must be a string.")

    # The salt is "mnemonic" + passphrase
    salt = "mnemonic" + passphrase

    # Use PBKDF2 with HMAC-SHA512 to derive the seed
    seed = pbkdf2_hmac(
        hash_name="sha512",
        password=mnemonic.encode("utf-8"),  # Convert mnemonic to bytes
        salt=salt.encode("utf-8"),          # Convert salt to bytes
        iterations=2048,                     # Standard number of iterations
        dklen=64                             # Desired key length in bytes (512 bits)
    )

    # Return the seed as a hexadecimal string
    return seed.hex()

def derive_bip32_root_key(seed: str) -> (str, str):
    """
    Derive the BIP-32 Root Key (xprv format) and fingerprint from the BIP-39 seed.

    Args:
        seed (str): The 512-bit seed as a hexadecimal string.

    Returns:
        tuple: (BIP-32 Root Key (xprv format), Root Fingerprint).
    """
    # Convert the seed from hex to bytes
    seed_bytes = bytes.fromhex(seed)

    # HMAC-SHA512 with key "Bitcoin seed"
    hmac_result = hmac.new(
        key=b"Bitcoin seed",
        msg=seed_bytes,
        digestmod=hashlib.sha512
    ).digest()

    # Split the HMAC result into Master Private Key and Chain Code
    master_private_key = hmac_result[:32]
    master_chain_code = hmac_result[32:]

    # Calculate the root fingerprint
    public_key = derive_public_key(master_private_key)
    fingerprint = hashlib.new('ripemd160', hashlib.sha256(public_key).digest()).digest()[:4].hex()

    # Create the serialized BIP-32 root key (xprv)
    version = b"\x04\x88\xad\xe4"  # Version for mainnet private keys (xprv)
    depth = b"\x00"  # Depth is 0 for master keys
    parent_fingerprint = b"\x00\x00\x00\x00"  # No parent, so fingerprint is 0
    child_number = b"\x00\x00\x00\x00"  # Master key is at index 0

    # Construct the payload
    payload = (
        version +
        depth +
        parent_fingerprint +
        child_number +
        master_chain_code +
        b"\x00" + master_private_key  # Prepend 0x00 to the private key
    )

    # Calculate the checksum
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]

    # Base58 encode the result
    xprv = base58.b58encode(payload + checksum).decode("utf-8")

    return xprv, fingerprint

def derive_public_key(private_key: bytes) -> bytes:
    """
    Derive the public key from a private key using the secp256k1 curve.

    Args:
        private_key (bytes): The private key as a byte string.

    Returns:
        bytes: The corresponding compressed public key.
    """


    sk = SigningKey.from_string(private_key, curve=SECP256k1)
    vk = sk.verifying_key
    compressed_prefix = b"\x02" if vk.pubkey.point.y() % 2 == 0 else b"\x03"
    return compressed_prefix + number_to_string(vk.pubkey.point.x(), vk.pubkey.order)

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Derive a 512-bit seed, BIP-32 root key, and root fingerprint from a BIP-39 mnemonic and passphrase.")
    parser.add_argument("mnemonic", type=str, help="The 24-word mnemonic phrase.")
    parser.add_argument("--passphrase", type=str, default="", help="Optional passphrase (default is empty). Special characters are supported.")

    # Parse arguments
    args = parser.parse_args()

    # Derive the 512-bit BIP39 seed
    seed = derive_bip39_seed(args.mnemonic, args.passphrase)
    print(f"Derived Seed (Hex): {seed}")

    # Derive the BIP-32 root key (xprv) and fingerprint
    xprv, fingerprint = derive_bip32_root_key(seed)
    print(f"BIP-32 Root Key (xprv): {xprv}")
    print(f"BIP-32 Root Fingerprint: {fingerprint}")

# Usage:
# Use single quotes so that special characters are handled literally
# python derive_bip39_seed.py 'your 24-word mnemonic here' --passphrase 'your optional passphrase'
