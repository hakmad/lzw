#!/usr/bin/env python3

"""LZW program.

The source for this program can be found at https://github.com/hakmad/lzw/.
Please see the README.md file that is shown there as it goes over important
information regarding the usage of this program and the structure of the
files it creates.
"""

import argparse
import struct


def compress(uncompressed_data, verbose):
    """Compress a string and return a list of integers and a dictionary.

    Uses the LZW compression algorithm to compress a string. This particular
    implementation will build a dictionary from uncompressed_data using
    set to get all the unique characters in the string, and then incrementing
    a counter to get the codes. When the table fills up, it stops adding new
    strings to the table, but keeps attempting to compress data by adding
    codes to the compressed_data list. When compression is complete, it
    returns initial_table (the table before extra codes were added to it) as
    well as compressed_data which contains the actual compressed data.

    Keyword arguments:
    uncompressed_data (str)     String to compress.
    verbose (bool)              Print information during compression?

    Returns:
    compressed_data (list)      Integers representing the compressed data.
    initial_table (dict)        Table of characters and codes used by LZW.
    """
    if verbose:
        print("Initialising empty list for compressed data...")

    compressed_data = []

    if verbose:
        print("Getting unique characters in uncompressed data...")

    # Set creates unique entries.
    unique_chars = list(set(uncompressed_data))

    if verbose:
        print("Unique characters in uncompressed data:")

        for char in unique_chars:
            print(char, end=" ")
        print()

    if verbose:
        print("Creating string table...")

    max_table_size = 2 ** 16
    initial_table = {unique_chars[i]: i for i in range(len(unique_chars))}
    # table is copy of initial_table, initial_table is kept till the end.
    table = initial_table.copy()

    # Get the maximum value from the dictionary, this is table_size.
    # (+ 1 because we are using table_size as a counter).
    table_size = table[max(table, key=table.get)] + 1

    if verbose:
        print("Table size: {}".format(table_size))
        print("Maximum table size: {}".format(max_table_size))
        print("Table structure:")

        for char, code in table.items():
            print("Character: {}, maps to code: {}".format(char, code))

        print("Beginning compression...")

    prefix = ""
    for char in uncompressed_data:
        if verbose:
            print("Current prefix: {}".format(prefix))
            print("Current character: {}".format(char))

        if prefix + char in table:
            if verbose:
                print("Prefix + character in string table! Concatenating character to prefix...")

            prefix += char

        else:
            if verbose:
                print("Prefix + character not in string table! Adding prefix code to compressed data...")

            compressed_data.append(table[prefix])

            # Use table_size as counter.
            if not(table_size > max_table_size - 1):
                if verbose:
                    print("Space available in table! Adding prefix + character to string table with code {} and incrementing table size...".format(table_size))

                table[prefix + char] = table_size
                table_size += 1

            if verbose:
                print("Setting character to prefix...")

            prefix = char

    # prefix may still contain data, append to list.
    if prefix:
        if verbose:
            print("Prefix still exists, adding prefix code to compressed data...")

        compressed_data.append(table[prefix])

    if verbose:
        print("Compression complete!")

        print("Table size: {}".format(table_size))
        print("Table structure:")

        for string, code in table.items():
            print("String: {}, maps to code {}".format(char, code))

        print("Compressed data size: {}".format(len(compressed_data)))
        print("Compressed data:")
        
        for code in compressed_data:
            print(code, end=" ")
        print()

        print("Returning compressed data and initial string table...")
    
    return compressed_data, initial_table


def uncompress(compressed_data, table, verbose):
    """Uncompress a list using a table and return a string.

    Uses the LZW uncompression algorithm to uncompress a list of integers that
    represents some compressed data. Also requires a dictionary that represnts
    the table used to compress the string table in it's initial state during
    compression. Gets the maximum value of the dictionary from the table to
    get the size of the table and then reverses the table so that it can be
    used effectively by the uncompression algorithm. Outputs the character of
    the first code to uncompressed_data and pops it from compressed_data so
    that the for loop that follows doesn't try to read the same code again.
    When uncompression is complete it returns uncompressed_data.

    Keyword arguments:
    compressed_data (list)      Integers to uncompress
    table (dict)                Table of characters and codes used by LZW.
    verbose (bool)              Print information during uncompression?

    Returns:
    uncompressed_data (str)     String representing the uncompressed data.
    """
    if verbose:
        print("Initialising empty string for uncompressed data...")

    uncompressed_data = ""

    if verbose:
        print("Reversing table and getting table size...")

    # Get the maximum value of the dictionary, this is table_size
    # (+ 1 because we are using table_size as a counter).
    table_size = table[max(table, key=table.get)] + 1

    # Reverse the table so that codes map to strings.
    table = {value: key for key, value in table.items()}

    if verbose:
        print("Table size: {}".format(table_size))
        print("Table structure:")

        for code, char in table.items():
            print("Code: {}, maps to character: {}".format(code, char))

        print("Beginning uncompression...")

    # Get the first item from the table and pop it so that the for loop
    # doesn't try to read it.
    current = table[compressed_data.pop(0)]
    uncompressed_data += current
    previous = current

    for current in compressed_data:
        if verbose:
            print("Current code: {}".format(current))
            print("Previous string: {}".format(previous))

        if current in table:
            if verbose:
                print("Code in table! Setting output to codes string...")

            output = table[current]

        elif current == table_size:
            if verbose:
                print("Code is equal to size of table! Setting output to previous string concatenated with its own first character...")

            output = previous + previous[0]
        else:
            raise ValueError("Bad compression! Please run again with -v to see more details...")

        if verbose:
            print("Output string: {}".format(output))
            print("Adding output to uncompressed data...")
        
        uncompressed_data += output

        if verbose:
            print("Adding previous string + first letter in output string to table with code {} and incrementing table size...".format(table_size))

        table[table_size] = previous + output[0]
        table_size +=1

        if verbose:
            print("Setting previous string to output string...")

        previous = output

    if verbose:
        print("Uncompression complete!")

        print("Table size: {}".format(table_size))
        print("Table structure:")

        for code, string in table.items():
            print("Code: {}, maps to string: {}".format(code, string))

        print("Uncompressed data size: {}".format(len(uncompressed_data)))

        print("Returning uncompressed data...")

    return uncompressed_data


def compress_to_file(in_file, verbose):
    """Compress data in a file and write new file with compressed data.

    Compresses the data using the compress function. See README.md for details
    on the structure of the file.

    Keyword arguments:
    in_file (str)               Name of file to compress.
    verbose (bool)              Print information during compression?

    Returns:
    None
    """
    # Add ".lzw" extension to file.
    out_file = in_file + ".lzw"

    if verbose:
        print("Opening {} for reading...".format(in_file))

    # Get file data.
    with open(in_file, "r") as file:
        data = file.read()
    
    if verbose:
        print("Compressing data from file...")

    # Compress data.
    compressed_data, table = compress(data, verbose)

    if verbose:
        print("Getting initial string table size...")

    # Get the maximum value from the dictionary, this is table_size.
    table_size = table[max(table, key=table.get)]

    if verbose:
        print("Table size: {}".format(table_size))

        print("Opening {} for writing (bytes)...".format(out_file))

    # Write compressed data to file.
    with open(out_file, "wb") as file:
        if verbose:
            print("Writing table size to file...")
        
        # Write table_size with 1 byte.
        file.write(struct.pack("<B", table_size))
    
        if verbose:
            print("Writing table data to file...")

        # Write characters with 2 bytes and codes with 1 byte.
        for char, code in table.items():
            file.write(struct.pack("<H", ord(char)))
            file.write(struct.pack("<B", code))
    
        if verbose:
            print("Writing compressed data to file...")

        # Write all codes with 2 bytes.
        for data in compressed_data:
            file.write(struct.pack("<H", data))

    if verbose:
        print("File writing complete!")


def uncompress_from_file(in_file, verbose):
    """Uncompress data in a file and write new file with uncompressed data.

    Uncompresses the dat using the uncompress function. See README.md for
    details on the structure of the file.

    Keyword arguments:
    in_file (str)               Name of the file to uncompress.
    verbose (bool)              Print information during uncompression?

    Returns:
    None.
    """
    # Attempt to remove ".lzw" extension (note: this will overwrite the file
    # if the file doesn't have ".lzw" extension).
    out_file = in_file.replace(".lzw", "")

    if verbose:
        print("Opening {} for reading (bytes)...".format(in_file))

    # Get file data.
    with open(in_file, "rb") as file:
        if verbose:
            print("Initialising empty list for compressed data and empty table for table data...")

        compressed_data = []
        table = {}

        if verbose:
            print("Getting table size from file...")

        table_size = struct.unpack("<B", file.read(1))[0]

        if verbose:
            print("Table size: {}".format(table_size))
            print("Getting rest of table data...")

        # Build up table by reading 3 bytes at a time, the first 2 being
        # characters and the last being it's code.
        for i in range(table_size + 1):
            char = chr(struct.unpack("<H", file.read(2))[0])
            code = struct.unpack("<B", file.read(1))[0]

            table[char] = code

        if verbose:
            print("Getting compressed data...")

        # Continuously get 2 bytes at a time until file is empty.
        while True:
            data = file.read(2)
            if not data:
                break
            else:
                data = struct.unpack("<H", data)[0]
                compressed_data.append(data)

    if verbose:
        print("Uncompressing data from file...")

    # Uncompress data.
    uncompressed_data = uncompress(compressed_data, table, verbose)

    if verbose:
        print("Opening {} for writing...".format(out_file))

    # Write uncompressed data to file.
    with open(out_file, "w") as file:
        if verbose:
            print("Writing uncompressed data to file...")

        file.write(uncompressed_data)

    if verbose:
        print("File writing done!")


def main():
    """Function that is run if the script is called as an executable.

    See README.md (or run the program with the -h option) to see how to use
    it.
    """
    parser = argparse.ArgumentParser(
            description="perform LZW compression on a file",
            epilog="available online at: https://github.com/hakmad/lzw/")

    # Group for output options.
    output_opts = parser.add_mutually_exclusive_group()

    output_opts.add_argument("-v", "--verbose", action="store_true",
            dest="verbose", help="verbose mode")
    output_opts.add_argument("-q", "--quiet", action="store_true",
            dest="quiet", help="quiet mode")

    # Group for what to actually do with data (compress/uncompress?).
    compress_opts = parser.add_mutually_exclusive_group(required=True)

    compress_opts.add_argument("-c", "--compress", action="store",
            dest="to_compress", help="compress a file", metavar="file",
            nargs="?")
    compress_opts.add_argument("-u", "--uncompress", action="store",
            dest="to_uncompress", help="uncompress a file", metavar="file",
            nargs="?")

    # Get arguments.
    args = parser.parse_args()

    # Handle options.
    if args.to_compress:
        if not(args.quiet):
            print("Compressing {} to {} ...".format(args.to_compress,
                args.to_compress + ".lzw"))

        compress_to_file(args.to_compress, args.verbose)

        if not(args.quiet):
            print("Done!")

    elif args.to_uncompress:
        if not(args.quiet):
            print("Uncompressing {} to {} ...".format(args.to_uncompress,
                args.to_uncompress.replace(".lzw", "")))

        uncompress_from_file(args.to_uncompress, args.verbose)

        if not(args.quiet):
            print("Done!")

# If called as an executable...
if __name__ == "__main__":
    main()
