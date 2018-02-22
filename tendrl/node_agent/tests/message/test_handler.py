from mock import MagicMock
from mock import patch
import os
import pytest
import socket
import struct

from tendrl.commons.message import Message
from tendrl.node_agent.message import handler


class Socket(object):
    def __init__(self, addr=None, port=None):
        pass

    def bind(self, path):
        return True

    def listen(self, intervel):
        return True

    def accept(self):
        return self, None

    def close(self):
        return True

    def recv(self, value):
        return "testing"


def fail_fromfd(obj, value):
    raise ValueError


def fail_socket(obj, value):
    raise ValueError


def read_socket(obj, conn):
    obj._complete.set()


@patch.object(os.path, "exists")
@patch.object(os, "remove")
def test_run(remove, exists):
    remove.return_value = True
    exists.return_value = True
    with patch.object(socket, "fromfd", fail_fromfd):
        with patch.object(socket, "socket", fail_socket):
            with pytest.raises(ValueError):
                handler.MessageHandler().run()
    with patch.object(socket, "fromfd", fail_fromfd):
        with patch.object(socket, "socket", Socket):
            with patch.object(
                    handler.MessageHandler, "read_socket", read_socket):
                handler.MessageHandler().run()


@patch.object(struct, "unpack")
@patch.object(Message, "from_json")
def test_read_socket(from_json, unpack):
    unpack.return_value = [1]
    from_json.return_value = Message(
        "notice",
        "testing",
        {"alert_condition_status": None,
         "alert_condition_state": None,
         "alert_condition_unset": None
         },
        caller={},
        node_id=123
    )
    handler.Logger = MagicMock()
    handler.update_alert = MagicMock()
    handler.MessageHandler().read_socket(Socket())
    unpack.return_value = [{}]
    with pytest.raises(UnboundLocalError):
        handler.MessageHandler().read_socket(Socket())
