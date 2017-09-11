from io import BlockingIOError
import os
import struct
import sys
import traceback

import gevent
import gevent.event
import gevent.greenlet
from gevent.server import StreamServer
from gevent import socket
from gevent.socket import error as socket_error
from gevent.socket import timeout as socket_timeout


from tendrl.commons.logger import Logger
from tendrl.commons.message import Message
from tendrl.node_agent.alert import update_alert

MESSAGE_SOCK_PATH = "/var/run/tendrl/message.sock"
NOTICE_PRIORITY = "notice"


class MessageHandler(gevent.greenlet.Greenlet):
    def __init__(self):
        super(MessageHandler, self).__init__()
        self.server = StreamServer(
            self.bind_unix_listener(),
            self.read_socket
        )

    def read_socket(self, sock, *args):
        try:
            size = self._msg_length(sock)
            data = self._read(sock, size)
            frmt = "=%ds" % size
            msg = struct.unpack(frmt, data)
            message = Message.from_json(msg[0])
            # Logger is in commons so passing alert from here
            alert_conditions = [
                "alert_condition_status",
                "alert_condition_state",
                "alert_condition_unset"
            ]
            if message.priority == NOTICE_PRIORITY:
                alert = True
                for alert_condition in alert_conditions:
                    if not alert_condition in message.payload:
                        alert = False
                        break
                if alert:
                    update_alert(
                        message
                    )
            gevent.sleep(3)
            Logger(message)
        except (socket_error, socket_timeout):
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(
                exc_type, exc_value, exc_tb, file=sys.stderr)
        except (TypeError, ValueError, KeyError, AttributeError):
            sys.stderr.write(
                "Unable to log the message.%s\n" % data)
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(
                exc_type, exc_value, exc_tb, file=sys.stderr)

    def _read(self, sock, size):
        data = ''
        while len(data) < size:
            data_tmp = sock.recv(size - len(data))
            data += data_tmp
            if data_tmp == '':
                raise RuntimeError("Message socket connection broken")
        return data

    def _msg_length(self, sock):
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
        except Exception:
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb,
                                      file=sys.stderr)
