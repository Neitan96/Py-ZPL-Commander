from __future__ import annotations
from typing import Literal

import os
import re
from abc import ABC
import socket

from pyzplcommander.core import ZplCommandSender
from pyzplcommander.commands import ZplCommands
from pyzplcommander.label import ZplLabel


class ZebraPrinter(ZplCommandSender, ABC):
    """Classe base para impressoras ZPL."""

    def new_label(self) -> ZplLabel:
        """Inicia a criação de uma nova etiqueta.

        Returns:
            ZplLabel: Objeto de etiqueta ZPL.
        """
        return ZplLabel(self)

    def host_status(self) -> str:
        """Verifica o status da impressora.

        Returns:
            str: Status da impressora.
        """
        return self.send_command(ZplCommands.HOST_STATUS(), get_response=True)

    @staticmethod
    def _parse_host_status(status: str) -> dict:
        """Converte a resposta do status da impressora em um dicionário.

        Args:
            status (str): Resposta do status da impressora.

        Returns:
            dict: Status da impressora.
        """

        status_reg = re.compile(
            '\x02'
            r'(?P<interface>\d+),(?P<paper_out>\d+),(?P<pause>\d+),(?P<label_length>\d+),'
            r'(?P<number_of_formats_recv_buf>\d+),(?P<buffer_full>\d+),(?P<comm_diag_mode>\d+),'
            r'(?P<partial_format>\d+),\d+,(?P<corrupt_ram>\d+),(?P<under_temp>\d+),(?P<over_temp>\d+)'
            '\x03\r\n\x02'
            r'(?P<func_settings>\d+),\d+,(?P<head_up>\d+),(?P<ribbon_out>\d+),(?P<thermoal_transfer>\d+),'
            r'(?P<print_mode>\d+),(?P<print_width_mode>\d+),(?P<label_waiting>\d+),(?P<labels_remaining>\d+),'
            r'(?P<format_while_printing>\d+),(?P<graphics_stored_in_mem>\d+)'
            '\x03\r\n\x02'
            r'(?P<password>\w+),(?P<static_ram>\d+)\x03'
        )
        status_match = status_reg.match(status.strip())
        if status_match is None:
            raise ValueError('Host status response is invalid.')

        status_dict: dict[str, str | int | dict] = status_match.groupdict()
        status_dict = {key: int(value) for key, value in status_dict.items()}

        bauds_dict = {
            '0000': 110, '0001': 300, '0010': 600, '0011': 1200, '0100': 2400, '0101': 4800,
            '0110': 9600, '0111': 19200, '1000': 28800, '1001': 38400, '1010': 57600, '1011': 14400
        }

        interface = status_dict['interface']
        interface: str = format(interface, '09b')
        status_dict['interface'] = {
            'handshake': 'Xon/Xoff' if interface[1] == '0' else 'DTR',
            'parity': 'Odd' if interface[2] == '0' else 'Even',
            'status': 'Disabled' if interface[3] == '0' else 'Enabled',
            'stop_bits': '2 bits' if interface[4] == '0' else '1 bit',
            'data_bits': '7 bits' if interface[5] == '0' else '8 bits',
            'baud': bauds_dict[interface[0]+interface[6:9]]
        }

        status_dict['paper_out'] = 'Out' if status_dict['paper_out'] == 1 else 'In'
        status_dict['pause'] = 'Pause' if status_dict['pause'] == 1 else 'Resume'
        status_dict['buffer_full'] = 'Full' if status_dict['buffer_full'] == 1 else 'Not Full'
        status_dict['comm_diag_mode'] = 'On' if status_dict['comm_diag_mode'] == 1 else 'Off'
        status_dict['partial_format'] = 'Partial' if status_dict['partial_format'] == 1 else 'Full'
        status_dict['corrupt_ram'] = 'Data lost' if status_dict['corrupt_ram'] == 1 else 'Not Corrupt'
        status_dict['under_temp'] = 'Under Temp' if status_dict['under_temp'] == 1 else 'Normal Temp'
        status_dict['over_temp'] = 'Over Temp' if status_dict['over_temp'] == 1 else 'Normal Temp'

        func_settings = format(status_dict['func_settings'], '08b')
        status_dict['func_settings'] = {
            'media_type': 'Die-Cut' if func_settings[0] == '0' else 'Continuous',
            'sensor_profile': 'Off' if func_settings[1] == '0' else 'On',
            'communications_diagnostics': 'Off' if func_settings[2] == '0' else 'On',
            'print_mode': 'Direct Thermal' if func_settings[3] == '0' else 'Thermal Transfer',
        }

        status_dict['head_up'] = 'Up' if status_dict['head_up'] == 1 else 'Down'
        status_dict['ribbon_out'] = 'Out' if status_dict['ribbon_out'] == 1 else 'In'
        status_dict['thermoal_transfer'] = 'Thermal Transfer'\
            if status_dict['thermoal_transfer'] == 1 else 'Direct Thermal'

        print_mode_dict = {
            '0': 'Rewind', '1': 'Peel-Off', '2': 'Tear-Off', '3': 'Cutter', '4': 'Applicator', '5': 'Delayed cut',
            '6': 'Linerless Peel', '7': 'Linerless Rewind', '8': 'Partial Cutter', '9': 'RFID', 'K': 'Kiosk',
            'S': 'Kiosk CutStream', 'A': 'Kiosk CutStream'
        }

        status_dict['label_waiting'] = 'Waiting' if status_dict['label_waiting'] == 1 else 'Not Waiting'
        status_dict['print_mode'] = print_mode_dict[str(status_dict['print_mode'])]
        status_dict['static_ram'] = 'Installed' if status_dict['static_ram'] == 1 else 'Not installed'

        return status_dict

    def host_status_dict(self) -> dict | None:
        """Verifica o status da impressora e retorna um dicionário.

        Se a impressora não suportar o comando de status ou a resposta for inválida, retorna None.

        Descrição dos valores do dicionário:
        - interface: Configuração da interface de comunicação, contendo:
            - handshake: Handshake, Xon/Xoff ou DTR.
            - parity: Paridade, Odd ou Even.
            - status: Status da interface, Disabled ou Enabled.
            - stop_bits: Bits de parada, 2 bits ou 1 bit.
            - data_bits: Bits de dados, 7 bits ou 8 bits.
            - baud: Velocidade de comunicação.
        - paper_out: Flag de papel fora, Out ou In.
        - pause: Flag de pausa, Pause ou Resume.
        - label_length: Comprimento da etiqueta, em pontos.
        - number_of_formats_recv_buf: Número de formatos no buffer de recebimento.
        - buffer_full: Flag de buffer cheio, Full ou Not Full.
        - comm_diag_mode: Flag modo de diagnóstico de comunicação, On ou Off.
        - partial_format: Flag de formato parcial, Partial ou Full.
        - corrupt_ram: Flag de RAM corrompida, Data lost ou Not Corrupt.
        - under_temp: Temperatura baixa, Under Temp ou Normal Temp.
        - over_temp: Temperatura alta, Over Temp ou Normal Temp.
        - func_settings: Configurações de função, contendo:
            - media_type: Tipo de mídia, Die-Cut ou Continuous.
            - sensor_profile: Perfil do sensor, On ou Off.
            - communications_diagnostics: Diagnóstico de comunicação, On ou Off.
            - print_mode: Modo de impressão, Direct Thermal ou Thermal Transfer.
        - head_up: Cabeça de impressão levantada, Up ou Down.
        - ribbon_out: Ribbon fora, Out ou In.
        - thermoal_transfer: Transferência térmica, Thermal Transfer ou Direct Thermal.
        - print_mode: Modo de impressão, Rewind, Peel-Off, Tear-Off, Cutter, Applicator, Delayed cut, Linerless Peel,
                        Linerless Rewind, Partial Cutter, RFID, Kiosk, Kiosk CutStream.
        - print_width_mode: Modo de largura de impressão.
        - label_waiting: Etiqueta esperando, Waiting ou Not Waiting.
        - labels_remaining: Etiquetas restantes.
        - format_while_printing: Formato enquanto imprime, On ou Off.
        - graphics_stored_in_mem: Gráficos armazenados na memória.
        - password: Senha.
        - static_ram: RAM estática, Installed ou Not installed.

        Notes:
            Quando a impressora está em algumas condições não irá responder ao comando de status, sendo:
            - Saída de papel
            - Ribbon fora
            - Cabeça de impressão levantada
            - Temperatura muito alta
            - Rebobinador de etiquetas cheio

        Returns:
            dict: Status da impressora.
        """
        status = self.host_status()
        if not status or '' not in status:
            return None
        return self._parse_host_status(self.host_status())
    
    def host_diagnostic(self) -> str | None:
        """Verifica o status de diagnóstico da impressora.

        Returns:
            str: Status da impressora.
        """
        return self.send_command(ZplCommands.HOST_DIAGNOSTIC(), get_response=True)
    
    def host_diagnostic_dict(self) -> dict | None:
        """Verifica o status de diagnóstico da impressora e retorna um dicionário.
        
        Se a impressora não suportar o comando de diagnóstico ou a resposta for inválida, retorna None.

        Returns:
            dict: Status de diagnóstico da impressora.
        """
        status = self.host_diagnostic()

        def is_float(x):
            try:
                float(x)
                return True
            except ValueError:
                return False
        
        status = [x for x in status[3:-3].split('\r\n') if x != '']
        status = [x.split(':') for x in status]
        status = [x.strip() for sublist in status for x in sublist]
        status = [x.split(' = ') for x in status]
        status = {key: value if not is_float(value) else float(value) for key, value in status}

        return status

    def host_configuration(self) -> str:
        """Verifica a configuração da impressora.

        Returns:
            str: Configuração da impressora.
        """
        return self.send_command(str(ZplCommands.LABEL_START_BLOCK()) + str(ZplCommands.HOST_CONFIGURATION()) +
                                 str(ZplCommands.LABEL_END_BLOCK()), get_response=True)

    def host_information(self) -> str:
        """Verifica as informações da impressora.

        Returns:
            str: Informações da impressora.
        """
        return self.send_command(ZplCommands.HOST_INFORMATION(), get_response=True)

    def host_memory(self):
        """Verifica a memória da impressora.

        Returns:
            str: Memória da impressora.
        """
        return self.send_command(ZplCommands.HOST_MEMORY(), get_response=True)

    def host_query(self, query: Literal['ES', 'HA', 'JT', 'MA', 'MI', 'OD', 'PH', 'PP', 'SN', 'UI']) -> str:
        """Consulta a impressora.

        Args:
            query (str): Tipo de consulta.

        Returns:
            str: Resposta da impressora.
        """
        return self.send_command(ZplCommands.HOST_QUERY(query), get_response=True)


class ZebraPromptFakePrinter(ZebraPrinter):
    """Classe de impressora falsa para testes de prompt de comando."""

    def send_command(self, command: str | any, get_response: bool = False) -> None | str:
        print(str(command))
        return None

    @staticmethod
    def load_cmd_file(command_name: str) -> str:
        file_name = os.path.join(os.path.dirname(__file__), 'fakeouts', 'cmd_' + command_name + '.txt')
        with open(file_name, 'r', newline='\r\n', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def save_cmd_file(command_name: str, output: str):
        file_name = os.path.join(os.path.dirname(__file__), 'fakeouts', 'cmd_' + command_name + '.txt')
        with open(file_name, 'w', newline='\n', encoding='utf-8') as f:
            f.write(output)

    def host_status(self) -> str:
        return self.load_cmd_file('hs')

    def host_diagnostic(self) -> str:
        return self.load_cmd_file('hd')

    def host_configuration(self) -> str:
        return self.load_cmd_file('hh')

    def host_information(self) -> str:
        return self.load_cmd_file('hi')

    def host_memory(self):
        return self.load_cmd_file('hm')

    def host_query(self, query: Literal['ES', 'HA', 'JT', 'MA', 'MI', 'OD', 'PH', 'PP', 'SN', 'UI']) -> str:
        retuns_fakes = {
            'ES': '\r\n\r\n'
                  '  PRINTER STATUS                            \r\n'
                  '   ERRORS:         0 00000000 00000000      \r\n'
                  '   WARNINGS:       1 00000000 00002000      \r\n'
                  '',
            'HA': '\r\n\r\n'
                  '  MAC ADDRESS                               \r\n'
                  '   00:07:4D:76:7F:55                        \r\n'
                  '',
            'JT': '\r\n\r\n'
                  '  HEAD TEST RESULTS                         \r\n'
                  '   0,A,0000,0000,0000                       \r\n'
                  '',
            'MA': '\r\n\r\n'
                  '  MAINTENANCE ALERT SETTINGS                \r\n'
                  '   HEAD REPLACEMENT INTERVAL:       50 km   \r\n'
                  '   HEAD REPLACEMENT FREQUENCY:       0 M    \r\n'
                  '   HEAD CLEANING INTERVAL:           0 M    \r\n'
                  '   HEAD CLEANING FREQUENCY:          0 M    \r\n'
                  '   PRINT REPLACEMENT ALERT:           NO    \r\n'
                  '   PRINT CLEANING ALERT:              NO    \r\n'
                  '   UNITS:                              I    \r\n'
                  '',
            'MI': '\r\n\r\n'
                  '  MAINTENANCE ALERT MESSAGES                \r\n'
                  '   CLEAN: PLEASE CLEAN PRINT HEAD\r\n'
                  '   REPLACE: PLEASE REPLACE PRINT HEAD\r\n'
                  '',
            'OD': '\r\n\r\n'
                  '  PRINT METERS                              \r\n'
                  '   TOTAL NONRESETTABLE:        1330401 "    \r\n'
                  '   USER RESETTABLE CNTR1:      1330401 "    \r\n'
                  '   USER RESETTABLE CNTR2:      1330401 "    \r\n'
                  '',
            'PH': '\r\n\r\n'
                  '  LAST CLEANED:              1330401 "      \r\n'
                  '  HEAD LIFE HISTORY                         \r\n'
                  '   #   DISTANCE                             \r\n'
                  '   1:    1330401 "                          \r\n'
                  '',
            'PP': '\r\n\r\n'
                  '  PLUG AND PLAY MESSAGES                    \r\n'
                  '   MFG: Zebra Technologies\r\n'
                  '   CMD: ZPL\r\n'
                  '   MDL: ZT230\r\n'
                  '',
            'SN': '\r\n\r\n'
                  '  SERIAL NUMBER                             \r\n'
                  '   52J171600089                             \r\n'
                  '',
            'UI': '\r\n\r\n'
                  '  USB INFORMATION                           \r\n'
                  '   PID:                         00D5        \r\n'
                  '   RELEASE VERSION:             01.01       \r\n'
                  ''
        }
        return retuns_fakes[query]

    def host_w(self):
        return self.load_cmd_file('hw')

    def host_xml(self):
        return self.load_cmd_file('hz')

    def host_u(self):
        return self.load_cmd_file('hu')


class ZebraNetworkPrinter(ZebraPrinter):
    """Classe de impressora conectada via rede.

    A impressora deve estar configurada para receber comandos ZPL via TCP/IP.

    Args:
        host (str): Endereço IP ou nome de domínio da impressora.
        port (int): Porta de comunicação da impressora (default: 9100).
        timeout (int): Tempo limite de espera para resposta da impressora (default: None).
    """

    host: str
    port: int

    connection: socket.socket | None
    default_timeout: float

    check_conn_on_send: bool
    auto_close_conn_on_send: bool

    def __init__(self, host: str, port: int = 9100, timeout: int = None):
        super().__init__()
        self.host = host
        self.port = port
        self.connection = None
        self.default_timeout = timeout or -1

        self.check_conn_on_send = True
        self.auto_close_conn_on_send = True

    def connect(self) -> None:
        """Conecta-se à impressora."""
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.host, self.port))
        if self.default_timeout is None or self.default_timeout < 0:
            self.default_timeout = self.connection.timeout

    def disconnect(self) -> None:
        """Desconecta-se da impressora."""
        self.connection.close()
        self.connection = None

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

    def send_command(self, command: str | any, get_response: bool = False) -> None | str:
        """Envia um comando para a impressora.

        Args:
            command (str | any): Comando ZPL a ser enviado.
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

    def send_commands(self, commands: list[str | any], get_response: bool = False) -> list[str] | None:
        """Envia uma lista de comandos para a impressora.

        Args:
            commands (list[str | any]): Lista de comandos ZPL a serem enviados.
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
        if self.connection is None:
            return False
        try:
            self.connection.sendall(bytes(str(ZplCommands.FIELD_COMMENT) + 'TESTE_CONNECTION', 'UTF-8'))
        except OSError:
            return False
