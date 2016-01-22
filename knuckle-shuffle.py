#!/usr/bin/env python
""" Docstring """

#-- Dependancies
import sys
import math
#import signal
#import socket


#-- Globals all in constants
ENDFLAG = 0
CHARSET = sorted("abc")
INDEXES = [0, 0, 0]


def smart_inc():
    """ Increments the indexes in a way such that it doesn't allow for a
        smaller sorted token as they would've been processed in a token
        permutation. (ie. abc -> acc -> bbb -> bbc -> bcc etc. because
        abc -> aca is in print_shuffle(aac) -> [aac, aca, caa])
    """
    global INDEXES, CHARSET
    
    #-- Find the first incrementable index (RTL)
    i = len(INDEXES) - 1
    while (i > 0) and (INDEXES[i] == (len(CHARSET) - 1)):
        i -= 1
    
    #-- Increment
    INDEXES[i] += 1
    
    if INDEXES[i] == len(CHARSET):
        #-- We've reached the end of all possible increments
        return False
    else:
        #-- Set all indexes to the right of the incremented
        #   index to value at incremented index.
        i += 1
        while i < len(INDEXES):
            INDEXES[i] = INDEXES[i - 1]
            i += 1
        
    #-- Further increments possible.
    return True


def print_shuffle(chars, prefix=""):
    """ Generates all unique permutations of a char array 
    """
    global ENDFLAG
    
    total = 0
    if len(chars) == 1:
        #-- End of recursion reached and successful token found.
        sys.stdout.write(prefix + chars[0] + "\n")
        sys.stdout.flush()
        total = 1
    else:
        #-- Cycle through allcharacters in the chars array
        for i in range(len(chars)):
            #-- Because of smart_inc, we no longer need to check whether 
            #   the current permutation is larger than the smallest token.
            #   The 2nd condition is therefore redundant and not needed:
            #     > (prefix+chars[i]) >= strlowest[0:len(prefix) + 1]
            
            #-- If the character at the current position also to the right
            #   we don't need process it as it would create duplicates. 
            if (ENDFLAG == 0) and (chars[i] not in chars[i + 1:]):
                tchr = list(chars)
                tpop = tchr.pop(i)
                total += print_shuffle(tchr, prefix + tpop)
    
    return total
    

def get_token():
    """ Returns the currently computed token character array.
    """
    global CHARSET, INDEXES
    
    token = []
    for i in INDEXES:
        token += list(CHARSET[i])
    return token


def get_strtoken():
    """ Like get_token(), but returns the currently computed token as a string.
    """
    global CHARSET, INDEXES
    
    strtoken = ""
    for idx in INDEXES:
        strtoken += CHARSET[idx]
    return strtoken
    

def get_args():
    """ Gets the comand line arguments
    """
    global INDEXES, CHARSET
    defaults = ["abcdefghjklmnpqrstuvwxyz", 8, ""]
    for i in range(1, len(sys.argv)):
        #print sys.argv[i]
        if (sys.argv[i][0:3] == "-c=") and (len(sys.argv[i]) > 3):
            #-- Set token charset
            defaults[0] = sys.argv[i][3:]
        elif (sys.argv[i][0:3] == "-l=") and (len(sys.argv[i]) > 3):
            #-- Set token length
            defaults[1] = int(sys.argv[i][3:])
        elif (sys.argv[i][0:3] == "-s=") and (len(sys.argv[i]) > 3):
            #-- Set starting token
            defaults[2] = "".join(sorted(sys.argv[i][3:].strip()))
    
    #-- Build charset
    CHARSET = sorted(set(sorted(defaults[0])))
    
    #-- Build Index list
    INDEXES = [0 for _ in range(defaults[1])]
    
    #-- Set the start INDEXES
    if len(defaults[2]):
        for i in range(min(len(defaults[2]), defaults[1])):
            if defaults[2][i] in CHARSET:
                INDEXES[i] = CHARSET.index(defaults[2][i])
    
    #-- May change here eventually. 
    return True


def shuffle_count(token=INDEXES):
    """ Calculates the number of unique permutations for a given string/array.
            MATH:> p = n! / a! * b! * ... * k!
    """
    set_t = set(token)
    if len(set_t) == len(token):
        #-- all characters are different
        result = math.factorial(len(token))
    else:
        if (len(token) - len(set_t)) == 2:
            #-- Only one character is repeated
            result = 0.5 * math.factorial(len(token))
        else:
            #-- One or more characters are repeated
            factp = 1
            for idx in set_t:
                factp *= math.factorial(token.count(idx))
            result = math.factorial(len(token)) / factp
    return result


def get_strtoken_at(mininc):
    """ Calcualates the first token after mininc increments and exits.
    """
    #Test:
    #print getfactprod("abc") #6 [abc, acb, bac, bca, cab, cba]
    #print getfactprod("abb") #3 [abb, bab, bba]
    #print getfactprod("aaa") #1 [aaa]
    
    i = 0
    last_print = 0
    while i < mininc:
        i += shuffle_count()
        if (i - last_print) >= (mininc / 10):
            last_print = i
            print "%s: %s" % (i, get_strtoken())
        if i < mininc:
            smart_inc()
            
    print
    print "%s: %s (Final)" % (i, get_strtoken())
    exit(0)


def progress_save():
    """ Saves the current token to a file named sess.txt in the cwd.
            [token]::[charset]::[indexes]
    """
    fobj = open("sess.txt", "w+")
    fobj.write( get_strtoken() + "::" + 
                "".join(CHARSET).encode("hex") + "::" +
                ",".join([str(_x) for _x in INDEXES]))
    fobj.close()


def progress_load(f_sess):
    """ Loads file from session file
    """
    pass


def print_exit():
    """ Prints exit info to stderr. Message depends on the exit conditions.
    """
    global ENDFLAG, INDEXES, CHARSET
    
    #-- Print last token that was processed
    if ENDFLAG == 1:
        sys.stderr.write("\n\nExiting at: [ %s ]\n" % get_strtoken())
    else:
        sys.stderr.write("\nWeird Exit [ %s ]\n" % ENDFLAG)
    sys.stderr.flush()

    
#==[ Main ]====================================================================
#print_shuffle(sorted("abc"))
#exit(0)

#-- Start the brute-force loop
CONTINUE = get_args()
#get_strtoken_at(60000000)

try:
    #-- Brute Force happens here
    progr = 0
    while (ENDFLAG == 0) and CONTINUE:
        #-- Save progress every 500'000 keys
        if progr >= 500000:
            progr -= 500000
            progress_save()
        
        #-- Every day i'm shufflin'
        progr += print_shuffle(get_token())
        if ENDFLAG == 0:
            CONTINUE = smart_inc()
            
except KeyboardInterrupt: #-- Ctrl+Break handler
    #-- Print notification
    sys.stderr.write("\n\nUser called Ctrl+Break...\n")
    sys.stderr.flush()
    
    #-- Save progress
    progress_save()

    #-- Let the program know it's ended
    ENDFLAG = 1

except IOError: #-- Prevent broken pipe error
    pass
        
except ValueError: #-- Any other error
    exit(0)
    
print_exit()
