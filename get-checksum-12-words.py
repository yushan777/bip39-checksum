import argparse
import hashlib

# For 12 words:
#
# First 11 words provide 11 × 11 = 121 bits of entropy
# The 12th word is calculated from:
#
# First 11 words (121 bits)
# Plus 7 additional bits (to make 128 bits of entropy)
# Plus 4 bits of checksum

# ====================================================================
def concatenate_binary_indices(indices):
    # Concatenate the first 11 words into a single string
    return ''.join(f"{index:011b}" for index in indices)

# ====================================================================
def hex_to_binary(hex_string):
    # Remove '0x' prefix if present
    hex_string = hex_string.replace('0x', '')

    # Convert to integer, then to binary, and remove '0b' prefix
    binary = bin(int(hex_string, 16))[2:]

    # Pad with zeros to ensure each hex digit becomes 4 bits
    padding_length = len(hex_string) * 4
    binary = binary.zfill(padding_length)

    # only return the first 4 bits of the hash (for 12-word phrases)
    return binary[:4]

# ====================================================================
def split_into_chunks(binary_string):
    chunk_size = 11
    return [binary_string[i:i+chunk_size] for i in range(0, len(binary_string), chunk_size)]

# ====================================================================
def check_all_12th_words(binary_string_121, bip39_wordlist):
    print("\nAll possible valid 12th words:")
    print(f"{'7 bits':<8} | {'Checksum':>8} | {'BIP39 Line #':>12} | {'Word'}")
    print("-" * 45)

    # Try all 128 possible 7-bit combinations
    for i in range(128):
        # Convert number to 7-bit binary string
        seven_bits = format(i, '07b')

        # Create 128-bit entropy with these 7 bits
        binary_string_128 = binary_string_121 + seven_bits

        # Convert binary string to bytes for SHA256
        bytes_data_128 = int(binary_string_128, 2).to_bytes((len(binary_string_128) + 7) // 8, byteorder='big')

        # Calculate SHA256 hash
        sha256_hash = hashlib.sha256(bytes_data_128).hexdigest()

        # Get first 4 bits of hash
        hash_binary_first_4_bits = hex_to_binary(sha256_hash)

        # Combine 7 bits + 4 bits to get 11-bit word index
        word_index_binary = seven_bits + hash_binary_first_4_bits
        word_index = int(word_index_binary, 2)
        word = bip39_wordlist[word_index]

        print(f"{seven_bits:<8} | {hash_binary_first_4_bits:>8} | {word_index + 1:>12} | {word}")

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

    # Print concatenated binary of the first 11 words
    if found_indices:
        print("\n121-bits (11 words):")
        binary_string_121 = concatenate_binary_indices(found_indices)
        print(f'{binary_string_121}\n')

        # split into 11-bit chunks
        chunks_list = split_into_chunks(binary_string_121)

        print(f"{'Word #':<6} | {'BIP39':<12} | {'BIP39':7} | {'BIP39':11} | {'BIP39'}")
        print(f"{'':6} | {'Word':12} | {'Line #':7} | {'Value (Dec)':>11} | {'Value (Bin)'}")
        print("-" * 65)
        for i, chunk in enumerate(chunks_list[:11]):  # Only iterate through first 11 chunks
            decimal_value = int(chunk, 2)
            word_num = decimal_value + 1
            word = bip39_wordlist[decimal_value]
            print(f"Word {i + 1:<2} | {word:<12} | {word_num:>6} | {decimal_value:>11} | {chunk}")

        check_all_12th_words(binary_string_121, bip39_wordlist)

if __name__ == "__main__":
    main()