#!/usr/bin/env python

import math, random


def draw_graph(title, keys, arr_data):
    """ Draws an ascii graph. the variable keys is two nested arrays, x-axis and y-axis and title the title.
    """
    #-- Normalize
    total = 0.0
    for value in arr_data:
        total += value
    total = 1 / total
    
    vmax = 0.0
    vnml = []
    for idx in range(len(arr_data)):
        vnml.append(round(arr_data[idx] * total, 3))
        vmax = max(vmax, vnml[-1])
    
    #-- Plot
    glen = 18
    step = vmax / glen
    
    matrix = []
    for idx in range(glen):
        matrix.append(list())
        for value in vnml:
            if value >= (step * idx):
                matrix[-1].append("*")
            else:
                matrix[-1].append(" ")
    
    #-- Draw
    idx = 0
    while idx < glen:
        idx += 1
        if idx != glen:
            print ("     %s" % round((glen - idx) * step, 2))[-5:], "| " + "  ".join(matrix[glen - idx]) + " "
        else:
            print ("     %s" % round((glen - idx) * step, 2))[-5:], "+-" + "--".join(matrix[glen - idx]) + "-"
    print "        " + "  ".join(keys)


def montecarlo(iterations, token_length):
    """
    """
    print "\n\nMontecarlo for token of length %s over %s iterations:" % (token_length, iterations)
    data = [0 for _ in range(16)]

    idx = 0
    moan = math.floor(iterations / 5)
    while idx < iterations:
        idx += 1
        if idx % moan == 0:
            print "%s%% >> %s" % (round((100 * idx) / iterations, 2), ",".join([str(_n) for _n in data]))
        
        token = [random.randrange(16) for _ in range(token_length)]
        tmax = 0
        tmin = 15
        for char in token:
            tmax = max(tmax, char)
            tmin = min(tmin, char)
        
        data[tmax - tmin] += 1
    
    print "Montecarlo done.\n"
    return data


for idx in range(3):
    data = montecarlo(10000000, 9 + idx)
    draw_graph("", ["%s" % hex(idx)[-1] for idx in range(16)], data)

