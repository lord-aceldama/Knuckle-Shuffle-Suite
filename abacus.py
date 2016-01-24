#!/usr/bin/env python

#-- Making Pylint behave
# pylint: disable = old-style-class
# pylint: disable = trailing-whitespace
# pylint: disable = line-too-long
# pylint: disable = bad-whitespace

""" Knuckle Shuffle
    
    author: aceldama.v1.0 at gmail
    
    Licensed under the GNU General Public License Version 2 (GNU GPL v2), 
        available at: http://www.gnu.org/licenses/gpl-2.0.txt
    
    (C) 2015 David A Swanepoel

    -----------------

    UNDER CONSTRUCTION: so many things to do still...
"""

#-- Dependencies
#import math


#-- Global Constants
CHARSET = sorted("abcdef")


#-- Abacus class
class Abacus():
    """ For the theory on what makes abacus work, see the abacus.md file in the git repo at:
        https://github.com/lord-aceldama/Knuckle-Shuffle-Suite/blob/master/abacus.md
    """
    
    #-- Constants
    #[None]
    
    
    #-- Global Vars
    _charset = None     # [str] character set to be broken up and scanned.
    _checked = None     # [dict([chr]:[set])] keeps track of which chars were scanned together.
    _abacus  = None     # [list(int)] indexes of the charset subset.
    _indexes = None     # [list(int)] current token charset indexes
    
    
    #-- Special class methods
    def __init__(self, charset, token=None, token_length=None):
        """ Initializes the class. Requires a valid charset and also either a valid token
            or valid token length.
            
            VARIABLES: 
                charset:        [str] of length 1 or greater
                
                token:          [str] consisting of unique characters. In order to get
                                the abacus indexes from the token chars, they must all
                                be unique.
                
                token_length:   [int] of value greater than 0. When a token length is 
                                suplied, we assume the user intends to start from the
                                very beginning.
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
            #-- Init abacus incexes from token_length.
            self._abacus = range(token_length)
            
        else:
            #-- Init indexes from token.
            self._indexes = [self._charset.index(token_char) for token_char in sorted(token)]
            
            #-- Build checked matrix. *cough* No idea how i'm going get that done efficiently. *cough*
            
    
    
    def __str__(self):
        """ Returns the current token string. DOES NOT include a newline character and
            DOES NOT calculate the next token automatically. See: Abacus.print_token()
        """
        token = ""
        for idx in self._indexes:
            token += self._charset[idx]
        return token
    
    
    #-- Private methods
    def _fromindexes(self, indexes):
        """ Docstring.
        """
        offsets = [] + self._abacus
        for idx in range(1, len(indexes)):
            offsets += [0 for _ in range(1, indexes[idx] - indexes[idx - 1])]
        
        return  [1] + offsets + [1]
    
    
    def _fromstrtoken(self, token):
        """ Returns the abacus from the given token string.
        """
        offsets = [] + self._charset[0]
        
        return offsets + sorted(token)
    
    
    #-- Public methods
    def str_token(self):
        """ Returns the current token string """
        return str(self)
    
    
    def _shift(self):
        """ Docstring.
        """
        offset = 0
        shifts = []
        while offset + self._indexes[-1] < len(self._charset):
            subset = ""
            for nchr in self._indexes:
                subset += self._charset[offset + nchr]
            shifts += [subset]
            offset += 1
        
        return shifts
    
    
    def inc(self):
        """ Calculates the next token. """
        return self._indexes[0] #-- To Do
    
    
    def print_token(self):
        """ Returns the current token and calculates the next. Includes the 
            newline charcter in the returned string.
        """
        token = str(self) + "\n"
        self.inc()
        return token


#print gen_subsets(CHARSET, 4)
