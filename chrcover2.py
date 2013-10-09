import argparse
import functools as ft

import numpy as np
import pybedtools as bed

from _tosi import to_si

hg19 = bed.genome_registry.hg19 # this is an OrderedDict

# Keep only contigs uniquely mapped to chromosomes
genome_length = np.sum([v[1] for v in hg19.values()[:25]])


def get_coverage(bedtool, pred=None):
    """Get a BED map where each nucleotide position appears at most once.

    Parameters
    ----------
    bedtool : a BedTool object
        An arbitrary BedTool object (or anything that can be cast as one
        by the BedTool constructor).
    pred : function mapping Interval to bool, optional
        Only keep intervals satisfying `pred`.

    Returns
    -------
    merge : BedTool object
        The merged segments in `bedtool`.
    """
    bedtool = bed.BedTool(bedtool)
    bedtool = bedtool.sort().merge()
    if pred is None:
        pred = lambda x: True
    merge = bedtool.filter(pred).saveas()
    return merge


def overlap_coverages(cover1, cover2):
    """Find the overlapping coverage between two coverage maps.

    Parameters
    ----------
    cover1, cover2: BedTool objects

    Returns
    -------
    cover_out : BedTool object
        Intersection of the two input BedTool objects
    """
    cover_out = cover1.intersect(cover2).sort().merge()
    return cover_out


def number_of_bases_covered(cover):
    """Compute the number of true bases in a cover dictionary.

    Parameters
    ----------
    cover : BedTool object
        A BED map *assumed* not to contain overlapping regions.

    Returns
    -------
    n : int
        The number of bases covered in the BED map.
    """
    n = sum(map(len, cover))
    return n


def in_mapped_contig(ival, reference=hg19, chroms=25):
    """Determine whether `ival` is in a contig mapped to a reference chromosome.

    Parameters
    ----------
    ival : pybedtools Interval object
        The interval being tested.
    reference : OrderedDict of {string: (int, int)}
        The reference genome.
    chroms : int
        The `chroms` first items in `reference` are considered chromosome
        contigs.

    Returns
    -------
    is_mapped : bool
        Whether `ival` is mapped to a chromosome contig.
    """
    return ival.chrom in reference.keys()[:chroms]


def main():
    """Run a few length or intersection calculations on human BED files.
    """
    parser = argparse.ArgumentParser(
        description='Compute coverage and other stats of BED files.')
    parser.add_argument('bed_files', nargs='+', metavar='BEDFILE',
                        help='One or more BED files.')
    parser.add_argument('-o', '--output', metavar='FN_OUT',
                        help='Save the intersection file.')
    args = parser.parse_args()
    get_coverage_chrom = ft.partial(get_coverage, pred=in_mapped_contig)
    beds = map(get_coverage_chrom, args.bed_files)
    if len(beds) > 1:
        intersect = reduce(overlap_coverages, beds)
        beds.append(intersect)
        if args.output is not None:
            intersect.saveas(args.output)
            args.bed_files.append(args.output)
        else:
            args.bed_files.append('intersect')
    bases = map(number_of_bases_covered, beds)
    percents = map(lambda x: 100 * float(x) / genome_length, bases)
    print "filename, number of bases, percent of genome"
    for fn, base, perc in zip(args.bed_files, bases, percents):
        print fn, to_si(base), '%.2f' % perc


if __name__ == '__main__':
    main()
