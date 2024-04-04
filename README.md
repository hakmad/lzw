# LZW

Command line tool to compress files using the [Lempel-Ziv-Welch
algorithm](https://en.wikipedia.org/wiki/Lempel%E2%80%93Ziv%E2%80%93Welch).

## Usage

This script can be used as both a standalone program as well as a module
that can be imported to another script. It is primarily designed for
compressing text. If used as a standalone program, its usage is as follows:

```
lzw.py [-h] [-v | -q] (-c [file] | -u [file])
```

It takes the following arguments:

```
    -h, --help          show a help message and exit
    -v, --verbose       verbose mode
    -q, --quiet         quiet mode
    -c [file], --compress [file]
                        compress a file
    -u [file], --uncompress [file]
                        uncompress a file
```

For example, to compress a file `text.txt`, do:

```
lzw.py -c text.txt
```

Or alternatively:

```
lzw.py --compress text.txt
```

To uncompress a file `text.txt.lzw`, do:

```
lzw.py -u text.txt.lzw
```

To suppress output, do:

```
lzw.py -q -c text.txt
```

To get more detailed output, do:

```
lzw.py -v -c text.txt
```

## Requirements

This project requires Python 3+. It also uses the following libraries:

- `struct`: for writing byte data.
- `argparse`: for handling arguments.

These libraries are provided as standard with most Python installations.

## File Structure

The structure of the files produced is as follows:
    Byte 1:                 Header data containing the size of the table (N).
    Byte 2 to N * 3         Table information.
    Byte N * 3 + 1 to EOF   Compressed data.

The table information is split into 3 bytes: the first 2 bytes represent the
Unicode code that corresponds to the character (NOT the code in the table, for
example the character Σ would be represnted as 931). The next byte represnts
corresponding code in the table. Everything afterwards is read 2 bytes at a
time to form 16 bit integers, this is the actual compressed data.

## Implementation Details

This particular implementation uses 16 bits to store all codes. It doesn't use
variable width codes (see the improvement section for details), and so all
codes are stored using 2 bytes. This still achieves pretty good compression
ratios.

This particular implementation will build a dictionary from
`uncompressed_data` using a set to get all the unique characters in the
string, and then incrementing a counter to get the codes. This is in contrast
with other implementations which build a dictionary by doing something like:

```
table = {chr(i): i for i in range(256)}
```

The reason this is done is because it may be the case that there is a
character in `uncompressed_data` that is not in extended ASCII. If this
happens, then the compression will not be able to complete as some of the
characters are not in the initial table.

This particular implementation uses a custom file format to store data. See
the notes on the program structure for details.

With some tweaking, it is possible to use this program on data other than just
text. However, it is not likely to produce good compression ratios.

## Improvements

Some improvements can be made to this program:

- Using `StringIO` or some other more efficient method for writing strings to
improve speed.
- Using variable width codes to improve compression ratios.
- Using a "clear code" in the dictionary to clear the dictionary when it gets
full or when the compression ratio drops.
- Using a file format compatible with the Unix `compress` tool so that it can
be compatible with other data.
- Rewriting the program in a different language which is faster and also has
more access to lower level bit manipulation (such as Java or C/C++).

## Bugs

Currently, there is a bug in the program to do with newlines when compressing.
If the file contains carriage returns being used as newlines, these will not
appear in the uncompressed version of the file. Internally, Python will report
the files as being identical, however an external tool (such as `diff`) will
state that they are in fact different (to view the differences you may need to
do `diff file1 file2 | cat -t`). Unfortunately this is a problem with the way
that `file.read()` works in Python so there is no current fix.
