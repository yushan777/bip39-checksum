import argparse
import hashlib

# For 24 words:
#
# First 23 words provide 23 × 11 = 253 bits of entropy
#
# The 24th word is calculated from:
#
# First 23 words (253 bits)
# Plus 3 additional bits (to make 256 bits of entropy)
# Plus 8 bits of checksum calculated from hashing the first 256 bits

# ====================================================================
def concatenate_binary_indices(indices):
    """Concatenate the first 23 words (binary indices) into a single string."""
    return ''.join(f"{index:011b}" for index in indices)

# ====================================================================
def hex_to_binary(hex_string):
    # Remove '0x' prefix if present
    hex_string = hex_string.replace('0x', '')

    # Convert to integer, then to binary, and remove '0b' prefix
    binary = bin(int(hex_string, 16))[2:]

    # Pad with zeros to ensure each hex digit becomes 4 bits
    # (each hex digit should correspond to 4 binary digits)
    padding_length = len(hex_string) * 4
    binary = binary.zfill(padding_length)

    # only return the first 8 bits of the hash
    return binary[:8]

# ====================================================================
def split_into_chunks(binary_string):
    chunk_size = 11
    return [binary_string[i:i+chunk_size] for i in range(0, len(binary_string), chunk_size)]

# ====================================================================
# ====================================================================
def check_all_24th_words(binary_string_253, bip39_wordlist):
    print("\nAll possible valid 24th words:")
    print(f"{'3 bits':<8} | {'Checksum':>8} | {'BIP39 Line #':>12} | {'Word'}")
    print("-" * 45)

    # Try all 8 possible 3-bit combinations: 000, 001, 010, 011, 100, 101, 110, 111
    for i in range(8):
        # Convert number to 3-bit binary string
        three_bits = format(i, '03b')

        # Create 256-bit entropy with these 3 bits
        binary_string_256 = binary_string_253 + three_bits

        # Convert binary string to bytes for SHA256
        bytes_data_256 = int(binary_string_256, 2).to_bytes((len(binary_string_256) + 7) // 8, byteorder='big')

        # Calculate SHA256 hash
        sha256_hash = hashlib.sha256(bytes_data_256).hexdigest()

        # Get first 8 bits of hash
        hash_binary_first_8_bits = hex_to_binary(sha256_hash)

        # Combine 3 bits + 8 bits to get 11-bit word index
        word_index_binary = three_bits + hash_binary_first_8_bits
        word_index = int(word_index_binary, 2)
        word = bip39_wordlist[word_index]

        print(f"{three_bits:<8} | {hash_binary_first_8_bits:>8} | {word_index + 1:>12} | {word}")
# ====================================================================
def main():
    parser = argparse.ArgumentParser(description='Process BIP39 wordlist')
    parser.add_argument('words', nargs='+', help='List of words to process')

    args = parser.parse_args()
    input_words = args.words

    # Define the file path
    file_path = "bip39_wordlist.txt"

    # Read the file and load words into a list
    with open(file_path, "r") as file:
        bip39_wordlist = [line.strip() for line in file if line.strip()]

    # Store indices for valid words
    found_indices = []
    for i, word in enumerate(input_words, 1):
        try:
            index = bip39_wordlist.index(word)
            found_indices.append(index)
        except ValueError:
            print(f"{i:<6} : {word:<10} : Not found in wordlist")

    # Print concatenated binary of the first 23 words
    if found_indices:
        print("\n253-bits (23 words):")
        binary_string_253 = concatenate_binary_indices(found_indices)
        print(f'{binary_string_253}\n')

        # split into 11-bit chunks
        chunks_list = split_into_chunks(binary_string_253)

        print(f"{'Word #':<6} | {'BIP39':<12} | {'BIP39':7} | {'BIP39':11} | {'BIP39'}")
        print(f"{'':6} | {'Word':12} | {'Line #':7} | {'Value (Dec)':>11} | {'Value (Bin)'}")
        print("-" * 65)  # Extended separator line for new column
        for i, chunk in enumerate(chunks_list[:23]):  # Only iterate through first 23 chunks
            decimal_value = int(chunk, 2)  # Convert binary to decimal
            word_num = decimal_value + 1  # Add 1 to get the line number
            word = bip39_wordlist[decimal_value]  # Look up the word using decimal_value as index
            print(f"Word {i + 1:<2} | {word:<12} | {word_num:>6} | {decimal_value:>11} | {chunk}")


        check_all_24th_words(binary_string_253, bip39_wordlist)

if __name__ == "__main__":
    main()