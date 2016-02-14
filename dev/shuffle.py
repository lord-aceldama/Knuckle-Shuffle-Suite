""" SHUFFLE
    
    author: aceldama.v1.0 at gmail
    
    Licensed under the GNU General Public License Version 2 (GNU GPL v2), 
        available at: http://www.gnu.org/licenses/gpl-2.0.txt
    
    (C) 2016 David A Swanepoel
"""

#-- Import Dependencies
import sys, math
import xifo


#===================================================================================================[ SHUFFLE CLASS ]==
class Shuffle(object):
    """ Calculates (and print) all unique permutations of a given token string. I'm putting this
        in a dedicated class because I plan to add multi-processing and buffering capabilities
        later on.
        
        Non-recursive permutations: 
            http://stackoverflow.com/questions/18227931/iterative-solution-for-finding-string-permutations
    """
    
    #-- Constants -----------------------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Output --------------------------------------------------------------------------------------------------------
    _stdout = sys.stdout
    _stderr = sys.stderr
    
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    _queue = xifo.Queue()
    _stack = xifo.DictStack(token="", prefix="", idx = 0)
    
    _current = ""
    _progval = 0
    _progmax = 0
    
    
    #-- Special class methods -----------------------------------------------------------------------------------------
    def __init__(self, std_out=None, std_err=None):
        """ Docstring.
        """
        #-- Set output vectors.
        if std_out is not None:
            self._stdout = std_out
        
        if std_err is not None:
            self._stderr = std_err
        
    
    def __str__(self):
        """ Returns data containing the current token, unshuffled token and progress. """
        return "{0}:{1}[{2}/{3}] ({4:.2%})".format(self._current, self.token, 
                                                   self._progval + 1, self._progmax, 
                                                   1. * self.pos / self._progmax)
    
    
    def __len__(self):
        """ Returns the amount of tokens left to return.
        """
        return max(0, self._progmax - self._progval)
    
    
    #-- Properties ----------------------------------------------------------------------------------------------------
    @property
    def progress(self):
        """ Returns a tuple containing the overall percentage, value and maximum as a tuple as well as the queue length
            contained in a tuple.
        """
        x_percent  = round((100.0 * self._progval) / self._progmax, 2)
        x_progress = (self._progval, self._progmax)
        return (x_percent, x_progress, len(self._queue))
    
    
    @property
    def pos(self):
        """ X """
        return self._progval + 1
    
    
    @property
    def done(self):
        """ Returns True if there are no more tokens to return. """
        return (len(self._stack) == 0) and (len(self._queue) == 0)
    
    
    @property
    def token(self):
        """ Returns the current shuffled token. If all jobs are complete, None is returned.
        """
        value = None
        if len(self._stack) > 0:
            value = self._stack.top["prefix"] + self._stack.top["token"]
        return value
        
    
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
        """ Builds the stack branch until a leaf is found. Also increases the progress counter. """
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
            self._stack_from_queue()
    
    
    def _stack_from_queue(self):
        """ Pop queue and build new stack. """
        if (len(self._queue) > 0) and (len(self._stack) == 0):
            #-- Current stack processing complete, so pop and process.
            self._current = self._queue.pop()
            self._stack_push_child(self._current, "")
            self._stack_build_branch()
    
    
    def _shift(self):
        """ Pops the current token off the queue if stack is empty and populates/progresses the stack.
        """
        if not self.done:
            self._progval += 1
            self._stack_next_branch()
    
    
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
    
    
    #-- Public Static Methods -----------------------------------------------------------------------------------------
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

    
    #-- Public Methods ------------------------------------------------------------------------------------------------
    def reset(self, charset=None):
        """ To do.
        """
    
    
    def add(self, *tokens):
        """ Adds the token to the shuffle queue provided there isn't another exact token queued for processing. Returns
            len(Shuffle).
        """
        for token in tokens:
            if not self._queue.contains(token):
                self._progmax += Shuffle.shuffle_count(token)
                self._queue.push(token)
        
        self._stack_from_queue()
        return len(self)
    
    
    def next(self):
        """ Returns the current token and moves on to the next.
        """
        value = self.token 
        self._shift()
        return value
    
    
    #-- Generator
    def next_n(self, qty_max=None):
        """ Generator that yields the next tokens or completes early if Shuffle.done is True or qty_max is supplied 
            and reached.
        """
        idx = 0
        while (not self.done) and ((qty_max is None) or (idx < qty_max)):
            idx += 1
            yield self.next()
    
    
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


#====================================================================================================[ TEST METHODS ]==
def test_shuffle():
    """ Test run """
    test_token = "aabc"
    test = Shuffle()
    test.print_shuffle(test_token)
    print test.shuffle_count(test_token)
    test.non_recursive_shuffle(test_token)
    print "\n\n"
    
    test = Shuffle()
    print test.add(test_token, "abb")
    while not test.done:
        print test.token#, test._stack
        test.next()


#============================================================================================================[ MAIN ]==
if __name__ == "__main__":
    DEBUG_MODE = True
    test_shuffle()

