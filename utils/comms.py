'''
Class for inter-panel UDP communication

This based loosly on the Arduino-style of async
operations where you call a function each loop to check
if data is available.

1. Import and create instance
    import comms
    c = comms.Comms()

2. Begin the communications with the panel name
    c.begin("zoltar")

3. Listen for any data and pull out the tuple
    if c.available():
       # origin = original panel (e.g. "xy_chase", "color_match")
       # data = data sent from panel
       (origin, data) = c.recv()

4. Broadcast data to all panels
    c.send('RESET');
    c.send('COMPLETE');
'''

import socket
import collections

DEFAULT_PORT = 43822

class Comms:
    def __init__(self):
        pass

    def begin(self, name, port = DEFAULT_PORT):
        self.name = name
        self.port = port
        self.messages = collections.deque([])

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setblocking(0)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock.bind(('' , self.port))

    def send(self, data, port = 0):
        if not port:
            port = self.port

        message = (self.name + ':' + data).encode()
        self.sock.sendto(message, ('<broadcast>', port))
    
    def available(self):
        while True:
            origin = False
            message = ""

            try:
                (data, addr) = self.sock.recvfrom(1024)
                decoded = data.decode()
                ( origin, message ) = decoded.split(':', 1)
            except BlockingIOError:
                pass
            except ValueError:
                pass

            if origin == False:
                break

            self.messages.append( (origin, message) )

        return len(self.messages)

    
    def recv(self):
        try:
            return self.messages.popleft()
        except:
            return ("", "")
