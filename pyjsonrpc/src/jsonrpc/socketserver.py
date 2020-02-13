# Copyright (c) 2008, Michael Lunnay <mlunnay@gmail.com.au>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import SocketServer
import socket
import logging

__all__ = ['TCPServiceServer', 'ThreadedTCPServiceServer', 'ServiceRequestHandler']

RECVSIZE = 1024

class ServiceRequestHandler(object):
    def __init__(self, serviceHandler):
        self.serviceHandler = serviceHandler
        
    def __call__(self, *args, **kwargs):
        handler = self.serviceHandler
        class StreamRequestHandler (SocketServer.BaseRequestHandler):
            def handle(self):
                log = logging.getLogger('service')
                log.info('recieved request from %s' % self.client_address[0])
                json = ''
                try:
                    while 1:
                        recv = self.request.recv(RECVSIZE)
                        json += recv
                        if len(recv) != RECVSIZE:
                            break
                        
                    log.debug('request: %s' % json)
                    ret = handler.handleRequest(json)
    
                    if ret != None:
                        log.debug('returning: %s' % ret)
                        self.request.send(ret)
                except socket.error, msg:
                    log.debug('connection reset by %s' % self.client_address[0])
                    return
        
        return StreamRequestHandler(*args, **kwargs)

class TCPServiceServer(SocketServer.TCPServer):
    def __init__(self, server_address, serviceHandler):
        SocketServer.TCPServer.__init__(self, server_address, ServiceRequestHandler(serviceHandler))
        
class ThreadedTCPServiceServer(SocketServer.ThreadingMixIn, TCPServiceServer): pass

if __name__ == '__main__':
    import socket
    import threading
    import base
    import logging

    handler = logging.FileHandler('../socketserver.log')
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    log = logging.getLogger('service')
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

#    address = ('localhost', 0) # let the kernel give us a port
    address = ('', 50042)
    server = TCPServiceServer(address, base.ServiceHandler('SocketServerTest'))
    ip, port = server.server_address # find out what port we were given

    t = threading.Thread(target=server.serve_forever)
    t.setDaemon(True) # don't hang on exit
    t.start()
    print 'Server loop running in thread:', t.getName(), 'on port:', port

    import time
    import sys
    try:
        while 1:
            time.sleep(1.0)
    except KeyboardInterrupt, e:
        server.socket.close()
        sys.exit(0)
        

    # Connect to the server
#    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#    s.connect((ip, port))
#
#    # Send the data
#    message = '{"jsonrpc": "2.0", "method": "system.echo", "params": ["test", 2.2, true], "id": 234}'
#    print 'Sending : "%s"' % message
#    len_sent = s.send(message)
#
#    # Receive a response
#    response = s.recv(1024)
#    print 'Received: "%s"' % response
#
#    # Clean up
#    s.close()
#    server.socket.close()

