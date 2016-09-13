""" Brute: Incremental, Permutation, Shuffle and Abacus
    
    author: aceldama.v1.0 at gmail
    
    Licensed under the GNU General Public License Version 2 (GNU GPL v2), 
        available at: http://www.gnu.org/licenses/gpl-2.0.txt
    
    (C) 2016 David A Swanepoel
"""

#-- Import Dependencies
import sys
import math
from xifo import DictStack


#===============================================================================================[ INCREMENTAL CLASS ]==
class Incremental(object):
    """ The most basic brute force type class: Incremental. They don't get much simpler than this.
        
            EXPOSES:
                Methods:
                    resume(token)               : Resumes from the specified token.
                    reset()                     : Resets the token to position 0.
                    inc()                       : Increments the brute-force token by one position. Overflow errors
                                                  are possible, and will perform a reset as well as raise a soft error.
                
                Properties:
                    (rw) [str] token            : Gets or sets the current token. The token supplied may only
                                                  contain chars present in the charset supplied during init.
                    (ro) [tuple] progress       : Returns the current progress and max value as a tuple.
                    (ro) [float] percent_done   : Returns the progress as a percentage.
                    (ro) [bool] done            : Returns True if the current token is the last token.
    """
    #-- Constants -----------------------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Output --------------------------------------------------------------------------------------------------------
    _stderr = None
    
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    _chars      = []
    _index      = []
    
    _prog_max   = 1
    _progress   = 0
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    def __init__(self, chars, length=None, token=None, std_err=None):
        """ Initializes the object. Either length or token are required.
        """
        #-- Set up debug output.
        if isinstance(std_err, file) and (self._stderr is not std_err):
            self._stderr = std_err
        
        #-- Set up starting token and surrounding variables.
        self._chars = sorted(set(chars))
        self.token = token
        if (len(self._index) == 0) and (isinstance(length, int) or isinstance(token, str)):
            #-- Token fallback
            self.token = self._chars[0] * (length if isinstance(length, int) else len(token))
        
        if len(self._index) == 0:
            #-- User is a "special needs" case...
            self._error("ERROR: Invalid starting token and/or token length.")
    
    
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
        return self._prog_max
    
    
    #-- Properties ----------------------------------------------------------------------------------------------------
    @property
    def token(self):
        """ Returns the current token. """
        return str(self)
    @token.setter
    def token(self, value):
        """ Sets the token and resumes. """
        if isinstance(value, str) and (str(self) != value) and (len(value) > 0):
            i = 0
            flag = True
            while flag and (i < len(value)):
                flag = value[i] in self._chars
                i += 1
                
            if flag:
                #-- Set up the index to resume from
                self._index = [self._chars.index(value[i]) for i in xrange(len(value))]
                
                #-- Set the current and maximum progress values
                self._prog_max = 0
                self._progress = 0
                for idx in xrange(len(self._index)):
                    self._prog_max = (self._prog_max * len(self._chars)) + len(self._chars) - 1
                    self._progress = (self._progress * len(self._chars)) + self._index[idx]
                self._prog_max += 1
                self._progress += 1
            else:
                self._error("ERROR: Supplied token [ {} ] contains bad chars. Using [ {} ]\n".format(value, str(self)))
    
    
    @property
    def progress(self):
        """ Returns the current progress. See also __len__ for max value.
        """
        return self._progress
    
    
    @property
    def percent_done(self):
        """ Returns the progress in percent.
        """
        return 100.0 * self._progress / self._prog_max 
    
    
    @property
    def done(self):
        """ Returns a boolean value which is true when the maximum number of permutations have been reached.
        """
        return self._index.count(len(self._chars) - 1) == len(self._index)
    
    
    #-- Private Methods -----------------------------------------------------------------------------------------------
    def _error(self, text):
        """ Prints an error to stderr if it's set.
        """
        if self._stderr is not None:
            self._stderr.write(text)
    
    
    #-- Public Methods ------------------------------------------------------------------------------------------------
    def resume(self, token):
        """ Attempts to set the token to the one supplied. Retrns True if it was successful or False otherwise.
        """
        self.token = token
        return self.token == token
    
    
    def reset(self):
        """ Resets the token to position 0.
        """
        self._progress = 1
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
            self._progress += 1
        else:
            #-- Overflow
            self._progress = 1
            self._error("WARNING: An overflow error occurred. Token reset to [ {} ]\n".format(str(self)))
        
        #-- Return the new token
        return str(self)


#===============================================================================================[ PERMUTATION CLASS ]==
class Permute(object):
    """ Calculates all unique permutations of a single given token string.
        
            EXPOSES:
                Constants:
                    [None]
                
                Static Methods:
                    Permutations(token)         : Returns the number of possible permutations for a given token.
                
                Methods:
                    resume(token)               : Resumes from the specified token.
                    reset()                     : Resets the token to position 0.
                    inc()                       : Moves to the next permutation until all permutations are done.
                                                  Returns the current token.
                
                Properties:
                    (rw) [str] token            : Gets or sets the token. 
                    (ro) [tuple] progress       : Returns the current progress and max value as a tuple.
                    (ro) [float] percent_done   : Returns the progress as a percentage.
                    (ro) [bool] done            : Returns True if the current token is the last token.
    """
    #-- Constants -----------------------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Output --------------------------------------------------------------------------------------------------------
    _stderr = None
    
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    _stack = DictStack(token="", prefix="", idx = 0)
    _progress   = 0
    _prog_max   = 0
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    def __init__(self, token, resume=False, std_err=None):
        """ Initializes the object. If resume=True, the token (which is sorted initially) will be progressed until the
            unsorted value of token is reached.
        """
        #-- Set up debug output.
        if isinstance(std_err, file) and (self._stderr is not std_err):
            self._stderr = std_err
        
        #-- 
        if isinstance(token, str) and (len(token) > 0):
            self.token = "".join(sorted(token))
            if self._prog_max == 0:
                pass #-- User is a special needs case
            elif isinstance(resume, bool) and resume:
                #-- Resume
                self.resume(token)
    
    
    def __str__(self):
        """ Returns a string containing the current token.
        """
        return self._stack.top["prefix"] + self._stack.top["token"] if len(self._stack) > 0 else ""
    
    
    def __len__(self):
        """ Returns the current progress value of the token.
        """
        return self._prog_max
    
    
    #-- Properties ----------------------------------------------------------------------------------------------------
    @property
    def token(self):
        """ Returns the name. """
        return str(self)
    @token.setter
    def token(self, value):
        """ Sets the name. """
        if isinstance(value, str) and (len(value) > 0) and (str(self) != value):
            #-- Empty the stack
            while len(self._stack):
                self._stack.pop()
            
            #-- Build the new stack
            self._stack_push_child("".join(sorted(value)), "")
            self._stack_build_branch()
            
            #-- Set progress trackers
            self._progress = 1
            self._prog_max = Permute.permutations(value)
    
    
    @property
    def progress(self):
        """ Returns the current progress. See also __len__ for max value.
        """
        return self._progress
    
    
    @property
    def percent_done(self):
        """ Returns the progress in percent.
        """
        return 100.0 * self._progress / self._prog_max 
    
    
    @property
    def done(self):
        """ Returns true if all permutations have been reached.
        """
        return self._prog_max == self._progress
    
    
    #-- Private Methods -----------------------------------------------------------------------------------------------
    def _stack_next_idx(self):
        """ Skip chars that are further down the string. """
        while self._stack.top["token"][self._stack.top["idx"]] in self._stack.top["token"][self._stack.top["idx"]+1:]:
            self._stack.top["idx"] += 1
    
    
    def _stack_push_child(self, token, prefix):
        """ Creates a new child for the stack and calculates the required index. """
        self._stack.push(token = token, prefix = prefix, idx = 0)
        self._stack_next_idx()
    
    
    def _stack_build_branch(self):
        """ Builds the stack branch until a leaf is found. """
        while len(self._stack.top["token"]) > 1:
            self._stack_push_child(self._stack.top["token"][:self._stack.top["idx"]] + 
                                   self._stack.top["token"][self._stack.top["idx"] + 1:],
                                   self._stack.top["prefix"] + self._stack.top["token"][self._stack.top["idx"]])
    
    
    def _stack_next_branch(self):
        """ Collapses the current leaf-bearing branch until it reaches the next fork and increases the index. """
        while (len(self._stack) > 0) and (len(self._stack.top["token"]) == self._stack.top["idx"] + 1):
            self._stack.pop()
        
        if len(self._stack) > 0:
            self._stack.top["idx"] += 1
            self._stack_next_idx()
            self._stack_build_branch()
        else:
            pass #self._stack_from_queue()
    
    
    #-- Public Static Methods -----------------------------------------------------------------------------------------
    @staticmethod
    def permutations(token):
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

    
    #-- Public Methods ------------------------------------------------------------------------------------------------
    def reset(self):
        """ Resets to the first permutation.
        """
        if self._prog_max > 0:
            #-- First see if we need to reinitialize the stack
            if self._progress > 1:
                #-- Empty stack to first value
                while len(self._stack) > 1:
                    self._stack.pop()
                
                #-- Reset progress
                self._progress = 1
                self._stack.top["idx"] = 0
                
                #-- Rebuild first branch
                self._stack_build_branch()
        else:
            pass #-- Token not yet initialized
        
    
    
    def resume(self, token):
        """ Seeks to the provided token permutation. If the supplied token is different to the current token, it is
            replaced by the new one. Returns True if it was succesful.
        """
        flag = False
        if isinstance(token, str) and len(token):
            if self.token != "".join(sorted(token)):
                #-- Set new token
                self.token = token
            else:
                #-- Reset the stack
                self.reset()
            
            #-- Seek token
            """ [ NOTE ]: Build stack and use Permute.permutations(token) to skip dead branches.     << [ INEFFICIENT ]
            """ # pylint: disable=pointless-string-statement
            while self.token != token:  
                self.inc()
            
            flag = True
        else:
            pass #-- User is a special needs case
        
        return flag
    
    
    def inc(self):
        """ Progresses the stack and returns the next token.
        """
        if self._prog_max > 0:
            if not self.done:
                self._stack_next_branch()
                self._progress += 1
            else:
                pass #-- Shall we overflow?
        else:
            pass #-- User is a special needs case
        
        return self.token


#===================================================================================================[ SHUFFLE CLASS ]==
class Shuffle(Incremental):
    """ Calculates all unique permutations of a given token string.
        
            EXPOSES:
                Constants:
                    [None]
                
                Methods:
                    resume(token)               : Resumes from the specified token.
                    reset()                     : Resets the token to position 0.
                    inc()                       : Moves to the next permutation until all permutations are done.
                                                  Returns the current token.
                
                Properties:
                    (rw) [str] token            : Gets or sets the token. 
                    (ro) [tuple] progress       : Returns the current progress and max value as a tuple.
                    (ro) [float] percent_done   : Returns the progress as a percentage.
                    (ro) [bool] done            : Returns True if the current token is the last token.
    """
    #-- Constants -----------------------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Output --------------------------------------------------------------------------------------------------------
    _stderr = None
    
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Properties ----------------------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Private Methods -----------------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Public Methods ------------------------------------------------------------------------------------------------
    #[None]


#====================================================================================================[ ABACUS CLASS ]==
class Abacus(Incremental):
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
    #[None]
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Properties ----------------------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Private Methods -----------------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Public Methods ------------------------------------------------------------------------------------------------
    #[None]


#===========================================================================================================[ DEBUG ]==
def debug():
    """ Test method. """
    def dump(test):
        """ Prints all values in test.
        """
        for _ in range(len(test)):
            print "[ {} ] {:3.2f}% ({}/{})".format(test, test.percent_done, test.progress, len(test))
            if not test.done:
                test.inc()
            else:
                break
    
    
    def test_incremental():
        """ Tests the Incremental class.
        """
        test = Incremental("abc", 3, std_err=sys.stderr)
        #test.resume("bax")  #-- Token resume failure test
        #test.resume("bac")
        #test = Incremental("abc", token="abca")
        
        #-- Iteration test
        dump(test)
        
        #-- Overflow test
        print "[", test.inc(), "] <- Overflow test"
        
    
    def test_permute():
        """ Tests the Permute class.
        """
        test = Permute("abcdefg")
        test.resume("gfdceba")
        #test.resume("bac")  #-- Resumes with current token
        #test.resume("bax")  #-- Sets new token and resumes
        
        #-- Iteration test
        dump(test)
    
    
    def test_shuffle():
        """ Tests the Shuffle class.
        """
        test = Shuffle("abc", 3, std_err=sys.stderr)
        test.resume("bax")
    
    
    def test_abacus():
        """ Tests the Abacus class.
        """
    
    #-- Pick and test a class for debugging.
    idx=1
    if idx == 0:
        test_incremental()
    elif idx == 1:
        test_permute()
    elif idx == 2:
        test_shuffle()
    elif idx == 3:
        test_abacus()
        


#============================================================================================================[ MAIN ]==
if __name__ == "__main__":
    DEBUG_MODE = True
    debug()

