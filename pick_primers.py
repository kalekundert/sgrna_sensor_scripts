#!/usr/bin/env python3

"""\
Automatically design primers that can be used to construct the given sgRNA 
design by overlap extension PCR.  There are a number of parameters controlling 
how ideal the primers have to be, and you can play with them to get more or 
fewer results.

I ended up not using this script in favor of ordering my designs as gBlocks 
gene fragments from IDT.  The PCR assembly takes as long as it takes IDT to 
deliver gBlocks, and the gBlocks are much higher purity.  The gBlocks are also 
not that much more expensive at $90 per design.  Most of the primers are ~$30, 
and then you have to add reagents and my time.

Usage:
    pick_primers.py <name> [options]

Options:
    --max-num-primers NUM
    --min-primer-len LEN            [default: 40]
    --max-primer-len LEN            [default: 50]
    --min-overlap-len LEN           [default: 18]
    --max-overlap-len LEN           [default: 22]
    --min-overlap-tm CELSIUS        [default: 52.0]
    --max-overlap-tm CELSIUS        [default: 58.0]
    --max-tm-diff DELTA-CELSIUS     [default: 2.0]
    --max-gc-content PERCENT        [default: 0.6]
    --min-gc-content PERCENT        [default: 0.3]
    -c, --color WHEN                [default: auto]
    -q, --header-only
"""

import sys, docopt
import pcr_helper, sgrna_sensor

args = docopt.docopt(__doc__)

print('$ ' + ' '.join(sys.argv))
print()

design = sgrna_sensor.from_name(args['<name>'])

assembler = pcr_helper.PcrAssembly()
assembler.max_num_primers = int(args['--max-num-primers'] or 0)
assembler.min_primer_len = int(args['--min-primer-len'])
assembler.max_primer_len = int(args['--max-primer-len'])
assembler.min_overlap_len = int(args['--min-overlap-len'])
assembler.max_overlap_len = int(args['--max-overlap-len'])
assembler.min_overlap_tm = float(args['--min-overlap-tm'])
assembler.max_overlap_tm = float(args['--max-overlap-tm'])
assembler.max_tm_diff = float(args['--max-tm-diff'])
assembler.max_gc_content = float(args['--max-gc-content'])
assembler.min_gc_content = float(args['--min-gc-content'])
assembler.use_color = args['--color']

assembler.find_primers(design)
assembler.print_primers(args['--header-only'])









