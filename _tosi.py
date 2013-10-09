#!/usr/bin/env python
# -*- coding: utf-8 -*-

# copied with modifications from http://stackoverflow.com/a/15734251/224254 by @scls

import math

def to_si(d):
    incPrefixes = ['k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
    decPrefixes = ['m', 'µ', 'n', 'p', 'f', 'a', 'z', 'y']

    if d != 0:
        degree = int(math.floor(math.log10(math.fabs(d)) / 3))
    else:
        degree = 0

    prefix = ''

    if degree != 0:
        ds = degree/math.fabs(degree)
        if ds == 1:
            if degree - 1 < len(incPrefixes):
                prefix = incPrefixes[degree - 1]
            else:
                prefix = incPrefixes[-1]
                degree = len(incPrefixes)
        elif ds == -1:
            if -degree - 1 < len(decPrefixes):
                prefix = decPrefixes[-degree - 1]
            else:
                prefix = decPrefixes[-1]
                degree = -len(decPrefixes)

        scaled = float(d * math.pow(1000, -degree))
        s = "{scaled}{prefix}".format(scaled=('%.3g' % scaled), prefix=prefix)

    else:
        s = "{d}".format(d='%.3g' % d)

    return(s)
