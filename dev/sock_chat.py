""" EMPTY TEMPLATE
    
    author: aceldama.v1.0 at gmail
    
    Licensed under the GNU General Public License Version 2 (GNU GPL v2), 
        available at: http://www.gnu.org/licenses/gpl-2.0.txt
    
    (C) 2016 David A Swanepoel
"""

#-- Import Dependencies
import socket, select, time
from threading import Thread


#====================================================================================================[ SERVER CLASS ]==
class Server(object):
    """ A very basic TCP chat server.
        
            RESEARCH:
                - https://docs.python.org/2/library/socket.html
                - http://www.binarytides.com/python-socket-server-code-example/
                - http://www.binarytides.com/code-chat-application-server-client-sockets-python/
                - http://www.saltycrane.com/blog/2008/09/simplistic-python-thread-example/
            
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
    BUFFER_LEN   = 2**12            #-- 4096: Advisable to keep it as an exponent of 2
    DEFAULT_PORT = 61616
    TOKEN_STRING = ["CONNECT", "DISCONNECT"]
    CONNECT, DISCONNECT = range(len(TOKEN_STRING))
    
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    _client = []
    _client_data = [[], [], []]     #-- [[indexes], [ttl], [available indexes]]
    _server = None
    _thread = None
    _callback = None
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    def __init__(self, port=DEFAULT_PORT, callback=None):
        """ Initializes the object.
        """
        #-- Initialize the server socket
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind(("0.0.0.0", port))
     
        # Add server socket to the list of readable connections
        self._client.append(self._server)
        
        #-- Check if a callback function is supplied
        if (callback is not None) and hasattr(callback, "__call__"):
            self._callback = callback
        
    
    def __str__(self):
        """ Returns a string representation of the version.
        """
        result = ""
        return result
        
    
    
    #-- Properties ----------------------------------------------------------------------------------------------------
    #@property
    #def name(self):
    #    """ Returns the name. """
    #    return self._name
    #@name.setter
    #def name(self, value):
    #    """ Sets the name. """
    
    
    #-- Private Methods -----------------------------------------------------------------------------------------------
    def _broadcast(self, message):
        """ Sends a message to all connected clients.
        """
        for socket in self._client:
            if socket != server_socket and socket != sock :
                try :
                    socket.send(message)
                except :
                    # broken socket connection may be, chat client pressed ctrl+c for example
                    socket.close()
                    CONNECTION_LIST.remove(socket)    
    
    
    @staticmethod
    def _spit(text):
        """ Just prints a message to stdout.
        """
        print text
    
    
    #-- Public Methods ------------------------------------------------------------------------------------------------
    def start(self):
        """ Starts the server
        """
        print "Server started on port {0}".format(port)
        self._server.listen(10)
    
    
    def stop(self):
        """ Stops the server and tries to let all connected clients know.
        """
        self._server.close()    
    
    
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
    CONNECTION_LIST = []    # list of socket clients
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    PORT = 5000
         
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this has no effect, why ?
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)
 
    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)
 
    print "Chat server started on port " + str(PORT)
 
    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
 
        for sock in read_sockets:
             
            #New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
                print "Client (%s, %s) connected" % addr
                 
            #Some incoming message from a client
            else:
                # Data recieved from client, process it
                try:
                    #In Windows, sometimes when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                    data = sock.recv(RECV_BUFFER)
                    # echo back the client message
                    if data:
                        sock.send('OK ... ' + data)
                 
                # client disconnected, so remove from socket list
                except:
                    broadcast_data(sock, "Client (%s, %s) is offline" % addr)
                    print "Client (%s, %s) is offline" % addr
                    sock.close()
                    CONNECTION_LIST.remove(sock)
                    continue
         
    server_socket.close() 

#============================================================================================================[ MAIN ]==
if __name__ == "__main__":
    DEBUG_MODE = True
    debug()

