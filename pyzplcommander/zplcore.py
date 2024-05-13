from __future__ import annotations
from abc import ABC, abstractmethod

from pyzplcommander.zplcommands import ZplCommands


class ZplCommandSender(ABC):

    @abstractmethod
    def send_command(self, command: ZplCommands | str | bytes, get_response: bool = False) -> None | str:
        pass

    @abstractmethod
    def send_commands(self, commands: list[ZplCommands | str | bytes], get_response: bool = False) -> list[str] | None:
        pass


class ZplCommandsDump:

    printer: ZplCommandSender
    _commands_zpl: dict[int, list[str]]
    _cmd_start: str
    _cmd_end: str

    def __init__(self, printer: ZplCommandSender = None, cmd_start_block: str = None, cmd_end_block: str = None):
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

    def _return_printer(self, printer: ZplCommandSender = None):
        if printer is None:
            printer = self.printer
        return printer

    def send_command(self, printer: ZplCommandSender = None, get_response: bool = False) -> list[str] | None:
        return self._return_printer(printer).send_command(self.dump_zpl(), get_response=get_response)

    def send_commands(self, format_values: list[dict], printer: ZplCommandSender = None,
                      get_response: bool = False) -> list[str] | None:
        model_command = self.dump_zpl()
        commands = []
        for values_format in format_values:
            commands.append(model_command.format(**values_format))

        return self._return_printer(printer).send_commands(commands, get_response=get_response)
