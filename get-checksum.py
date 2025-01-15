import argparse
import hashlib

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
def iterate_3bit_combinations():
    """
    Iterate through all 3-bit combinations for first part of 24th word that will be incl. in checksum.
    """
    for i in range(8):  # There are 2^3 = 8 combinations for 3 bits
        # Convert the number to binary, padded to 3 digits
        binary_combination = format(i, '03b')
        print(binary_combination)

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

    # Print index for each input word
    print("Word # : Word       : Word      : Index   : Index")
    print("       :            : Line      : (Dec)   : (Bin)")
    print("-" * 65)
    for i, word in enumerate(input_words, 1):
        try:
            index = bip39_wordlist.index(word)
            word_num = index + 1
            binary_index = f"{index:011b}"
            print(f"{i:<6} : {word:<10} : {word_num:<9} : {index:<7} : {binary_index}")
            found_indices.append(index)
        except ValueError:
            print(f"{i:<6} : {word:<10} : Not found in wordlist")

    # Print concatenated binary of the first 23 words
    if found_indices:
        print("\n253-bits (23 words):")
        binary_string = concatenate_binary_indices(found_indices)
        print(binary_string)
        print("\n")

        # SHA256 hash function is performed on 256 bits, but the first 23 words only give us 253 bits
        # so we need 3 additional bits added to the entropy so far before we perform a SHA256 hash on it
        # first 3-bit combo - 000
        binary_string_256 = binary_string + "000"
        print("Full 256-bit Entropy:")
        print(binary_string_256)
        print("\n")

        print("Perform SHA256 on 256-bit entropy...")
        # Convert binary string to bytes
        bytes_data_256 = int(binary_string_256, 2).to_bytes((len(binary_string_256) + 7) // 8, byteorder='big')

        # Calculate SHA256 hash
        sha256_hash = hashlib.sha256(bytes_data_256).hexdigest()

        # print the hash (hexadecimal)
        print(sha256_hash)
        print("\n")

        # convert to binary and only return the first 8 bits
        hash_binary_first_8_bits = hex_to_binary(sha256_hash)
        print(hash_binary_first_8_bits)
        print("\n")

        # append this to the original 256 entropy to now give us 264 bits
        binary_string_264 = binary_string_256 + hash_binary_first_8_bits

        print("Full 264-bit Number:")
        print(binary_string_264)
        print("\n")

        # split into 11-bit chuncks
        chunks_list = split_into_chunks(binary_string_264)

        for i, chunk in enumerate(chunks_list):
            print(f"Chunk {i + 1}: {chunk}")

if __name__ == "__main__":
    main()