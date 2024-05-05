from __future__ import annotations
from abc import ABC, abstractmethod
import socket

from pyzplcommander.zplcommands import ZplCommands, ZplStandardFonts, ZplOrientation, ZplDirection, ZplJustification


class ZplPrinter(ABC):

    @abstractmethod
    def send_command(self, command: ZplCommands | str | bytes, get_response: bool = False) -> None | str:
        pass

    @abstractmethod
    def send_commands(self, commands: list[ZplCommands | str | bytes], get_response: bool = False) -> list[str] | None:
        pass

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


class ZplCommandsDump:

    printer: ZplPrinter | str
    _commands_zpl: dict[int, list[str]]
    _cmd_start: str
    _cmd_end: str

    def __init__(self, printer: ZplPrinter | str = None, cmd_start_block: str = None, cmd_end_block: str = None):
        self.printer = printer
        self._commands_zpl = {}
        self._cmd_start = cmd_start_block
        self._cmd_end = cmd_end_block

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.send_command()

    @staticmethod
    def _compile_params(params: list[any]) -> str:
        if params is None or len(params) < 1:
            return ''

        last_value = -1
        for index in range(len(params)-1, -1, -1):
            if params[index] is not None:
                last_value = index
                break

        return ','.join(map(lambda x: None if x is None else str(x), params[:last_value+1]))

    def dump_zpl(self, break_lines: bool = True):
        break_lines = '\r\n' if break_lines else ''
        zpl_dump = None
        for order_cmd in sorted(self._commands_zpl.keys()):
            if zpl_dump is None:
                zpl_dump = (self._cmd_start + break_lines) if self._cmd_start else ''
            else:
                zpl_dump += break_lines
            zpl_dump += break_lines.join(self._commands_zpl[order_cmd])
        return zpl_dump + ((break_lines + self._cmd_end) or '')

    def add_command(self, command: ZplCommands | str, params: list[any] = None, position: int = 0) -> ZplCommandsDump:
        if isinstance(command, ZplCommands):
            command = command.value.command

        cmd = command + self._compile_params(params)

        if position not in self._commands_zpl:
            self._commands_zpl[position] = []

        self._commands_zpl[position].append(cmd)
        return self

    def set_command(self, command: ZplCommands | str, params: list[any] = None, position: int = 0) -> ZplCommandsDump:
        self._commands_zpl[position] = []
        return self.add_command(command, params, position)

    def _return_printer(self, printer: ZplPrinter | str = None):
        if printer is None:
            printer = self.printer
        if isinstance(printer, str):
            printer = ZplNetworkPrinter(printer)
        return printer

    def send_command(self, printer: ZplPrinter | str = None, get_response: bool = False) -> list[str] | None:
        return self._return_printer(printer).send_command(self.dump_zpl(), get_response=get_response)

    def send_commands(self, format_values: list[dict], printer: ZplPrinter | str = None,
                      get_response: bool = False) -> list[str] | None:
        model_command = self.dump_zpl()
        commands = []
        for values_format in format_values:
            commands.append(model_command.format(**values_format))

        return self._return_printer(printer).send_commands(commands, get_response=get_response)


class ZplLabelField(ZplCommandsDump):

    zpl_label: ZplLabel

    def __init__(self, zpl_label: ZplLabel):
        super().__init__(cmd_end_block=ZplCommands.FIELD_SEPARATOR.value.command)
        self.zpl_label = zpl_label

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finalize_field()

    def finalize_field(self) -> ZplLabel:
        self.zpl_label.add_command(self.dump_zpl(break_lines=False))
        return self.zpl_label

    def add_text(self, text_value) -> ZplLabelField:
        self.set_command(ZplCommands.FIELD_DATA, position=10)
        self.add_command(text_value, position=11)
        return self

    def set_text(self, text_value) -> ZplLabelField:
        self.set_command(ZplCommands.FIELD_DATA, position=10)
        self.set_command(text_value, position=11)
        return self

    def position(self, x: int, y: int):
        self.add_command(ZplCommands.FIELD_ORIGIN, [x, y])
        return self

    def font(self, font_name: str | ZplStandardFonts, orientation: str | ZplOrientation = None,
             height: int = None, width: int = None):

        if isinstance(font_name, ZplStandardFonts):
            font_name = font_name.value.name

        if isinstance(orientation, ZplOrientation):
            orientation = orientation.value

        self.add_command(ZplCommands.FIELD_FONT, [font_name, orientation, height, width])
        return self

    def custom_font(self, font: str, orientation: str | ZplOrientation = None,
                    height: int = None, width: int = None):

        if isinstance(orientation, ZplOrientation):
            orientation = orientation.value

        self.add_command(ZplCommands.FIELD_FONT, [orientation, height, width, font])
        return self

    def direction(self, direction: str | ZplDirection = 'V', additional_chars: int = None):

        if isinstance(direction, ZplDirection):
            direction = direction.value

        self.add_command(ZplCommands.FIELD_DIRECTION, [direction, additional_chars])
        return self

    def multiline_block(self, width_block: int = None, number_lines: int = None, space_between_lines: int = None,
                        text_justification: str | ZplJustification = None, indent_seconds_line: int = None):

        if isinstance(text_justification, ZplJustification):
            text_justification = text_justification.value

        self.add_command(ZplCommands.FIELD_BLOCK, [
            width_block, number_lines, space_between_lines, text_justification, indent_seconds_line
        ])
        return self


class ZplLabel(ZplCommandsDump):

    def __init__(self, printer: ZplPrinter | str = None):
        super().__init__(
            printer,
            ZplCommands.LABEL_START_BLOCK.value.command,
            ZplCommands.LABEL_END_BLOCK.value.command
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.send_command()

    def font(self, font: ZplStandardFonts | str, height: int | None = None, width: int | None = None):
        if isinstance(font, ZplStandardFonts):
            font = font.value.name

        self.add_command(ZplCommands.LABEL_FONT_DEFAULT, [font, height, width])
        return self

    def comment(self, comment: str):
        self.add_command(ZplCommands.FIELD_COMMENT, [comment])
        return self

    def new_field(self) -> ZplLabelField:
        return ZplLabelField(self)
