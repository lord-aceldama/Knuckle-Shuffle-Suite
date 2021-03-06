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
        
        EXPOSES:
            Methods:
                add(option)             : Adds an option and re-parses command-line arguments ["cmd args" herafter]
            
            Functions:
                [list] value(option)    : Returns a list containing option and synonym value(s)
                [type] type(option)     : Returns the user-defined type of an option
                [bool] isset(*option)   : Returns true if the option is present in the cmd args.
                [list] synonyms(option) : Returns a list containing option's synonyms.
            
            Properties:
                (ro) [list] orphans     : Returns a list of orphan arguments (cmd args without a preceeding option) 
    """
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    _parsed  = {}   # Dict containing parsed options
    _orphans = []   # Args that weren't preceeded by a valid option
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    def __init__(self, *options):
        """ Initializes the class. Options can be either strings or tuples/lists. If a tuple/list is supplied, then
            it needs to be in the format ([type, ]name[, synonym[, synonym_n]]).
        """
        self._parse_options(options)
    
    
    def __str__(self):
        """ Returns a string representation of the parsed command-line arguments.
        """
            
        result = "ARGS({0}/{1})".format(len(self), len(self._parsed.keys()))
        r_temp = []
        for key in self._parsed.keys():
            if self._parsed[key]["link"] is None:
                #-- Primary option token
                r_temp.append("{0}({1},{2})".format(key, self._parsed[key]["type"].__name__, "{0}"))
                if self._parsed[key]["value"] is None:
                    r_temp[-1] = r_temp[-1].format("0" if self._parsed[key]["isset"] else "-")
                else:
                    r_temp[-1] = r_temp[-1].format(len(list(self._parsed[key]["value"])))
                
                #-- Option links
                key_links = ", ".join(self.synonyms(key))
                r_temp[-1] += "->[{0}]".format(key_links) if len(key_links) > 0 else ""
                
        return result + (": [{0}]".format(", ".join(r_temp)) if len(r_temp) > 0 else "")
    
    
    def __len__(self):
        """ Returns the number of valid options being checked. Synonyms count as a single entry.
        """
        count = 0
        for key in self._parsed.keys():
            if self._parsed[key]["link"] is None:
                count += 1
        return count
    
    
    #-- Properties ----------------------------------------------------------------------------------------------------
    @property
    def orphans(self):
        """ Return a list of orphans. """
        return self._orphans
    
    
    #-- Private static methods ----------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Public static methods -----------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Private methods -----------------------------------------------------------------------------------------------
    def _add_raw(self, opt_type, opt_name, opt_link):
        """ Adds a single processed option to the parsed dictionary, provided it doesn't already exist.
        """
        if (len(opt_name) > 0) and (opt_name not in self._parsed.keys()):
            self._parsed[opt_name] = { "link" : opt_link, "type" : opt_type, "value":None, "isset":False }
    
    
    def _add(self, opt):
        """ Processes tuples/lists and option names.
        """
        if type(opt) in [list, tuple]:
            #-- Type and/or synonym(s) specified: ([type, ]name[, synonym[, synonym_n]])
            if len(opt) > 1:
                opt_synonym = None
                start_index = 1 if (type(opt[0]) == type) else 0
                for opt_name in opt[start_index:]:
                    if opt_synonym is not None:
                        #-- Link to existing option.
                        self._add_raw(None, opt_name.strip(), opt_synonym)
                    else:
                        #-- New option.
                        opt_synonym = opt_name.strip()
                        self._add_raw(str if start_index == 0 else opt[0], opt_name.strip(), None)
        else:
            #-- Single option.
            self._add_raw(str, opt.strip(), None)
    
    
    def _parse_args(self):
        """ Parses the command-line arguments.
        """
        #-- Kill orphans. (Yes, I'm a sociopath)
        self._orphans = []
        
        #-- Empty all option values.
        for key in self._parsed:
            self._parsed[key]["value"] = None
        
        #-- Fill option values.
        c_opt = ""
        for arg in sys.argv[1:]:
            clean = arg.strip()
            if clean in self._parsed.keys():
                #-- Select primary synonym instead.
                c_opt = clean if self._parsed[clean]["link"] is None else self._parsed[clean]["link"]
                self._parsed[c_opt]["isset"] = True
            else: 
                if len(c_opt) > 0:
                    #-- Type conversion
                    if self._parsed[c_opt]["type"] is not str:
                        #-- Force the type.
                        clean = self._parsed[c_opt]["type"](arg)
                    
                    #-- Process value
                    if self._parsed[c_opt]["value"] is None:
                        #-- Set the value.
                        self._parsed[c_opt]["value"] = arg
                    elif type(self._parsed[c_opt]["value"]) is list:
                        #-- Add to the value.
                        self._parsed[c_opt]["value"].append(arg)
                    else:
                        #-- Convert to list.
                        self._parsed[c_opt]["value"] = [self._parsed[c_opt]["value"], arg]
                else:
                    #-- Orphan
                    self._orphans.append(arg)
    
    
    def _parse_options(self, options):
        """ Parses the user-supplied option list.
        """
        #-- First get the options sorted...
        self._parsed = dict()
        for opt in options:
            self._add(opt)
        
        #-- ...and then, the command line arguments.
        self._parse_args()
    
    
    def _get_root(self, option, does_not_exist=None):
        """ Returns the primary link for the option, or a dne's value if the option does not exist.
        """
        root = option if option in self._parsed.keys() else does_not_exist
        if root == option:
            if self._parsed[root]["link"] is not None:
                root = self._parsed[root]["link"]
        return root
    
    
    #-- Public methods ------------------------------------------------------------------------------------------------
    def add(self, option):
        """ Add a single option and re-parse the command-line arguments.
        """
        self._add(option)
        self._parse_args()
    
    
    def value(self, option):
        """ Returns a value (or list of values if more than one was found) or None if it was not supplied.
        """
        result = self._get_root(option, None)
        if result is not None:
            result = self._parsed[result]["value"]
        return result
    
    
    def type(self, option):
        """ Returns the type of a given option or none if the option does not exist.
        """
        result = None
        if option in self._parsed.keys():
            result = self._parsed[self._get_root(option)]["type"]
        return result
    
    
    def isset(self, *option):
        """ Returns true if the option (or its synonym[s]) is present in the command-line.
        """
        idx = 0
        flag = len(option) > 0
        while flag and (idx < len(option)):
            flag = (option[idx] in self._parsed.keys()) and self._parsed[self._get_root(option[idx])]["isset"]
            idx += 1
        return flag
    
    
    def synonyms(self, option):
        """ Returns a list containing an option's links.
        """
        result = []
        for key in self._parsed.keys():
            if self._parsed[key]["link"] == option:
                result.append(key)
        return result


#====================================================================================================[ TEST METHODS ]==
def test_cmdargs():
    """ Test run 
    
        COMMAND LINE:
            > python cmdargs.py orphan --wants "a" --cracker --salty preferred ""
     
        OUTPUT:
            > ARGS(5/8): [-f(str,-), --wants(str,1)->[-a, --cracker], --fiddle(int,-)->[--sticks], --polly(str,-), 
              --salty(str,2)]
            > --salty: ['preferred', '']
            > Orphans: ['orphan']
    """
    test = CmdArgs("-f", (int, "--fiddle", "--sticks"), (str, "--polly"), ("--wants", "-a", "--cracker"), "--salty")
    print test
    print "--salty:", test.value("--salty")
    print "Orphans:", test.orphans


#============================================================================================================[ MAIN ]==
if __name__ == "__main__":
    DEBUG_MODE = True
    test_cmdargs()

