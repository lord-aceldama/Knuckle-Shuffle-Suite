""" Brute
    
    author: aceldama.v1.0 at gmail
    
    Licensed under the GNU General Public License Version 2 (GNU GPL v2), 
        available at: http://www.gnu.org/licenses/gpl-2.0.txt
    
    (C) 2016 David A Swanepoel
"""

#-- Import Dependencies
import sys


#=================================================================================================[ FORCE_INC CLASS ]==
class Incremental(object):
    """ The most basic brute force type class: Incremental. They don't get much simpler than this.
        
            EXPOSES:
                Constants:
                    [None]
                
                Methods:
                    resume(token)           : Resumes from the specified token.
                    reset()                 : Resets the token to position 0.
                    inc()                   : Increments the brute-force token by one position. Overflow errors are
                                              possible, and will perform a reset as well as raise a soft error.
                
                Properties:
                    (rw) [str] token        : Gets or sets the current token. The token supplied can only contain 
                                              characters present in the charset supplied during init.
                    (ro) [tuple] progress   : Returns the current progress and max value as a tuple.
                    (ro) [bool] done        : Returns True if the current token is the last token.
    """
    
    #-- Constants -----------------------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Output --------------------------------------------------------------------------------------------------------
    _stderr = None
    
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    _chars      = []
    _index      = []
    _progress   = 0
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    def __init__(self, chars, length, token_start=None, std_err=None):
        """ Initializes the object.
        """
        self._chars = sorted(set(chars))
        self._index = [0 for _ in xrange(max(1, length))]
        if (type(std_err) is file) and (self._stderr is not std_err):
            self._stderr = std_err
        self.token = token_start
    
    
    def __str__(self):
        """ Returns a string containing the current token.
        """
        result = ""
        if (len(self._chars) > 0) and (len(self._index) > 0):
            for i in self._index:
                result += self._chars[i]
        return result
    
    
    def __len__(self):
        """ Returns the current progress value of the token.
        """
        i = 0
        for idx in self._index:
            i = (i * len(self._chars)) + self._index[idx]
        return i
    
    
    #-- Properties ----------------------------------------------------------------------------------------------------
    @property
    def token(self):
        """ Returns the name. """
        return str(self)
    @token.setter
    def token(self, value):
        """ Sets the name. """
        if (type(value) is str) and (str(self) != value) and (len(value) > 0):
            i = 0
            flag = True
            while flag and (i < len(value)):
                flag = value[i] in self._chars
                i += 1
                
            if flag:
                self._index = [self._chars.index(value[i]) for i in xrange(len(value))]
            else:
                self._error("ERROR: Supplied token [ {} ] contains bad chars. Using [ {} ]\n".format(value, str(self)))
    
    
    @property
    def progress(self):
        """ Returns a tuple containing the current progress and maximum
        """
        prog_val = 0
        prog_max = 0
        for idx in self._index:
            prog_val = (prog_val * len(self._chars)) + idx
            prog_max = (prog_max * len(self._chars)) + len(self._chars) - 1
        
        return (prog_val, prog_max)
    
    @property
    def done(self):
        """ Returns a boolean value which is true when the maximum number of permutations have been reached.
        """
        return self._index.count(len(self._chars) - 1) == len(self._index)
    
    
    #-- Private Methods -----------------------------------------------------------------------------------------------
    def _error(self, text):
        """ Prints an error to stderr is it's set.
        """
        if self._stderr is not None:
            self._stderr.write(text)
    
    
    #-- Public Methods ------------------------------------------------------------------------------------------------
    def resume(self, token):
        """ Attempts to set the token to the one supplied.
        """
        self.token = token
    
    
    def reset(self):
        """ Resets the token to position 0.
        """
        for i in xrange(len(self._index)):
            self._index[i] = 0
    
    
    def inc(self):
        """ Increments the brute-force token by one position.
        """
        idx = len(self._index) - 1
        while (idx >= 0) and (self._index[idx] == (len(self._chars) - 1)):
            self._index[idx] = 0
            idx -= 1
        if idx >= 0:
            self._index[idx] += 1
        else:
            #-- Overflow
            self._error("WARNING: An overflow error occurred. Token reset to [ {} ]\n".format(str(self)))
        return str(self)


#===========================================================================================================[ DEBUG ]==
def debug():
    """ Test method. """
    #test = Incremental("abc", 3, "bbb")
    test = Incremental("abc", 3, std_err=sys.stderr)
    test.resume("bax")
    test.resume("bac")
    print test, test.progress
    while not test.done:
        print test.inc(), test.progress
    test.inc()


#============================================================================================================[ MAIN ]==
if __name__ == "__main__":
    DEBUG_MODE = True
    debug()

