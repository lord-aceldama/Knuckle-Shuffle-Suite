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
                - https://docs.python.org/2/library/socket.html
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
    BUFFER_LEN   = 2**12    #-- 4096: Advisable to keep it as an exponent of 2
    DEFAULT_PORT = 61616
    
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    _clients = []
    _server = None
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    def __init__(self, port=DEFAULT_PORT):
        """ Initializes the object.
        """
        #-- Initialize the server socket
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind(("0.0.0.0", port))
        self._server.listen(10)
     
        # Add server socket to the list of readable connections
        self._clients.append(self._server)
     
        print "Server started on port {0}".format(port)
     
        while 1:
            # Get the list sockets which are ready to be read through select
            read_sockets, write_sockets, error_sockets = select.select(self._clients, [], [])
     
            for sock in read_sockets:
                #New connection
                if sock == server_socket:
                    # Handle the case in which there is a new connection recieved through server_socket
                    sockfd, addr = server_socket.accept()
                    CONNECTION_LIST.append(sockfd)
                    print "Client (%s, %s) connected" % addr
                     
                    broadcast_data(sockfd, "[%s:%s] entered room\n" % addr)
                 
                #Some incoming message from a client
                else:
                    # Data recieved from client, process it
                    try:
                        #In Windows, sometimes when a TCP program closes abruptly,
                        # a "Connection reset by peer" exception will be thrown
                        data = sock.recv(RECV_BUFFER)
                        if data:
                            broadcast_data(sock, "\r" + '<' + str(sock.getpeername()) + '> ' + data)                
                     
                    except:
                        broadcast_data(sock, "Client (%s, %s) is offline" % addr)
                        print "Client (%s, %s) is offline" % addr
                        sock.close()
                        CONNECTION_LIST.remove(sock)
                        continue
         
        server_socket.close()    
    
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

