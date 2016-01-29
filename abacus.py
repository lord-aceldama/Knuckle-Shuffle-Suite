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


#-- Global Constants
DEBUG_MODE = True       # For the printing of Debug Messages to stderr


#-- Abacus class
class Abacus():
    """ For the theory on what makes abacus work, see the abacus.md file in the git repo at:
        https://github.com/lord-aceldama/Knuckle-Shuffle-Suite/blob/master/abacus.md
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
        assert(self._chkvar(str, charset, 1)),      "ERR: Bad charset."
        assert(self._chkvar(int, token_length, 1) or
               self._chkvar(str, token, 1)),        "ERR: Either token or token_length required."
        assert(self._chkunique(token) or
               self._chkvar(str, subset, 1)),       "ERR: Subset required if token contains duplicate chars."
        assert(self._chkvar(int, token_length, 1) or
               self._chkunique(token) or
               (self._chkvar(str, subset, 1) and
                self._chkunique(subset))),          "ERR: Required subset contains duplicate chars."
        
        #-- Set output vector (Abacus does not print to stdout, but may print messages to stderr).
        if std_err is not None:
            self._stderr = std_err
        
        #-- Non-fatal errors (warnings)
        if not self._chkunique(token):
            if not self._chkvar(str, subset, 1):
                self._print("WARNING", "Token ignored as it contains duplicate chars and no subset supplied.")
                ignore_token  = True
            elif not self._chkunique(subset):
                self._print("WARNING", "Both token and subset ignored because they contain duplicate characters.")
                ignore_token  = True
                ignore_subset = True
        
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
        assert(not (ignore_token_length and ignore_token and ignore_subset)), "ERR: Required parameters ignored."
        
        #-- Global variable initialization
        self._charset = sorted(set(charset))
        self._checked = {char : set([]) for char in self._charset}
        
        #-- Fill in the blanks
        if ignore_token:
            if ignore_subset:
                #-- Generate token from subset.
                token = "".join([charset[0] for _ in range(token_length)])
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
        self._opt_chr = [range(token_length) for _ in range(token_length)]
        self._opt_idx = [0 for _ in range(token_length)]
        
        #-- Build checked matrix by iterating through all the abacus charset subsets until the
        #   target subset is reached. 
        #       *cough*  No idea how i'm going get that done any more efficiently.  *cough*
        abacus_target = ",".join([self._charset.index(token_char) for token_char in sorted(subset)])
        while ",".join(self._abacus) != abacus_target:
            self._shift()   #-- Updates self._checked and self._eff_idx
        
        #-- Save reset parameters
        self._startup["checked"] = dict(self._checked)
        self._startup["abacus"]  = list(self._abacus)
        self._startup["opt_idx"] = list(self._opt_idx)
        self._startup["opt_chr"] = [list(lst) for lst in self._opt_chr]
    
    
    def __str__(self):
        """ Returns the current token string or and empty string if the entire keyspace 
            has been completed.
        """
        token = ""
        if not self._alldone:
            for idx in self._opt_idx:
                token += self._opt_chr[idx]
        
        return token
    
    
    #-- Private static methods
    @staticmethod
    def _chkvar(var_type, var, var_min=None, var_max=None):
        """ Shorthand for checking variables on given criteria. """
        flag = type(var) is var_type
        
        if flag or (var_type in [int, float]):
            #-- Check int
            if type(var_min):
                flag = (var >= 0)
            if type(var_max) in [int, float]:
                flag = (var <= 0)
                
        if flag or (var_type in [str, list, tuple]):
            #-- Check string, list or tuple
            if type(var_min) is int:
                flag = (len(var) >= 0)
            if type(var_max) is int:
                flag = (len(var) <= 0)
        
        #-- Return result
        return flag
    
    
    @staticmethod
    def _chkunique(var):
        """ Checks whether a string, list or tuple consists of unique chars/items. """
        return len(var) == len(set(sorted(var)))

    
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
    
    
    def _get_optimised_charset(self):
        """ Looks at the current char subset and matches it with the checked chars 
            dictionary to create an efficient bundle for use in the inc() method.
            The idea is to create an array with the characters that have been checked.
        """
        
        #-- Build full set.
        abacus_chars = [self._charset[idx] for idx in self._abacus]
        tmp = list(abacus_chars)
        
        #-- Get set stats.
        #partial_sets    = 0
        empty_sets      = 0
        complete_sets   = 0
        for char in abacus_chars:
            if len(self._checked[char]) == len(self._abacus):
                complete_sets += 1
            if len(self._checked[char]) == 0:
                empty_sets += 1
            #else:
            #    partial_sets += 1
        
        #-- Optimise
        if complete_sets < len(abacus_chars):
            #-- Set first and last entries are static
            for idx in range(1, len(tmp) - 1):
                tmp[idx] = list(abacus_chars)
            
            if empty_sets == 1:
                #-- Set only the last entry as static
                tmp[idx] = list(abacus_chars)
        
        #-- Return charset
        return tmp
    
    
    #-- Public methods
    def reset(self):
        """ Resets and returns the old and new tokens as a tuple. """
        assert(self._charset is not None), "ERR: Charset not initialized."
        assert(self._startup is not None), "ERR: Startup not initialized."
        
        #-- Get current token
        old_token = str(self)
        
        #-- Reset state
        self._alldone = False
        self._checked = dict(self._startup["checked"])
        self._abacus  = list(self._startup["abacus"])
        self._opt_idx = list(self._startup["opt_idx"])
        self._opt_chr = list([list(lst) for lst in self._startup["opt_chr"]])
        
        #-- Return state tuple
        return (old_token, str(self))
    
    
    def inc(self):
        """ Returns the current token and then calculates the next one, shifting the abacus as
            required. If the entire keyspace has been processed, an empty token is returned.
        """
        #-- Grab the current token
        token = str(self)
        if self._chkvar(str, token, 1):
            #-- Inc efficient indexes.
            idx  = len(self._opt_idx[0]) - 1
            self._opt_idx[idx] += 1
            while (idx >= 0) and (self._opt_idx[idx] >= len(self._opt_chr[idx])):
                self._opt_idx[idx] = 0
                idx -= 1
                self._opt_idx[idx] += 1
            
            #-- Check if we need to shift.
            if self._opt_idx[0] >= len(self._opt_chr[0]):
                self._shift()
        
        #-- Return the token we got before doing the increment.
        return token
    
    
    def done(self):
        """ Returns a simple boolean to say if work's complete. """
        return self._alldone


#-- Shuffle Class (Stub)
class Shuffle():
    """ Docstring. """
    
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
    def _print_debug(self, text):
        """ Prints the value of the text variable to stderr if the DEBUG_MODE global
            variable is set to True.
        """
        if ('DEBUG_MODE' in globals()) and (DEBUG_MODE == True):
            if (self._stderr is not None) and (type(text) is str) and len(text):
                self._stderr.write("DEBUG::SHUFFLE> " + text + "\n")
                self._stderr.flush()
    
    
    #-- Public Methods
    def reset(self, charset=None):
        """ Docstring. """
        
        
    def print_shuffle(self):
        """ Generates and prints all unique permutations of a char array.
        """


def debug_test():
    """ Test run """
    test = Abacus("abcde", token_length=3)
    stop = 0
    while not (test.done() or (stop > 100)):
        print "%s: %s" % (stop, test.inc())
        stop += 1

debug_test()
