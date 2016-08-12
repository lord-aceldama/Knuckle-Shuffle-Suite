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
    DEFAULT_BUFFER  = 2**12         #-- 4096: Advisable to keep it as an exponent of 2
    DEFAULT_PORT    = 61616
    DEFAULT_BACKLOG = 5
    
    TOKEN_STRING    = ["CONNECT", "READY", "MESSAGE", "DISCONNECT"]
    CONNECT, READY, MESSAGE, DISCONNECT = range(len(TOKEN_STRING))
    
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    _server_data    = { "port"      : DEFAULT_PORT,
                        "backlog"   : DEFAULT_BACKLOG,
                        "buffer"    : DEFAULT_BUFFER }
    _server_thread = None
    _callback = None
    _running = False
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    def __init__(self, port=None, callback=None):
        """ Initializes the object.
        """
        #-- Check if a valid port is supplied
        if (port is not None) and (type(port) is int) and (port > 0) and (port < 65536):
            self._server_data["port"] = port
        
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
    def _run_server(self):
        """ Thread runs this to keep server alert or terminate it.
        """
        #-- Initialize the server socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print " > Socket created"
         
        #-- Bind socket to local host and port
        try:
            server.bind(("0.0.0.0", self._server_data["port"]))
            print ' > Socket bind complete'
        except socket.error as msg:
            print ' > Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            flag = False
         
        if flag:
            #-- Start listening on socket
            server.listen(self._server_data["backlog"])
            print ' > Server now listening for active connections.'
            
            self._running = True
            while self._running:
                conn, addr = server.accept()
                print '   - Connected with ' + addr[0] + ':' + str(addr[1])
                 
                #start new thread for client.
                #start_new_thread(clientthread ,(conn,))
                
                #self._thread = Thread(target=self._run, args=(self,))
                #print " > Thread started."
                time.sleep(50.0/1000.0) #-- 50ms
            
        
        print " > Server stopped."
        self._server.close()
    
        
    #def _broadcast(self, message):
    #    """ Sends a message to all connected clients.
    #    """
    #    for socket in self._client:
    #        if socket != server_socket and socket != sock :
    #            try :
    #                socket.send(message)
    #            except :
    #                # broken socket connection may be, chat client pressed ctrl+c for example
    #                socket.close()
    #                CONNECTION_LIST.remove(socket)    
    
    
    @staticmethod
    def _spit(text):
        """ Just prints a message to stdout.
        """
        print text
    
    
    #-- Public Methods ------------------------------------------------------------------------------------------------
    def start(self):
        """ Starts the server
        """
        flag = True
    
    
    def stop(self):
        """ Simply stops the server.
        """
        if self._running:
            print " > Terminating thread..."
            self._running = False
    
    
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
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)
 
    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)
 
    print "Chat server started on port " + str(PORT)
 
    try:
        while 1:
            #-- Get the list sockets which are ready to be read through select
            read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, [], [])
            for sock in read_sockets:
                #-- New connection
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
    
    except KeyboardInterrupt:
        print "\n\nUser had enough. Exiting..."
    
    server_socket.close()


#============================================================================================================[ MAIN ]==
if __name__ == "__main__":
    DEBUG_MODE = True
    debug()

