import argparse
import hashlib
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class PhraseSpec:
    initial_entropy_bits: int
    extra_bits: int
    checksum_bits: int
    total_words: int

    @property
    def total_bits(self) -> int:
        return self.initial_entropy_bits + self.extra_bits


class TerminalColor:
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

    @staticmethod
    def colorize(text: str, color: str) -> str:
        return f"{color}{text}{TerminalColor.RESET}"


# Maps number of input words to their specifications
PHRASE_SPECS: Dict[int, PhraseSpec] = {
    11: PhraseSpec(121, 7, 4, 12),  # 12 words
    14: PhraseSpec(154, 6, 5, 15),  # 15 words
    17: PhraseSpec(187, 5, 6, 18),  # 18 words
    20: PhraseSpec(220, 4, 7, 21),  # 21 words
    23: PhraseSpec(253, 3, 8, 24)  # 24 words
}


class BIP39Validator:
    def __init__(self, wordlist_path: str = "bip39_wordlist.txt"):
        self.wordlist = self._load_wordlist(wordlist_path)

    def _load_wordlist(self, path: str) -> List[str]:
        """Load and validate the BIP39 wordlist."""
        try:
            with open(path, "r", encoding='utf-8') as file:
                wordlist = [line.strip() for line in file if line.strip()]
            if len(wordlist) != 2048:  # BIP39 requires exactly 2048 words
                raise ValueError(f"Invalid wordlist length: {len(wordlist)}")
            return wordlist
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not find wordlist at {path}")

    def get_word_index(self, word: str) -> Optional[int]:
        """Get the index of a word in the wordlist."""
        try:
            return self.wordlist.index(word)
        except ValueError:
            return None

    def binary_to_index(self, binary: str) -> int:
        """Convert an 11-bit binary string to a wordlist index."""
        return int(binary, 2)

    def index_to_binary(self, index: int) -> str:
        """Convert a wordlist index to an 11-bit binary string."""
        return format(index, '011b')

    def calculate_checksum(self, entropy_bits: str, num_checksum_bits: int) -> str:
        """Calculate the checksum for given entropy bits."""
        # Convert binary string to bytes
        entropy_int = int(entropy_bits, 2)
        entropy_bytes = entropy_int.to_bytes((len(entropy_bits) + 7) // 8, byteorder='big')

        # Calculate SHA256
        sha256_hash = hashlib.sha256(entropy_bytes).hexdigest()

        # Convert to binary and take required number of bits
        hash_binary = bin(int(sha256_hash, 16))[2:].zfill(256)
        return hash_binary[:num_checksum_bits]

    def find_valid_last_words(self, input_indices: List[int], spec: PhraseSpec) -> List[tuple[str, str, int, str]]:
        """Find all valid last words for the given partial phrase."""
        # Concatenate binary indices
        binary_string = ''.join(self.index_to_binary(idx) for idx in input_indices)
        valid_words = []

        # Try all possible extra bit combinations
        for i in range(2 ** spec.extra_bits):
            extra_bits = format(i, f'0{spec.extra_bits}b')
            total_entropy = binary_string + extra_bits

            # Calculate checksum
            checksum = self.calculate_checksum(total_entropy, spec.checksum_bits)

            # Combine extra bits and checksum to get word index
            word_index = self.binary_to_index(extra_bits + checksum)
            word = self.wordlist[word_index]

            valid_words.append((extra_bits, checksum, word_index, word))

        return valid_words


def main():
    parser = argparse.ArgumentParser(
        description='Process BIP39 wordlist (enter N-1 words for N-word phrase)'
    )
    parser.add_argument('words', help='Space-separated list of words as a single argument')
    parser.add_argument('--wordlist', default='bip39_wordlist.txt',
                        help='Path to BIP39 wordlist file')
    args = parser.parse_args()

    # Split the single input string into individual words
    input_words = args.words.split()
    num_words = len(input_words)

    try:
        validator = BIP39Validator(args.wordlist)
    except (FileNotFoundError, ValueError) as e:
        print(TerminalColor.colorize(f"Error: {str(e)}", TerminalColor.RED))
        return

    if num_words not in PHRASE_SPECS:
        valid_lengths = ", ".join(str(n) for n in sorted(PHRASE_SPECS.keys()))
        print(TerminalColor.colorize(
            f"Error: Please provide {valid_lengths} words for generating "
            f"{sorted(spec.total_words for spec in PHRASE_SPECS.values())} "
            "word phrases respectively", TerminalColor.RED))
        return

    # Convert words to indices
    indices = []
    for i, word in enumerate(input_words, 1):
        index = validator.get_word_index(word)
        if index is None:
            print(TerminalColor.colorize(
                f"Word {i}: '{word}' not found in wordlist", TerminalColor.RED))
            return
        indices.append(index)

    spec = PHRASE_SPECS[num_words]

    # Print initial entropy
    binary_string = ''.join(validator.index_to_binary(idx) for idx in indices)
    print(TerminalColor.colorize(
        f"\n{spec.initial_entropy_bits}-bits ({num_words} words):",
        TerminalColor.BRIGHT_CYAN))
    print(TerminalColor.colorize(binary_string, TerminalColor.YELLOW))

    # Print word details table
    print("\nInput phrase analysis:")
    print(TerminalColor.colorize(
        "Word # | Word        | Line #  | Value (Dec) | Value (Bin)",
        TerminalColor.BRIGHT_BLACK))
    print("-" * 65)

    for i, index in enumerate(indices):
        word = validator.wordlist[index]
        bin_value = validator.index_to_binary(index)
        print(
            f"{TerminalColor.colorize(f'Word {i + 1:2}', TerminalColor.CYAN)} | "
            f"{TerminalColor.colorize(f'{word:<11}', TerminalColor.MAGENTA)} | "
            f"{TerminalColor.colorize(f'{index + 1:>7}', TerminalColor.BLUE)} | "
            f"{TerminalColor.colorize(f'{index:>10}', TerminalColor.GREEN)} | "
            f"{TerminalColor.colorize(bin_value, TerminalColor.YELLOW)}"
        )

    # Find and display valid last words
    valid_words = validator.find_valid_last_words(indices, spec)
    print(f"\n{TerminalColor.colorize(f'Valid {spec.total_words}th words:', TerminalColor.BRIGHT_CYAN)}")
    print(TerminalColor.colorize(
        "Extra bits | Checksum | Line #    | Word",
        TerminalColor.BRIGHT_BLACK))
    print("-" * 45)

    for extra_bits, checksum, index, word in valid_words:
        print(
            f"{TerminalColor.colorize(extra_bits, TerminalColor.YELLOW):<18} | "
            f"{TerminalColor.colorize(checksum, TerminalColor.GREEN):>8} | "
            f"{TerminalColor.colorize(str(index + 1), TerminalColor.BLUE):>9} | "
            f"{TerminalColor.colorize(word, TerminalColor.MAGENTA)}"
        )



if __name__ == "__main__":
    main()