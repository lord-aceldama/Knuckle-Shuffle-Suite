""" EMPTY TEMPLATE
    
    author: aceldama.v1.0 at gmail
    
    Licensed under the GNU General Public License Version 2 (GNU GPL v2), 
        available at: http://www.gnu.org/licenses/gpl-2.0.txt
    
    (C) 2016 David A Swanepoel
"""

#-- Import Dependencies
import socket, select


#====================================================================================================[ SERVER CLASS ]==
class Server(object):
    """ A very basic TCP chat server.
        
            RESEARCH:
                - http://www.binarytides.com/code-chat-application-server-client-sockets-python/
            
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
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    PORT = 5000
    
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    _clients = []
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    def __init__(self):
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
    def send(self, client_id, data):
        """ X
        """
        return False
    
    
    def send_all(self, data):
        """ X
        """
        return False


#===========================================================================================================[ DEBUG ]==
def debug():
    """ Test method. """
 

#============================================================================================================[ MAIN ]==
if __name__ == "__main__":
    DEBUG_MODE = True
    debug()

