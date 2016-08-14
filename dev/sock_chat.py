""" EMPTY TEMPLATE
    
    author: aceldama.v1.0 at gmail
    
    Licensed under the GNU General Public License Version 2 (GNU GPL v2), 
        available at: http://www.gnu.org/licenses/gpl-2.0.txt
    
    (C) 2016 David A Swanepoel
"""

#-- Import Dependencies
import socket, time
from threading import Thread
#from xifo import Queue


#====================================================================================================[ SERVER CLASS ]==
class Server(Thread):
    """ A very basic TCP chat server.
        
            RESEARCH:
                - https://docs.python.org/2/library/socket.html
                - http://www.binarytides.com/python-socket-server-code-example/
                - http://www.binarytides.com/code-chat-application-server-client-sockets-python/
                - http://www.saltycrane.com/blog/2008/09/simplistic-python-thread-example/
                - https://pymotw.com/2/asyncore/index.html#module-asyncore
            
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
    #-- Sub Classes ---------------------------------------------------------------------------------------------------
    class _Client(Thread):
        """ X
        """
        #-- Constants ---------------------------------------------------------------------------------------------
        #[None]
        
        
        #-- Global Vars -------------------------------------------------------------------------------------------
        _id         = ""
        _addr       = ("0.0.0.0", 0)
        _socket     = None
        _handler    = None
        
        
        #-- Special Class Methods ---------------------------------------------------------------------------------
        def __init__(self, client_socket, client_id, client_handler, client_address):
            """ X
            """
            #-- Inherit Base Class
            Thread.__init__(self)
            
            #-- Initialise globals
            self._socket = client_socket
            self._id = client_id
            self._addr = client_address
            self._handler = client_handler
            
            #-- Start monitoring the socket
            self.start()
    
        
        #-- Properties --------------------------------------------------------------------------------------------
        @property
        def id(self):
            """ Returns the client's id string.
            """
            return self._id
        
        
        @property
        def addr(self):
            """ Returns a tuple containing the ip and port of the client.
            """
            return self._addr
        
        
        #@property
        #def id(self):
        #    """ Gets the port the server is listening on.
        #    """
        #    return self._id
        #@id.setter
        #def id(self, value):
        #    """ Sets the port the server is listening on.
        #    """
        
        
        #-- Private Methods ---------------------------------------------------------------------------------------
        #[None]
        
        
        #-- Public Methods ----------------------------------------------------------------------------------------
        def run(self):
            """ X
            """
        
        
        def send(self, data):
            """ X
            """
        
        
        def kill(self):
            """ X
            """
    
    
    #-- Constants -----------------------------------------------------------------------------------------------------
    DEFAULT     = { "buffer"    : 2**12,    #-- 4096: Advisable to keep it as an exponent of 2
                    "port"      : 61616,
                    "backlog"   : 5 }
    
    #TOKEN_STRING    = ["CONNECT", "READY", "MESSAGE", "DISCONNECT"]
    #CONNECT, READY, MESSAGE, DISCONNECT = range(len(TOKEN_STRING))
    
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    _clients = []
    _client_id = 0
    _server_data    = { "port"      : DEFAULT["port"],
                        "backlog"   : DEFAULT["backlog"],
                        "buffer"    : DEFAULT["buffer"]     }
    _server  = None
    _handler = None
    _running = False
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    def __init__(self, port=None, custom_handler=None):
        """ Initializes the object.
        """
        #-- Inherit Base Class
        Thread.__init__(self)
        
        #-- Daemonize the server thread in case the user doesn't invoke stop()
        self.daemon = True
        
        #-- Check if a valid custom port is supplied
        if (port is not None) and (type(port) is int) and (port > 0) and (port < 65536):
            self._server_data["port"] = port
        
        #-- Check if a valid custom event handler is supplied
        if custom_handler is not None:
            self.handler = custom_handler
    
    
    #-- Properties ----------------------------------------------------------------------------------------------------
    @property
    def port(self):
        """ Gets the port the server is listening on.
        """
        return self._server_data["port"]
    @port.setter
    def port(self, value):
        """ Sets the port the server is listening on.
        """
        if (not self._running) and (type(value) is int) and (value < 65536) and (value >= 0):
            self._server_data["port"] = value
    
        
    @property
    def handler(self):
        """ Returns the event handler.
        """
        return self._handler
    @handler.setter
    def handler(self, value):
        """ Sets the event handler.
        """
        if (value is not None) and hasattr(value, "__call__") and (self._handler is not value):
            self._handler = value
    
        
    @property
    def running(self):
        """ Returns True if the server is running.
        """
        return self._running
    
    
    #-- Private Methods -----------------------------------------------------------------------------------------------
    def start(self):
        """ X
        """
        print " > Server thread started."

        #-- Initialize the server socket
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print " > Socket created"
         
        #-- Bind socket to local host and port
        try:
            print " > Attempting to bind to port..."
            self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server.bind(("0.0.0.0", self._server_data["port"]))
            print ' > Bind successful.'
            self._running = True
            
            #-- Inherit
            Thread.start(self)
        
        except socket.error as msg:
            print " > Bind failed.\n    - Code:    {0}\n    - Message: {1}".format(str(msg[0]), msg[1])
            
            #-- Clean up mess
            self._server.close()
        
        
    def run(self):
        """ Thread runs this to keep server alert or terminate it.
        """
        #-- Start listening on socket
        self._server.listen(self._server_data["backlog"])
        print ' > Server now listening for active connections.'
        
        while self._running:
            (client_socket, address) = self._server.accept()
            self._clients.append(Server._Client(client_socket, self._client_id, None, tuple(address)))
        
        #_rx = [self._server]
        #while self._running:
        #    readable, writable, failed = select.select(_rx, [], [])
        #    for check in readable:
        #        if check is self._server:
        #            conn, addr = self._server.accept()
        #            _rx.append(conn)
        #            print '   - Connected with {0}:{1}'.format(addr[0], str(addr[1]))
        #            #start new thread for client.
        #            #start_new_thread(clientthread ,(conn,))
        #        else:
        #            data = check.recv(self._server_data["buffer"])
        #            check.send(" > Received {0} bytes of data.".format(len(data)))
        #            print " - Client: {0}".format(data)
        #    
        #    for check in writable:
        #        print check
        #    
        #    for check in failed:
        #        print check
        
        self._server.close()
        print " > Server stopped."
        print " > Server thread terminated."
    
    
    @staticmethod
    def _spit(text):
        """ Just prints a message to stdout.
        """
        print text
    
    
    #-- Public Methods ------------------------------------------------------------------------------------------------
    def send(self, data, client_id=None):
        """ X
        """
        return self, data, client_id
        
    
    def stop(self):
        """ Try to clean up all the threads. It shouldn't matter too much though as threads are daemonized.
        """
        if self.running:
            print " > Shutting down clients..."
            
            print " > Shutting down server..."
            self._server.shutdown(1)
            self._server.close()
            self._running = False
            print " > Server is now dead."
        
        self._Thread__stop(self) # pylint: disable=no-member



#===========================================================================================================[ DEBUG ]==
def debug():
    """ Test method. """
    #for f_cknugget in dir(socket):
    #for f_cknugget in dir(Thread):
    #    print f_cknugget
    #print type(Thread._Thread__stop)
    
    test = Server()
    test.start()
    try:
        time.sleep(25)
    except KeyboardInterrupt:
        print "\r > Seems we're terminating early!"
    test.stop()


#============================================================================================================[ MAIN ]==
if __name__ == "__main__":
    DEBUG_MODE = True
    debug()

