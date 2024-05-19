from __future__ import annotations
from abc import ABC
import socket

from pyzplcommander.core import ZplCommandSender
from pyzplcommander.commands import ZplCommands
from pyzplcommander.label import ZplLabel


class ZplPrinter(ZplCommandSender, ABC):
    """Classe base para impressoras ZPL."""

    def new_label(self) -> ZplLabel:
        """Inicia a criação de uma nova etiqueta.

        Returns:
            ZplLabel: Objeto de etiqueta ZPL.
        """
        return ZplLabel(self)


class ZplPromptFakePrinter(ZplPrinter):
    """Classe de impressora falsa para testes de prompt de comando."""

    def send_command(self, command: str, get_response: bool = False) -> None | str:
        print(str(command))
        return None


class ZplNetworkPrinter(ZplPrinter):
    """Classe de impressora conectada via rede.

    A impressora deve estar configurada para receber comandos ZPL via TCP/IP.

    Args:
        printer_host (str): Endereço IP ou nome de domínio da impressora.
        printer_port (int): Porta de comunicação da impressora (default: 9100).
        timeout (int): Tempo limite de espera para resposta da impressora (default: None).
    """

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

    def connect(self) -> None:
        """Conecta-se à impressora."""
        self.connection.connect((self.printer_host, self.printer_port))
        if self.default_timeout < 0:
            self.default_timeout = self.connection.timeout

    def disconnect(self) -> None:
        """Desconecta-se da impressora."""
        self.connection.close()

    def recv_all(self, timeout: float = 2, buffer_size: int = 1024) -> str:
        """Recebe a resposta da impressora.

        Args:
            timeout (float): Tempo limite de espera para resposta da impressora (default: 2).
            buffer_size (int): Tamanho do buffer de leitura (default: 1024).

        Returns:
            str: Resposta da impressora.
        """
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

    def _send_command(self, command: str, get_response: bool = False) -> None | str:
        """Envia um comando para a impressora.

        Args:
            command (str): Comando ZPL a ser enviado.
            get_response (bool): Indica se deve-se esperar uma resposta da impressora (default: False).

        Returns:
            None | str: Resposta da impressora, se get_response=True.
        """
        self.connection.settimeout(self.default_timeout)
        self.connection.sendall(bytes(str(command), 'UTF-8'))
        if get_response:
            return self.recv_all()

    def send_command(self, command: str, get_response: bool = False) -> None | str:
        """Envia um comando para a impressora.

        Args:
            command (str): Comando ZPL a ser enviado.
            get_response (bool): Indica se deve-se esperar uma resposta da impressora (default: False).

        Returns:
            None | str: Resposta da impressora, se get_response=True.
        """
        if self.check_conn_on_send and not self.connected():
            self.connect()

        result_recv = self._send_command(command=command, get_response=get_response)

        if self.check_conn_on_send and self.auto_close_conn_on_send:
            self.disconnect()

        return result_recv

    def send_commands(self, commands: list[str], get_response: bool = False) -> list[str] | None:
        """Envia uma lista de comandos para a impressora.

        Args:
            commands (list[str]): Lista de comandos ZPL a serem enviados.
            get_response (bool): Indica se deve-se esperar uma resposta da impressora (default: False).

        Returns:
            list[str] | None: Lista de respostas da impressora, se get_response=True.
        """
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
        """Verifica se a impressora está conectada.

        Returns:
            bool: True se conectado, False caso contrário.
        """
        try:
            self.connection.sendall(bytes(str(ZplCommands.FIELD_COMMENT) + 'TESTE_CONNECTION', 'UTF-8'))
        except OSError:
            return False
