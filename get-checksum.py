import argparse
import hashlib

# Terminal colors
class tcolor:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'

def color_text(text, color):
    return f"{color}{text}{tcolor.RESET}"

# BIP39 Phrase Specifications:
#
# Words    Total Bits   Initial Entropy    Extra Bits Needed  Checksum Bits
# 12       132          11×11=121          7  (128-121)       (121+7) / 32 = 4
# 15       165          14×11=154          6  (160-154)       (154+6) / 32 = 5
# 18       198          17×11=187          5  (192-187)       (187+5) / 32 = 6
# 21       231          20×11=220          4  (224-220)       (220+4) / 32 = 7
# 24       264          23×11=253          3  (256-253)       (253+3) / 32 = 8

# Lookup table for phrase specifications
PHRASE_SPECS = {
    11: {"initial_entropy_bits": 121, "extra_bits": 7, "checksum_bits": 4},   # 12 words
    14: {"initial_entropy_bits": 154, "extra_bits": 6, "checksum_bits": 5},   # 15 words
    17: {"initial_entropy_bits": 187, "extra_bits": 5, "checksum_bits": 6},   # 18 words
    20: {"initial_entropy_bits": 220, "extra_bits": 4, "checksum_bits": 7},   # 21 words
    23: {"initial_entropy_bits": 253, "extra_bits": 3, "checksum_bits": 8}    # 24 words
}

# ====================================================================
def concatenate_binary_indices(indices):
    """Concatenate the word indices into a single binary string."""
    return ''.join(f"{index:011b}" for index in indices)

# ====================================================================
def hex_to_binary(hex_string, num_bits):
    """Convert hex string to binary and return specified number of bits."""
    # Remove '0x' prefix if present
    hex_string = hex_string.replace('0x', '')

    # Convert to integer, then to binary, and remove '0b' prefix
    binary = bin(int(hex_string, 16))[2:]

    # Pad with zeros to ensure each hex digit becomes 4 bits
    padding_length = len(hex_string) * 4
    binary = binary.zfill(padding_length)

    # Return specified number of bits
    return binary[:num_bits]

# ====================================================================
def split_into_chunks(binary_string):
    """Split binary string into 11-bit chunks."""
    chunk_size = 11
    return [binary_string[i:i+chunk_size] for i in range(0, len(binary_string), chunk_size)]

# ====================================================================
def check_last_word(binary_string, bip39_wordlist, num_words):
    """Check all possible valid last words based on the phrase length."""
    specs = PHRASE_SPECS[num_words]
    extra_bits_size = specs["extra_bits"]
    initial_entropy_size = specs["initial_entropy_bits"]
    checksum_bits = specs["checksum_bits"]
    num_combinations = 2 ** extra_bits_size

    print(f"\n{color_text('All possible valid ' + str(num_words + 1) + 'th words:', tcolor.BRIGHT_CYAN)}")
    header = f"{f'Extra bits':<10} | {'Checksum':>8} | {'BIP39 Line #':>12} | {'Word'}"
    print(color_text(header, tcolor.BRIGHT_BLACK))
    print("-" * 45)

    # Try all possible combinations
    for i in range(num_combinations):
        # Convert number to binary string of appropriate length
        extra_bits = format(i, f'0{extra_bits_size}b')

        # Create total entropy with these extra bits
        binary_string_total = binary_string + extra_bits

        # Convert binary string to bytes for SHA256
        bytes_data = int(binary_string_total, 2).to_bytes((len(binary_string_total) + 7) // 8, byteorder='big')

        # Calculate SHA256 hash
        sha256_hash = hashlib.sha256(bytes_data).hexdigest()

        # Get first N bits of hash
        hash_binary = hex_to_binary(sha256_hash, checksum_bits)

        # Combine extra bits + checksum bits to get 11-bit word index
        word_index_binary = extra_bits + hash_binary
        word_index = int(word_index_binary, 2)
        word = bip39_wordlist[word_index]

        # Color the output
        colored_extra = color_text(extra_bits, tcolor.YELLOW)
        colored_hash = color_text(hash_binary, tcolor.GREEN)
        colored_index = color_text(str(word_index + 1), tcolor.BLUE)
        colored_word = color_text(word, tcolor.MAGENTA)

        print(f"{colored_extra:<18} | {colored_hash:>16} | {colored_index:>12} | {colored_word}")

# ====================================================================
def main():
    parser = argparse.ArgumentParser(
        description='Process BIP39 wordlist (enter N-1 words for N-word phrase, where N is 12, 15, 18, 21, or 24)'
    )
    parser.add_argument('words', nargs='+', help='List of words')

    args = parser.parse_args()
    input_words = args.words
    num_words = len(input_words)

    # Check valid number of input words
    if num_words not in PHRASE_SPECS:
        valid_lengths = ", ".join(str(n) for n in sorted(PHRASE_SPECS.keys()))
        error_msg = f"Error: Please provide {valid_lengths} words for generating {sorted(n+1 for n in PHRASE_SPECS.keys())} word phrases respectively"
        print(color_text(error_msg, tcolor.RED))
        return

    # Define the file path
    file_path = "bip39_wordlist.txt"

    # Read the file and load words into a list
    try:
        with open(file_path, "r") as file:
            bip39_wordlist = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(color_text(f"Error: Could not find {file_path}", tcolor.RED))
        return

    # Store indices for valid words
    found_indices = []
    for i, word in enumerate(input_words, 1):
        try:
            index = bip39_wordlist.index(word)
            found_indices.append(index)
        except ValueError:
            error = f"{i:<6} : {word:<10} : Not found in wordlist"
            print(color_text(error, tcolor.RED))

    # Process if valid words were found
    if found_indices:
        # Calculate total bits based on number of words
        initial_entropy_bits = num_words * 11

        title = f"\n{initial_entropy_bits}-bits ({num_words} words):"
        print(color_text(title, tcolor.BRIGHT_CYAN))
        binary_string = concatenate_binary_indices(found_indices)
        print(color_text(binary_string, tcolor.YELLOW))
        print()

        # Split into 11-bit chunks
        chunks_list = split_into_chunks(binary_string)

        # Print table headers
        header = f"{'Word #':<6} | {'BIP39':<12} | {'BIP39':7} | {'BIP39':11} | {'BIP39'}"
        subheader = f"{'':6} | {'Word':12} | {'Line #':7} | {'Value (Dec)':>11} | {'Value (Bin)'}"
        print(color_text(header, tcolor.BRIGHT_BLACK))
        print(color_text(subheader, tcolor.BRIGHT_BLACK))
        print("-" * 65)

        # Print word details
        for i, chunk in enumerate(chunks_list[:num_words]):
            decimal_value = int(chunk, 2)
            word_num = decimal_value + 1
            word = bip39_wordlist[decimal_value]

            word_num_col = color_text(f"Word {i + 1:<2}", tcolor.CYAN)
            word_col = color_text(f"{word:<12}", tcolor.MAGENTA)
            line_col = color_text(f"{word_num:>6}", tcolor.BLUE)
            dec_col = color_text(f"{decimal_value:>11}", tcolor.GREEN)
            bin_col = color_text(chunk, tcolor.YELLOW)

            print(f"{word_num_col} | {word_col} | {line_col} | {dec_col} | {bin_col}")

        check_last_word(binary_string, bip39_wordlist, num_words)

if __name__ == "__main__":
    main()