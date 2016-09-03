""" COMMUNICATE:  A TCP SERVER/CLIENT
    
    author: aceldama.v1.0 at gmail
    
    Licensed under the GNU General Public License Version 2 (GNU GPL v2), 
        available at: http://www.gnu.org/licenses/gpl-2.0.txt
    
    (C) 2016 David A Swanepoel
"""

#-- Import Dependencies
import socket, time, sys
from threading import Thread
from xifo import Queue


#====================================================================================================[ SERVER CLASS ]==
class Server(Thread):
    """ A very basic asynchronous TCP server.
        
            RESEARCH:
                - https://docs.python.org/2/library/socket.html
                - http://www.binarytides.com/python-socket-server-code-example/
                - http://www.binarytides.com/code-chat-application-server-client-sockets-python/
                - http://www.saltycrane.com/blog/2008/09/simplistic-python-thread-example/
                - https://pymotw.com/2/asyncore/index.html#module-asyncore
            
            EXPOSES:
                Constants:
                    DEFAULT['buffer']       : (int) Default buffer rx/tx size.
                    DEFAULT['port']         : (int) Default port the server runs on.
                    DEFAULT['backlog']      : (int) Default maximum number of pending connections.
                
                Methods:
                    start()                 : Starts the server and sets up socket.
                    send(data, [client_id]) : Sends data. If client_id was supplied, it will send the data only to that
                                              client, otherwise it broadcasts the data to all connected clients.
                    stop([finish_jobs])     : Stops the server and kills all connected clients. If finish_jobs was
                                              supplied, it will either wait until all client send queues are empty if 
                                              the value was True, or wait a maximum of N seconds if it was an integer.
                
                Properties:
                    (rw) [int] port         : Gets or sets the port the server will be listening on. If the server is 
                                              running, the port number becomes read-only.
                    (rw) [function] handler : The main async event handler function. Parameters that are passed are as
                                              follows: event(token, data)
                    (ro) [bool] running     : Returns True if the server is online and listening. False otherwise.
    """
    #-- Sub-Classes ---------------------------------------------------------------------------------------------------
    class _Client(Thread):
        """ A class to be used by the server to create and handle asynchronous client interactions.
                
                EXPOSES:
                    Constants:
                        BUFFER_SIZE             : (int) Inherited from Server.DEFAULT['buffer'].
                    
                    Methods:
                        send(data)              : Queues data to be sent to the client. The queue is handled by 
                                                  self._check_queue which is run in a thread.
                        kill([finish_jobs])     : Kills the socket. If finish_jobs was supplied, it will either 
                                                  wait until all client send queues are empty if the value was 
                                                  True, or wait a maximum of N seconds if it was an integer.
                    
                    Properties:
                        (ro) [str] id           : Returns the unique id supplied at initialization.
                        (ro) (str, int) addr    : Returns a tuple containing the ip and port of the client.
                        (ro) [bool] running     : Returns True if the client is still alive and running.
        """
        #-- Constants - -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        #[None]
        
        
        #-- Global Vars -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        _id         = ""
        _addr       = ("0.0.0.0", 0)
        _buffer     = None
        _socket     = None
        _handler    = None
        _running    = False
        _transmit   = None      #-- Thread monitoring queue
        _queue      = Queue()
        
        
        #-- Special Class Methods - -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        def __init__(self, client_socket, client_id, client_handler, client_address, client_buffer=4096):
            """ Starts up and manages the client socket as an individual thread.
                
                    SYNTAX:
                        x = _Client(client_socket, client_id, client_handler, client_address)
                        x = _Client(client_socket, client_id, client_handler, client_address, client_buffer)

                    VARIABLES:
                        client_socket:  [obj] The socket the client is connected to.
                        client_id:      [str] A unique identifier for the client.
                        client_handler: [function] Event handler. Passes event(id, token, data).
                        client_address: [tuple] The client ip and port.
                        client_buffer:  [int] Optional. Sets the maximum read/write buffer size of the client. (bytes)
            """
            #-- Inherit from Base Class
            Thread.__init__(self)
            
            #-- Initialise globals and properties
            self._socket = client_socket
            self._id = client_id
            self._addr = client_address
            self._handler = client_handler
            self.buffer_size = client_buffer
            
            #-- Start monitoring the socket
            self.start()
            self._event("CONNECT", "")
    
        
        #-- Properties --- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
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
        
        
        @property
        def buffer_size(self):
            """ Returns the maximum buffer size of the client.
            """
            return self._buffer
        @buffer_size.setter
        def buffer_size(self, value):
            """ Sets the maximum buffer size of the client.
            """
            if (type(value) is int) and (value > 0) and (value != self._buffer):
                self._buffer = value
        
        
        @property
        def running(self):
            """ Returns True if the client is alive (running).
            """
            return self._running
        
        
        #-- Private Methods - -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        def _event(self, token, data):
            """ Raises an event or if no event handler was set it prints to stdout.
            """
            if self._handler is None:
                print "  - ID({3})::{0}({2})> {1}".format(token.upper(), data.strip(), len(data), self._id)
            else:
                self._handler(self.id, token.upper(), data)
        
        
        def _check_queue(self):
            """ Checks if there's any data in the queue to be transmitted to the socket.
            """
            while self._running:
                if len(self._queue):
                    #-- Transmit the dtata that's waiting to be sent.
                    _tx = self._queue.pop()
                    self._event("TX", _tx)
                    self._socket.send(_tx)
                else:
                    #-- For efficiency, just check 4 times a second.
                    time.sleep(0.25)
        
        
        def run(self):
            """ Waits for data from the socket and raises an event if it arrives.
            """
            if not self._running:
                #-- Start client automation.
                self._running = True
            
                #-- Start the transmitter
                self._transmit = Thread(target=self._check_queue)
                self._transmit.daemon = True
                self._transmit.start()
                
                #-- Start the receiver
                while self._running:
                    #-- Wait for data from client.
                    data = self._socket.recv(self.buffer_size)
                    if data:
                        #-- Trigger event handler.
                        self._event("RX", data)
                    else:
                        #-- Socket closed.
                        self.kill()
            else:
                #-- Client already running. Do nothing.
                pass
        
        
        #-- Public Methods -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
        def send(self, data):
            """ Queues data to be sent to the client. If the data to be sent is too big, it breaks it up into chunks 
                and queues them as separate transmissions.
            """
            idx = 0
            while (idx < len(data)) and self._running:
                #-- Queue the data chunk(s) for transmission.
                self._queue.push(data[idx : min(len(data) - idx, self.buffer_size)])
                idx += self.buffer_size
        
        
        def kill(self, finish_jobs=False):
            """ Ends the thread and kills the socket. If finish_jobs is set to True, kill will
                wait until all jobs are finished regardless of how long it takes. If it is an 
                integer, it will give the thread up to the amount of seconds specified.
            """
            #-- Send the terminate signal
            self._running = False
            
            #-- Stop the queue manager thread
            timeout = 2.0
            self._event("INFO", "Giving {:.2f} seconds for client queue manager to terminate...".format(timeout))
            self._transmit.join(timeout)
            if self._transmit.isAlive():
                self._event("WARN", "Queue manager thread appears to be immortal. I don't know why...")
            else:
                self._event("INFO", "The queue manager is no more.")
            
            #-- Attempt to finish sending up any unsent data (if any)
            if len(self._queue) and finish_jobs:
                #-- Give the queue some time to get empty.
                self._event("INFO", "Waiting for client to catch up. ({0} tasks)".format(len(self._queue)))
                tfj = type(finish_jobs)
                now = time.time
                tstart = now()
                while len(self._queue) and ((tfj is bool) or ((tfj is int) and ((now() - tstart) > finish_jobs))):
                    #-- Just wait a bit...
                    time.sleep(0.2)
                
                if self._queue.empty:
                    self._event("INFO", "All tasks caught up successfully.")
                
            if len(self._queue):
                #-- Let the user know about aborted tasks.
                self._event("WARN", "Aborted {0} pending tasks.".format(len(self._queue)))
            
            #-- All done
            self._socket.close()
            self._event("INFO", "Connection Terminated.")
    
    
    #-- Constants -----------------------------------------------------------------------------------------------------
    DEFAULT     = { "buffer"    : 2**12,    #-- 4096: Advisable to keep it as an exponent of 2
                    "port"      : 61616,
                    "backlog"   : 5         }
    
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    _clients = []
    _client_id = 1
    _server_data    = { "port"      : DEFAULT["port"],
                        "backlog"   : DEFAULT["backlog"],
                        "buffer"    : DEFAULT["buffer"]     }
    _server  = None
    _handler = None
    _running = False
    
    _monitor = None
    _last_gc = 0
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    def __init__(self, port=None, custom_handler=None):
        """ Initializes the object.
            
                SYNTAX:
                    x = Server()
                    x = Server([port])
                    x = Server([port, [custom_handler]])
                    x = Server(custom_handler=function)
                    
                VARIABLES:
                    port:           [int] The port the server will be listening on.
                    custom_handler: [function] Event handler. Passes event(token, id, data). In the case of the server
                                    calling the handler, the id is 0. Client ids are always 1 or greater.
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
        
        #-- Start up the garbage collector
        self._monitor = Thread(target=self._monitor_clients)
        self._monitor.daemon = True
    
    
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
    def _event(self, sender_id, token, data):
        """ Calls the custom event handler or dumps it to stdout.
        """
        if self._handler is None:
            if sender_id is 0:
                #-- It's the server
                print " [ {0} ] > {1}".format(token.upper(), data.strip())
            else:
                #-- It's a client
                print "  - ID({3})::{0}({2})> {1}".format(token.upper(), data.strip(), len(data), sender_id)
        else:
            self._handler(token.upper(), sender_id, data)
    
    
    def _monitor_clients(self):
        """ Thread that monitors for disconnected clients and cleans them up accordingly.
        """
        while self._running:
            #-- Find all dead clients
            lst_pop = []
            for i in range(len(self._clients)):
                if not self._clients[i].running:
                    lst_pop.append(i)
            
            #-- Remove them
            while len(lst_pop):
                self._event(0, "INFO", "GC Disposed of client. (ID:{0})".format(self._clients.pop(lst_pop.pop()).id))
            
            #-- Wait a few seconds before scanning again
            self._last_gc = time.time()
            while (time.time() - self._last_gc) < 5:
                time.sleep(0.1)
    
    
    def _reset(self):
        """ Resets the global variables responsible for client tracking etc.
        """
        if self._running():
            #-- Stop first
            self.stop()
        
        #-- Reset globals
        self._clients   = []
        self._client_id = 1
        
    
    
    def run(self):
        """ Thread runs this to keep server alert or terminate it.
        """
        self._event(0, "INFO", "Server thread started.")

        #-- Initialize the server socket
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._event(0, "INFO", "Socket created.")
         
        #-- Bind socket to local host and port
        try:
            self._event(0, "INFO", "Attempting to bind to port...")
            self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server.bind(("0.0.0.0", self._server_data["port"]))
            self._event(0, "INFO", "Bind successful.")
            self._running = True
            
            #-- Start garbage collector
            self._monitor.start()
            
            #-- Start listening on socket
            self._server.listen(self._server_data["backlog"])
            self._event(0, "STATUS", "Online and listening for new connections.")
            
            #-- Handle incoming connections
            while self._running:
                (client_socket, address) = self._server.accept()
                self._clients.append(Server._Client(client_socket, self._client_id, self._event, 
                                                    tuple(address), self.DEFAULT['buffer']))
                self._client_id += 1
            
            self._server.close()
            self._event(0, "INFO", "Server thread terminated.")
            self._event(0, "STATUS", "Server stopped.")
        
        except socket.error as msg:
            self._event(0, "ERROR", "Bind failed. Code [{0}]: {1}".format(msg[0], msg[1]))
            
            #-- Clean up mess
            self._server.close()

    
    def _force_gc(self, last=15.0):
        """ Forces a garbage collection.
        """
        if (len(self._clients) > 0) and ((time.time() - self._last_gc) > last):
            self._event(0, "INFO" ,"Forcing garbage collection.")
            self._last_gc = 0
            while self._last_gc == 0:
                time.sleep(0.1)
            self._event(0, "INFO" ,"Garbage collection done.")
    
    
    #-- Public Methods ------------------------------------------------------------------------------------------------
    def send(self, data, client_id=None):
        """ Sends data to a specific client if a client id is supplied. Otherwise broadcasts data to all clients.
        """
        flag = 0
        self._force_gc()
        if len(self._clients) == 0:
            self._event(0, "WARN", "No connected clients to receive data.")
        else:
            for cli in self._clients:
                if (client_id is None) or (cli.id == client_id):
                    flag += 1
                    cli.send(data)
            
            if flag > 0:
                self._event(0, "INFO", "Data sent to {0} clients.".format(flag))
            else:
                self._event(0, "WARN", "Client not found. Data not sent. (ID:{0})".format(client_id))
        
        return flag > 0
        
    
    def stop(self):
        """ Try to clean up all the threads. It shouldn't matter too much though as threads are daemonized.
        """
        if self.running:
            self._event(0, "INFO", "Shutting down clients...")
            for cli in self._clients:
                cli.kill()

            self._event(0, "INFO", "Shutting down server...")
            self._server.shutdown(1)
            self._server.close()
            self._running = False

        self._event(0, "STATUS", "Offline")
        self._Thread__stop() # pylint: disable=no-member



#====================================================================================================[ CLIENT CLASS ]==
class Client(Thread):
    """ A very basic asynchronous TCP client.
        
            RESEARCH:
                - https://en.wikipedia.org/wiki/Hostname
            
            EXPOSES:
                Constants:
                    DEFAULT['buffer']       : (int) Default buffer rx/tx size.
                    DEFAULT['port']         : (int) Default port the server runs on.
                    DEFAULT['backlog']      : (int) Default maximum number of pending connections.
                
                Methods:
                    start()                 : Starts the server and sets up socket.
                    send(data, [client_id]) : Sends data. If client_id was supplied, it will send the data only to that
                                              client, otherwise it broadcasts the data to all connected clients.
                    stop([finish_jobs])     : Stops the server and kills all connected clients. If finish_jobs was
                                              supplied, it will either wait until all client send queues are empty if 
                                              the value was True, or wait a maximum of N seconds if it was an integer.
                
                Properties:
                    (rw) [int] port         : Gets or sets the port the server will be listening on. If the server is 
                                              running, the port number becomes read-only.
                    (rw) [function] handler : The main async event handler function. Parameters that are passed are as
                                              follows: event(token, data)
                    (ro) [bool] running     : Returns True if the server is online and listening. False otherwise.
    """
    
    #-- Constants -----------------------------------------------------------------------------------------------------
    #[None]
    
    
    #-- Global Vars ---------------------------------------------------------------------------------------------------
    _server     = { 'addr'  : None,
                    'port'  : None }
    _handler    = None
    _running    = False
    
    
    #-- Special Class Methods -----------------------------------------------------------------------------------------
    def __init__(self, server_name, server_port=None, custom_handler=None):
        """ Initializes the object.
            
                SYNTAX:
                    x = Client("127.0.0.1")
                    x = Client("server.example.com", 51617)
                    x = Client("127.0.0.1", 51617, custom_handler)
                    x = Client("127.0.0.1", custom_handler=handler_function)
                    
                VARIABLES:
                    server_name:    [str] The IP or FQDN of the server.
                    server_port:    [int] The port the remote server is listening on.
                    custom_handler: [function] Event handler. Passes event(token, data).
        """
        #-- Inherit Base Class
        Thread.__init__(self)
        
        #-- Set up the local vars
        self._server_name   = server_name
        self._server_name   = server_port
        self._event_handler = custom_handler
    
    
    #-- Properties ----------------------------------------------------------------------------------------------------
    @property
    def _server_addr(self):
        """ Returns the server's ip or domain name.
        """
        return self._server['addr']
    @_server_addr.setter
    def _server_addr(self, value):
        """ Sets the server's ip or domain name if the client isn't running.
        """
        if (not self._running) and (type(value) is str):
            #-- Preliminary clean
            temp = value.strip()
            
            #-- Start validation
            if (temp != self._server['addr']) and (len(temp) > 0) and (len(temp) < 255):
                #-- Check for IPv4
                try:
                    socket.inet_aton(temp)
                    flag = False
                
                except socket.error:
                    try:
                        #-- Check for IPv6
                        socket.inet_pton(temp)
                        flag = False
                        
                    except socket.error:
                        #-- Check for FQDN
                        flag = (temp[-2:] == "..")                          #-- FQDNs cannot end in ".."
                        for x in temp.split("."):
                            #-- Stop the loop if a violation was found.
                            if flag: 
                                break
                            
                            #-- Check that each domain label:
                            flag = flag or (len(x) == 0) and (len(x) > 63)  #-- Is 1-63 chars long
                            flag = flag or ("-" not in [temp[0], temp[-1]]) #-- Cannot start or end with "-"
                            
                            y = 0                                           #-- Doesn't contain invalid chars.
                            while not (flag or (y >= len(x))):
                                flag = temp[y].upper() not in "0123456789-ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                                y += 1
                            
                finally:
                    #-- If the flag was flipped again (ie. False), it appears to be a valid IPv1, IPv6 or fqdn.
                    if not flag:
                        self._server['addr'] = temp
    
    
    @property
    def _server_port(self):
        """ Returns the server's remote port.
        """
        return self._server['port']
    @_server_port.setter
    def _server_port(self, value):
        """ Sets the server's remote port if the client isn't running.
        """
        if (not self._running) and (type(value) is int) and (value != self._server['port']):
            if (value > 0) or (value <= 65535):
                self._server['port'] = value
    
    
    @property
    def _event_handler(self):
        """ Returns the client event handler.
        """
    @_event_handler.setter
    def _event_handler(self, value):
        """ Sets the client event handler.
        """
    
    
    #-- Private Methods -----------------------------------------------------------------------------------------------
    def _set_server(self, server_name, server_port, custom_handler):
        """ Sets the initialization server variables.
        """
        #-- Assertions
        assert type(server_name) is str, "Server name needs to be a string."
        assert len(server_name.trim()) > 1, "Server name needs cannot be a zero length string."
        
        #-- Init
        self._server_name = server_name
        self._server_port = server_port
        self._handler = custom_handler
    
    
    #-- Public Methods ------------------------------------------------------------------------------------------------
    #[None]


#===========================================================================================================[ DEBUG ]==
def debug():
    """ Test method.
    """
    # SAUSAGEFEST: aircrack-ng -w - ../../crack/lab-password.cap | grep -o -P "(FOUND! \[ .* \]|not in dict)"
    test = None
    try:
        test_server = "--SERVER" in [i.upper() for i in sys.argv]
        print "[ Starting a {} ]".format("server" if test_server else "client")
        if (len(sys.argv) == 2) and test_server:
            #-- Start a server
            test = Server()
            test.start()
            time.sleep(8)
            for i in range(12):
                test.send(["ah\n", "stayin' alive\n"][int((i % 6) / 4.0)])
                time.sleep(0.6 + 0.5 * int((i % 6) / 4.0))
        else:
            #-- Start a client (or clients)
            test = Client("127.0.0.1")
            test.start()
            time.sleep(8)
        
    except KeyboardInterrupt:
        print "\r > Seems we're terminating early!"
        
    finally:
        test.stop()
    


#============================================================================================================[ MAIN ]==
if __name__ == "__main__":
    DEBUG_MODE = True
    debug()

