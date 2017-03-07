import gevent.event
import gevent.greenlet
from gevent.server import StreamServer
from gevent import socket
from gevent.socket import error as socket_error
from gevent.socket import timeout as socket_timeout
from io import BlockingIOError
import os
import sys
from tendrl.commons.message import Message
from tendrl.node_agent.message.logger import Logger
import traceback

RECEIVE_DATA_SIZE = 4096


class MessageHandler(gevent.greenlet.Greenlet):
    def __init__(self):
        super(MessageHandler, self).__init__()
        self.server = StreamServer(
            self.bind_unix_listener(),
            self.read_socket
        )

    def read_socket(self, sock, address):
        try:
            self.data = sock.recv(RECEIVE_DATA_SIZE)
            message = Message.from_json(self.data)
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

    def _run(self):
        try:
            self.server.serve_forever()
        except (TypeError, BlockingIOError, socket_error, ValueError):
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(
                exc_type, exc_value, exc_tb, file=sys.stderr)

    def stop(self):
        socket_path = tendrl_ns.config.data['logging_socket_path']
        self.sock.close()
        if os.path.exists(socket_path):
            os.remove(socket_path)
        self.server.close()

    def bind_unix_listener(self):
        socket_path = tendrl_ns.config.data['logging_socket_path']
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            if os.path.exists(socket_path):
                os.remove(socket_path)
            self.sock.setblocking(0)
            self.sock.bind(socket_path)
            self.sock.listen(50)
        except (TypeError, BlockingIOError, socket_error, ValueError):
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(
                exc_type, exc_value, exc_tb, file=sys.stderr)
        return self.sock
