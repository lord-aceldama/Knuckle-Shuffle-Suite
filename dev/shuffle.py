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
    _stack = xifo.DictStack(token="", prefix="", index = 0)
    
    
    #-- Special class methods -----------------------------------------------------------------------------------------
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
    
    
    #-- Private Methods -----------------------------------------------------------------------------------------------
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
    
    
    #-- Public Methods ------------------------------------------------------------------------------------------------
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


#====================================================================================================[ TEST METHODS ]==
def test_shuffle():
    """ Test run """
    test_token = "abba"
    test = Shuffle()
    test.print_shuffle(test_token)
    print test.shuffle_count(test_token)
    test.non_recursive_shuffle(test_token)


#============================================================================================================[ MAIN ]==
if __name__ == "__main__":
    DEBUG_MODE = True
    test_shuffle()

