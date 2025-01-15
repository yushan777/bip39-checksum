import argparse

# ====================================================================
def concatenate_binary_indices(indices):
    """Concatenate the first 23 words (binary indices) into a single string."""
    return ''.join(f"{index:011b}" for index in indices)

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

    # Print concatenated binary if we found any valid words
    if found_indices:
        print("\n253-bits (23 words):")
        binary_string = concatenate_binary_indices(found_indices)
        print(binary_string)
        print("\n")

    # Debug ===========================================================================
    ## Print the first 10 words with their decimal index, binary index, and word number
    #print("Index : Binary Index : Word Number : Word")
    #for index, word in enumerate(bip39_wordlist[:10]):
    #    binary_index = f"{index:011b}"  # Convert index to 11-bit binary
    #    word_number = index + 1         # Word number starts from 1 (index +1)
    #    print(f"{index:>5} : {binary_index}  : {word_number:>11} : {word}")

if __name__ == "__main__":
    main()