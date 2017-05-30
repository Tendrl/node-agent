import os
from io import BlockingIOError
import sys
import struct
import traceback

import gevent
import gevent.event
import gevent.greenlet
from gevent.server import StreamServer
from gevent import socket
from gevent.socket import error as socket_error
from gevent.socket import timeout as socket_timeout


from tendrl.commons.message import Message
from tendrl.commons.logger import Logger


MESSAGE_SOCK_PATH = "/var/run/tendrl/message.sock"


class MessageHandler(gevent.greenlet.Greenlet):
    def __init__(self):
        super(MessageHandler, self).__init__()
        self.server = StreamServer(
            self.bind_unix_listener(),
            self.read_socket
        )

    def read_socket(self, sock, *args):
        try:
            size = self._msgLength(sock)
            data = self._read(sock, size)
            frmt = "=%ds" % size
            msg = struct.unpack(frmt, data)
            message = Message.from_json(msg[0])
            gevent.sleep(3)
            Logger(message)
        except (socket_error, socket_timeout):
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(
                exc_type, exc_value, exc_tb, file=sys.stderr)
        except (TypeError, ValueError, KeyError, AttributeError):
            sys.stderr.write(
                "Unable to log the message.%s\n" % self.data)
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(
                exc_type, exc_value, exc_tb, file=sys.stderr)
            
    def _read(self, sock, size):
        data = ''
        while len(data) < size:
            dataTmp = sock.recv(size-len(data))
            data += dataTmp
            if dataTmp == '':
                raise RuntimeError("Message socket connection broken")
        return data
    
    def _msgLength(self, sock):
        d = self._read(sock, 4)
        s = struct.unpack('=I', d)
        return s[0]
    
    def _run(self):
        try:
            self.server.serve_forever()
        except (TypeError, BlockingIOError, socket_error, ValueError):
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(
                exc_type, exc_value, exc_tb, file=sys.stderr)

    def stop(self):
        pass

    def bind_unix_listener(self):
        # http://0pointer.de/blog/projects/systemd.html (search "file
        # descriptor 3")
        try:
            socket_fd = 3
            self.sock = socket.fromfd(socket_fd, socket.AF_UNIX,
                                      socket.SOCK_STREAM)
            self.sock.setblocking(0)
            self.sock.listen(50)
            return self.sock
        except (TypeError, BlockingIOError, socket_error, ValueError):
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb,
                                      file=sys.stderr)
            pass
        try:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            if os.path.exists(MESSAGE_SOCK_PATH):
                os.remove(MESSAGE_SOCK_PATH)
            self.sock.setblocking(0)
            self.sock.bind(MESSAGE_SOCK_PATH)
            self.sock.listen(50)
            return self.sock
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb,
                                  file=sys.stderr)        
