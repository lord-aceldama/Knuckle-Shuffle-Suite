""" VERSION
    
    author: aceldama.v1.0 at gmail
    
    Licensed under the GNU General Public License Version 2 (GNU GPL v2), 
        available at: http://www.gnu.org/licenses/gpl-2.0.txt
    
    (C) 2016 David A Swanepoel
"""

#-- Import Dependencies
#[None]


#=====================================================================================================[ QUEUE CLASS ]==
class Version(object):
    """ Simple version control class. They don't get much simpler than this...
        GUIDELINE: https://en.wikipedia.org/wiki/Software_versioning

            EXPOSES:
                Properties:
                    (ro) [str] name         : Returns the name of the applocation.
                    (ro) [int] major:       : Returns application's major version.
                    (ro) [int] minor        : Returns application's minor version.
                    (ro) [int] stage        : Returns application's development stage.
                    (ro) [int] revision     : Returns current stage's revision.
    """
    
    #-- Constants -----------------------------------------------------------------------------------------------------
    STAGE = { 0: ["a",  "alpha"],
              1: ["b",  "beta"],
              2: ["rc", "release candidate"],
              3: ["r",  "release"]              }
    
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    _name = ""
    _version = []
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    def __init__(self, name, major, minor, stage, revision=0):
        """ Initializes the object.
        """
        self._name = name
        self._version = [major, minor, stage, revision]
    
    
    def __str__(self):
        """ Initializes the object.
        """
        result = "{0} v{1}.{2}-{3}{4}".format(self._name, self._version[0], self._version[1], 
                                              self.STAGE[self._version[2]][0],
                                              self._version[3] if self._version[3] > 0 else "")
        return result
        
    
    
    #-- Properties ----------------------------------------------------------------------------------------------------
    @property
    def name(self):
        """ Returns the name of the applocation. """
        return self._name
    
    
    def major(self):
        """ Returns application's major version. """
        return self._version[0]
    
    
    def minor(self):
        """ Returns application's minor version. """
        return self._version[1]
    
    
    def stage(self):
        """ Returns application's development stage. """
        return self._version[2]
    
    
    def revision(self):
        """ Returns current stage's revision. """
        return self._version[3]
    
    
    #-- Private Methods -----------------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Public Methods ------------------------------------------------------------------------------------------------
    #[None]


#============================================================================================================[ MAIN ]==
#[None]
