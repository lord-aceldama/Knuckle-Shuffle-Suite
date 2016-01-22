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
    """ For the theory on what makes abacus work, see the md file in the git repo at:
        https://github.com/lord-aceldama/Knuckle-Shuffle-Suite/blob/master/abacus.md
    """
    
    #-- Constants
    #[None]
    
    
    #-- Global Vars
    _charset = None     # [str] character set to be broken up and scanned
    _checked = None     # [dict([chr]:[set])] keeps track of which chars were scanned together.
    _indexes = None     # 
    _abacus  = None     # 
    
    
    #-- Special class methods
    def __init__(self, charset, token=None, token_length=None):
        """ Initializes the class. Requires a valid charset and also either
            a valid token or valid token length.
            
            VARIABLES: 
                charset:        [str] of length 1 or greater
                
                token:          [str] consisting of unique characters. If chars
                                are repeated, the correct indexes cannot be 
                                deduced.
                
                token_length:   [int] of value greater than 0
        """
        #-- Primary Assertions
        assert((type(charset) is str) and (len(charset) > 0)),      "ERR: Bad charset."
        assert(((type(token) is str) and (len(token) > 0)) or
               ((token is None) and (type(token_length) is int) and
                (len(token) == len(set(sorted(token)))))),          "ERR: Bad token/token_length."
        
        #-- Initialization
        self._charset = sorted(set(charset))
        self._checked = {char : set([]) for char in self._charset}


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
