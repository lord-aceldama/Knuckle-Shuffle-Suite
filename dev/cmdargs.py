""" CMDARGS
    
    author: aceldama.v1.0 at gmail
    
    Licensed under the GNU General Public License Version 2 (GNU GPL v2), 
        available at: http://www.gnu.org/licenses/gpl-2.0.txt
    
    (C) 2016 David A Swanepoel
"""

#-- Import Dependencies
import sys


#==================================================================================================[ CMD ARGS CLASS ]==
class CmdArgs(object):
    """ A class that is supposed to simplifiy command-line argument retrieval.
    """
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    _emo  = None    # Case sensitive flag.
    _opts = []      # Options to look for.
    _args = {}      # Args to parse - we save it to speed up case-insensitive scans
    
    _parsed = {}    # Dict containing parsed options
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    def __init__(self, case_sensitive, *options):
        """ X
        """
        self.match_case = case_sensitive
        self._parse(options)
    
    
    #-- Properties ----------------------------------------------------------------------------------------------------
    @property
    def match_case(self, value):
        """ X
        """
        if (value != self._emo) and (type(value) == bool):
            self._emo = value
    
    
    #-- Private static methods ----------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Public static methods -----------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Private methods -----------------------------------------------------------------------------------------------
    def _parse(self, *options):
        """ X
        """
        def modify_if(flag, value, *modifier):
            """ X
            """
            result = value
            if flag:
                for modify in modifier:
                    result = modify(result)
            return result
        
        self._parsed = dict()
        for idx in xrange(2):
            flag = idx == 0
            self._parsed[flag] = {"opts":set(), "vals":dict(), "args":list()}
            for arg in sys.argv[:1]:
                self._parsed[flag]["args"].append(modify_if(not flag, arg, str.upper))
            for opt in options:
                self._parsed[flag]["opts"].add(modify_if(not flag, opt, str.upper, str.strip))
        
        return False
    
    
    #-- Public methods ------------------------------------------------------------------------------------------------
    def is_set(self, option):
        """ X
        """
    
    
    def value(self, option, synonym = None):
        """ X
        """


#====================================================================================================[ TEST METHODS ]==
def test_cmdargs():
    """ Test run """


#============================================================================================================[ MAIN ]==
if __name__ == "__main__":
    DEBUG_MODE = True
    test_cmdargs()

