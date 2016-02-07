#!/usr/bin/env python

""" Knuckle Shuffle
    
    author: aceldama.v1.0 at gmail
    
    Licensed under the GNU General Public License Version 2 (GNU GPL v2), 
        available at: http://www.gnu.org/licenses/gpl-2.0.txt
    
    (C) 2016 David A Swanepoel

    -----------------

    UNDER CONSTRUCTION: so many things to do still...
"""

#-- Dependencies
import sys
import math


#-- Global Constants
DEBUG_MODE = True       # For the printing of Debug Messages to stderr


#----------------------------------------------------------------------------------------------------[ ABACUS CLASS ]--
class Abacus(object):
    """ For the theory on what makes abacus work, see the abacus.md file in the git repo at:
        https://github.com/lord-aceldama/Knuckle-Shuffle-Suite/blob/master/abacus.md
        
            EXPOSES:
                reset()
                next()
                done()
                abacus_string()
    """
    
    #-- Constants
    #[None]
    
    
    #-- Output
    _stderr = sys.stderr
    
    
    #-- Global Vars
    _startup = None     # {}                variables for reset go here.
    _alldone = False    # [bool]            flag for keeping track when entire keyspace has been searched.
    
    _charset = None     # str               character set to be broken up and scanned.
    _checked = None     # {chr:set([chr])}  keeps track of which chars were scanned together.
    _abacus  = None     # [int]             indexes of the charset subset.
    _opt_chr = None     # [[chr]]           optimised (precalculated) characters.
    _opt_idx = None     # [int]             current optimised charset indexes.
    
    
    #-- Special class methods
    def __init__(self, charset, token=None, subset=None, token_length=None, std_err=None):
        """ Initializes the class. Requires a valid charset and also either a valid token
            or valid token length.
                
            SYNTAX
                x = Abacus(charset, (token[, subset] | [[token,] subset,] token_length)[, std_err])

            VARIABLES: 
                charset:        [str] the character set we wish to brute-force.
                
                token:          [str] the token from which to resume. If the token
                                contains repeated chars, a subset is required as we 
                                cannot deduce the subset the keyspace falls in. In 
                                cases where a token is supplied, token_length will be
                                ignored because len(token), unless the user screwed 
                                up, should do the same thing.
                                
                subset:         [str] the current subset to be resumed from. It is
                                only required in cases where only the token_length
                                or a token with repeating characters is given.
                
                token_length:   [int] If token_length is supplied, token, start token
                                and subset are all optional.
                
                std_err:        Is either PIPE, a valid file descriptor or an existing
                                file object. This is where the class's error and debug
                                output goes to.
            
            EXAMPLE:
                x = Abacus("abcde")
                x = Abacus("abcde", "bde")
                x = Abacus("abcde", "bbe", "bde")
                x = Abacus("abcde", token_length:=3)
        """
        #-- Local ignore flags
        ignore_token_length = False
        ignore_token        = False
        ignore_subset       = False
        
        #-- Make sure the user didn't mess up when passing parameters.
        assert(self._chkvar(str, charset, 1)),      "Bad charset."
        assert(self._chkvar(int, token_length, 1) or
               self._chkvar(str, token, 1)),        "Either token or token_length required."
        assert(self._chkvar(int, token_length, 1) or
               self._chkunique(token) or
               (self._chkvar(str, subset, 1) and
                self._chkunique(subset))),          "Required subset contains duplicate chars."
        
        #-- Set output vector (Abacus does not print to stdout, but may print messages to stderr).
        if std_err is not None:
            self._stderr = std_err
        
        #-- Non-fatal errors (warnings)
        if not self._chkunique(token):
            if not self._chkunique(subset):
                self._print("WARNING", "Both token and subset ignored because they contain duplicate characters.")
                ignore_token  = True
                ignore_subset = True
            elif not self._chkvar(str, subset, 1):
                self._print("WARNING", "Token ignored as it contains duplicate chars and no subset supplied.")
                ignore_token  = True
        
        if self._chkvar(int, token_length, 1):
            if (not ignore_token) and self._chkvar(str, token, 1) and (token_length != len(token)):
                self._print("WARNING", "Token ignored as len(token) does not match token_length.")
                ignore_token  = True
            if (not ignore_subset) and self._chkvar(str, subset, 1) and (token_length != len(subset)):
                self._print("WARNING", "Subset ignored as len(subset) does not match token_length.")
                ignore_subset = True
        else:
            ignore_token_length = True
        
        #-- Last check(s)
        assert(not (ignore_token_length and ignore_token and ignore_subset)), "Required parameters ignored."
        
        #-- Global variable initialization
        self._charset = sorted(set(charset))
        self._checked = {char : set([]) for char in self._charset}
        
        #-- Fill in the blanks
        if ignore_token:
            if ignore_subset:
                #-- Generate token from subset.
                token = "".join([charset[idx] for idx in range(token_length)])
            else:
                #-- Generate token from token_length.
                token = "".join(sorted(subset))

        if ignore_subset:
            #-- Generate subset from token.
            subset = "".join(sorted(token))
        
        if ignore_token_length:
            #-- Generate token_length from token.
            token_length = len(token)
            
        #-- On first run, we generate the special optimised subset.
        self._abacus  = range(token_length)
        self._checked = {char:set([]) for char in self._charset}
        self._opt_chr = [[self._charset[idx] for idx in range(token_length)] for _ in range(token_length)]
        
        #-- Update the optimised indexes
        skipped = self._resume(subset, token)
        if (skipped[0] > 0) or skipped[1]:
            if not skipped[1]:
                self._print("INFO", "Resumed skipping %s tokens." % skipped[0])
            else:
                self._print("INFO", "Resumed skipping %s tokens and updating token." % skipped[0])
        
        #-- Save reset parameters
        self._startup = {}
        self._startup["abacus"]  = list(self._abacus)
        self._startup["checked"] = self._checked.copy()
        self._startup["opt_idx"] = list(self._opt_idx)
        self._startup["opt_chr"] = [list(lst) for lst in self._opt_chr]
    
    
    def __str__(self):
        """ Returns the current token string or and empty string if the entire keyspace 
            has been completed.
        """
        token = ""
        if not self._alldone:
            idx = 0
            while idx < len(self._opt_idx):
                token +=  self._opt_chr[idx][self._opt_idx[idx]]
                idx += 1
        
        return token
    
    
    #-- Private static methods
    @staticmethod
    def _chkvar(var_type, var, var_min=None, var_max=None):
        """ Shorthand for checking variables on given criteria. """
        flag = type(var) is var_type
        
        if flag and (var_type in [int, float]):
            #-- Check int
            if type(var_min):
                flag = (var >= var_min)
            if type(var_max) in [int, float]:
                flag = (var <= var_max)
        elif flag and (var_type in [str, list, tuple]):
            #-- Check string, list or tuple
            if type(var_min) is int:
                flag = (len(var) >= var_min)
            if type(var_max) is int:
                flag = (len(var) <= var_max)
        
        #-- Return result
        return flag
    
    
    @staticmethod
    def _chkunique(var):
        """ Checks whether a string, list or tuple consists of unique chars/items. """
        flag = False
        if type(var) in [str, list, tuple]:
            flag = len(var) == len(set(sorted(var)))
        return flag

    
    @staticmethod
    def _get_optimised_type(stats):
        """ Returns an integer representation of the distinct types of optimised token 
            stats, namely 0:Empty, 1:SingleEmpty, 2:Partial and 3:Complete. 
        """
        #-- Assume 2 static optimized charsets. (most common)
        stat_type = 2
        if stats[1] * stats[2] == 0:
            if stats[0] + stats[1] == 0:
                #-- All chars in set checked.
                stat_type = 3
            elif stats[1] + stats[2] == 0:
                #-- No chars in set checked.
                stat_type = 0
            else:
                #-- 1 static optimized charset.
                stat_type = 1
        return stat_type
    
    
    #-- Private methods
    def _print(self, state, text):
        """ Prints the value of the text variable to stderr if it has been set to something
            other than none. State is just the indicator variable for the message source like 
            debug, warning or error etc.
        """
        if self._stderr is not None:
            if (type(text) is str) and len(text):
                self._stderr.write("ABACUS::" + state + "> " + text + "\n")
                self._stderr.flush()
    
    
    def _print_debug(self, text):
        """ Prints the value of the text variable to stderr if the DEBUG_MODE global
            variable is set to True.
        """
        if ('DEBUG_MODE' in globals()) and (DEBUG_MODE == True):
            self._print("DEBUG", text)
    
    
    def _shift(self):
        """ This updates both the abacus as well as the checked matrix. For more info
            on exactly how it works, see the documentation which will (eventually) be
            include a detailed segment on the shift method.
            
            Returns True until the abacus expands beyond the scope of the charset, ie. 
            abacus[-1] < len(charset).
        """
        #-- Update checked characters dictionary.
        checked_chars = [self._charset[idx] for idx in self._abacus]
        for char in checked_chars:
            self._checked[char].update(checked_chars)
        
        #-- Perform the abacus shift operation.
        if (self._abacus[-1] + 1) < len(self._charset):
            #-- Shift the abacus one position on
            for idx in range(len(self._abacus)):
                self._abacus[idx] += 1
        else:
            #-- Shift the entire abacus back to first position.
            offset = self._abacus[0]
            for idx in range(len(self._abacus)):
                self._abacus[idx] -= offset
            
            #-- Progress the abacus.                # xooo
            self._abacus[1] += 1                                            #-- [0] stays stationary, increment [1].
            if (len(self._abacus) > 2) and (self._abacus[1] == self._abacus[2]):
                #-- Index collision detected!       # x-8o          x-8-o
                idx = 2
                flr = 1
                while (idx < len(self._abacus)) and (self._abacus[idx - 1] == self._abacus[idx]):
                    self._abacus[idx - 1] = flr     # xooo  xooo    xoo-o   #-- Move colliding value to floor.
                    flr += 1                        #  || // ||      ||     #-- Increment floor position.
                    self._abacus[idx] += 1          # xo-8  xoo-o   xo-oo   #-- Increment checked value.
                    idx += 1                                                #-- Increment position to check.
        
        #-- Let the user know whether continuing is possible.
        self._alldone = self._abacus[-1] >= len(self._charset)
        
        #-- Characters changed, see if we need a new optimisation.
        if not self._alldone:
            #-- Zero the indexes.
            self._opt_idx = [0 for _ in self._abacus]
            
            #-- Get the new optimized charset.
            self._opt_chr = self._get_optimised_charset()
        
        #-- Return True if we haven't finished scanning the charset.
        return not self._alldone
    
    
    def _get_optimised_stats(self):
        """ Moved this segment to it's own dedicated function for reuse in self._reset().
            It returns a tuple containing number of empty, partial and complete sets, as
            well as the full abacus character list (in that order).
        """
        #-- Build full set.
        abacus_chars = [self._charset[idx] for idx in self._abacus]
        search_chars = set(abacus_chars)
        
        #-- Get set stats.
        empty_sets      = 0
        partial_sets    = 0
        complete_sets   = 0
        for char in abacus_chars:
            if search_chars.issubset(self._checked[char]):
                complete_sets += 1
            elif len(self._checked[char]) == 0:
                empty_sets += 1
            else:
                partial_sets += 1
        
        #-- Return tuple.
        return (empty_sets, partial_sets, complete_sets, abacus_chars)
    
    
    def _get_optimised_charset(self):
        """ Looks at the current char subset and matches it with the checked chars 
            dictionary to create an efficient bundle for use in the inc() method.
            The idea is to create an array with the characters that have been checked.
        """
        #-- Set up an array containing single-value (static value) arrays.
        tmp = [[self._charset[idx]] for idx in self._abacus]
        
        #-- Optimise.
        stats = self._get_optimised_stats()
        if stats[2] < len(stats[3]):
            #-- Set first and last entries are static.
            for idx in range(1, len(tmp) - 1):
                tmp[idx] = stats[3]
            
            if stats[0] == 1:
                #-- Set only the last entry as static
                tmp[0] = stats[3]
        
        #-- Return charset.
        return tmp
    
    
    def _resume(self, subset, token):
        """ Builds a checked matrix by iterating through all the abacus charset subsets until the
            target subset and token is reached. 
                *cough*  No idea how i'm going get that done any more efficiently.  *cough*
            Returns the number of token permutations skipped (eventually... ...returns 0 for now)
        """
        #-- Token counter.
        count = 0
        
        #-- Reset the indexes
        self._opt_idx = [0 for _ in range(len(token))]
        
        #-- Big steps: Shift abacus
        stats = self._get_optimised_stats()
        abacus_target = ",".join([str(self._charset.index(token_char)) for token_char in sorted(subset)])
        while ",".join([str(token_char) for token_char in self._abacus]) != abacus_target:
            #-- Get permutation count
            self._print_debug("%s: %s -> %s" % (stats[:3], self._abacus, [self._charset[idx] for idx in self._abacus]))
            self._print_debug("Chk: %s" % {char:self._checked[char]  for char in stats[3]})
            
            t_len = len(self._abacus)
            t_exp = t_len ** t_len
            stype = self._get_optimised_type(stats)
            if stype == 0:
                #-- No chars in set checked.
                count += t_exp
            elif stype == 1:
                #-- 1 Static optimized charsets.
                t_sum = t_exp - ((t_len - 1) ** t_len)
                count += t_sum
            elif stype == 2:
                #-- 2 Static optimized charsets.
                t_sum = t_exp + ((t_len - 2) ** t_len) - 2 * ((t_len - 1) ** t_len)
                count += t_sum
            else: #-- stype == 3:
                #-- All chars checked.
                t_sum = math.factorial(len(self._abacus))
                count += t_sum
            
            #-- Updates self._checked and self._eff_idx
            self._shift()
            stats = self._get_optimised_stats()
        
        #-- Little steps: Adjust the optimised indexes accordingly.
        idx = 0
        token_updated = subset != token
        while token_updated and (idx < len(self._opt_idx)):
            #self._print_debug("T: %s IDX: %s, CHR: %s" % (token, self._opt_idx, self._opt_chr))
            assert (token[idx] in self._opt_chr[idx]
                   ), ("Invalid token for subset. (%s[%s]%s) %s"
                      ) % (token[:idx], token[idx], token[idx + 1:], self._opt_chr)
            
            self._opt_idx[idx] = self._opt_chr[idx].index(token[idx])
            idx += 1
        
        return (count, token_updated)
    
    #-- Public methods
    def reset(self):
        """ Resets and returns the old and new tokens as a tuple. """
        assert(self._charset is not None), "Charset not initialized."
        assert(self._startup is not None), "Startup not initialized."
        
        #-- Get current token
        old_token = str(self)
        
        #-- Reset state
        self._alldone = False
        self._checked = self._startup["checked"].copy()
        self._abacus  = list(self._startup["abacus"])
        self._opt_idx = list(self._startup["opt_idx"])
        self._opt_chr = list([list(lst) for lst in self._startup["opt_chr"]])
        
        #-- Return state tuple
        return (old_token, str(self))
    
    
    def next(self):
        """ Returns the current token and then calculates the next one, shifting the abacus as
            required. If the entire keyspace has been processed, an empty token is returned.
        """
        #-- Grab the current token
        token = str(self)
        if self._chkvar(str, token, 1):
            #-- Inc efficient indexes.
            idx  = len(self._opt_idx) - 1
            self._opt_idx[idx] += 1
            while (idx >= 0) and (self._opt_idx[idx] >= len(self._opt_chr[idx])):
                self._opt_idx[idx] = 0
                idx -= 1
                self._opt_idx[idx] += 1
            
            #-- Check if we need to shift.
            if idx < 0:
                #-- Yes, shift.
                self._shift()
            else:
                #-- No, just iron out the indexes to avoid duplicate shuffles.
                idx += 1
                while idx < len(self._opt_idx):
                    self._opt_idx[idx] = min(self._opt_idx[idx - 1], len(self._opt_chr[idx]) - 1)
                    idx += 1
        
        #-- Return the token we got before doing the increment.
        return token
    
    
    def done(self):
        """ Returns a simple boolean to say if work's complete. """
        return self._alldone
    
    
    def abacus_data(self):
        """ Returns a string representation of the current abacus. """
        tmp  = ""
        tmp2 = ""
        for idx in range(len(self._charset)):
            if idx in self._abacus:
                tmp  += self._charset[idx]
                tmp2 +=  self._charset[idx]
            else:
                tmp += "-"
        return (tmp, tmp2, self._get_optimised_stats()[0:3])


#---------------------------------------------------------------------------------------------------[ SHUFFLE CLASS ]--
class Shuffle(object):
    """ Calculates (and print) all unique permutations of a given token string. I'm putting this
        in a dedicated class because I plan to add multi-processing and buffering capabilities
        later on.
        
        Non-recursive permutations: 
            http://stackoverflow.com/questions/18227931/iterative-solution-for-finding-string-permutations
    """
    
    #-- Constants
    #[None]
    
    
    #-- Output
    _stdout = sys.stdout
    _stderr = sys.stderr
    
    
    #-- Global Vars
    #[None]
    
    
    #-- Special class methods
    def __init__(self, std_out=None, std_err=None):
        """ Docstring. """
        
        #-- Set output vectors.
        if std_out is not None:
            self._stdout = std_out
        
        if std_err is not None:
            self._stderr = std_err
        
    
    def __str__(self):
        """ Docstring. """
        return ""
    
    
    #-- Private Methods
    def _print(self, text):
        """ Prints text to stdout.
        """
        if (self._stdout is not None) and (type(text) is str):
            self._stdout.write(text + "\n")
            self._stdout.flush()
    
    def _print_stderr(self, text, token="INFO"):
        """ Prints text to stderr.
        """
        if (self._stderr is not None) and (type(text) is str):
            self._stdout.write("SHUFFLE::" + token + "> " + text + "\n")
            self._stdout.flush()
    
    
    def _print_debug(self, text):
        """ Prints the value of the text variable to stderr if the DEBUG_MODE global
            variable is set to True.
        """
        if ('DEBUG_MODE' in globals()) and (DEBUG_MODE == True):
            self._print_stderr(text, "DEBUG")
    
    
    #-- Public Static Methods
    @staticmethod
    def shuffle_count(token):
        """ Calculates the number of unique permutations for a given string/array.
                MATH:> p = n! / a! * b! * ... * k!
        """
        set_t = set(token)
        if len(set_t) == len(token):
            #-- all characters are different
            result = math.factorial(len(token))
        else:
            if (len(token) - len(set_t)) == 1:
                #-- Only one character is repeated
                result = 0.5 * math.factorial(len(token))
            else:
                #-- One or more characters are repeated
                factp = 1
                for idx in set_t:
                    factp *= math.factorial(token.count(idx))
                result = math.factorial(len(token)) / factp
        return result

    
    @staticmethod
    def non_recursive_shuffle(token):
        """ Planning to use this to create a "next" or "inc" function which should make resuming 
            from a previously calculated token easier.
        """
        def get_stack(token, prefix):
            """ test """
            idx = 0
            while token[idx] in token[idx + 1:]:
                idx += 1
            return [token, prefix, idx]
            
        def get_stack_child(parent):
            """ test """
            return get_stack(parent[0][:parent[2]] + parent[0][parent[2] + 1:], parent[1] + parent[0][parent[2]])
        
        def get_stack_next(stack):
            """ test """
            #-- Expand it
            while len(stack[-1][0]) > 1:
                stack.append(get_stack_child(stack[-1]))
            
            #-- Register it
            leaf = stack[-1][1] + stack[-1][0]
            
            #-- Pop it
            while (len(stack) > 0) and (len(stack[-1][0]) == (stack[-1][2] + 1)):
                stack.pop()
            
            if len(stack) > 0:
                stack[-1][2] += 1
                while stack[-1][0][stack[-1][2]] in  stack[-1][0][stack[-1][2] + 1:]:
                    stack[-1][2] += 1
            
            #-- Return it
            return leaf
            
        #-- New token added.
        stack = []
        stack.append(get_stack(token, ""))  #-- [(token, prefix, idx)]
        
        total = 0
        while (len(stack) > 0) and (total < 30):
            print get_stack_next(stack), " >> ", stack
            total += 1
        
        return total
    
    
    #-- Public Methods
    def reset(self, charset=None):
        """ To do. """
    
    def print_shuffle(self, token, prefix=""):
        """ Generates and prints all unique permutations of a token string. It 
            currently returns the total amount of permutations.
        """
        total = 0
        if len(token) == 1:
            #-- End of recursion reached and successful token found.
            self._print(prefix + token[0])
            total = 1
        else:
            #-- Cycle through allcharacters in the chars array
            idx = 0
            while idx < len(token):
                #-- If the character at the current position also to the right
                #   we don't need process it as it would create duplicates. 
                if token[idx] not in token[idx + 1:]:
                    total += self.print_shuffle(token[:idx] + token[idx + 1:], prefix + token[idx])
                idx += 1
        return total


#------------------------------------------------------------------------------------------------------------[ MAIN ]--
def debug_test_abacus():
    """ Test run """
    shuffle = Shuffle()
    #test = Abacus("abcde", token_length = 3)
    
    #test = Abacus("abcde", token_length = 4)
    #test = Abacus("abcde", "acde", "acde")
    
    #test = Abacus("abcde", token_length = 6)   #-- Fix Me!!
    #test = Abacus("abcde", "bde")              #-- Fix Me!!
    #test = Abacus("abcde", "ace", "ace")
    
    #test = Abacus("01adoprswxyz", "1adoprssw", "01adoprsw", token_length=len("password1"))
    #test = Abacus("0123456789abcdef", "abcd", "abcd", 4)
    #test = Abacus("0123456789abcdef", token_length=6)
    test = Abacus("abc", token_length=3)
    
    stop = 0
    while not (test.done() or (stop < 0)):
        token = test.next()
        #abacus = test.abacus_data()
        #print "\n%s     < %s" % (token, abacus[0])
        shuffle.print_shuffle(token)
        stop += 1


def debug_test_shuffle():
    """ Test run """
    test_token = "abba"
    test = Shuffle()
    test.print_shuffle(test_token)
    print test.shuffle_count(test_token)
    test.non_recursive_shuffle(test_token)

    
if DEBUG_MODE:
    #debug_test_abacus()
    debug_test_shuffle()

