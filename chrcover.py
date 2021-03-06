import argparse
import functools as ft
import numpy as np

from _tosi import to_si

chr_lens = { # hg19 coordinates
    'chr1' : 249250621,
    'chr2' : 243199373,
    'chr3' : 198022430,
    'chr4' : 191154276,
    'chr5' : 180915260,
    'chr6' : 171115067,
    'chr7' : 159138663,
    'chr8' : 146364022,
    'chr9' : 141213431,
    'chr10': 135534747,
    'chr11': 135006516,
    'chr12': 133851895,
    'chr13': 115169878,
    'chr14': 107349540,
    'chr15': 102531392,
    'chr16':  90354753,
    'chr17':  81195210,
    'chr18':  78077248,
    'chr19':  59128983,
    'chr20':  63025520,
    'chr21':  48129895,
    'chr22':  51304566,
    'chrX' : 155270560,
    'chrY' :  59373566
}

genome_length = np.sum(chr_lens.values())


def get_coverage(bed_fn, lens=chr_lens, verbose=False):
    """Get a set of chromosomes as bool arrays of coverage.

    Parameters
    ----------
    bed_fn : string
        Filename of a BED file.
    lens : {string: int}, optional
        A map of chromosome names to lengths, to build the bool arrays.
    verbose : bool, optional
        Print out error information

    Returns
    -------
    chrs : dict {string: np.array(bool)}
    """
    chrs = {}
    n_skipped = 0
    n_total = 0
    for chr_name in lens:
        chrs[chr_name] = np.zeros(lens[chr_name], np.bool)
    with open(bed_fn, 'r') as bed:
        for line in bed:
            line = line.split('\t')
            name = line[0]
            start, end = int(line[1]), int(line[2])
            try:
                chrs[name][start:end] = True
            except KeyError:
                n_skipped += 1
            n_total += 1
    if verbose:
        print "Skipped", n_skipped, "of", n_total, "lines"
    return chrs


def overlap_coverages(cover1, cover2):
    """Find the overlapping coverage between two coverage maps.

    Parameters
    ----------
    cover1, cover2: {string: np.array(bool)}
        Coverage maps as produced by 'get_coverage'.

    Returns
    -------
    cover_out : {string: np.array(bool)}
        A coverage map that intersects the two input coverages.

    Notes
    -----
    This function assumes that both input coverage maps have exactly the same
    keys.
    """
    cover_out = {}
    for chr_name in cover1:
        cover_out[chr_name] = cover1[chr_name] * cover2[chr_name]
    return cover_out


def number_of_bases_covered(cover):
    """Compute the number of true bases in a cover dictionary.

    Parameters
    ----------
    cover : {string: np.array(bool)}
        A cover map as returned by 'get_coverage'.

    Returns
    -------
    n : int
        The number of bases covered in the cover object.
    """
    n = sum(map(np.sum, cover.values()))
    return n


def main():
    """Run a few length or intersection calculations on human BED files.
    """
    parser = argparse.ArgumentParser(
        description='Compute coverage and other stats of BED files.')
    parser.add_argument('bed_files', nargs='+', metavar='BEDFILE',
                        help='One or more BED files.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print runtime information')
    args = parser.parse_args()
    get_coverage_v = ft.partial(get_coverage, verbose=args.verbose)
    beds = map(get_coverage_v, args.bed_files)
    if len(beds) > 1:
        intersect = reduce(overlap_coverages, beds)
        beds.append(intersect)
        args.bed_files.append('intersect')
    bases = map(number_of_bases_covered, beds)
    percents = map(lambda x: 100 * float(x) / genome_length, bases)
    print "filename, number of bases, percent of genome"
    for fn, base, perc in zip(args.bed_files, bases, percents):
        print fn, to_si(base), '%.2f' % perc


if __name__ == '__main__':
    main()
