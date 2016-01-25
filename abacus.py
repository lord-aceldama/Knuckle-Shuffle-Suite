#!/usr/bin/env python

#-- Making Pylint behave (Haters gonna hate)
# pylint: disable = old-style-class
# pylint: disable = trailing-whitespace
# pylint: disable = line-too-long
# pylint: disable = bad-whitespace
# pylint: disable = too-many-arguments

""" Knuckle Shuffle
    
    author: aceldama.v1.0 at gmail
    
    Licensed under the GNU General Public License Version 2 (GNU GPL v2), 
        available at: http://www.gnu.org/licenses/gpl-2.0.txt
    
    (C) 2015 David A Swanepoel

    -----------------

    UNDER CONSTRUCTION: so many things to do still...
"""

#-- Dependencies
import sys


#-- Global Constants
CHARSET = sorted("abcdef")


#-- Abacus class
class Abacus():
    """ For the theory on what makes abacus work, see the abacus.md file in the git repo at:
        https://github.com/lord-aceldama/Knuckle-Shuffle-Suite/blob/master/abacus.md
    """
    
    #-- Constants
    #[None]
    
    
    #-- Output
    _stdout = sys.stdout
    _stderr = sys.stderr
    
    
    #-- Global Vars
    _charset = None     # str               character set to be broken up and scanned.
    _checked = None     # {chr:set([chr])}  keeps track of which chars were scanned together.
    _abacus  = None     # [int]             indexes of the charset subset.
    _indexes = None     # [int]             current token charset indexes
    
    
    #-- Special class methods
    def __init__(self, charset, token=None, token_length=None, std_out=None, std_err=None): #subset=None
        """ Initializes the class. Requires a valid charset and also either a valid token
            or valid token length.
            
            VARIABLES: 
                charset:        [str] of length 1 or greater
                
                **subset:**     [str] where 0 < len(subset) <= len(charset)
                
                token:          [str] consisting of unique characters. In order to get
                                the abacus indexes from the token chars, they must all
                                be unique.
                
                token_length:   [int] of value greater than 0. When a token length is 
                                suplied, we assume the user intends to start from the
                                very beginning.
                
                stdout:         Is either PIPE, a valid file descriptor or an existing
                                file object. This is where the class's successfully
                                generated output goes.
                
                stderr:         Is either PIPE, a valid file descriptor or an existing
                                file object. This is where the class's error output
                                goes.
        """
        #-- Make sure the user didn't mess up when passing parameters.
        assert((type(charset) is str) and (len(charset) > 0)),      "ERR: Bad charset."
        assert(((type(token) is str) and (len(token) > 0)) or
               ((token is None) and (type(token_length) is int) and
                (len(token) == len(set(sorted(token)))))),          "ERR: Bad token/token_length."
        
        #-- Initialization
        self._charset = sorted(set(charset))
        self._checked = {char : set([]) for char in self._charset}
        if token is None:
            #-- Init abacus indexes from token_length.
            self._abacus = range(token_length)
            
        else:
            #-- Init abacus indexes from token.
            self._abacus = range(len(token))
            abacus_target = ",".join([self._charset.index(token_char) for token_char in sorted(token)])
            
            #-- Build checked matrix by iterating through all the abacus charset subsets until the
            #   target subset is reached. 
            #       *cough*  No idea how i'm going get that done more efficiently.  *cough*
            while ",".join(self._abacus) != abacus_target:
                self._shift()
                
                #-- Remove when _shift works.
                self._abacus = [self._charset.index(token_char) for token_char in sorted(token)]
            
            #-- Set up the indexes
            self._indexes = range(len(self._abacus))

        #-- Set output vectors
        if std_out is not None:
            self._stdout = std_out
        
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
    
    
    #-- Private methods
    def _shift(self):
        """ This updates both the abacus as well as the checked matrix. For more info
            on exactly how it works, see the documentation which will (eventually) be
            include a detailed segment on the shift method.
            
            Returns True until the abacus expands beyond the scope of the charset, ie. 
            abacus[-1] < len(charset).
        """
        #-- Update checked matrix
        for char in self._abacus:
            self._checked[char] = self._checked[char].union(self._abacus)
        
        #-- Perform the abacus shift operation.
        if (self._abacus[-1] + 1) < len(self._charset):
            #-- Shift the abacus one position on
            for idx in range(len(self._abacus)):
                self._abacus[idx] += 1
        else:
            #-- Shift the entire abacus back to first position
            offset = self._abacus[0]
            for idx in range(len(self._abacus)):
                self._abacus[idx] -= offset
            
            #-- Progress the abacus                 # xooo
            self._abacus[1] += 1 #-- 1st value stays stationary, we start from the 2nd.
            if (len(self._abacus) > 2) and (self._abacus[1] == self._abacus[2]):
                #-- Index collision detected        # x-8o          x-8-o
                idx = 2
                flr = 1
                while (idx < len(self._abacus)) and (self._abacus[idx - 1] == self._abacus[idx]):
                    self._abacus[idx - 1] = flr     # xooo  xooo    xoo-o
                    flr += 1                        #  || // ||      ||
                    self._abacus[idx] += 1          # xo-8  xoo-o   xo-oo
                    idx += 1
        
        #-- Let the user know whether continuing is possible
        return self._abacus[-1] < len(self._charset)
    
    
    #-- Public methods
    def str_token(self):
        """ Returns the current token string """
        return str(self)
    
    
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


#print gen_subsets(CHARSET, 4)
