from __future__ import annotations
from typing import Literal

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

    def host_status(self) -> str:
        return ('030,0,0,0346,000,0,0,0,000,0,0,0\r\n'
                '000,0,0,1,0,2,4,0,00000000,1,012\r\n'
                '1234,0\r\n')

    def host_diagnostic(self) -> str:
        return ('\r\n'
                'Head Temp = 24\r\n'
                'Head Temp = 24\r\n'
                'Ambient Temp = 165\r\n'
                'Head Test = Test Not Run\r\n'
                'Darkness Adjust = 17\r\n'
                'Print Speed = 2.0\r\n'
                'Slew Speed = 2.0\r\n'
                'Backfeed Speed = 2.0\r\n'
                'Static_pitch_length = 0346\r\n'
                'Dynamic_pitch_length = 0362\r\n'
                'Max_dynamic_pitch_length = 0366\r\n'
                'Min_dynamic_pitch_length = 0359\r\n'
                'COMMAND PFX = ~ : FORMAT PFX = ^ : DELIMITER = ,\r\n'
                'Dynamic_top_position = 0000\r\n'
                '\r\n'
                'No ribbon A/D = 0000\r\n'
                '\r\n'
                'PCB Temp = 163\r\n'
                '\r\n')

    def host_configuration(self) -> str:
        return ('  10                  LCD CONTRAST      \r\n'
                '  +17.0               DARKNESS          \r\n'
                '  2.0 IPS             PRINT SPEED       \r\n'
                '  +000                TEAR OFF          \r\n'
                '  TEAR OFF            PRINT MODE        \r\n'
                '  GAP/NOTCH           MEDIA TYPE        \r\n'
                '  REFLECTIVE          SENSOR SELECT     \r\n'
                '  DIRECT-THERMAL      PRINT METHOD      \r\n'
                '  609                 PRINT WIDTH       \r\n'
                '  0346                LABEL LENGTH      \r\n'
                '  P1028902/1704-00574 PRINT HEAD ID     \r\n'
                '  39.0IN   988MM      MAXIMUM LENGTH    \r\n'
                '  MAINT. OFF          EARLY WARNING     \r\n'
                '  NOT CONNECTED       USB COMM.         \r\n'
                '  BIDIRECTIONAL       PARALLEL COMM.    \r\n'
                '  RS232               SERIAL COMM.      \r\n'
                '  9600                BAUD              \r\n'
                '  8 BITS              DATA BITS         \r\n'
                '  NONE                PARITY            \r\n'
                '  XON/XOFF            HOST HANDSHAKE    \r\n'
                '  NONE                PROTOCOL          \r\n'
                '  NORMAL MODE         COMMUNICATIONS    \r\n'
                '  <~>  7EH            CONTROL PREFIX    \r\n'
                '  <^>  5EH            FORMAT PREFIX     \r\n'
                '  <,>  2CH            DELIMITER CHAR    \r\n'
                '  ZPL II              ZPL MODE          \r\n'
                '  INACTIVE            COMMAND OVERRIDE  \r\n'
                '  CALIBRATION         MEDIA POWER UP    \r\n'
                '  CALIBRATION         HEAD CLOSE        \r\n'
                '  DEFAULT             BACKFEED          \r\n'
                '  +000                LABEL TOP         \r\n'
                '  +0000               LEFT POSITION     \r\n'
                '  ENABLED             REPRINT MODE      \r\n'
                '  020                 WEB SENSOR        \r\n'
                '  024                 MEDIA SENSOR      \r\n'
                '  255                 TAKE LABEL        \r\n'
                '  086                 MARK SENSOR       \r\n'
                '  037                 MARK MED SENSOR   \r\n'
                '  000                 TRANS GAIN        \r\n'
                '  000                 TRANS BASE        \r\n'
                '  100                 TRANS LED         \r\n'
                '  002                 MARK GAIN         \r\n'
                '  088                 MARK LED          \r\n'
                '  DPCSWFXM            MODES ENABLED     \r\n'
                '  ........            MODES DISABLED    \r\n'
                '   832 8/MM FULL      RESOLUTION        \r\n'
                '  4.0                 LINK-OS VERSION   \r\n'
                '  V72.20.01Z <-       FIRMWARE          \r\n'
                '  1.3                 XML SCHEMA        \r\n'
                '  6.5.0 19.7          HARDWARE ID       \r\n'
                '  4096k............R: RAM               \r\n'
                '  32768k...........E: ONBOARD FLASH     \r\n'
                '  NONE                FORMAT CONVERT    \r\n'
                '  FW VERSION          IDLE DISPLAY      \r\n'
                '  11/02/16            RTC DATE          \r\n'
                '  15:45               RTC TIME          \r\n'
                '  DISABLED            ZBI               \r\n'
                '  2.1                 ZBI VERSION       \r\n'
                '  READY               ZBI STATUS        \r\n'
                '  443,279 LABELS      NONRESET CNTR     \r\n'
                '  443,279 LABELS      RESET CNTR1       \r\n'
                '  443,279 LABELS      RESET CNTR2       \r\n'
                '  1,330,385 IN        NONRESET CNTR     \r\n'
                '  1,330,385 IN        RESET CNTR1       \r\n'
                '  1,330,385 IN        RESET CNTR2       \r\n'
                '  3,379,178 CM        NONRESET CNTR     \r\n'
                '  3,379,178 CM        RESET CNTR1       \r\n'
                '  3,379,178 CM        RESET CNTR2       \r\n'
                '  001 WIRED           SLOT 1            \r\n'
                '')

    def host_information(self) -> str:
        return 'ZT230-200dpi,V72.20.01Z,8,4096KB\r\n'

    def host_memory(self):
        return '4096,4096,4074\r\n'

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
        return ('\r\n'
                '- DIR R:*.* \r\n'
                '\r\n'
                '-   4171776 bytes free R: RAM \r\n'
                '')

    def host_xml(self):
        return("<?xml version='1.0'?>\r\n"
               "<ZEBRA-ELTRON-PERSONALITY>\r\n"
                "<DEFINITIONS>\r\n"
                "<MODEL>ZT230</MODEL>\r\n"
                "<FIRMWARE-VERSION>V72.20.01Z</FIRMWARE-VERSION>\r\n"
                "<LINK-OS-VERSION>4.0</LINK-OS-VERSION>\r\n"
                "<XML-SCHEMA-VERSION>1.3</XML-SCHEMA-VERSION>\r\n"
                "<PLUG-AND-PLAY-VALUE>MANUFACTURER:Zebra Technologies ;COMMAND SET:ZPL;MODEL:ZTC ZT230-200dpi ZPL;CLASS:PRINTER;OPTIONS:XML;</PLUG-AND-PLAY-VALUE>\r\n"
                "<ZBI>DISABLED</ZBI>\r\n"
                "<DOTS-PER-MM>8</DOTS-PER-MM>\r\n"
                "<DOTS-PER-DOTROW>832</DOTS-PER-DOTROW>\r\n"
                "<PHYSICAL-MEMORY>\r\n"
                "<TYPE ENUM='R, E, B, A'>R</TYPE>\r\n"
                "<SIZE>4194304</SIZE>\r\n"
                "<AVAILABLE>4171776</AVAILABLE>\r\n"
                "</PHYSICAL-MEMORY>\r\n"
                "<PHYSICAL-MEMORY>\r\n"
                "<TYPE ENUM='R, E, B, A'>E</TYPE>\r\n"
                "<SIZE>33554432</SIZE>\r\n"
                "<AVAILABLE>33340928</AVAILABLE>\r\n"
                "</PHYSICAL-MEMORY>\r\n"
                "<OPTIONS>\r\n"
                "<CUTTER BOOL='Y,N'>N</CUTTER>\r\n"
                "<LINER-TAKEUP BOOL='Y,N'>N</LINER-TAKEUP>\r\n"
                "<VALUE-PEEL-REWIND BOOL='Y,N'>N</VALUE-PEEL-REWIND>\r\n"
                "<APPLICATOR BOOL='Y,N'>N</APPLICATOR>\r\n"
                "<PEEL BOOL='Y,N'>N</PEEL>\r\n"
                "</OPTIONS>\r\n"
                "<WIRELESS-PRINTSERVER>\r\n"
                "<PRODUCT-NAME>ZebraNet Wireless PS</PRODUCT-NAME>\r\n"
                "<PRINTSERVER-FIRMWARE-VERSION>V72.20.01Z</PRINTSERVER-FIRMWARE-VERSION>\r\n"
                "<PRODUCT-NUMBER>79071</PRODUCT-NUMBER>\r\n"
                "<MFG-ID>H</MFG-ID>\r\n"
                "<CARD-ID>H</CARD-ID>\r\n"
                "<CARD-FIRMWARE>00.00.00</CARD-FIRMWARE>\r\n"
                "<MAC-ADDRESS>00:00:00:00:00:00</MAC-ADDRESS>\r\n"
                "<DATE-CODE>0161A</DATE-CODE>\r\n"
                "<PRINTER-STATUS>Online</PRINTER-STATUS>\r\n"
                "<CONNECTED-TO>ZTC  ZT230-203dpi ,</CONNECTED-TO>\r\n"
                "<BIDI-STATUS-ENABLED>Y</BIDI-STATUS-ENABLED>\r\n"
                "<SYSTEM-UPTIME>26 days 16 hours 44 mins 42 secs</SYSTEM-UPTIME>\r\n"
                "</WIRELESS-PRINTSERVER>\r\n"
                "</DEFINITIONS>\r\n"
                "<SAVED-SETTINGS>\r\n"
                "<NAME>52J171600089</NAME>\r\n"
                "<DESCRIPTION></DESCRIPTION>\r\n"
                "<DISPLAY-CONTRAST MIN='3' MAX='15'>\r\n"
                "<CURRENT>10</CURRENT>\r\n"
                "<STORED>10</STORED>\r\n"
                "<DEFAULT>10</DEFAULT>\r\n"
                "</DISPLAY-CONTRAST>\r\n"
                "<MEDIA-DARKNESS MIN='0.0' MAX='30.0'>\r\n"
                "<CURRENT>17.0</CURRENT>\r\n"
                "<STORED>17.0</STORED>\r\n"
                "<DEFAULT>10.0</DEFAULT>\r\n"
                "</MEDIA-DARKNESS>\r\n"
                "<TEAR-OFF-POSITION MIN='-120' MAX='120'>\r\n"
                "<CURRENT>0</CURRENT>\r\n"
                "<STORED>0</STORED>\r\n"
                "<DEFAULT>0</DEFAULT>\r\n"
                "</TEAR-OFF-POSITION>\r\n"
                "<PRINT-MODE>\r\n"
                "<MODE ENUM='REWIND, TEAR OFF, PEEL OFF, CUTTER, DELAYED CUT, APPLICATOR, LINERLESS-P, LINERLESS-R, LINERLESS-T, '>\r\n"
                "<CURRENT>TEAR OFF</CURRENT>\r\n"
                "<STORED>TEAR OFF</STORED>\r\n"
                "<DEFAULT>TEAR OFF</DEFAULT>\r\n"
                "</MODE>\r\n"
                "</PRINT-MODE>\r\n"
                "<MEDIA-TRACKING ENUM='CONTINUOUS, NON-CONTINUOUS'>\r\n"
                "<CURRENT>NON-CONTINUOUS</CURRENT>\r\n"
                "<STORED>NON-CONTINUOUS</STORED>\r\n"
                "<DEFAULT>NON-CONTINUOUS</DEFAULT>\r\n"
                "</MEDIA-TRACKING>\r\n"
                "<MEDIA-TYPE ENUM='DIRECT-THERMAL, THERMAL-TRANS.'>\r\n"
                "<CURRENT>DIRECT-THERMAL</CURRENT>\r\n"
                "<STORED>DIRECT-THERMAL</STORED>\r\n"
                "<DEFAULT>THERMAL-TRANS.</DEFAULT>\r\n"
                "</MEDIA-TYPE>\r\n"
                "<PRINT-WIDTH MIN='2' MAX='832'>\r\n"
                "<CURRENT>609</CURRENT>\r\n"
                "<STORED>609</STORED>\r\n"
                "<DEFAULT>832</DEFAULT>\r\n"
                "</PRINT-WIDTH>\r\n"
                "<EARLY-WARNING-MEDIA BOOL='Y,N'>\r\n"
                "<CURRENT>N</CURRENT>\r\n"
                "<STORED>N</STORED>\r\n"
                "<DEFAULT>N</DEFAULT>\r\n"
                "</EARLY-WARNING-MEDIA>\r\n"
                "<LABELS-PER-ROLL MIN='100' MAX='9999'>\r\n"
                "<CURRENT>900</CURRENT>\r\n"
                "<STORED>900</STORED>\r\n"
                "<DEFAULT>900</DEFAULT>\r\n"
                "</LABELS-PER-ROLL>\r\n"
                "<RIBBON-LENGTH ENUM='100 M  328 FT, 150 M  492 FT, 200 M  656 FT, 250 M  820 FT, 300 M  984 FT, 350 M  1148 FT, 400 M  1312 FT, 450 M  1476 FT'>\r\n"
                "<CURRENT>450 M  1476 FT</CURRENT>\r\n"
                "<STORED>450 M  1476 FT</STORED>\r\n"
                "<DEFAULT>450 M  1476 FT</DEFAULT>\r\n"
                "</RIBBON-LENGTH>\r\n"
                "<EARLY-WARNING-MAINTENANCE BOOL='Y,N'>\r\n"
                "<CURRENT>N</CURRENT>\r\n"
                "<STORED>N</STORED>\r\n"
                "<DEFAULT>N</DEFAULT>\r\n"
                "</EARLY-WARNING-MAINTENANCE>\r\n"
                "<HEAD-CLEANING ENUM='0 M  0 FT, 100 M  328 FT, 150 M  492 FT, 200 M  656 FT, 250 M  820 FT, 300 M  984 FT, 350 M  1148 FT, 400 M  1312 FT, 450 M  1476 FT'>\r\n"
                "<CURRENT>450 M  1476 FT</CURRENT>\r\n"
                "<STORED>450 M  1476 FT</STORED>\r\n"
                "<DEFAULT>450 M  1476 FT</DEFAULT>\r\n"
                "</HEAD-CLEANING>\r\n"
                "<SERIAL-PORT1>\r\n"
                "<BAUD ENUM='4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200'>\r\n"
                "<CURRENT>9600</CURRENT>\r\n"
                "<STORED>9600</STORED>\r\n"
                "<DEFAULT>9600</DEFAULT>\r\n"
                "</BAUD>\r\n"
                "<DATA-BITS ENUM='7 BITS, 8 BITS'>\r\n"
                "<CURRENT>8 BITS</CURRENT>\r\n"
                "<STORED>8 BITS</STORED>\r\n"
                "<DEFAULT>8 BITS</DEFAULT>\r\n"
                "</DATA-BITS>\r\n"
                "<PARITY ENUM='NONE, ODD, EVEN'>\r\n"
                "<CURRENT>NONE</CURRENT>\r\n"
                "<STORED>NONE</STORED>\r\n"
                "<DEFAULT>NONE</DEFAULT>\r\n"
                "</PARITY>\r\n"
                "<STOP-BITS ENUM='1 STOP BIT, 2 STOP BITS'>\r\n"
                "<CURRENT>1 STOP BIT</CURRENT>\r\n"
                "<STORED>1 STOP BIT</STORED>\r\n"
                "<DEFAULT>1 STOP BIT</DEFAULT>\r\n"
                "</STOP-BITS>\r\n"
                "<HANDSHAKE ENUM='XON/XOFF, DSR/DTR, RTS/CTS, APL-I, DTR &amp; XON/XOFF'>\r\n"
                "<CURRENT>XON/XOFF</CURRENT>\r\n"
                "<STORED>XON/XOFF</STORED>\r\n"
                "<DEFAULT>XON/XOFF</DEFAULT>\r\n"
                "</HANDSHAKE>\r\n"
                "<PROTOCOL ENUM='NONE, ZEBRA, ACK_NAK'>\r\n"
                "<CURRENT>NONE</CURRENT>\r\n"
                "<STORED>NONE</STORED>\r\n"
                "<DEFAULT>NONE</DEFAULT>\r\n"
                "</PROTOCOL>\r\n"
                "</SERIAL-PORT1>\r\n"
                "<ZNET-ID MIN='0' MAX='999'>\r\n"
                "<CURRENT>0</CURRENT>\r\n"
                "<STORED>0</STORED>\r\n"
                "<DEFAULT>0</DEFAULT>\r\n"
                "</ZNET-ID>\r\n"
                "<PROTOCOL-1284-4 BOOL='Y,N'>\r\n"
                "<CURRENT>N</CURRENT>\r\n"
                "<STORED>N</STORED>\r\n"
                "<DEFAULT>N</DEFAULT>\r\n"
                "</PROTOCOL-1284-4>\r\n"
                "<WARN-HEAD-COLD BOOL='Y,N'>\r\n"
                "<CURRENT>N</CURRENT>\r\n"
                "<STORED>N</STORED>\r\n"
                "<DEFAULT>N</DEFAULT>\r\n"
                "</WARN-HEAD-COLD>\r\n"
                "<TILDE-DEFINE MIN='0' MAX='255'>\r\n"
                "<CURRENT>126</CURRENT>\r\n"
                "<STORED>126</STORED>\r\n"
                "<DEFAULT>126</DEFAULT>\r\n"
                "</TILDE-DEFINE>\r\n"
                "<CARET-DEFINE MIN='0' MAX='255'>\r\n"
                "<CURRENT>94</CURRENT>\r\n"
                "<STORED>94</STORED>\r\n"
                "<DEFAULT>94</DEFAULT>\r\n"
                "</CARET-DEFINE>\r\n"
                "<DELIM-DEFINE MIN='0' MAX='255'>\r\n"
                "<CURRENT>44</CURRENT>\r\n"
                "<STORED>44</STORED>\r\n"
                "<DEFAULT>44</DEFAULT>\r\n"
                "</DELIM-DEFINE>\r\n"
                "<LABEL-DESCRIPTION-LANGUAGE ENUM='ZPL II, ZPL'>\r\n"
                "<CURRENT>ZPL II</CURRENT>\r\n"
                "<STORED>ZPL II</STORED>\r\n"
                "<DEFAULT>ZPL II</DEFAULT>\r\n"
                "</LABEL-DESCRIPTION-LANGUAGE>\r\n"
                "<MEDIA-FEED>\r\n"
                "<POWER-UP ENUM='FEED, CALIBRATION, LENGTH, SHORT CAL, NO MOTION'>\r\n"
                "<CURRENT>CALIBRATION</CURRENT>\r\n"
                "<STORED>CALIBRATION</STORED>\r\n"
                "<DEFAULT>CALIBRATION</DEFAULT>\r\n"
                "</POWER-UP>\r\n"
                "<HEAD-CLOSE ENUM='FEED, CALIBRATION, LENGTH, SHORT CAL, NO MOTION'>\r\n"
                "<CURRENT>CALIBRATION</CURRENT>\r\n"
                "<STORED>CALIBRATION</STORED>\r\n"
                "<DEFAULT>CALIBRATION</DEFAULT>\r\n"
                "</HEAD-CLOSE>\r\n"
                "</MEDIA-FEED>\r\n"
                "<BACKFEED-PERCENT ENUM='BEFORE, 10%, 20%, 30%, 40%, 50%, 60%, 70%, 80%, DEFAULT, AFTER, OFF'>\r\n"
                "<CURRENT>DEFAULT</CURRENT>\r\n"
                "<STORED>DEFAULT</STORED>\r\n"
                "<DEFAULT>DEFAULT</DEFAULT>\r\n"
                "</BACKFEED-PERCENT>\r\n"
                "<LABEL-TOP MIN='-120' MAX='120'>\r\n"
                "<CURRENT>0</CURRENT>\r\n"
                "<STORED>0</STORED>\r\n"
                "<DEFAULT>0</DEFAULT>\r\n"
                "</LABEL-TOP>\r\n"
                "<CALIBRATION-VALUES>\r\n"
                "<CALIBRATED-LABEL-LENGTH MIN='0' MAX='7967'>\r\n"
                "<CURRENT>346</CURRENT>\r\n"
                "<STORED>346</STORED>\r\n"
                "<DEFAULT>1225</DEFAULT>\r\n"
                "</CALIBRATED-LABEL-LENGTH>\r\n"
                "<WEB-SENSOR MIN='0' MAX='100'>\r\n"
                "<CURRENT>20</CURRENT>\r\n"
                "<STORED>20</STORED>\r\n"
                "<DEFAULT>20</DEFAULT>\r\n"
                "</WEB-SENSOR>\r\n"
                "<MEDIA-SENSOR MIN='0' MAX='100'>\r\n"
                "<CURRENT>24</CURRENT>\r\n"
                "<STORED>24</STORED>\r\n"
                "<DEFAULT>24</DEFAULT>\r\n"
                "</MEDIA-SENSOR>\r\n"
                "<RIBBON-SENSOR MIN='0' MAX='100'>\r\n"
                "<CURRENT>40</CURRENT>\r\n"
                "<STORED>40</STORED>\r\n"
                "<DEFAULT>50</DEFAULT>\r\n"
                "</RIBBON-SENSOR>\r\n"
                "<MARK-SENSOR MIN='0' MAX='100'>\r\n"
                "<CURRENT>86</CURRENT>\r\n"
                "<STORED>86</STORED>\r\n"
                "<DEFAULT>27</DEFAULT>\r\n"
                "</MARK-SENSOR>\r\n"
                "<MARK-MEDIA-SENSOR MIN='0' MAX='100'>\r\n"
                "<CURRENT>37</CURRENT>\r\n"
                "<STORED>37</STORED>\r\n"
                "<DEFAULT>27</DEFAULT>\r\n"
                "</MARK-MEDIA-SENSOR>\r\n"
                "<TRANSMISSIVE-GAIN MIN='0' MAX='255'>\r\n"
                "<CURRENT>0</CURRENT>\r\n"
                "<STORED>0</STORED>\r\n"
                "<DEFAULT>128</DEFAULT>\r\n"
                "</TRANSMISSIVE-GAIN>\r\n"
                "<TRANSMISSIVE-BASE MIN='0' MAX='100'>\r\n"
                "<CURRENT>0</CURRENT>\r\n"
                "<STORED>0</STORED>\r\n"
                "<DEFAULT>0</DEFAULT>\r\n"
                "</TRANSMISSIVE-BASE>\r\n"
                "<TRANSMISSIVE-LED MIN='0' MAX='100'>\r\n"
                "<CURRENT>100</CURRENT>\r\n"
                "<STORED>100</STORED>\r\n"
                "<DEFAULT>50</DEFAULT>\r\n"
                "</TRANSMISSIVE-LED>\r\n"
                "<RIBBON-GAIN MIN='0' MAX='255'>\r\n"
                "<CURRENT>1</CURRENT>\r\n"
                "<STORED>1</STORED>\r\n"
                "<DEFAULT>128</DEFAULT>\r\n"
                "</RIBBON-GAIN>\r\n"
                "<MARK-GAIN MIN='0' MAX='255'>\r\n"
                "<CURRENT>2</CURRENT>\r\n"
                "<STORED>2</STORED>\r\n"
                "<DEFAULT>128</DEFAULT>\r\n"
                "</MARK-GAIN>\r\n"
                "</CALIBRATION-VALUES>\r\n"
                "<HALF-DENSITY BOOL='Y,N'>\r\n"
                "<CURRENT>N</CURRENT>\r\n"
                "<STORED>N</STORED>\r\n"
                "<DEFAULT>N</DEFAULT>\r\n"
                "</HALF-DENSITY>\r\n"
                "<OPERATOR-LANGUAGE ENUM='ENGLISH, SPANISH, FRENCH, GERMAN, ITALIAN, NORWEGIAN, PORTUGUESE, SWEDISH, DANISH, SPANISH2, DUTCH, FINNISH, JAPAN, KOREAN, SIMP CHINESE, TRAD CHINESE, RUSSIAN, POLISH, CZECH, ROMANIAN'>\r\n"
                "<CURRENT>ENGLISH</CURRENT>\r\n"
                "<STORED>ENGLISH</STORED>\r\n"
                "<DEFAULT>ENGLISH</DEFAULT>\r\n"
                "</OPERATOR-LANGUAGE>\r\n"
                "<MODE-PROTECTION>\r\n"
                "<DISABLE-DARKNESS BOOL='Y,N'>\r\n"
                "<CURRENT>N</CURRENT>\r\n"
                "<STORED>N</STORED>\r\n"
                "<DEFAULT>N</DEFAULT>\r\n"
                "</DISABLE-DARKNESS>\r\n"
                "<DISABLE-POSITION BOOL='Y,N'>\r\n"
                "<CURRENT>N</CURRENT>\r\n"
                "<STORED>N</STORED>\r\n"
                "<DEFAULT>N</DEFAULT>\r\n"
                "</DISABLE-POSITION>\r\n"
                "<DISABLE-CALIBRATION BOOL='Y,N'>\r\n"
                "<CURRENT>N</CURRENT>\r\n"
                "<STORED>N</STORED>\r\n"
                "<DEFAULT>N</DEFAULT>\r\n"
                "</DISABLE-CALIBRATION>\r\n"
                "<DISABLE-SAVE-CONFIGURATION BOOL='Y,N'>\r\n"
                "<CURRENT>N</CURRENT>\r\n"
                "<STORED>N</STORED>\r\n"
                "<DEFAULT>N</DEFAULT>\r\n"
                "</DISABLE-SAVE-CONFIGURATION>\r\n"
                "<DISABLE-PAUSE-KEY BOOL='Y,N'>\r\n"
                "<CURRENT>N</CURRENT>\r\n"
                "<STORED>N</STORED>\r\n"
                "<DEFAULT>N</DEFAULT>\r\n"
                "</DISABLE-PAUSE-KEY>\r\n"
                "<DISABLE-FEED-KEY BOOL='Y,N'>\r\n"
                "<CURRENT>N</CURRENT>\r\n"
                "<STORED>N</STORED>\r\n"
                "<DEFAULT>N</DEFAULT>\r\n"
                "</DISABLE-FEED-KEY>\r\n"
                "<DISABLE-CANCEL-KEY BOOL='Y,N'>\r\n"
                "<CURRENT>N</CURRENT>\r\n"
                "<STORED>N</STORED>\r\n"
                "<DEFAULT>N</DEFAULT>\r\n"
                "</DISABLE-CANCEL-KEY>\r\n"
                "<DISABLE-MENU BOOL='Y,N'>\r\n"
                "<CURRENT>N</CURRENT>\r\n"
                "<STORED>N</STORED>\r\n"
                "<DEFAULT>N</DEFAULT>\r\n"
                "</DISABLE-MENU>\r\n"
                "</MODE-PROTECTION>\r\n"
                "<MEMORY-ALIAS>\r\n"
                "<DRIVE-A ENUM='R, E, B, A'>\r\n"
                "<CURRENT>E</CURRENT>\r\n"
                "<STORED>E</STORED>\r\n"
                "<DEFAULT>A</DEFAULT>\r\n"
                "</DRIVE-A>\r\n"
                "<DRIVE-B ENUM='R, E, B, A'>\r\n"
                "<CURRENT>B</CURRENT>\r\n"
                "<STORED>B</STORED>\r\n"
                "<DEFAULT>B</DEFAULT>\r\n"
                "</DRIVE-B>\r\n"
                "<DRIVE-E ENUM='R, E, B, A'>\r\n"
                "<CURRENT>E</CURRENT>\r\n"
                "<STORED>E</STORED>\r\n"
                "<DEFAULT>E</DEFAULT>\r\n"
                "</DRIVE-E>\r\n"
                "<DRIVE-R ENUM='R, E, B, A'>\r\n"
                "<CURRENT>R</CURRENT>\r\n"
                "<STORED>R</STORED>\r\n"
                "<DEFAULT>R</DEFAULT>\r\n"
                "</DRIVE-R>\r\n"
                "</MEMORY-ALIAS>\r\n"
                "<PASSWORD MIN='0' MAX='9999'>\r\n"
                "<CURRENT>1234</CURRENT>\r\n"
                "<STORED>1234</STORED>\r\n"
                "<DEFAULT>1234</DEFAULT>\r\n"
                "</PASSWORD>\r\n"
                "<MAX-LABEL-LENGTH MIN='0' MAX='7967'>\r\n"
                "<CURRENT>7917</CURRENT>\r\n"
                "<STORED>7917</STORED>\r\n"
                "<DEFAULT>7967</DEFAULT>\r\n"
                "</MAX-LABEL-LENGTH>\r\n"
                "<VERIFIER-PORT ENUM='OFF, VER-RPRNT ERR, VER-THRUPUT'>\r\n"
                "<CURRENT>OFF</CURRENT>\r\n"
                "<STORED>OFF</STORED>\r\n"
                "<DEFAULT>OFF</DEFAULT>\r\n"
                "</VERIFIER-PORT>\r\n"
                "<APPLICATOR-PORT ENUM='OFF, MODE 1, MODE 2, MODE 3, MODE 4'>\r\n"
                "<CURRENT>OFF</CURRENT>\r\n"
                "<STORED>OFF</STORED>\r\n"
                "<DEFAULT>OFF</DEFAULT>\r\n"
                "</APPLICATOR-PORT>\r\n"
                "<START-PRINT-SIG ENUM='PULSE MODE, LEVEL MODE'>\r\n"
                "<CURRENT>PULSE MODE</CURRENT>\r\n"
                "<STORED>PULSE MODE</STORED>\r\n"
                "<DEFAULT>PULSE MODE</DEFAULT>\r\n"
                "</START-PRINT-SIG>\r\n"
                "<RESYNCH-MODE ENUM='FEED MODE, ERROR MODE'>\r\n"
                "<CURRENT>FEED MODE</CURRENT>\r\n"
                "<STORED>FEED MODE</STORED>\r\n"
                "<DEFAULT>FEED MODE</DEFAULT>\r\n"
                "</RESYNCH-MODE>\r\n"
                "<PRE-PEEL BOOL='Y,N'>\r\n"
                "<CURRENT>N</CURRENT>\r\n"
                "<STORED>N</STORED>\r\n"
                "<DEFAULT>N</DEFAULT>\r\n"
                "</PRE-PEEL>\r\n"
                "<PRINTER-SLEEP>\r\n"
                "<FORCE-OFF-MODE BOOL='Y,N'>\r\n"
                "<CURRENT>N</CURRENT>\r\n"
                "<STORED>N</STORED>\r\n"
                "<DEFAULT>N</DEFAULT>\r\n"
                "</FORCE-OFF-MODE>\r\n"
                "<IDLE-TIME MIN='0' MAX='999999'>\r\n"
                "<CURRENT>0</CURRENT>\r\n"
                "<STORED>0</STORED>\r\n"
                "<DEFAULT>0</DEFAULT>\r\n"
                "</IDLE-TIME>\r\n"
                "</PRINTER-SLEEP>\r\n"
                "<UNSOLICITED-MESSAGES>\r\n"
                "<CURRENT>\r\n"
                "<MESSAGE>\r\n"
                "<CONDITION ENUM='ALL MESSAGES, PAPER OUT, RIBBON OUT, HEAD TOO HOT, HEAD COLD, HEAD OPEN, SUPPLY TOO HOT, RIBBON IN, REWIND, CUTTER JAMMED, PRINTER PAUSED, PQ JOB COMPLETED, LABEL READY, HEAD ELEMENT BAD, BASIC RUNTIME, BASIC FORCED, POWER ON, CLEAN PRINTHEAD, MEDIA LOW, RIBBON LOW, REPLACE HEAD, BATTERY LOW, RFID ERROR, MOTOR OVERTEMP, PRINTHEAD SHUTDOWN, COLD START, SGD SET, SHUTTING DOWN, RESTARTING, NO READER PRESENT, THERMISTOR FAULT, INVALID HEAD, COUNTRY CODE ERROR, MCR RESULT READY, PMCU DOWNLOAD, RIBBON AUTH ERROR, ODOMETER TRIGGERED'>\r\n"
                "COLD START</CONDITION>\r\n"
                "<DESTINATION ENUM='SERIAL, PARALLEL, E-MAIL, TCP, UDP, SNMP, USB, HTTP-POST, BLUETOOTH, SDK'>\r\n"
                "SNMP</DESTINATION>\r\n"
                "<SET BOOL='Y,N'>Y</SET>\r\n"
                "<CLEAR BOOL='Y,N'>N</CLEAR>\r\n"
                "<DESTINATION-DATA>255.255.255.255</DESTINATION-DATA>\r\n"
                "<PORT MIN='0' MAX='65535'>162</PORT>\r\n"
                "<SGD-NAME></SGD-NAME>\r\n"
                "</MESSAGE>\r\n"
                "</CURRENT>\r\n"
                "<STORED>\r\n"
                "<MESSAGE>\r\n"
                "<CONDITION ENUM='ALL MESSAGES, PAPER OUT, RIBBON OUT, HEAD TOO HOT, HEAD COLD, HEAD OPEN, SUPPLY TOO HOT, RIBBON IN, REWIND, CUTTER JAMMED, PRINTER PAUSED, PQ JOB COMPLETED, LABEL READY, HEAD ELEMENT BAD, BASIC RUNTIME, BASIC FORCED, POWER ON, CLEAN PRINTHEAD, MEDIA LOW, RIBBON LOW, REPLACE HEAD, BATTERY LOW, RFID ERROR, MOTOR OVERTEMP, PRINTHEAD SHUTDOWN, COLD START, SGD SET, SHUTTING DOWN, RESTARTING, NO READER PRESENT, THERMISTOR FAULT, INVALID HEAD, COUNTRY CODE ERROR, MCR RESULT READY, PMCU DOWNLOAD, RIBBON AUTH ERROR, ODOMETER TRIGGERED'>\r\n"
                "COLD START</CONDITION>\r\n"
                "<DESTINATION ENUM='SERIAL, PARALLEL, E-MAIL, TCP, UDP, SNMP, USB, HTTP-POST, BLUETOOTH, SDK'>\r\n"
                "SNMP</DESTINATION>\r\n"
                "<SET BOOL='Y,N'>Y</SET>\r\n"
                "<CLEAR BOOL='Y,N'>N</CLEAR>\r\n"
                "<DESTINATION-DATA>255.255.255.255</DESTINATION-DATA>\r\n"
                "<PORT MIN='0' MAX='65535'>162</PORT>\r\n"
                "<SGD-NAME></SGD-NAME>\r\n"
                "</MESSAGE>\r\n"
                "</STORED>\r\n"
                "</UNSOLICITED-MESSAGES>\r\n"
                "<WIRELESS-PRINTSERVER>\r\n"
                "<WIRELESS-SETTINGS>\r\n"
                "<ESSID>\r\n"
                "<CURRENT>125</CURRENT>\r\n"
                "<STORED>125</STORED>\r\n"
                "<DEFAULT>125</DEFAULT>\r\n"
                "</ESSID>\r\n"
                "<OPERATING-MODE ENUM='AD-HOC, INFRASTRUCTURE'>\r\n"
                "<CURRENT>INFRASTRUCTURE</CURRENT>\r\n"
                "<STORED>INFRASTRUCTURE</STORED>\r\n"
                "<DEFAULT>INFRASTRUCTURE</DEFAULT>\r\n"
                "</OPERATING-MODE>\r\n"
                "<PREAMBLE ENUM='LONG, SHORT'>\r\n"
                "<CURRENT>LONG</CURRENT>\r\n"
                "<STORED>LONG</STORED>\r\n"
                "<DEFAULT>LONG</DEFAULT>\r\n"
                "</PREAMBLE>\r\n"
                "<WLAN-PULSE-ENABLED BOOL='ON,OFF'>\r\n"
                "<CURRENT>ON</CURRENT>\r\n"
                "<STORED>ON</STORED>\r\n"
                "<DEFAULT>ON</DEFAULT>\r\n"
                "</WLAN-PULSE-ENABLED>\r\n"
                "<WLAN-PULSE-RATE MIN='5' MAX='300'>\r\n"
                "<CURRENT>15</CURRENT>\r\n"
                "<STORED>15</STORED>\r\n"
                "<DEFAULT>15</DEFAULT>\r\n"
                "</WLAN-PULSE-RATE>\r\n"
                "<WLAN-INTERNATIONAL-MODE ENUM='OFF, ON, AUTO'>\r\n"
                "<CURRENT>OFF</CURRENT>\r\n"
                "<STORED>OFF</STORED>\r\n"
                "<DEFAULT>OFF</DEFAULT>\r\n"
                "</WLAN-INTERNATIONAL-MODE>\r\n"
                "<WLAN-CHANNEL-MASK>\r\n"
                "<CURRENT>7FF</CURRENT>\r\n"
                "<STORED>7FF</STORED>\r\n"
                "<DEFAULT>7FF</DEFAULT>\r\n"
                "</WLAN-CHANNEL-MASK>\r\n"
                "<WEP-ENCRYPTION-INDEX ENUM='1, 2, 3, 4'>\r\n"
                "<CURRENT>1</CURRENT>\r\n"
                "<STORED>1</STORED>\r\n"
                "<DEFAULT>1</DEFAULT>\r\n"
                "</WEP-ENCRYPTION-INDEX>\r\n"
                "<WEP-AUTH-TYPE ENUM='OPEN, SHARED'>\r\n"
                "<CURRENT>OPEN</CURRENT>\r\n"
                "<STORED>OPEN</STORED>\r\n"
                "<DEFAULT>OPEN</DEFAULT>\r\n"
                "</WEP-AUTH-TYPE>\r\n"
                "<WEP-ENCRYPTION-KEY-1>\r\n"
                "<CURRENT>*****</CURRENT>\r\n"
                "<STORED>*****</STORED>\r\n"
                "<DEFAULT>*****</DEFAULT>\r\n"
                "</WEP-ENCRYPTION-KEY-1>\r\n"
                "<WEP-ENCRYPTION-KEY-2>\r\n"
                "<CURRENT>*****</CURRENT>\r\n"
                "<STORED>*****</STORED>\r\n"
                "<DEFAULT>*****</DEFAULT>\r\n"
                "</WEP-ENCRYPTION-KEY-2>\r\n"
                "<WEP-ENCRYPTION-KEY-3>\r\n"
                "<CURRENT>*****</CURRENT>\r\n"
                "<STORED>*****</STORED>\r\n"
                "<DEFAULT>*****</DEFAULT>\r\n"
                "</WEP-ENCRYPTION-KEY-3>\r\n"
                "<WEP-ENCRYPTION-KEY-4>\r\n"
                "<CURRENT>*****</CURRENT>\r\n"
                "<STORED>*****</STORED>\r\n"
                "<DEFAULT>*****</DEFAULT>\r\n"
                "</WEP-ENCRYPTION-KEY-4>\r\n"
                "<KERBEROS-USERNAME>\r\n"
                "<CURRENT></CURRENT>\r\n"
                "<STORED></STORED>\r\n"
                "<DEFAULT></DEFAULT>\r\n"
                "</KERBEROS-USERNAME>\r\n"
                "<KERBEROS-PASSWORD>\r\n"
                "<CURRENT>*****</CURRENT>\r\n"
                "<STORED>*****</STORED>\r\n"
                "<DEFAULT>*****</DEFAULT>\r\n"
                "</KERBEROS-PASSWORD>\r\n"
                "<KERBEROS-REALM>\r\n"
                "<CURRENT>kerberos</CURRENT>\r\n"
                "<STORED>kerberos</STORED>\r\n"
                "<DEFAULT>kerberos</DEFAULT>\r\n"
                "</KERBEROS-REALM>\r\n"
                "<KERBEROS-KDC>\r\n"
                "<CURRENT>krbtgt</CURRENT>\r\n"
                "<STORED>krbtgt</STORED>\r\n"
                "<DEFAULT>krbtgt</DEFAULT>\r\n"
                "</KERBEROS-KDC>\r\n"
                "<WLAN-USERNAME>\r\n"
                "<CURRENT></CURRENT>\r\n"
                "<STORED></STORED>\r\n"
                "<DEFAULT></DEFAULT>\r\n"
                "</WLAN-USERNAME>\r\n"
                "<WLAN-PASSWORD>\r\n"
                "<CURRENT>*****</CURRENT>\r\n"
                "<STORED>*****</STORED>\r\n"
                "<DEFAULT>*****</DEFAULT>\r\n"
                "</WLAN-PASSWORD>\r\n"
                "<WPA-PRE-SHARED-KEY>\r\n"
                "<CURRENT>*****</CURRENT>\r\n"
                "<STORED>*****</STORED>\r\n"
                "<DEFAULT>*****</DEFAULT>\r\n"
                "</WPA-PRE-SHARED-KEY>\r\n"
                "<WLAN-SECURITY ENUM='INVALID MODE, NONE, WEP 40-BIT, WEP 128-BIT, EAP-TLS, EAP-TTLS, EAP-FAST, PEAP, LEAP, WPA PSK, WPA EAP-TLS, WPA EAP-TTLS, WPA EAP-FAST, WPA PEAP, WPA LEAP'>\r\n"
                "<CURRENT>NONE</CURRENT>\r\n"
                "<STORED></STORED>\r\n"
                "<DEFAULT>NONE</DEFAULT>\r\n"
                "</WLAN-SECURITY>\r\n"
                "<PRIVATE-KEY>\r\n"
                "<CURRENT>*****</CURRENT>\r\n"
                "<STORED>*****</STORED>\r\n"
                "<DEFAULT>*****</DEFAULT>\r\n"
                "</PRIVATE-KEY>\r\n"
                "<REGION-CODE>\r\n"
                "<CURRENT>all</CURRENT>\r\n"
                "<STORED>all</STORED>\r\n"
                "<DEFAULT>all</DEFAULT>\r\n"
                "</REGION-CODE>\r\n"
                "<COUNTRY-CODE>\r\n"
                "<CURRENT>all</CURRENT>\r\n"
                "<STORED>all</STORED>\r\n"
                "<DEFAULT>all</DEFAULT>\r\n"
                "</COUNTRY-CODE>\r\n"
                "</WIRELESS-SETTINGS>\r\n"
                "</WIRELESS-PRINTSERVER>\r\n"
                "<CAPTURE>\r\n"
                "<CHANNEL1>\r\n"
                "<PORT ENUM='serial,usb,bt,parallel,off'>\r\n"
                "off</PORT>\r\n"
                "<DELIMITER>\r\n"
                "<![CDATA[\r\n"
                "]]></DELIMITER>\r\n"
                "<MAX-LENGTH>\r\n"
                "1000</MAX-LENGTH>\r\n"
                "<COUNT>\r\n"
                "0</COUNT>\r\n"
                "<DATA>\r\n"
                "<RAW>\r\n"
                "<![CDATA[]]></RAW>\r\n"
                "<MIME>\r\n"
                "<![CDATA[]]></MIME>\r\n"
                "</DATA>\r\n"
                "</CHANNEL1>\r\n"
                "</CAPTURE>\r\n"
                "<WEBLINK>\r\n"
                "<ENABLE BOOL='Y,N'>N</ENABLE>\r\n"
                "<PRINTER-RESET-REQUIRED BOOL='Y,N'>N</PRINTER-RESET-REQUIRED>\r\n"
                "<LOGGING>\r\n"
                "<MAX-ENTRIES>0</MAX-ENTRIES>\r\n"
                "</LOGGING>\r\n"
                "<IP>\r\n"
                "<CONN1>\r\n"
                "<LOCATION><![CDATA[]]></LOCATION>\r\n"
                "<RETRY-INTERVAL>10</RETRY-INTERVAL>\r\n"
                "<PROXY><![CDATA[]]></PROXY>\r\n"
                "<MAXIMUM-SIMULTANEOUS-CONNECTIONS>10</MAXIMUM-SIMULTANEOUS-CONNECTIONS>\r\n"
                "<AUTHENTICATION>\r\n"
                "<ENTRIES><![CDATA[]]></ENTRIES>\r\n"
                "</AUTHENTICATION>\r\n"
                "<TEST>\r\n"
                "<LOCATION><![CDATA[http://www.zebra.com/apps/linktest]]></LOCATION>\r\n"
                "<TEST-ON>failure</TEST-ON>\r\n"
                "<RETRY-INTERVAL>900</RETRY-INTERVAL>\r\n"
                "</TEST>\r\n"
                "</CONN1>\r\n"
                "<CONN2>\r\n"
                "<LOCATION><![CDATA[]]></LOCATION>\r\n"
                "<RETRY-INTERVAL>10</RETRY-INTERVAL>\r\n"
                "<PROXY><![CDATA[]]></PROXY>\r\n"
                "<MAXIMUM-SIMULTANEOUS-CONNECTIONS>10</MAXIMUM-SIMULTANEOUS-CONNECTIONS>\r\n"
                "<AUTHENTICATION>\r\n"
                "<ENTRIES><![CDATA[]]></ENTRIES>\r\n"
                "</AUTHENTICATION>\r\n"
                "<TEST>\r\n"
                "<LOCATION><![CDATA[http://www.zebra.com/apps/linktest]]></LOCATION>\r\n"
                "<TEST-ON>failure</TEST-ON>\r\n"
                "<RETRY-INTERVAL>900</RETRY-INTERVAL>\r\n"
                "</TEST>\r\n"
                "</CONN2>\r\n"
                "</IP>\r\n"
                "</WEBLINK>\r\n"
                "<ALERTS>\r\n"
                "<TRACKED_SETTINGS>\r\n"
                "<ZBI-NOTIFIED>\r\n"
                "<![CDATA[]]></ZBI-NOTIFIED>\r\n"
                "<LOG-TRACKED>\r\n"
                "<![CDATA[]]></LOG-TRACKED>\r\n"
                "<MAX-LOG-ENTRIES>\r\n"
                "100</MAX-LOG-ENTRIES>\r\n"
                "</TRACKED_SETTINGS>\r\n"
                "<HTTP>\r\n"
                "<PROXY>\r\n"
                "<![CDATA[]]></PROXY>\r\n"
                "<LOG-MAX-ENTRIES>\r\n"
                "0</LOG-MAX-ENTRIES>\r\n"
                "<AUTHENTICATION-ENTRIES>\r\n"
                "<![CDATA[]]></AUTHENTICATION-ENTRIES>\r\n"
                "</HTTP>\r\n"
                "</ALERTS>\r\n"
                "</SAVED-SETTINGS>\r\n"
                "<INTERFACES>\r\n"
                "<NETWORK>\r\n"
                "<ACTIVE-NETWORK-INTERFACE ENUM='Wireless, External Wired, UNKNOWN, Internal Wired'>\r\n"
                "Internal Wired</ACTIVE-NETWORK-INTERFACE>\r\n"
                "<NETWORK-SETTINGS-DIRTY BOOL='Y,N'>N</NETWORK-SETTINGS-DIRTY>\r\n"
                "<NETWORK-COMMON>\r\n"
                "<PROTOCOLS>\r\n"
                "<TCP>\r\n"
                "<ENABLED BOOL='Y,N'>Y</ENABLED>\r\n"
                "</TCP>\r\n"
                "<FTP>\r\n"
                "<ENABLED BOOL='Y,N'>Y</ENABLED>\r\n"
                "</FTP>\r\n"
                "<LPD>\r\n"
                "<ENABLED BOOL='Y,N'>Y</ENABLED>\r\n"
                "</LPD>\r\n"
                "<MAIL>\r\n"
                "<PS_DOMAIN>ZBRPrintServer.com</PS_DOMAIN>\r\n"
                "<SMTP>\r\n"
                "<ENABLED BOOL='Y,N'>Y</ENABLED>\r\n"
                "<SMTP-SERVER-ADDRESS>0.0.0.0</SMTP-SERVER-ADDRESS>\r\n"
                "</SMTP>\r\n"
                "<POP3>\r\n"
                "<ENABLED BOOL='Y,N'>Y</ENABLED>\r\n"
                "<POP3-SERVER-ADDRESS>0.0.0.0</POP3-SERVER-ADDRESS>\r\n"
                "<USER-NAME></USER-NAME>\r\n"
                "<PASSWORD>*****</PASSWORD>\r\n"
                "<POLLING-INTERVAL>240</POLLING-INTERVAL>\r\n"
                "</POP3>\r\n"
                "</MAIL>\r\n"
                "<TELNET>\r\n"
                "<ENABLED BOOL='Y,N'>Y</ENABLED>\r\n"
                "</TELNET>\r\n"
                "<UDP>\r\n"
                "<ENABLED BOOL='Y,N'>Y</ENABLED>\r\n"
                "<UDP-DISCOVERY-PORT>4201</UDP-DISCOVERY-PORT>\r\n"
                "</UDP>\r\n"
                "<HTTP>\r\n"
                "<ENABLED BOOL='Y,N'>Y</ENABLED>\r\n"
                "<HTTP-PORT>0</HTTP-PORT>\r\n"
                "</HTTP>\r\n"
                "<SNMP>\r\n"
                "<ENABLED BOOL='Y,N'>Y</ENABLED>\r\n"
                "<GET-COMMUNITY-NAME>public</GET-COMMUNITY-NAME>\r\n"
                "<SET-COMMUNITY-NAME>*****</SET-COMMUNITY-NAME>\r\n"
                "<TRAP-COMMUNITY-NAME>public</TRAP-COMMUNITY-NAME>\r\n"
                "</SNMP>\r\n"
                "</PROTOCOLS>\r\n"
                "</NETWORK-COMMON>\r\n"
                "<NETWORK-INTERFACE-SPECIFIC>\r\n"
                "<GENERAL>\r\n"
                "<MAC-ADDRESS>\r\n"
                "<INTERNAL-WIRED>00:07:4D:76:7F:55</INTERNAL-WIRED>\r\n"
                "<WIRELESS>00:00:00:00:00:00</WIRELESS>\r\n"
                "</MAC-ADDRESS>\r\n"
                "</GENERAL>\r\n"
                "<TCP>\r\n"
                "<IP-ADDRESS>\r\n"
                "<INTERNAL-WIRED>10.20.115.36</INTERNAL-WIRED>\r\n"
                "<WIRELESS>0.0.0.0</WIRELESS>\r\n"
                "</IP-ADDRESS>\r\n"
                "<SUBNET-MASK>\r\n"
                "<INTERNAL-WIRED>255.255.254.0</INTERNAL-WIRED>\r\n"
                "<WIRELESS>255.255.255.0</WIRELESS>\r\n"
                "</SUBNET-MASK>\r\n"
                "<DEFAULT-GATEWAY>\r\n"
                "<INTERNAL-WIRED>10.20.114.1</INTERNAL-WIRED>\r\n"
                "<WIRELESS>0.0.0.0</WIRELESS>\r\n"
                "</DEFAULT-GATEWAY>\r\n"
                "<IP-PROTOCOL ENUM='ALL, GLEANING ONLY, RARP, BOOTP, DHCP, DHCP AND BOOTP, PERMANENT'>\r\n"
                "<INTERNAL-WIRED>PERMANENT</INTERNAL-WIRED>\r\n"
                "<WIRELESS>ALL</WIRELESS>\r\n"
                "</IP-PROTOCOL>\r\n"
                "<DEFAULT-ADDRESS-ENABLED BOOL='YES,NO'>\r\n"
                "<INTERNAL-WIRED>YES</INTERNAL-WIRED>\r\n"
                "<WIRELESS>YES</WIRELESS>\r\n"
                "</DEFAULT-ADDRESS-ENABLED>\r\n"
                "<TIMEOUT-CHECKING-ENABLED BOOL='YES,NO'>\r\n"
                "<INTERNAL-WIRED>YES</INTERNAL-WIRED>\r\n"
                "<WIRELESS>YES</WIRELESS>\r\n"
                "</TIMEOUT-CHECKING-ENABLED>\r\n"
                "<TIMEOUT-CHECKING-VALUE>\r\n"
                "<INTERNAL-WIRED>300</INTERNAL-WIRED>\r\n"
                "<WIRELESS>300</WIRELESS>\r\n"
                "</TIMEOUT-CHECKING-VALUE>\r\n"
                "<ARP-INTERVAL>\r\n"
                "<INTERNAL-WIRED>0</INTERNAL-WIRED>\r\n"
                "<WIRELESS>0</WIRELESS>\r\n"
                "</ARP-INTERVAL>\r\n"
                "<BASE-RAW-PORT-NUMBER>\r\n"
                "<INTERNAL-WIRED>6101</INTERNAL-WIRED>\r\n"
                "<WIRELESS>6101</WIRELESS>\r\n"
                "</BASE-RAW-PORT-NUMBER>\r\n"
                "<BASE-RAW-PORT-NUMBER-ALTERNATE>\r\n"
                "<INTERNAL-WIRED>9100</INTERNAL-WIRED>\r\n"
                "<WIRELESS>9100</WIRELESS>\r\n"
                "</BASE-RAW-PORT-NUMBER-ALTERNATE>\r\n"
                "<BASE-JSON-CONFIG-PORT-NUMBER>\r\n"
                "<INTERNAL-WIRED>9200</INTERNAL-WIRED>\r\n"
                "<WIRELESS>9200</WIRELESS>\r\n"
                "</BASE-JSON-CONFIG-PORT-NUMBER>\r\n"
                "<WINS-ADDRESSING-PERMANENT BOOL='YES,NO'>\r\n"
                "<INTERNAL-WIRED>NO</INTERNAL-WIRED>\r\n"
                "<WIRELESS>NO</WIRELESS>\r\n"
                "</WINS-ADDRESSING-PERMANENT>\r\n"
                "<WINS-ADDRESS>\r\n"
                "<INTERNAL-WIRED>0.0.0.0</INTERNAL-WIRED>\r\n"
                "<WIRELESS>0.0.0.0</WIRELESS>\r\n"
                "</WINS-ADDRESS>\r\n"
                "</TCP>\r\n"
                "<DHCP-CLIENT-ID-SETTINGS>\r\n"
                "<ENABLED BOOL='YES,NO'>\r\n"
                "<INTERNAL-WIRED>NO</INTERNAL-WIRED>\r\n"
                "<WIRELESS>NO</WIRELESS>\r\n"
                "</ENABLED>\r\n"
                "<TYPE ENUM='STRING, MAC ADDRESS, HEX'>\r\n"
                "<INTERNAL-WIRED>MAC ADDRESS</INTERNAL-WIRED>\r\n"
                "<WIRELESS>MAC ADDRESS</WIRELESS>\r\n"
                "</TYPE>\r\n"
                "<PREFIX>\r\n"
                "<INTERNAL-WIRED></INTERNAL-WIRED>\r\n"
                "<WIRELESS></WIRELESS>\r\n"
                "</PREFIX>\r\n"
                "<SUFFIX>\r\n"
                "<INTERNAL-WIRED>00074D767F55</INTERNAL-WIRED>\r\n"
                "<WIRELESS>000000000000</WIRELESS>\r\n"
                "</SUFFIX>\r\n"
                "</DHCP-CLIENT-ID-SETTINGS>\r\n"
                "</NETWORK-INTERFACE-SPECIFIC>\r\n"
                "</NETWORK>\r\n"
                "</INTERFACES>\r\n"
                "<FORMAT-SETTINGS>\r\n"
                "<CODE-VALIDATION BOOL='Y,N'>N</CODE-VALIDATION>\r\n"
                "<REPRINT-AFTER-ERROR BOOL='Y,N'>Y</REPRINT-AFTER-ERROR>\r\n"
                "<MODE-UNITS ENUM='DOTS, INCHES, MILLIMETERS'>DOTS</MODE-UNITS>\r\n"
                "<LABEL-LENGTH MIN='0' MAX='7967'>346</LABEL-LENGTH>\r\n"
                "<LABEL-REVERSE BOOL='Y,N'>N</LABEL-REVERSE>\r\n"
                "<LABEL-SHIFT MIN='-9999' MAX='9999'>0</LABEL-SHIFT>\r\n"
                "<LABEL-HOME>\r\n"
                "<X-AXIS MIN='0' MAX='32000'>0</X-AXIS>\r\n"
                "<Y-AXIS MIN='0' MAX='32000'>0</Y-AXIS>\r\n"
                "</LABEL-HOME>\r\n"
                "<RELATIVE-DARKNESS MIN='-30.0' MAX='30.0'>0.0</RELATIVE-DARKNESS>\r\n"
                "<PRINT-RATE MIN='2.0' MAX='6.0'>2.0</PRINT-RATE>\r\n"
                "<VOID-PRINT-RATE MIN='2' MAX='6'>2</VOID-PRINT-RATE>\r\n"
                "<SLEW-RATE MIN='2.0' MAX='6.0'>2.0</SLEW-RATE>\r\n"
                "<BACKFEED-RATE MIN='2.0' MAX='6.0'>2.0</BACKFEED-RATE>\r\n"
                "<HEAD-TEST-INFO>\r\n"
                "<MANUAL-RANGE BOOL='Y,N'>N</MANUAL-RANGE>\r\n"
                "<FIRST-ELEMENT MIN='0' MAX='9999'>0</FIRST-ELEMENT>\r\n"
                "<LAST-ELEMENT MIN='0' MAX='9999'>9999</LAST-ELEMENT>\r\n"
                "</HEAD-TEST-INFO>\r\n"
                "<DEFAULT-FONT>\r\n"
                "<FONT-LETTER MIN='0' MAX='255'>48</FONT-LETTER>\r\n"
                "<HEIGHT MIN='1' MAX='9999'>45</HEIGHT>\r\n"
                "<WIDTH MIN='1' MAX='9999'>0</WIDTH>\r\n"
                "</DEFAULT-FONT>\r\n"
                "<DEFAULT-BARCODE>\r\n"
                "<RATIO MIN='2.0' MAX='3.0'>3.0</RATIO>\r\n"
                "<MODULE-WIDTH MIN='1' MAX='10'>3</MODULE-WIDTH>\r\n"
                "<HEIGHT MIN='1' MAX='9999'>69</HEIGHT>\r\n"
                "</DEFAULT-BARCODE>\r\n"
                "</FORMAT-SETTINGS>\r\n"
                "<STATUS>\r\n"
                "<TOTAL-LABELS-IN-BATCH>1</TOTAL-LABELS-IN-BATCH>\r\n"
                "<LABELS-REMAINING-IN-BATCH>0</LABELS-REMAINING-IN-BATCH>\r\n"
                "<PRINTHEAD-TEMP>\r\n"
                "<OVERTEMP-THRESHOLD>65</OVERTEMP-THRESHOLD>\r\n"
                "<UNDERTEMP-THRESHOLD>5</UNDERTEMP-THRESHOLD>\r\n"
                "<CURRENT>22</CURRENT>\r\n"
                "</PRINTHEAD-TEMP>\r\n"
                "<HEAD-ELEMENT-STATUS>\r\n"
                "<FAILED BOOL='Y,N'>N</FAILED>\r\n"
                "</HEAD-ELEMENT-STATUS>\r\n"
                "<HEAD-OPEN BOOL='Y,N'>N</HEAD-OPEN>\r\n"
                "<CONFIG-LOST-ERROR BOOL='Y,N'>N</CONFIG-LOST-ERROR>\r\n"
                "<RAM-ALLOCATION-ERROR BOOL='Y,N'>N</RAM-ALLOCATION-ERROR>\r\n"
                "<BITMAP-ALLOCATION-ERROR BOOL='Y,N'>N</BITMAP-ALLOCATION-ERROR>\r\n"
                "<STORED-FORMAT-ERROR BOOL='Y,N'>N</STORED-FORMAT-ERROR>\r\n"
                "<STORED-GRAPHIC-ERROR BOOL='Y,N'>N</STORED-GRAPHIC-ERROR>\r\n"
                "<STORED-BITMAP-ERROR BOOL='Y,N'>N</STORED-BITMAP-ERROR>\r\n"
                "<STORED-FONT-ERROR BOOL='Y,N'>N</STORED-FONT-ERROR>\r\n"
                "<CACHE-MEMORY-ERROR BOOL='Y,N'>N</CACHE-MEMORY-ERROR>\r\n"
                "<BASIC-FORCED-ERROR BOOL='Y,N'>N</BASIC-FORCED-ERROR>\r\n"
                "<HEAD-UNDERTEMP-WARNING BOOL='Y,N'>N</HEAD-UNDERTEMP-WARNING>\r\n"
                "<HEAD-OVERTEMP-ERROR BOOL='Y,N'>N</HEAD-OVERTEMP-ERROR>\r\n"
                "<RIBBON-IN-WARNING BOOL='Y,N'>N</RIBBON-IN-WARNING>\r\n"
                "<BUFFER-FULL-ERROR BOOL='Y,N'>N</BUFFER-FULL-ERROR>\r\n"
                "<CLEAN-PRINTHEAD-WARNING BOOL='Y,N'>N</CLEAN-PRINTHEAD-WARNING>\r\n"
                "<CUTTER-JAM-ERROR BOOL='Y,N'>N</CUTTER-JAM-ERROR>\r\n"
                "<COVER-OPEN BOOL='Y,N'>N</COVER-OPEN>\r\n"
                "<RIBBON-TENSION-ERROR BOOL='Y,N'>N</RIBBON-TENSION-ERROR>\r\n"
                "<VERIFIER-ERROR BOOL='Y,N'>N</VERIFIER-ERROR>\r\n"
                "<RIBBON-LOW-WARNING BOOL='Y,N'>N</RIBBON-LOW-WARNING>\r\n"
                "<MEDIA-LOW-WARNING BOOL='Y,N'>N</MEDIA-LOW-WARNING>\r\n"
                "<NUMBER-OF-FORMATS>1</NUMBER-OF-FORMATS>\r\n"
                "<PARTIAL-FORMAT-IN-PROGRESS BOOL='Y,N'>N</PARTIAL-FORMAT-IN-PROGRESS>\r\n"
                "<PAUSE BOOL='Y,N'>N</PAUSE>\r\n"
                "<PAPER-OUT BOOL='Y,N'>N</PAPER-OUT>\r\n"
                "<RIBBON-OUT BOOL='Y,N'>N</RIBBON-OUT>\r\n"
                "<PRINTER-COUNTER>\r\n"
                "<COUNTER1>\r\n"
                "<INCHES>1330401</INCHES>\r\n"
                "<CENTIMETERS>3379218</CENTIMETERS>\r\n"
                "<LABELS>443279</LABELS>\r\n"
                "</COUNTER1>\r\n"
                "<COUNTER2>\r\n"
                "<INCHES>1330401</INCHES>\r\n"
                "<CENTIMETERS>3379218</CENTIMETERS>\r\n"
                "<LABELS>443279</LABELS>\r\n"
                "</COUNTER2>\r\n"
                "<NON-RESET-COUNTER>\r\n"
                "<INCHES>1330401</INCHES>\r\n"
                "<CENTIMETERS>3379218</CENTIMETERS>\r\n"
                "<LABELS>50063</LABELS>\r\n"
                "</NON-RESET-COUNTER>\r\n"
                "</PRINTER-COUNTER>\r\n"
                "<MEDIA-REPLACED>0</MEDIA-REPLACED>\r\n"
                "<RIBBON-REPLACED>0</RIBBON-REPLACED>\r\n"
                "<HEAD-CLEANED>1330401</HEAD-CLEANED>\r\n"
                "<CLOCK>\r\n"
                "<DATE>\r\n"
                "20161102</DATE>\r\n"
                "<TIME>\r\n"
                "16:44:43</TIME>\r\n"
                "</CLOCK>\r\n"
                "<SENSOR-SELECT>REFLECTIVE</SENSOR-SELECT>\r\n"
                "</STATUS>\r\n"
                "<OBJECT-LIST>\r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='TTF' FORMAT='ZPL' SIZE='125904' PROTECTED='Y'>0</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='6839' PROTECTED='Y'>A</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>AZTEC</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='7746' PROTECTED='Y'>B</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='128' PROTECTED='Y'>BLUETOOTH_ICON</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='128' PROTECTED='Y'>BLUETOOTH_NOT_AVAILABLE_ICON</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>CODABAR</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>CODABLK</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>CODE11</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>CODE128</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>CODE39</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>CODE49</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>CODE93</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='10648' PROTECTED='Y'>D</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='128' PROTECTED='Y'>DATA_BLANK_ICON</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='128' PROTECTED='Y'>DATA_ICON</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='WML' FORMAT='ZPL' SIZE='2996' PROTECTED='Y'>DISPLYQR</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='122' PROTECTED='Y'>DOWN_ARROW_ICON</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='15691' PROTECTED='Y'>E12</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='47056' PROTECTED='Y'>E24</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='8520' PROTECTED='Y'>E6</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='10893' PROTECTED='Y'>E8</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>EAN-13</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>EAN-8</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='ZPL' FORMAT='ZPL' SIZE='3830' PROTECTED='Y'>ELEMENTOUT</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='17718' PROTECTED='Y'>EPL1</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='20918' PROTECTED='Y'>EPL2</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='24118' PROTECTED='Y'>EPL3</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='24118' PROTECTED='Y'>EPL300-1</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='30518' PROTECTED='Y'>EPL300-2</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='51318' PROTECTED='Y'>EPL300-3</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='72686' PROTECTED='Y'>EPL300-4</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='107958' PROTECTED='Y'>EPL300-5</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='32870' PROTECTED='Y'>EPL4</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='58038' PROTECTED='Y'>EPL5</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='8498' PROTECTED='Y'>EPL6</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='8928' PROTECTED='Y'>EPL7</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='128' PROTECTED='Y'>ETHERNET_ICON</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='13275' PROTECTED='Y'>F</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='ZPL' FORMAT='ZPL' SIZE='10420' PROTECTED='Y'>FIRSTDOTLOCATION</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='49663' PROTECTED='Y'>G</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='5470' PROTECTED='Y'>GS</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='11536' PROTECTED='Y'>H12</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='30436' PROTECTED='Y'>H24</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='7247' PROTECTED='Y'>H6</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='7825' PROTECTED='Y'>H8</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='WML' FORMAT='ZPL' SIZE='2429' PROTECTED='Y'>HOMEMENU</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>I2OF5</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>IDMATRIX</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='ZPL' FORMAT='ZPL' SIZE='9524' PROTECTED='Y'>IMAGECOMPRESSION</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>IND2OF5</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='WML' FORMAT='ZPL' SIZE='10189' PROTECTED='Y'>INDEX</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='400' PROTECTED='Y'>LANGUAGE</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='WML' FORMAT='ZPL' SIZE='12734' PROTECTED='Y'>LANGUAGE</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>LOGMARS</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='PNG' FORMAT='ZPL' SIZE='20154' PROTECTED='Y'>LOGO</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>MAXICODE</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='128' PROTECTED='Y'>MEDIA_BLANK_ICON</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='128' PROTECTED='Y'>MEDIA_ICON</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='TXT' FORMAT='ZPL' SIZE='46572' PROTECTED='Y'>MIB200</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>MICROPDF</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='5570' PROTECTED='Y'>MONOBD15</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>MSICODE</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='400' PROTECTED='Y'>NETWORK</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='WML' FORMAT='ZPL' SIZE='25574' PROTECTED='Y'>NETWORK</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='359678' PROTECTED='Y'>NJ20WGL4</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='710064' PROTECTED='Y'>NK20WGL4</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='1248664' PROTECTED='Y'>NS20WGL4</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='847138' PROTECTED='Y'>NT20WGL4</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='58' PROTECTED='Y'>ONEDOT</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='116' PROTECTED='Y'>P</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='WML' FORMAT='ZPL' SIZE='1304' PROTECTED='Y'>PASSWORD</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>PDF417</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>PLANETCD</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>PLESSEY</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='400' PROTECTED='Y'>PORTS</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='WML' FORMAT='ZPL' SIZE='8018' PROTECTED='Y'>PORTS</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>POSTNET</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='116' PROTECTED='Y'>Q</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='WML' FORMAT='ZPL' SIZE='3598' PROTECTED='Y'>QCKCNTDO</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='WML' FORMAT='ZPL' SIZE='2673' PROTECTED='Y'>QCKCNTMK</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>QRCODE</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='116' PROTECTED='Y'>R</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='NRD' FORMAT='ZPL' SIZE='297896' PROTECTED='Y'>REGDB</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='NRD' FORMAT='ZPL' SIZE='3' PROTECTED='Y'>REPRINT</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='NRD' FORMAT='ZPL' SIZE='3' PROTECTED='Y'>RESETNET</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='XML' FORMAT='ZPL' SIZE='32780' PROTECTED='Y'>RFIDRCPE</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='126' PROTECTED='Y'>RIBBON_IN_ICON</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='128' PROTECTED='Y'>RIBBON_OUT_ICON</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>RSS</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='116' PROTECTED='Y'>S</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>S2OF5</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='400' PROTECTED='Y'>SENSORS</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='WML' FORMAT='ZPL' SIZE='10293' PROTECTED='Y'>SENSORS</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='400' PROTECTED='Y'>SETTINGS</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='WML' FORMAT='ZPL' SIZE='17072' PROTECTED='Y'>SETTINGS</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='128' PROTECTED='Y'>SIGNAL_STRENGTH_0_BAR_ICON</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='128' PROTECTED='Y'>SIGNAL_STRENGTH_1_BAR_ICON</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='128' PROTECTED='Y'>SIGNAL_STRENGTH_2_BAR_ICON</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='128' PROTECTED='Y'>SIGNAL_STRENGTH_3_BAR_ICON</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='128' PROTECTED='Y'>SIGNAL_STRENGTH_4_BAR_ICON</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='222' PROTECTED='Y'>SPACE20</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='382' PROTECTED='Y'>SPACE34</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='116' PROTECTED='Y'>T</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='WML' FORMAT='ZPL' SIZE='16941' PROTECTED='Y'>TELNET</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>TLC39</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='400' PROTECTED='Y'>TOOLS</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='WML' FORMAT='ZPL' SIZE='24248' PROTECTED='Y'>TOOLS</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='116' PROTECTED='Y'>U</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='SS' FORMAT='ZPL' SIZE='11596' PROTECTED='Y'>UIF</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>UPC-A</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>UPC-E</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BAR' FORMAT='ZPL' SIZE='0' PROTECTED='Y'>UPC-EAN</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='BMP' FORMAT='ZPL' SIZE='122' PROTECTED='Y'>UP_ARROW_ICON</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='SS' FORMAT='ZPL' SIZE='11588' PROTECTED='Y'>UTT</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='Z:' TYPE='FNT' FORMAT='ZPL' SIZE='116' PROTECTED='Y'>V</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='E:' TYPE='GRF' FORMAT='ZPL' SIZE='4100' PROTECTED='N'>DAFIT000</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='E:' TYPE='GRF' FORMAT='ZPL' SIZE='4100' PROTECTED='N'>DAFIT001</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='E:' TYPE='GRF' FORMAT='ZPL' SIZE='7684' PROTECTED='N'>KANUI000</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='E:' TYPE='GRF' FORMAT='ZPL' SIZE='7684' PROTECTED='N'>KANUI001</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='E:' TYPE='GRF' FORMAT='ZPL' SIZE='7044' PROTECTED='N'>TRICA000</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='E:' TYPE='GRF' FORMAT='ZPL' SIZE='10244' PROTECTED='N'>TRICA001</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='E:' TYPE='TTF' FORMAT='ZPL' SIZE='169188' PROTECTED='Y'>TT0003M_</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='A:' TYPE='GRF' FORMAT='ZPL' SIZE='4100' PROTECTED='N'>DAFIT000</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='A:' TYPE='GRF' FORMAT='ZPL' SIZE='4100' PROTECTED='N'>DAFIT001</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='A:' TYPE='GRF' FORMAT='ZPL' SIZE='7684' PROTECTED='N'>KANUI000</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='A:' TYPE='GRF' FORMAT='ZPL' SIZE='7684' PROTECTED='N'>KANUI001</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='A:' TYPE='GRF' FORMAT='ZPL' SIZE='7044' PROTECTED='N'>TRICA000</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='A:' TYPE='GRF' FORMAT='ZPL' SIZE='10244' PROTECTED='N'>TRICA001</OBJECT> \r\n"
                "<OBJECT MEMORY-LOCATION='A:' TYPE='TTF' FORMAT='ZPL' SIZE='169188' PROTECTED='Y'>TT0003M_</OBJECT> \r\n"
                "</OBJECT-LIST>\r\n"
                "</ZEBRA-ELTRON-PERSONALITY>"
               )


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
