#!/usr/bin/env python

from .sequence import *
from .components import *

def wt_sgrna(target=None):
    """
    Return the wildtype sgRNA sequence, without a spacer.

    The construct is composed of 3 domains: stem, nexus, and hairpins.  The 
    stem domain encompasses the lower stem, the bulge, and the upper stem.  
    Attachments are allowed pretty much anywhere, although it would be prudent 
    to restrict this based on the structural biology of Cas9 if you're planning 
    to make random attachments.
    """
    sgrna = Construct('wt')

    if target is not None:
        sgrna += spacer(target)

    sgrna += Domain('stem', 'GUUUUAGAGCUAGAAAUAGCAAGUUAAAAU')
    sgrna += Domain('nexus', 'AAGGCUAGUCCGU')
    sgrna += Domain('hairpins', 'UAUCAACUUGAAAAAGUGGCACCGAGUCGGUGC')
    sgrna += Domain('tail', 'UUUUUU')

    sgrna['stem'].expected_fold = '((((((..((((....))))....))))))'
    sgrna['hairpins'].expected_fold = '.....((((....)))).((((((...))))))'

    sgrna['stem'].style = 'green'
    sgrna['nexus'].style = 'red'
    sgrna['hairpins'].style = 'blue'

    sgrna['stem'].attachment_sites = 'anywhere'
    sgrna['nexus'].attachment_sites = 'anywhere'
    sgrna['hairpins'].attachment_sites = 'anywhere'

    return sgrna

def dead_sgrna(target=None):
    """
    Return the sequence for the negative control sgRNA.

    This sequence has two mutations in the nexus region that prevent the sgRNA 
    from folding properly.  These mutations were described by Briner et al.
    """
    sgrna = wt_sgrna(target)
    sgrna.name = 'dead'

    sgrna['nexus'].mutable = True
    sgrna['nexus'].mutate(2, 'C')
    sgrna['nexus'].mutate(3, 'C')
    sgrna['nexus'].mutable = False

    return sgrna

def fold_upper_stem(N, linker_len=0, splitter_len=0, num_aptamers=1, ligand='theo', target='aavs'):
    """
    Insert the aptamer into the upper stem region of the sgRNA.

    The upper stem region of the sgRNA is very tolerant to mutation.  In the 
    natural CRISPR/Cas system, this stem is actually where the two strands of  
    guide RNA (crRNA and tracrRNA) come together.

    Parameters
    ----------
    N: int
        Indicate how many of the 4 upper stem base pairs should be preserved.  
        This parameters must be between 0 and 4.  The aptamer will be inserted 
        between the two ends of the stem.

    linker_len: int
        Indicate how many bases should separate the aptamer from the upper 
        stem.  The linker sequence will have a UUUCCCUUUCCC... pattern so that 
        the design doesn't have really long repeats or an out-of-whack GC%.

    splitter_len: int
        Indicate how many bases should separate the 3' half of the aptamer from 
        the 5' half.  The splitter sequence will have the same pattern as the 
        linker (see above).

    num_aptamers: int
        The number of aptamers to insert into the sgRNA.  The aptamers are 
        inserted within each other, in a manner than should give rise to 
        positive cooperativity.
    """

    if not 0 <= N <= 4:
        raise ValueError("Location for upper stem insertion must be between 0 and 4, not {}.".format(N))

    if num_aptamers != 1:
        args = N, linker_len, splitter_len, num_aptamers
    elif splitter_len != 0:
        args = N, linker_len, splitter_len
    else:
        args = N, linker_len

    sgrna = wt_sgrna(target)
    sgrna.name = make_name('us', *args)
    sgrna.attach(
            aptamer_insert(
                ligand,
                linker_len=linker_len,
                splitter_len=splitter_len,
                num_aptamers=num_aptamers,
            ),
            'stem', 8 + N,
            'stem', 20 - N,
    )
    return sgrna

def fold_lower_stem(N, linker_len=0, splitter_len=0, ligand='theo', target='aavs'):
    """
    Insert the aptamer into the lower stem region of the sgRNA.

    Parameters
    ----------
    N: int
        Indicate how many of the 6 upper stem base pairs should be preserved.  
        This parameters must be between 0 and 6, although in practice I only 
        expect to use values greater than 4 or 5.  Shorter than that and you'll 
        almost certainly interfere with normal Cas9 binding.

    linker_len: int
        Indicate how many base pairs should separate the aptamer from the upper 
        stem.  The linker sequence will have a UUUCCCUUUCCC... pattern so that 
        the design doesn't have really long repeats or an out-of-whack GC%.

    splitter_len: int
        Indicate how many bases should separate the 3' half of the aptamer from 
        the 5' half.  The splitter sequence will have the same pattern as the 
        linker (see above).
    """

    if not 0 <= N <= 6:
        raise ValueError("Location for lower stem insertion must be between 0 and 6, not {}.".format(N))

    if splitter_len != 0:
        args = N, linker_len, splitter_len
    else:
        args = N, linker_len

    sgrna = wt_sgrna(target)
    sgrna.name = make_name('ls', *args)
    sgrna.attach(
            aptamer_insert(
                ligand,
                linker_len=linker_len,
                splitter_len=splitter_len,
            ),
            'stem', 0 + N,
            'stem', 30 - N,
    )
    return sgrna

def fold_nexus(linker_len=0, ligand='theo', target='aavs'):
    """
    Insert the aptamer into the nexus region of the sgRNA.

    The nexus is a short (2 bp) stem connected by 5 residues with irregular 
    secondary structure.  Briner et al. (2014) and Nishimasu et al. (2014) both 
    studied how mutations to this area can affect binding, but the results 
    aren't easy to rationalize.  Either one of the stem base pairs, but not 
    both, can be mutated to AU (both are naturally GC) without affecting 
    function.  Mutations were also made to 4 of the 5 positions with irregular 
    structure (sometimes in conjunction with mutations elsewhere that weren't 
    obviously compensatory) and all of those mutants were functional.
    
    My takeaway is that replacing the 5 irregular residues with the aptamer and 
    a variable length linker might be a good strategy.  For now, I'm going to 
    neglect the possibility of keeping any of the 5 irregular nexus residues.  
    There are of course many ways to do that, but no reason to think that one 
    would be more promising that any other.

    Parameters
    ----------
    linker_len: int
        Indicate how many base pairs should separate the aptamer from the nexus 
        region stem.  The linker sequence will have a UUUCCC... pattern so that 
        the design doesn't have really long repeats or an out-of-whack GC%.
    """

    sgrna = wt_sgrna(target)
    sgrna.name = make_name('nx', linker_len)
    sgrna.attach(
            aptamer_insert(
                ligand,
                linker_len=linker_len,
                repeat_factory=lambda name, length: repeat(name, length, 'U'),
            ),
            'nexus', 4,
            'nexus', 9,
    )
    return sgrna
    
def fold_nexus_2(N, M, splitter_len=0, num_aptamers=1, ligand='theo', target='aavs'):
    """
    Insert the aptamer into the nexus region of the sgRNA.

    This design strategy expands upon the original fold_nexus() function, 
    which produced promising initial hits.  This strategy allows more control 
    over where the aptamer is inserted, by having the user specify the number 
    of nucleotides to keep (N and M) on both sides of the nexus.  This strategy 
    also places the repeat sequence inside the aptamer rather than around it, 
    and allows for more than one aptamer to be chained together.

    Parameters
    ----------
    N: int
        The number of base pairs to keep on the 5' side of the nexus, starting 
        from the base of the hairpin at position 53.

    M: int
        The number of base pairs to keep on the 3' side of the nexus, starting 
        from the base of the hairpin at position 61.

    splitter_len: int
        The number of base pairs to insert into the middle of the aptamer.  The 
        linker will have the sequence 'UCGUCG...', which was chosen because it 
        has very low complementarity with the rest of the design.

    num_aptamers: int
        The number of aptamers to insert into the sgRNA.  The aptamers are 
        inserted within each other, in a manner than should give rise to 
        positive cooperativity.
    """

    # Make sure the arguments have reasonable values.

    min_splitter_len = len(aptamer('theo', 'splitter'))

    if not 0 <= N <= 4:
        raise ValueError("nxx: N must be between 0 and 4, not {}".format(N))
    if not 0 <= M <= 5:
        raise ValueError("nxx: M must be between 0 and 5, not {}".format(N))
    if 0 < splitter_len <= min_splitter_len:
        raise ValueError("nxx: splitter_len must be longer than {} (the natural linker length).".format(min_splitter_len))
    if num_aptamers < 1:
        raise ValueError("nxx: Must have at least 1 aptamer")

    # Figure out what to name the construct.  Make an effort to exclude 
    # arguments that the user didn't actually specify from the name.

    if num_aptamers != 1:
        args = N, M, splitter_len, num_aptamers
    elif splitter_len != 0:
        args = N, M, splitter_len
    else:
        args = N, M

    # Create and return the construct using a helper function.

    sgrna = wt_sgrna(target)
    sgrna.name = make_name('nxx', *args)
    sgrna.attach(
            aptamer_insert(
                ligand,
                splitter_len=splitter_len,
                num_aptamers=num_aptamers,
            ),
            'nexus', 2 + N,
            'nexus', 11 - M,
    )
    return sgrna

def fold_hairpin(H, N, A=1, ligand='theo', target='aavs'):
    """
    Replace either of the hairpins with the aptamer.  Briner et al. showed that 
    the sgRNA is at least somewhat sensitive to the distance between the nexus 
    and the hairpins, so unfolding the first hairpin may be a successful way to 
    create a sensor.  They also showed that the sgRNA is very sensitive to the 
    removal of both hairpins, but not so much to the removal of just the first.  
    They didn't try removing just the second, but it's not unreasonable to 
    think that that might be a viable way to control the sgRNA.  

    Briner et al. also didn't try changing the sequence of either hairpins, so 
    I'm just assuming that they can be freely changed as long as the base 
    pairing is maintained.  In the crystal structure, the first hairpin is not 
    interacting with Cas9 at all and the second hairpin is unresolved, so I 
    think this assumption is reasonable.  It's also worth noting that the first 
    hairpin is solvent exposed, so it should be able to sterically accommodate 
    the aptamer.

    Parameters
    ----------
    H: int
        Which hairpin to replace.  Must be either 1 or 2.  Replacing the second 
        hairpin may not be a good idea, because it think it's part of the T7 
        terminator, but I can still test it in vitro.  Worst case is that it 
        won't work as expected in vivo.

    N: int
        Indicate how many of the wildtype base pairs should be preserved.  
        This parameters must be between 0 and the number of wildtype base 
        pairs, which is 4 for the first hairpin and 6 for the second.  The 
        aptamer will be inserted between the two ends of the stem.

    A: int
        The number of aptamers to insert into the sgRNA.  The aptamers are 
        inserted within each other, in a manner than should give rise to 
        positive cooperativity.

    ligand: str
        Which aptamer to insert into the sgRNA.  Must be one of the strings 
        accepted by the aptamer() function.

    target: str
        The name of the sequence the sgRNA should target, or None if you just 
        want the sgRNA without any spacer sequence at all.
    """
    if H not in (1, 2):
        raise ValueError("fh(H,N): H must be either 1 or 2")

    max_N = (4 if H == 1 else 6)
    if not 0 <= N <= max_N:
        raise ValueError("fh(H,N): N must be between 0 and {}".format(max_N))

    sgrna = wt_sgrna(target)
    sgrna.name = make_name('fh', H, N)
    sgrna.attach(
            aptamer_insert(ligand, num_aptamers=A),
            'hairpins',  5 + N if H == 1 else 18 + N,
            'hairpins', 17 - N if H == 1 else 33 - N,
    )
    return sgrna

def replace_hairpins(N, ligand='theo', target='aavs'):
    """
    Remove a portion of the 3' terminal hairpins and replace it with the 
    aptamer.
    
    Parameters
    ----------
    N: int
        Indicate how much of the 3' terminal hairpins should be kept, with the 
        counting starting at position 63.  An N of 33 therefore specifies that 
        the whole sgRNA should be kept (excluding the poly-U tail) and that the 
        aptamer should simply be added onto the end.  Values larger than 33 
        specify that a linker should be inserted between the sgRNA and the 
        aptamer.  Values smaller than 33 specify that some residues should be 
        truncated from the 3' end of the sgRNA.  The expected range for this 
        parameter is roughly 17-33.

    Returns
    -------
    sgRNA: Construct
        The specified construct will be returned, with a hexa-uracil tail will 
        added to the end for the benefit of the T7 polymerase.
    """
    design = wt_sgrna(target)
    design.name = make_name('hp', N)

    domain_len = len(design['hairpins'])
    insertion_site = min(N, domain_len)
    linker_len = max(0, N - domain_len), 0

    design.attach(
            aptamer_insert(ligand, linker_len=linker_len),
            'hairpins', insertion_site,
            'hairpins', '...',
    )
    return design

def induce_dimerization(half, N, target='aavs', ligand='theo'):
    """
    Split the guide RNA into its two naturally occurring halves, and use the 
    aptamer to bring those halves together in the presence of the ligand.  The 
    aptamer replaces some or all of the upper stem.  We have already observed 
    that an sgRNA with the upper stem fully replaced by the theophylline 
    aptamer is fully functional, so the design should work if the ligand 
    successfully induces dimerization.

    Parameters
    ----------
    half: 5 or 3
        Indicate which half of the split construct to return.  '5' and '3' 
        refer to the 5' and 3' halves, respectively.

    N: int
        Indicate how many of the 4 upper stem base pairs should be preserved.  
        This parameters must be between 0 and 4.
    """

    # Make sure the arguments make sense.

    half = str(half)
    N = int(N)

    if not 0 <= N <= 4:
        raise ValueError("Location for upper stem insertion must be between 0 and 4, not {}.".format(N))

    # Construct and return the requested sequence.

    design = Construct()
    design.name = make_name('id', half, N)
    wt = wt_sgrna(target)

    if half == '5':
        try: design += wt['spacer']
        except KeyError: pass
        design += wt['stem']
        design.attach(
                aptamer(ligand, '5'),
                'stem', 8 + N, 'stem', '...',
        )
    elif half == '3':
        design += wt
        design.attach(
                aptamer(ligand, '3'),
                'stem', '...', 'stem', 20 - N,
        )
    else:
        raise ValueError("Half for induced dimerization must be either 5 (for the 5' half) or 3 (for the 3' half), not '{}'.".format(half))

    return design

def serpentine_bulge(N, tuning_strategy='', A=1, ligand='theo', target='aavs'):
    """
    Sequester the bulge in a non-productive hairpin when the ligand isn't 
    present.  The bulge is an interesting target because it doesn't have to be 
    there, but if it is there it must be unpaired and it must have its wildtype 
    sequence.  This design uses the two adenosines that are naturally in the 
    bulge to construct a tetraloop that caps the non-productive hairpin.  Below 
    is an ASCII-art schematic of the design, along with an example sequence:

       ┌──────────┐┌───────────┐┌────┐┌────────────┐┌─────┐┌──────────┐ 
    5'─┤lower stem├┤  bulge''  ├┤theo├┤   bulge'   ├┤bulge├┤lower stem├─3'
       └──────────┘└───────────┘└────┘└────────────┘└─────┘└──────────┘ 
        GUUUUAga    UCGU(UAAAAU) ...  (GUUUUA)AC-GA  AA-GU  UAAAAU
                                                 └────┘
                                                tetraloop

    The length of the non-productive hairpin can be extended by including bases 
    from the lower stem, as shown in parentheses.  Mutations can be made in the 
    bulge', bulge'', and lower stem regions to tune the balance between the 
    "on" and "off" states.  The bulge itself is never changed.

    Parameters
    ----------
    N: int
        Indicate how long the non-productive hairpin should be.  It can't be 
        shorter than 2 base pairs.  The first two bases in the hairpin come 
        from the bulge, and subsequent bases come from the lower stem.

    A: int
        The number of aptamers to insert into the sgRNA.  The aptamers are 
        inserted within each other, in a manner than should give rise to 
        positive cooperativity.

    target: str
        The name of the sequence the sgRNA should target, or None if you just 
        want the sgRNA without any spacer sequence at all.
    """
    if N < 2:
        raise ValueError("sb(N): N must be 2 or greater")

    sgrna = wt_sgrna(target)
    sgrna.name = make_name('sb', N, tuning_strategy)
    sgrna.attach(
            serpentine_insert(
                ligand,
                wt_sgrna()['stem'][22:22+N], '3',
                tuning_strategy, num_aptamers=A,
            ),
            'stem', 8,
            'stem', 22,
    )
    sgrna['on'].prepend('UC')

    return sgrna

def serpentine_lower_stem(tuning_strategy='', A=1, ligand='theo', target='aavs'):
    """
    Sequester the nexus in base pairs with the lower stem in the absence of the 
    ligand.  This design is based off two ideas:
    
    1. That disrupting the nexus will be an effective way to deactivate the 
       sgRNA, because the nexus seems to be very sensitive to mutation.

    2. That the lower stem can be modified to have some complementarity with 
       the nexus, because the exact sequence of the lower stem seems to be 
       important, so long as it does actually form a stem.
    
    This design is named "serpentine_lower_stem" because it uses applies the 
    "serpentine" strategy to the lower stem region of the sgRNA.  A schematic 
    of this strategy is shown below.  The "serpentine" pattern is formed 
    because nexus' can base pair either with nexus or nexus''.  Note that the 
    length of the serpentine pattern is fixed at four base pairs, because the 
    length of the lower stem must be six base pairs (and two base pairs are 
    required to form the tetraloop).

       ┌───────┐┌──┐┌────┐┌────┐┌──────┐┌───────┐ 
    5'─┤nexus''├┤GA├┤theo├┤AAGU├┤nexus'├┤ nexus ├─3'
       └───────┘└──┘└────┘└────┘└──────┘└───────┘ 
        UC-GGCU  GA  ...   AAGU  AGCC-GA AA-GGCU
                                      └───┘
                                    tetraloop
    Parameters
    ----------
    A: int
        The number of aptamers to insert into the sgRNA.  The aptamers are 
        inserted within each other, in a manner than should give rise to 
        positive cooperativity.

    target: str
        The name of the sequence the sgRNA should target, or None if you just 
        want the sgRNA without any spacer sequence at all.
    """
    sgrna = wt_sgrna(target)
    sgrna.name = make_name('sl', tuning_strategy)
    sgrna.attach(
            serpentine_insert(
                ligand,
                'GGCU', '3',
                tuning_strategy,
                num_aptamers=A,
            ),
            'stem', 0,
            'nexus', 2,
    )
    sgrna['on'].prepend('UC')
    sgrna['on'].append('GA')
    sgrna['switch'].prepend('AAGU')
    return sgrna

def serpentine_lower_stem_around_nexus(tuning_strategy='', A=1, ligand='theo', target='aavs'):
    """
    Use the lower stem to extend the nexus stem in the absence of the aptamer 
    ligand.  This design is based of the idea that the sgRNA is very sensitive 
    to the length of the nexus stem and that the bases in the lower stem can be 
    freely mutated to complement the region just beyond the nexus stem.  The 
    extended stem will have a bulge because there is a short AA linker between 
    the lower stem and the nexus, and the length of the complementary region 
    will be fixed at 6 base pairs because the lower stem cannot be lengthened 
    or shortened.  A schematic of this design is shown below:

       ┌──────┐┌──┐┌────┐┌────┐┌──────┐┌──┐┌─────────┐┌──────┐ 
    5'─┤  on  ├┤GA├┤theo├┤AAGU├┤switch├┤AA├┤  nexus  ├┤ off  ├─3'
       └──────┘└──┘└────┘└────┘└──────┘└──┘└─────────┘└──────┘ 
        GUUAUC  GA  ...   AAGU  GAUAAC  AA  GGCUAGUCC  GUUAUC
    
    Parameters
    ----------
    A: int
        The number of aptamers to insert into the sgRNA.  The aptamers are 
        inserted within each other, in a manner than should give rise to 
        positive cooperativity.

    target: str
        The name of the sequence the sgRNA should target, or None if you just 
        want the sgRNA without any spacer sequence at all.
    """
    sgrna = wt_sgrna(target)
    sgrna.name = make_name('slx', tuning_strategy)
    sgrna.attach(
            serpentine_insert(
                ligand,
                'GUUAUC', '3',
                tuning_strategy,
                turn_seq='',
                num_aptamers=A,
            ),
            'stem', '...',
            'stem', '...',
    )
    sgrna['on'].append('GA')
    sgrna['switch'].prepend('AAGU')
    return sgrna

def serpentine_hairpin(N, tuning_strategy='', A=1, ligand='theo', target='aavs'):
    """
    Sequester the 3' end of the nexus in base pairs with the 5' strand of the 
    first hairpin in the absence of aptamer ligand.  This design is based on 
    the fact that proper nexus folding is required for sgRNA function and the 
    assumption that the sequence of the first hairpin can be changed if its 
    base pairing is maintained.  Briner et al. didn't actually test any point
    mutations in the first hairpin, but they did find that the whole hairpin 
    can be deleted so long as a two residue spacer is added to maintain the 
    positioning of the second hairpin.

       ┌────────────┐┌────┐┌──────┐┌────┐┌───────┐ 
    5'─┤   nexus    ├┤turn├┤nexus'├┤theo├┤nexus''├─3'
       └────────────┘└────┘└──────┘└────┘└───────┘ 
        GGCUAGUCCGUU  AUCA  AACG... ...   ...CGUU
    
    Parameters
    ----------
    N: int
        The length of the complementary region to insert, and also the length 
        of the first hairpin.  The hairpin is naturally 4 base pairs long, but 
        it's solvent exposed so in theory you can make it as long as you want.

    A: int
        The number of aptamers to insert into the sgRNA.  The aptamers are 
        inserted within each other, in a manner than should give rise to 
        positive cooperativity.

    target: str
        The name of the sequence the sgRNA should target, or None if you just 
        want the sgRNA without any spacer sequence at all.
    """
    if not 4 <= N <= 14:
        raise ValueError("sh(N): N must be between 4 and 14")

    sgrna = wt_sgrna(target)
    sgrna.name = make_name('sh', N, tuning_strategy)
    sgrna.attach(
            serpentine_insert(
                ligand,
                wt_sgrna().seq[44-N:44], '5',
                tuning_strategy,
                turn_seq='AUCA', # ANYA
                num_aptamers=A,
            ),
            'hairpins', 1,
            'hairpins', 17,
    )
    return sgrna

def circle_bulge(tuning_strategy='', A=1, ligand='theo', target='aavs'):
    """
    Extend the lower stem hairpin through the bulge when the small molecule is 
    absent.  This design is based off the fact that "straightening" the bulge 
    (i.e. mutating both side so they can base pair) completely eliminates Cas9 
    activity.  Note that this design unconditionally removes the 5' part of the 
    bulge, which has the sequence 'GA'.  In wildtype sgRNA, this mutation does
    not have a significant effect.  

    This design is named "circle_bulge" because it uses the "circle" strategy 
    to sequester the bulge region of the sgRNA.  A schematic of this strategy 
    is shown below.  The circle is formed when bulge' binds to either bulge'' 
    or bulge.  The sgRNA is only active when bulge is unpaired, and ligand 
    binding by the aptamer should encourage this conformation.

       ┌──────────┐┌──────┐┌────┐┌───────┐┌─────┐┌──────────┐ 
    5'─┤lower stem├┤bulge'├┤theo├┤bulge''├┤bulge├┤lower stem├─3'
       └──────────┘└──────┘└────┘└───────┘└─────┘└──────────┘ 
        GUUUUA      ACUU    ...   AAGU     AAGU   UAAAAU

    Parameters
    ----------
    A: int
        The number of aptamers to insert into the sgRNA.  The aptamers are 
        inserted within each other, in a manner than should give rise to 
        positive cooperativity.

    target: str
        The name of the sequence the sgRNA should target, or None if you just 
        want the sgRNA without any spacer sequence at all.
    """
    sgrna = wt_sgrna(target)
    sgrna.name = make_name('cb', tuning_strategy)
    sgrna.attach(
            circle_insert(
                ligand, 'AAGU', '3',
                tuning_strategy, num_aptamers=A,
            ),
            'stem', 6,
            'stem', 20,
    )
    return sgrna

def circle_bulge_combo(tuning_strategy, combo_strategy, combo_arg=None, A=1, ligand='theo', target='aavs'):
    """
    Combine the circle bulge design with orthogonal designs.  The idea is to 
    increase fold activation, possibly at the expense of affinity, by requiring 
    two switches to turn on.  Only a select set of orthogonal designs, known to 
    be functional on their own, can be combined with 'cb'.  This set includes 
    most of the 'slx' and 'sh' families of designs.

    Parameters
    ----------
    tuning_strategy: str
        A string specifying which mutation(s) to make in the 'cb' switch.

    combo_strategy: str
        A string specifying which design to integrate into 'cb'. Either 'slx' 
        or 'sh'.
        
    combo_arg:
        Arguments to the orthogonal design.  What's expected depends on the 
        value of 'combo_strategy'.
    """
    sgrna = circle_bulge(tuning_strategy)
    sgrna.name = make_name('cb', tuning_strategy, combo_strategy, combo_arg)

    # Serpentine the lower stem around the nexus.  This code isn't done by 
    # making an attachment, like all the other designs are, because its 
    # attachment would overlap with circle bulge.  Instead, the on and switch 
    # domains are directly mutated into the existing stem domain.

    if combo_strategy == 'slx':
        L = len(sgrna['stem'])
        switch_domain, on_domain, off_domain = tunable_switch(
                'GUUAUC', combo_arg or 'wo')
        sgrna['stem'].replace(0, 6, on_domain.seq)
        sgrna['stem'].replace(L-6, L, switch_domain.seq)

    # Serpentine the first hairpin.  This code is copied verbatim from the sh() 
    # function.

    elif combo_strategy == 'sh':
        if combo_arg is None:
            raise ValueError("The 'sh' combo strategy requires an argument.")
        sgrna.attach(
                serpentine_insert(
                    ligand,
                    wt_sgrna().seq[44-combo_arg:44], '5',
                    '',
                    turn_seq='AUCA', # ANYA
                    num_aptamers=A,
                ),
                'hairpins', 1,
                'hairpins', 17,
        )
    else:
        raise ValueError("unsupported strategy: '{}'".format(strategy))

    return sgrna

def circle_lower_stem(tuning_strategy='', A=1, ligand='theo', target='aavs'):
    """
    Sequester the 5' half of the nexus in base pairs with the 5' half of the 
    lower stem in the absence of aptamer ligand.  This strategy is based on  
    the fact that the nexus must be natively folded for the sgRNA to function 
    and that the specific sequence in the lower stem doesn't matter as long as 
    it's well base paired.

    This is an application of the "circle" strategy, which is known as "strand 
    displacement" in the literature.  The 5' half of the lower stem (nexus') 
    can either base pair with the 3' half of the lower stem (nexus'') or the 5' 
    half of the nexus.  The former is the active state and the latter is the 
    inactive state.  When the aptamer binds its ligand, that should encourage 
    the formation of the active state.  A schematic of the design strategy is 
    shown below:

       ┌──────┐┌──┐┌────┐┌────┐┌───────┐┌─────┐ 
    5'─┤nexus'├┤AG├┤theo├┤AAGU├┤nexus''├┤nexus├─3'
       └──────┘└──┘└────┘└────┘└───────┘└─────┘ 
        AGCCUU  AG  ...   AAGU  AAGGCU   AAGGCU 

    Note that the length of the nexus' and nexus'' sequences must be six, 
    because the length of the lower stem cannot change.  Currently, the 
    sequence is also fixed to match the start of the nexus (AAGGCU), but this 
    doesn't have to be the case.  Sliding this sequence in the 3' direction 
    could also yield viable designs.

    Parameters
    ----------
    A: int
        The number of aptamers to insert into the sgRNA.  The aptamers are 
        inserted within each other, in a manner than should give rise to 
        positive cooperativity.

    target: str
        The name of the sequence the sgRNA should target, or None if you just 
        want the sgRNA without any spacer sequence at all.
    """
    sgrna = wt_sgrna(target)
    sgrna.name = make_name('cl', tuning_strategy)
    sgrna.attach(
            circle_insert(
                ligand, 'AAGGCU', '3',
                tuning_strategy, num_aptamers=A,
            ),
            'stem', 0,
            'stem', '...',
    )
    sgrna['switch'].append('GA')
    sgrna['on'].prepend('AAGU')
    return sgrna

def circle_hairpin(N, tuning_strategy='', A=1, ligand='theo', target='aavs'):
    """
    Move the nexus closer to the hairpins in the absence of the aptamer's 
    ligand.  This design is supported by the fact that inserting one residue 
    into the region between the nexus and the hairpins substantially reduces 
    sgRNA function.  Briner et al. didn't try to remove residues from this 
    region, but it seems reasonable to expect that doing so would also be 
    quite deleterious.
    
    This is an application of the "circle" strategy, which is known as "strand 
    displacement" in the literature.  The 5' half of the first hairpin (ruler') 
    can either base pair with the 3' half of the same hairpin (ruler'') or the 
    region between the nexus and the hairpin (ruler).  The former is the 
    active state and the latter is the inactive state.  When the aptamer binds 
    its ligand, that should encourage the formation of the active state.  A 
    schematic of the design strategy is shown below:

       ┌──────┐┌───────┐┌────┐┌──────┐ 
    5'─┤ruler ├┤ruler''├┤theo├┤ruler'├─3'
       └──────┘└───────┘└────┘└──────┘ 
        ..AUCA  ..AUCA   ...   UGAU..  

    Parameters
    ----------
    N: int
        The length of the complementary region to insert, and also the length 
        of the first hairpin.  The hairpin is naturally 4 base pairs long, but 
        it's solvent exposed so in theory you can make it as long as you want.

    A: int
        The number of aptamers to insert into the sgRNA.  The aptamers are 
        inserted within each other, in a manner than should give rise to 
        positive cooperativity.

    target: str
        The name of the sequence the sgRNA should target, or None if you just 
        want the sgRNA without any spacer sequence at all.
    """
    sgrna = wt_sgrna(target)
    sgrna.name = make_name('ch', N, tuning_strategy)
    sgrna.attach(
            circle_insert(
                ligand,
                wt_sgrna().seq[48-N:48], '5',
                tuning_strategy,
                num_aptamers=A),
            'hairpins', 5,
            'hairpins', 17,
    )
    return sgrna

def hammerhead_upper_stem(mode, A=1, ligand='theo', target='aavs'):
    sgrna = wt_sgrna(target)
    sgrna.name = make_name('hu', mode)
    sgrna.attach(
            hammerhead_insert(ligand, mode, num_aptamers=A),
            'stem', 8,
            'stem', 20,
    )
    return sgrna

def hammerhead_nexus(mode, A=1, ligand='theo', target='aavs'):
    sgrna = wt_sgrna(target)
    sgrna.name = make_name('hx', mode)
    sgrna.attach(
            hammerhead_insert(ligand, mode, num_aptamers=A),
            'nexus', 2,
            'nexus', 11,
    )
    return sgrna

def hammerhead_hairpin(mode, A=1, ligand='theo', target='aavs'):
    sgrna = wt_sgrna(target)
    sgrna.name = make_name('hh', mode)
    sgrna.attach(
            hammerhead_insert(ligand, mode, num_aptamers=A),
            'hairpins', 5,
            'hairpins', 17,
    )
    return sgrna


## Abbreviations

# Strategy Abbreviations
# ======================
# f: fold
# s: serpentine
# c: circle
# h: hammerhead
# z: zipper (reserved)

# Domain Abbreviations
# ====================
# u: upper stem
# l: lower stem
# b: bulge
# x: nexus
# h: hairpins

wt = wt_sgrna
dead = dead_sgrna
fu = us = fold_upper_stem
fl = ls = fold_lower_stem
fx = nx = fold_nexus
fxx = nxx = fold_nexus_2
fh = fold_hairpin
hp = replace_hairpins
id = induce_dimerization
sb = serpentine_bulge
sl = serpentine_lower_stem
slx = serpentine_lower_stem_around_nexus
sh = serpentine_hairpin
cb = circle_bulge
cbc = circle_bulge_combo
cl = circle_lower_stem
ch = circle_hairpin
hu = hammerhead_upper_stem
hx = hammerhead_nexus
hh = hammerhead_hairpin

t7 = t7_promoter
th = theo = lambda: aptamer('theo')
