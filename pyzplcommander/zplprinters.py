from __future__ import annotations
from abc import ABC
import socket

from pyzplcommander.zplcore import ZplCommandSender
from pyzplcommander.zplcommands import ZplCommands
from pyzplcommander.zpllabel import ZplLabel


class ZplPrinter(ZplCommandSender, ABC):

    def new_label(self) -> ZplLabel:
        return ZplLabel(self)


class ZplPromptFakePrinter(ZplPrinter):

    def send_commands(self, commands: list[ZplCommands | str | bytes], get_response: bool = False) -> list[str] | None:
        for command in commands:
            self.send_command(command)
        return None

    def send_command(self, command: ZplCommands | str | bytes, get_response: bool = False) -> None | str:
        print(command)
        return None


class ZplNetworkPrinter(ZplPrinter):

    printer_host: str
    printer_port: int

    connection: socket.socket
    default_timeout: float

    check_conn_on_send: bool
    auto_close_conn_on_send: bool

    def __init__(self, printer_host: str, printer_port: int = 9100, timeout: int = None):
        super().__init__()
        self.printer_host = printer_host
        self.printer_port = printer_port
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if timeout is None:
            self.default_timeout = -1
        else:
            self.default_timeout = timeout

        self.check_conn_on_send = True
        self.auto_close_conn_on_send = True

    @staticmethod
    def _return_command(command: ZplCommands | str | bytes):
        if isinstance(command, ZplCommands):
            command = command.value
        if isinstance(command, tuple):
            command = command[0]
        if isinstance(command, str):
            command = bytes(command, 'UTF-8')
        return command

    def connect(self) -> None:
        self.connection.connect((self.printer_host, self.printer_port))
        if self.default_timeout < 0:
            self.default_timeout = self.connection.timeout

    def disconnect(self) -> None:
        self.connection.close()

    def recv_all(self, timeout: float = 2, buffer_size: int = 1024) -> str:
        self.connection.settimeout(timeout)
        message = b''
        while True:
            try:
                buffer_msg = self.connection.recv(buffer_size)
                if not buffer_msg:
                    break
                message += buffer_msg
            except socket.timeout:
                break

        self.connection.settimeout(self.default_timeout)
        return message.decode('UTF-8')

    def _send_command(self, command: ZplCommands | str | bytes, get_response: bool = False) -> None | str:
        self.connection.settimeout(self.default_timeout)
        self.connection.sendall(self._return_command(command))
        if get_response:
            return self.recv_all()

    def send_command(self, command: ZplCommands | str | bytes, get_response: bool = False) -> None | str:
        if self.check_conn_on_send and not self.connected():
            self.connect()

        result_recv = self._send_command(command=command, get_response=get_response)

        if self.check_conn_on_send and self.auto_close_conn_on_send:
            self.disconnect()

        return result_recv

    def send_commands(self, commands: list[ZplCommands | str | bytes], get_response: bool = False) -> list[str] | None:
        if self.check_conn_on_send and not self.connected():
            self.connect()

        results = []
        for command in commands:
            result_recv = self._send_command(command=command, get_response=get_response)
            if get_response:
                results.append(result_recv)

        if self.check_conn_on_send and self.auto_close_conn_on_send:
            self.disconnect()

        if get_response:
            return results

    def connected(self) -> bool:
        try:
            self.connection.sendall(bytes(ZplCommands.FIELD_COMMENT.value.command + 'TESTE_CONNECTION', 'UTF-8'))
        except OSError:
            return False
