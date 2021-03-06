""" Brute: Incremental, Permute, Shuffle and Abacus
    
    author: aceldama.v1.0 at gmail
    
    Licensed under the GNU General Public License Version 2 (GNU GPL v2),
        available at: http://www.gnu.org/licenses/gpl-2.0.txt
    
    (C) 2016 David A Swanepoel
"""

#-- Import Dependencies
import sys
import math
from xifo import DictStack
import traceback

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
                    (ro) [int] progress         : Returns the current progress. (See self.__len__() for max value)
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
            result = "".join([self._chars[i] for i in self._index])
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
                self._prog_max = len(self._chars) ** len(self._index)
                self._progress = 0
                for idx in xrange(len(self._index)):
                    self._progress = (self._progress * len(self._chars)) + self._index[idx]
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
        return 100.0 * self.progress / len(self)
    
    
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


#===================================================================================================[ PERMUTE CLASS ]==
class Permute(object):
    """ Calculates all unique permutations of a single given token string.
        
            EXPOSES:
                Constants:
                    [None]
                
                Static Methods:
                    Permutations(token)         : Returns the number of possible permutations for a given token.
                
                Methods:
                    resume(token)               : Resumes from the specified token.
                    reset()                     : Resets the object to the initial starting position.
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
        
        #-- Set up the token
        _stack = DictStack(token="", prefix="", idx = 0)
        if isinstance(token, str) and (len(token) > 0):
            self.token = "".join(sorted(token))
            if self._prog_max == 0:
                pass #-- User is a special needs case
            elif isinstance(resume, bool) and resume:
                #-- Resume
                self.token = token
    
    
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
        """ Returns the current token. """
        return str(self)
    @token.setter
    def token(self, value):
        """ Sets the current token. """
        if isinstance(value, str) and (len(value) > 0) and (str(self) != value) or (self._progress != 1):
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
        return int(result)

    
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
                    (ro) [str] token_base       : Returns the chars of the token currently being permuted. (sorted)
                    (ro) [int] progress         : Returns the current progress. (See self.__len__() for max value)
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
    
    _token_flag = True  #-- Optimize property to skip rebuilding token every time it's called.
    _token_base = ""
    
    _tumble     = None  #-- Will hold the Permute() object
    _prog_max   = 1
    _progress   = 0
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    #-- Inherited: __len__(self)
    def __init__(self, chars, length=None, token=None, std_err=None):
        """ Initializes the object. Either length or token are required.
        """
        #-- Inherit
        Incremental.__init__(self, chars, length, token, std_err)
    
    
    def __str__(self):
        """ Returns a string containing the current token.
        """
        return "" if self._tumble is None else str(self._tumble)
    
    
    #-- Properties ----------------------------------------------------------------------------------------------------
    #-- Inherited: percent_done, done
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
                #-- Reset the indexes
                self._token_flag = True
                self._index = [0 for _ in xrange(len(value))]
                
                #-- Set the maximum progress value
                self._prog_max = len(self._chars) ** len(self._index)
                
                #-- Set up the index to resume from
                self._progress = 0
                sort_value = "".join(sorted(value))
                while self.token_base != sort_value:
                    self._inc_base()
                
                if self._tumble is None:
                    self._tumble = Permute(value)
                
                if self.token_base != value:
                    self._tumble.resume(value)
            else:
                self._error("ERROR: Supplied token [ {} ] contains bad chars. Using [ {} ]\n".format(value, str(self)))
    
    
    @property
    def token_base(self):
        """ Returns the token currently being permuted.
        """
        if self._token_flag:
            self._token_flag = False
            self._token_base = Incremental.__str__(self)
        return self._token_base
    
    
    @property
    def progress(self):
        """ Returns the current progress. See also __len__ for max value.
        """
        return self._progress + self._tumble.progress
    
    
    #-- Private Methods -----------------------------------------------------------------------------------------------
    def _inc_base(self):
        """ Originally called smart_inc, _inc_base increments the base token in such a way that duplicates don't happen
            in permutations. Also increments the base progress.
        """
        if (len(self._index) and len(self._chars)) > 0:
            #-- Update progress base
            self._progress += Permute.permutations(self.token_base)
            
            #-- Increment base token indexes
            idx = len(self._index) - 1
            while self._index[idx] + 1 == len(self._chars):
                self._index[idx] = 0
                idx -= 1
            self._index[idx] += 1
            
            idx += 1
            while idx < len(self._index):
                self._index[idx] = self._index[idx - 1]
                idx += 1
            
            self._token_flag = True
            
            #-- Set up new tumbler
            self._tumble = Permute(self.token_base)
    
    
    #-- Public Methods ------------------------------------------------------------------------------------------------
    #-- Inherited: resume(token)
    def reset(self):
        """ Resets the token to position 0.
        """
        if (len(self._index) and len(self._chars)) > 0:
            #-- Reset progress counter
            self._progress = 0
            
            #-- Reset token base
            for i in xrange(len(self._index)):
                self._index[i] = 0
            self._token_flag = True
            
            #-- Reset tumbler
            self._tumble = Permute(self.token_base)
    
    
    def inc(self):
        """ Increments the tumbler until it's done. Once that happens, it increments the base token until the base token
            is also complete. Returns the next token.
        """
        if (len(self._index) and len(self._chars)) > 0:
            if not self._tumble.done:
                self._tumble.inc()
            else:
                self._inc_base()
        return str(self)


#====================================================================================================[ ABACUS CLASS ]==
class Abacus(Incremental):
    """ The most basic brute force type class: Incremental. They don't get much simpler than this.
        
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
                    (ro) [str] token_base       : Returns the chars of the token currently being permuted. (sorted)
                    (ro) [int] progress         : Returns the current progress. (See self.__len__() for max value)
                    (ro) [float] percent_done   : Returns the progress as a percentage.
                    (ro) [bool] done            : Returns True if the current token is the last token.
    """
    #-- Constants -----------------------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Output --------------------------------------------------------------------------------------------------------
    _stderr = None
    
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    _chars  = []    #-- The full charset
    _index  = []    #-- Indirect charset indexes. _index range optimized by _chokes.  ->  _chars[_abacus[_index[]]]
    
    _abacus = []    #-- Holds the abacus indexes so it is, effectively, a subset of _chars.
    _chokes = []    #-- Holds the token per-position ranges for _index.
    _checks = []    #-- Keeps track of which chars have been checked against which. Needed to generate _chokes.
    
    _tumble     = None  #-- Will hold the Permute() object
    _prog_max   = 1
    _progress   = 0
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    #Inherited: __len__(self)
    def __init__(self, chars, length=None, token=None, std_err=None):
        """ Initializes the object. Either length or token are required.
        """
        Incremental.__init__(self, chars, length, token, std_err)
    
    
    def __str__(self):
        """ Returns the current token.
        """
        #result = ""
        #if (len(self._chars) > 0) and (len(self._index) > 0):
        #    result = "".join([self._chars[self._abacus[idx]] for idx in self._index])
        return str(self._tumble) if self._tumble is not None else ""
    
    
    #-- Properties ----------------------------------------------------------------------------------------------------
    @property
    def token(self):
        """ Returns the current token. """
        return str(self) if str(self) is not None else ""
    @token.setter
    def token(self, value):
        """ Sets the token and resumes. """
        if isinstance(value, str) and (str(self) != value) and (len(value) > 0):
            seek_token = set(value)
            if seek_token.issubset(self._chars):
                #-- Global variable initialization
                if (len(self._index) != len(value)) or (len(self._abacus) != len(value)):
                    self._index = range(len(value))
                    self._index = [0] * len(value)
                self.reset()

                #-- Find point from which to resume
                seek_token = set([self._chars.index(char) for char in value])
                while not seek_token.issubset(self._abacus):
                    self.inc()
                    #print self.progress, self._chars, self._abacus, self._index, seek_token
                
                #-- Init the tumbler
                self._tumble.resume(value)
    
    
    @property
    def progress(self):
        """ Returns the current progress. See also __len__ for max value.
        """
        return self._progress + self._tumble.progress
    
    
    @property
    def base_token(self):
        """ Returns the current base token.
        """
        token = ""
        for idx in self._index:
            token += self._chars[self._abacus[idx]]
        return token
    
    
    @property
    def done(self):
        """ Returns true if the current progress equals the maximum progress.
        """
        return self.progress == len(self)
    
    
    #-- Private Methods -----------------------------------------------------------------------------------------------
    def _inc(self):
        """ Tries to perform an increment on the indexes and returns True if an overflow was not encountered.
        """
        idx  = len(self._index) - 1
        self._index[idx] += 1
        while (idx >= 0) and (self._index[idx] >= len(self._chokes[idx])):
            self._index[idx] = self._chokes[idx][0]
            idx -= 1
            self._index[idx] += 1
        
        if idx >= 0:
            #-- Iron out the indexes to avoid duplicate shuffles.
            print ""
            idx += 1
            while idx < len(self._index):
                self._index[idx] = max(self._index[idx - 1], self._index[idx])
                idx += 1
            
        return idx == len(self._index)

    
    def _abacus_digest(self):
        """ Returns a tuple containg number of unchecked, partially checked and fully checked characters.
        """
        empty_sets      = 0
        partial_sets    = 0
        complete_sets   = 0
        for idx in self._abacus:
            if self._checks[idx].issuperset(self._abacus):
                complete_sets += 1
            elif len(self._checks[idx]) == 0:
                empty_sets += 1
            else:
                partial_sets += 1
        return (empty_sets, partial_sets, complete_sets)

        
    def _inc_abacus(self):
        """ Shifts the abacus indexes and updates the progress, chokes and 
        """
        print "\n\n--[ WIBBLE ]----------------------------------------------"
        print [self._chars[idx] for idx in self._abacus]
        #-- Update checked characters dictionary.
        for idx in self._abacus:
            self._checks[idx].update(self._abacus)
        
        #-- Perform the abacus shift operation.
        if (self._abacus[-1] + 1) < len(self._chars):
            #-- Shift the abacus one position on
            for idx in range(len(self._abacus)):
                self._abacus[idx] += 1
        else:
            #-- Shift the entire abacus back to first position.
            idx = len(self._abacus)
            while idx > 0:
                idx -= 1
                self._abacus[idx] -= self._abacus[0]
            
            #-- Progress the abacus.                # xooo
            self._abacus[1] += 1                                            #-- [0] is static, inc index [1]
            if (len(self._abacus) > 2) and (self._abacus[1] == self._abacus[2]):
                #-- Index collision detected!       # x-8o          x-8-o
                idx = 2
                flr = 1
                while (idx < len(self._abacus)) and (self._abacus[idx - 1] == self._abacus[idx]):
                    self._abacus[idx - 1] = flr     # xooo  xooo    xoo-o   #-- Move colliding value to floor.
                    flr += 1                        #  || // ||      ||     #-- Increment floor position.
                    self._abacus[idx] += 1          # xo-8  xoo-o   xo-oo   #-- Increment checked value.
                    idx += 1                                                #-- Increment position to check.
        
        #-- Build new index chokes
        empty_sets, partial_sets, complete_sets = self._abacus_digest()
        #for idx in self._abacus:
        #    if self._checks[idx].issuperset(self._abacus):
        #        complete_sets += 1
        #    elif len(self._checks[idx]) == 0:
        #        empty_sets += 1
        #    else:
        #        partial_sets += 1
        
        if complete_sets < len(self._abacus):
            #-- Create a full chokes list
            self._chokes = [range(len(self._abacus)) for _ in self._abacus]

            if empty_sets < len(self._abacus):
                #-- Last index is always static after the initial set
                self._chokes[-1] = [self._chokes[-1][-1]]
                if (partial_sets > 1) and (empty_sets == 0):
                    #-- First index is also static
                    self._chokes[0] = [self._chokes[0][0]]
        else:
            self._chokes = [[idx] for idx in range(len(self._abacus))]
            
        
        #-- Zero out indexes
        self._index = [self._chokes[idx][0] for idx in range(len(self._chokes))]
        
        #--Debugging...
        print [self._chars[idx] for idx in self._abacus]
        print empty_sets, partial_sets, complete_sets, ":", self._chokes
        print
        for idx in range(len(self._checks)):
            fmt = "[{}] :" if idx in self._abacus else " {}  :"
            print fmt.format(self._chars[idx]), [self._chars[idx] for idx in sorted(self._checks[idx])]
        print
    
    
    #-- Public Methods ------------------------------------------------------------------------------------------------
    #-- Inherited: resume(token)
    def reset(self):
        """ X
        """
        if (len(self._index) and len(self._chars)) > 0:
            #-- Reset progress
            self._prog_max = len(self._chars) ** len(self._index)
            self._progress = 0
            
            print " >>", len(self._chars), len(self._index), len(self._chars) ** len(self._index)
            #-- Reset tracker
            self._checks = [set([]) for _ in self._chars]
            
            #-- Reset abacus and indexes
            self._abacus = range(min(len(self._index), len(self._chars)))
            self._index  = [0] * len(self._index)
            
            #-- Reset chokes (first set of brutes will not be choked)
            self._chokes = [list(self._abacus) for _ in range(len(self._index))]
            
            #-- Reset Tumbler
            self._tumble = Permute(self.base_token)
        else:
            pass #-- Object not set up yet!
    
    
    def inc(self):
        """ X
        """
        #-- Update checked characters dictionary.
        if (len(self._index) and len(self._chars)) > 0:
            if self._tumble.done:
                #-- Perform an inc and check if we need to shift the abacus.
                if not self._inc():
                    #-- Yes, shift the abacus.
                    self._inc_abacus()
                
                #-- Update progress and tumbler
                self._progress += len(self._tumble)
                self._tumble = Permute(self.base_token)
            else:
                self._tumble.inc()


#===========================================================================================================[ DEBUG ]==
def debug():
    """ Test method. """
    def dump(test):
        """ Prints all values in test.
        """
        for _ in range(len(test)):
            print "[ {} ] {:.2f}% ({}/{})".format(test, test.percent_done, test.progress, len(test))
            if not test.done:
                test.inc()
            else:
                break
    
    def test_incremental():
        """ Tests the Incremental class.
        """
        test = Incremental("abc", 3, std_err=sys.stderr)
        #test = Incremental("abc", token="abca")
        
        #test.resume("bax")      #-- Test invalid resume
        #test.resume("bac")      #-- Test vlaid resume
        
        return test
    
    def test_permute():
        """ Tests the Permute class.
        """
        test = Permute("abcdefgh")
        test.resume("hgfdceba")  #-- Test vlaid resume
        
        #test = Permute("abc")
        #test.resume("bac")      #-- Test vlaid resume
        #test.resume("bax")      #-- Test invalid resume
        
        return test
    
    def test_shuffle():
        """ Tests the Shuffle class.
        """
        test = Shuffle("abc", 3, std_err=sys.stderr)
        test.resume("cbc")      #-- Test vlaid resume
        #test.resume("bax")      #-- est invalid resume
        
        return test
    
    def test_abacus():
        """ Tests the Abacus class.
        """
        #test = Abacus("abcde", 3)
        #test.resume("gaff")      #-- Test vlaid resume
        #test.resume("eaa")      #-- Test vlaid resume
        #test.resume("bax")      #-- est invalid resume
        
        hold = []
        test = Shuffle("abcdefg", 4)
        while not test.done:
            hold.append(str(test))
            test.inc()
        hold.append(str(test))
        try:
            test = Abacus("abcdefg", 4)#, std_err=sys.stderr)
            for i in range(len(hold)):
                print "[ {}/{} ] {:.2f}% ({}/{})".format(test.base_token, test, test.percent_done, test.progress, len(test))
                hold.pop(hold.index(str(test)))
                test.inc()
        except Exception, e:
            sets = sorted(set(["".join(sorted(token)) for token in hold]))

            print "\n\n[{} orphans]".format(len(hold))
            while len(hold):
                i = 0
                tmp = hold.pop(0)
                while len(hold) and (i < 19):
                    tmp += "  " + hold.pop(0)
                    i += 1
                print tmp
                
            print "\n\n[{} sets]".format(len(sets))
            while len(sets):
                i = 0
                tmp = sets.pop(0)
                while len(sets) and (i < 19):
                    tmp += "  " + sets.pop(0)
                    i += 1
                print tmp
                
            traceback.print_exc()
            exit(0)
        
        return test
    
    #-- Pick and test a class for debugging.
    try:
        dump([test_incremental, test_permute, test_shuffle, test_abacus][3]())
    except KeyboardInterrupt:
        pass


#============================================================================================================[ MAIN ]==
if __name__ == "__main__":
    DEBUG_MODE = True
    debug()

