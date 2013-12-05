#!/usr/bin/env python
"""
Some tools save files in BED tabular format but erroneously use 1-based
indexing, instead of the prescribed 0-based indexing. This tool merely reads
the file, subtracts one from the interval start location, and saves to a new
file.
"""
import argparse

import pybedtools as bt


def start_subtract_one(ival):
    """Subtract 1 to the start of an Interval.

    Parameters
    ----------
    ival : Interval object
        The interval to be modified.

    Returns
    -------
    ival0 : Interval object
        The modified interval.
    """
    ival.start -= 1
    return ival


def one_to_zero_index(bed):
    """Convert a one-based BedTool object to a zero-based one.

    Parameters
    ----------
    bed : BedTool object
        The input BED object.

    Returns
    -------
    bed0 : BedTool object
        The modified BED object.
    """
    bed0 = bed.each(start_subtract_one)
    return bed0


def main():
    """Convert FAVR-indexed to BED-indexed files.
    """
    parser = argparse.ArgumentParser(
        description='Compute coverage and other stats of BED files.')
    parser.add_argument('bed_files', nargs='+', metavar='BEDFILE',
                        help='One or more BED files.')
    parser.add_argument('-s', '--suffix', default='.0.bed',
                        help='Append this suffix to mark output filename.')
    args = parser.parse_args()
    for fn in args.bed_files:
        b = bt.BedTool(fn)
        b0 = favr_to_zero_index(b)
        b0.saveas(fn + args.suffix)


if __name__ == '__main__':
    main()

