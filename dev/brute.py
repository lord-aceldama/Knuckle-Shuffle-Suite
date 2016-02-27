""" Brute
    
    author: aceldama.v1.0 at gmail
    
    Licensed under the GNU General Public License Version 2 (GNU GPL v2), 
        available at: http://www.gnu.org/licenses/gpl-2.0.txt
    
    (C) 2016 David A Swanepoel
"""

#-- Import Dependencies
#[None]


#=================================================================================================[ FORCE_INC CLASS ]==
class Force_Inc(object):
    """ The most basic incremental brute force class. They don't get much simpler than this...
        
            EXPOSES:
                Constants:
                    NAME
                
                Methods:
                    name                    : ?
                
                Functions:
                    [type] name             : ?
                
                Properties:
                    (rw) [str] name         : ?
    """
    
    #-- Constants -----------------------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    def __init__(self, characters, length_start, length_end=None, std_out=None, std_err=None):
        """ Initializes the object.
        """
    
    
    def __str__(self):
        """ Returns a string representation of the version.
        """
        result = ""
        return result
        
    
    
    #-- Properties ----------------------------------------------------------------------------------------------------
    @property
    def name(self):
        """ Returns the name. """
        return self._name
    @name.setter
    def name(self, value):
        """ Sets the name. """
    
    
    #-- Private Methods -----------------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Public Methods ------------------------------------------------------------------------------------------------
    #[None]


#===========================================================================================================[ DEBUG ]==
def debug():
    """ Test method. """
 

#============================================================================================================[ MAIN ]==
if __name__ == "__main__":
    DEBUG_MODE = True
    debug()

