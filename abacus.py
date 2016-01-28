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
    _charset = None     # str                   character set to be broken up and scanned.
    _checked = None     # {chr:set([chr])}      keeps track of which chars were scanned together.
    _abacus  = None     # [int]                 indexes of the charset subset.
    _indexes = None     # [int]                 current token charset indexes.
    _eff_idx = None     # [int, [chr], [chr]]   groups matched and unmached chars to speed up inc().
    
    
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
                                
                subset:         [str] the current subset to be resumed from. It is only
                                required in cases where only the token_length or a token
                                containing duplicate characters is supplied.
                
                token_length:   [int] If token_length is supplied, token, start token and 
                                subset are all optional.
                
                stderr:         Is either PIPE, a valid file descriptor or an existing
                                file object. This is where the class's error and debug
                                output goes to.
            
            EXAMPLE:
                x = Abacus("abcde")
                x = Abacus("abcde", "bde")
                x = Abacus("abcde", "bbe", "bde")
                x = Abacus("abcde", token_length:=3)
        """
        #-- Make sure the user didn't mess up when passing parameters.
        assert(self._chkvar(str, charset, 1)),  "ERR: Bad charset."
        assert(self._chkvar(int, token_length, 1) or 
               self._chkvar(str, token, 1)),    "ERR: Either token or token_length required."    
        assert(self._chkvar(str, subset, 1) and 
               self._chkvar(str, subset, 1)),   "ERR: Bad starting subset."
        assert(self._chkvar(str, subset, 1)),   "ERR: Bad starting token."
        
        assert(self._chkvar(str, subset, 1, len(charset))),         "ERR: "
        
        assert(((type(token) is str) and (len(token) > 0)) or
               ((token is None) and (type(token_length) is int) and
                (len(token) == len(set(sorted(token)))))),          "ERR: Bad token/token_length."
        
        #-- Initialization
        self._charset = sorted(set(charset))
        self._checked = {char : set([]) for char in self._charset}
        
        if token is None:
            #-- Init abacus indexes from token_length.
            self._abacus = range(token_length)
            
            #-- Create and zero the indexes.
            self._indexes = [0 for _ in range(token_length)]
            
        else:
            #-- Init abacus indexes from token.
            self._abacus = range(len(token))
            abacus_target = ",".join([self._charset.index(token_char) for token_char in sorted(token)])
            
            #-- Build checked matrix by iterating through all the abacus charset subsets until the
            #   target subset is reached. 
            #       *cough*  No idea how i'm going get that done any more efficiently.  *cough*
            while ",".join(self._abacus) != abacus_target:
                self._shift()
            
            #-- Set up the indexes from the recovered abacus.
            self._indexes = range(len(self._abacus))
    
        #-- Init grouped chars.
        self._eff_idx = self._get_efficient_charset()
        
        #-- Set output vectors (Abacus does not print to stdout, but may print messages to stderr).
        if std_err is not None:
            self._stderr = std_err
    
    
    def __str__(self):
        """ Returns the current token string. DOES NOT include a newline character and
            DOES NOT calculate the next token automatically. See: Abacus.print_token()
        """
        token = ""
        for idx in self._indexes:
            token += self._charset[self._abacus[idx]]
        
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
    
    
    #-- Private methods
    def _print_debug(self, text):
        """ Prints the value of the text variable to stderr if the DEBUG_MODE global
            variable is set to True.
        """
        if ('DEBUG_MODE' in globals()) and (DEBUG_MODE == True):
            if (self._stderr is not None) and (type(text) is str) and len(text):
                self._stderr.write("DEBUG::ABACUS> " + text + "\n")
                self._stderr.flush()
    
    
    def _shift(self):
        """ This updates both the abacus as well as the checked matrix. For more info
            on exactly how it works, see the documentation which will (eventually) be
            include a detailed segment on the shift method.
            
            Returns True until the abacus expands beyond the scope of the charset, ie. 
            abacus[-1] < len(charset).
        """
        #-- Update checked characters dictionary.
        for char in self._abacus:
            self._checked[char] = self._checked[char].union(self._abacus)
        
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
        
        #-- Grouped the indexes to speed up inc.
        self._eff_idx = self._get_efficient_charset()
        
        #-- Let the user know whether continuing is possible.
        return self._abacus[-1] < len(self._charset)
    
    
    def _get_efficient_charset(self):
        """ Looks at the current char subset and matches it with the checked chars 
            dictionary to create an efficient bundle for use in the inc() method.
            The idea is to create an array with the characters that have been checked.
                [[indexes], [[charset pos1], ..., [charset posN]]]
        """
        tmp = [[], [[],[],[]]]
        
        if len(tmp[1]) > 0:
            tmp[0] = len(self._abacus) - 2
            
        return tmp
    
    
    #-- Public methods
    def inc(self):
        """ Calculates the next token and shifts the abacus as required. """
        return self._indexes[0] #-- To Do
    
    
    def print_token(self):
        """ Returns the current token and calculates the next. Includes the 
            newline charcter in the returned string.
        """
        token = str(self) + "\n"
        self.inc()
        return token


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


#print gen_subsets(CHARSET, 4)
