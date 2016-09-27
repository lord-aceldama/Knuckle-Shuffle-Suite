from brute import Permute
from brute import Incremental

SHOW_PERMS = False
CHARS  = "abcdefg"
LENGTH = 5


#----------------------------------------------------------------------------------------------------------------------
def get_abacus(abacus):
    token = ""
    for idx in range(len(CHARS)):
        token += CHARS[idx] if idx in abacus else "-"
    return token


def cm_print(abacus, checked):
    for idx in range(len(CHARS)):
        tmp = ("  [{}] : " if idx in abacus else "   {}  : ").format(CHARS[idx])
        for idx2 in range(len(CHARS)):
            tmp += CHARS[idx2] if idx2 in checked[idx] else "+" if (idx2 in abacus) and (idx in abacus) else "-"
        if (idx in abacus):
            tmp += "  <- "
            if len(checked[idx]) == 0:
                tmp += "None"
            elif checked[idx].issuperset(abacus):
                tmp += "Full"
            else:
                tmp += "Part"
                
        print tmp


def is_done(abacus):
    flag = abacus[0] == 0
    idx = 1
    while flag and (idx < len(abacus)):
        flag = flag and abacus[-idx] == len(CHARS) - idx
        idx += 1
    return flag

    
def inc_abacus(abacus):
    if abacus[-1] < len(CHARS) - 1:
        for idx in range(len(abacus)):
            abacus[idx] += 1
    else:
        idx = len(abacus)
        while idx > 0:
            idx -= 1
            abacus[idx] -= abacus[0]
        
        idx = 1
        abacus[idx] += 1
        while (idx < len(abacus) - 1) and (abacus[idx] == abacus[idx + 1]):
            abacus[idx] = abacus[idx - 1] + 1
            idx += 1
            abacus[idx] += 1


def find_all(abacus, full):
    check = set("".join([CHARS[idx] for idx in abacus]))
    found = []
    for token in full:
        if check.issuperset(token):
            found.append(token)
    
    for token in found:
        full.remove(token)
    
    return found


def find_actual(abacus, checked):
    def _stat(abacus, checked):
        empty_sets      = 0
        partial_sets    = 0
        complete_sets   = 0
        for idx in abacus:
            if checked[idx].issuperset(abacus):
                complete_sets += 1
            elif len(checked[idx]) == 0:
                empty_sets += 1
            else:
                partial_sets += 1
        return (empty_sets, partial_sets, complete_sets)
    
    def _tokens(abacus, choke):
        t = []
        idx = 1
        index = [choke[i][0] for i in range(len(abacus))]
        while idx > 0:
            t.append("".join([CHARS[abacus[i]] for i in index]))
            idx = len(index)-1
            while (idx >= 0) and ((index[idx] + 1) >= len(choke[idx])):
                index[idx] = choke[idx][0]
                idx -= 1
            if idx >= 0:
                index[idx] += 1
                idx += 1
                while idx < len(index):
                    index[idx] = max(index[idx], index[idx-1])
                    idx += 1
        return t
    
    empty_sets, partial_sets, complete_sets = _stat(abacus, checked)
    choke = [range(len(abacus)) for _ in abacus]
    if complete_sets < len(abacus):
        if empty_sets < len(abacus):
            #-- Last index is always static after the initial set
            choke[-1] = [choke[-1][-1]]
            if (partial_sets > 1) and (empty_sets == 0):
                #-- First index is also static
                choke[0] = [choke[0][0]]
    else:
        choke = [[i] for i in range(len(abacus))]
    
    return _tokens(abacus, choke)


#----------------------------------------------------------------------------------------------------------------------
#-- Set up the abacus and create a tracker for orphans
checked = [set([]) for _ in CHARS]
abacus = range(LENGTH)
miss = []

#-- Get all the base tokens
test = Incremental(CHARS, LENGTH)
full = set([str(test)])
while not test.done:
    test.inc()
    full.add("".join(sorted(str(test))))
full = sorted(full)

flag = False
total = 0
while not flag:
    found  = find_all(abacus, full)
    actual = find_actual(abacus, checked)
    miss += sorted(set(found).difference(actual))
    print get_abacus(abacus), " [base tokens: {}]".format(len(found))
    
    #-- Print checked matrix
    cm_print(abacus, checked)
    print
    
    #-- Print base tokens and their permutations
    count = 0
    for token in found:
        perms = Permute.permutations(token)
        count += perms
        print " ", token, "[{}]{}".format(perms, ("" if token in actual else "  <- MISS"))
        if SHOW_PERMS and (perms > 1):
            shuffle = Permute(token)
            while not shuffle.done:
                prn = "  "
                col = 0
                while (not shuffle.done) and (col < (1 * LENGTH)):
                    prn += "  " + str(shuffle)
                    shuffle.inc()
                    col += 1
                if shuffle.done:
                    print prn, "", shuffle
                else:
                    print prn
    
    #-- Update checked
    for idx in abacus:
        checked[idx].update(abacus)
    
    print "MISS:", sorted(set(found).difference(actual))
    print "TOTAL:", count, "\n"
    total += count
    
    flag = is_done(abacus)
    if not flag:
        print
        inc_abacus(abacus)

print "\n\nMISSED TOKENS ({}):".format(len(miss))
match = [[] for _ in miss]
abacus = range(LENGTH)
while not is_done(abacus):
    for i in range(len(miss)):
        token = "".join([CHARS[idx] for idx in abacus])
        if set(miss[i]).issubset(token):
            match[i].append(token)
    inc_abacus(abacus)

for i in range(len(miss)):
    print "  {}: {}".format(miss[i], match[i])

print "\nTOTAL TOKENS:", total




