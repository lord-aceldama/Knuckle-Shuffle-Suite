from brute import Incremental
from brute import Permute

CHARS  = "abcdefg"
LENGTH = 4


def get_abacus(abacus):
    token = ""
    for idx in range(len(CHARS)):
        token += CHARS[idx] if idx in abacus else "-"
    return token


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
    
    lines = []
    while len(lines) * 10 < len(found):
        lines += ["  xx"]
    
    return found

#-- Get the smart incs
test = Incremental(CHARS, LENGTH)
full = set([str(test)])
while not test.done:
    test.inc()
    full.add("".join(sorted(str(test))))
full = sorted(full)

#-- Build abacus
abacus = range(LENGTH)

flag = False
total = 0
while not flag:
    found = find_all(abacus, full)
    print get_abacus(abacus), "[{}]".format(len(found))
    count = 0
    for token in found:
        perms = Permute.permutations(token)
        count += perms
        print " ", token, "[{}]".format(perms)
        if perms > 1:
            shuffle = Permute(token)
            while not shuffle.done:
                prn = "  "
                while (not shuffle.done) and (len(prn) < 25):
                    prn += "  " + str(shuffle)
                    shuffle.inc()
                if shuffle.done:
                    print prn, "", shuffle
                else:
                    print prn
    
    print "TOTAL:", count, "\n"
    total += count
    
    flag = is_done(abacus)
    if not flag:
        print
        inc_abacus(abacus)

print "\n\nMISSED TOKENS:", full
print "TOTAL TOKENS:", total
