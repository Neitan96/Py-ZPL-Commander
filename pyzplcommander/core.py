from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal
import copy


class ZplCommandSender(ABC):
    """ZplCommandSender é uma classe abstrata para classes que enviam comandos ZPL."""

    @abstractmethod
    def send_command(self, command: str | any, get_response: bool = False) -> None | str:
        """Envia um comando ZPL.

        Args:
            command (str | any): Comando ZPL
            get_response (bool, optional): Obter resposta do comando
        """
        pass

    def send_commands(self, commands: list[str | any], get_response: bool = False) -> None | list[str]:
        """Envia uma lista de comandos ZPL.

        Args:
            commands (list[str | any]): Lista de comandos ZPL
            get_response (bool, optional): Obter resposta do comando
        """
        results = []
        for command in commands:
            results.append(self.send_command(command, get_response))

        if get_response:
            return results


@dataclass
class FontDotsProperties:
    """FontDotsProperties é uma classe para representar as propriedades de uma fonte.
    Usada para armazenar as propriedades de uma fonte de texto para cálculos de impressão.

    Args:
        letter_width (int): Largura da letra em pontos
        letter_height (int): Altura da letra em pontos
        space_width (int): Largura do espaço em pontos
    """

    letter_width: int  # Largura da letra em pontos
    letter_height: int  # Altura da letra em pontos
    space_width: int  # Largura do espaço em pontos


@dataclass
class ZebraProperties:
    """ZebraProperties é uma classe para representar as propriedades da impressora Zebra.
    É usada para armazenar as propriedades da impressora, de impressão, de etiquetas ou de campos.

    Feita para cálcular posições e tamanho de campos e etiqueta dinamicamente cam base nos comandos e parâmetros,
    sem precisar de cálculos manuais.

    Ao cálcular dinamicamente as posições e tamanhos, é possível criar etiquetas e campos de forma dinâmica,
    sem precisar fazer testes e ajustes manuais.
    """

    # Propriedades da impressora
    density: Literal[6, 8, 12, 24] = field(default=8)  # Densidade de impressão em pontos por milímetro

    # Propriedades da etiqueta
    label_width: int = field(default=101)  # Largura da etiqueta em milímetros
    label_height: int = field(default=152)  # Altura da etiqueta em milímetros

    # Propriedades voláteis
    font_dots: FontDotsProperties = field(default=None)  # Propriedades da fonte de texto
    prefix_format: str = field(default='^')  # Prefixo do formato ZPL
    prefix_command: str = field(default='~')  # Prefixo do comando ZPL
    params_delimiter: str = field(default=',')  # Delimitador de parâmetros


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class ZplDump(ABC):
    """ZplDump é uma classe abstrata para classes que geram um dump de comandos ZPL."""

    @abstractmethod
    def dump_zpl(self, zebra_props: ZebraProperties = None, break_lines: bool = True) -> str:
        """Gera um dump de comandos ZPL.

        Args:
            zebra_props (ZebraProperties, optional): Propriedades da impressora
            break_lines (bool, optional): Quebra de linha
        Returns:
            str: Dump de comandos ZPL
        """
        pass

    def get_new_properties(self, zebra_props: ZebraProperties) -> ZebraProperties:
        """Retorna um novo objeto ZebraProperties com as propriedades atualizadas.
        Usado para quando o ZPL faz alterações nas propriedades, caso não faça alterações, retorna o mesmo objeto.

        Args:
            zebra_props (ZebraProperties): Propriedades da impressora
        """
        return zebra_props

    def get_origin_position(self, zebra_props: ZebraProperties) -> (int, int):
        """Retorna a posição inicial do objeto ZPL em pontos.

        Args:
            zebra_props (ZebraProperties): Propriedades da impressora
        Returns:
            int: Posição X em pontos
            int: Posição Y em pontos
        """
        return -1, -1

    def get_size(self, zebra_props: ZebraProperties) -> (int, int):
        """Retorna o tamanho do objeto ZPL em pontos.

        Args:
            zebra_props (ZebraProperties): Propriedades da impressora
        Returns:
            int: Largura em pontos
            int: Altura em pontos
        """
        return -1, -1

    def send_to(self, sender: ZplCommandSender, get_response: bool = False) -> None | str:
        """Envia o comando ZPL.

        Args:
            sender (ZplCommandSender): Objeto que envia o comando
            get_response (bool, optional): Obter resposta do comando
        """
        return sender.send_command(self.dump_zpl(), get_response)

    def __str__(self):
        """Retorna o dump de comandos ZPL."""
        return self.dump_zpl()


class ZplCommand(ZplDump):
    """ZplCommand é uma classe para representar um comando ZPL.

    Contém informações sobre o comando, como descrição, parâmetros, valores, etc.

    Args:
        command (str): O comando ZPL, ex: '^FO'
        cmd_type (Literal['format', 'command']): Tipo do comando, 'format' para comandos de formatação
                                                e 'command' para comandos de impressão
        description (str, optional): Descrição do comando
        params_description (list[str], optional): Lista de descrições dos parâmetros
        params_default (list[str], optional): Lista de valores padrão dos parâmetros
        params_required (int, optional): Quantidade de parâmetros obrigatórios
        command_response (bool, optional): Se o comando retorna uma resposta
    """

    _command: str
    _cmd_type: Literal['format', 'command']
    _description: str
    _params_description: list[str]
    _params_default: list[str]
    _params_required: int
    _command_response: bool

    def __init__(self, command: str, cmd_type: Literal['format', 'command'], description: str = None,
                 params_description: list[str] = None, params_default: list[str] = None,
                 params_required: int = 0, command_response: bool = False):
        self._command = command
        self._cmd_type = cmd_type
        self._description = description
        self._params_description = params_description
        self._params_default = params_default
        self._params_required = params_required
        self._command_response = command_response

    @property
    def command(self) -> str:
        """Retorna o comando ZPL."""
        return self._command

    @property
    def cmd_type(self) -> Literal['format', 'command']:
        """Retorna o tipo do comando."""
        return self._cmd_type

    @property
    def description(self) -> str:
        """Retorna a descrição do comando."""
        return self._description

    @property
    def params_description(self) -> list[str]:
        """Retorna a lista de descrições dos parâmetros."""
        return self._params_description

    @property
    def params_default(self) -> list[str]:
        """Retorna a lista de valores padrão dos parâmetros."""
        return self._params_default

    @property
    def params_required(self) -> int:
        """Retorna a quantidade de parâmetros obrigatórios."""
        return self._params_required

    @property
    def command_response(self) -> bool:
        """Retorna se o comando retorna uma resposta."""
        return self._command_response

    def _prefix_param(self, zebra_props: ZebraProperties = None) -> str:
        """Retorna o prefixo do comando ZPL.

        Args:
            zebra_props (ZebraProperties): Propriedades da impressora
        """
        if self.cmd_type == 'format':
            return zebra_props.prefix_format if zebra_props is not None else '^'

        if self.cmd_type == 'command':
            return zebra_props.prefix_command if zebra_props is not None else '~'

        return ''

    def dump_zpl(self, zebra_props: ZebraProperties = None, break_lines: bool = True) -> str:
        """Retorna o comando ZPL com prefixo.

        Args:
            zebra_props (ZebraProperties, optional): Propriedades da impressora
            break_lines (bool, optional): Quebra de linha
        Returns:
            str: Dump de comandos ZPL
        """
        return self._prefix_param(zebra_props) + self._command

    def get_param_index(self, param: str) -> int:
        """Retorna o índice do parâmetro pelo nome do parâmetro.

        Args:
            param (str): Nome do parâmetro
        """
        if param is None or self._params_description is None:
            return -1
        return self._params_description.index(param)

    def command_params(self, params: list[str | any] = None) -> ZplCommandParams:
        """Cria um novo comando com parâmetros.

        Args:
            params (list[str], optional): Lista de parâmetros
        """
        return self(params)

    def __copy__(self):
        return ZplCommand(self._command, self._cmd_type, self._description, self._params_description,
                          self._params_default, self._params_required, self._command_response)

    def __deepcopy__(self, memo):
        return ZplCommand(self._command, self._cmd_type, self._description, self._params_description,
                          self._params_default, self._params_required, self._command_response)

    def __call__(self, *params) -> ZplCommandParams:
        """Cria um novo comando com parâmetros.

        Args:
            params: Parâmetros
        """
        params = params[0] if len(params) == 1 and isinstance(params[0], list) else list(params)
        return ZplCommandParams(copy.copy(self), params)

    def __repr__(self):
        return (f'<ZplCommand: {self._command}, '
                f'Type: {self._cmd_type}, '
                f'Description: {self._description}>, '
                f'Params: {self._params_description}>')


class ZplCommandParams(ZplDump):
    """ZplCommandParams é uma classe para representar um comando ZPL com parâmetros.

    Args:
        command (ZplCommand | str): Comando ZPL
        params (list[str], optional): Lista de parâmetros
    """

    command: ZplCommand | str
    params: list[str | None]

    def __init__(self, command: ZplCommand | str, params: list[str | any] = None):
        self.command = command
        self.params = [str(param) if param is not None else None for param in params]

    def set_param_by_name(self, param: str, value: str):
        """Define o valor de um parâmetro pelo nome do parâmetro.

        Args:
            param (str): Nome do parâmetro
            value(str): Valor do parâmetro
        """
        self.set_param(self.command.get_param_index(param), value)

    def set_param(self, index: int, value: str):
        """Define o valor de um parâmetro pelo índice do parâmetro.

        Args:
            index (int): Índice do parâmetro
            value(str): Valor do parâmetro
        """
        if index < 0 or index is None:
            return
        if self.params is None:
            self.params = []
        while len(self.params) <= index:
            self.params.append(None)
        self.params[index] = value

    def append_param(self, value: str):
        """Adiciona um valor ao final da lista de parâmetros.

        Args:
            value(str): Valor do parâmetro
        """
        if self.params is None:
            self.params = []
        self.params.append(value)

    def get_param(self, index: int) -> str | None:
        """Retorna o valor de um parâmetro pelo índice do parâmetro.

        Args:
            index (int): Índice do parâmetro
        """
        if self.params is not None and index in self.params:
            return self.params[index]
        return None

    def get_param_by_name(self, param: str) -> str | None:
        """Retorna o valor de um parâmetro pelo nome do parâmetro.

        Args:
            param (str): Nome do parâmetro
        """
        index = self.command.get_param_index(param)
        if index < 0:
            return None
        return self.params[index]

    @staticmethod
    def format_params_to_zpl(params: list[any]) -> str:
        """Formata os parâmetros para o formato ZPL.

        Args:
            params (list[any]): Lista de parâmetros
        """
        if params is None or len(params) < 1:
            return ''

        last_value = -1
        for index in range(len(params)-1, -1, -1):
            if params[index] is not None:
                last_value = index
                break

        return ','.join(map(lambda x: '' if x is None else str(x), params[:last_value+1]))

    def dump_zpl(self, zebra_props: ZebraProperties = None, break_lines: bool = True) -> str:
        """Retorna o comando ZPL com parâmetros.

        Args:
            zebra_props (ZebraProperties, optional): Propriedades da impressora
            break_lines (bool, optional): Quebra de linha
        Returns:
            str: Dump de comandos ZPL
        """
        if isinstance(self.command, ZplDump):
            return self.command.dump_zpl(zebra_props, break_lines) + self.format_params_to_zpl(self.params)

        return str(self.command)+self.format_params_to_zpl(self.params)

    def __repr__(self):
        return f'<ZplCommandValue: {self.command.__repr__()}, Params: {",".join(self.params)}>'


class ZplCommandsBlock(ZplDump):
    """ZplCommandsBlock é uma classe para representar um bloco de comandos ZPL.

    Args:
        start_block (ZplCommandValue, optional): Comando de início do bloco
        end_block (ZplCommandValue, optional): Comando de fim do bloco
    """

    start_block: str
    end_block: str
    commands: dict[str, list[ZplCommandParams | str]]

    zpl_dump_zpl: None | str
    zpl_dump_props: None | ZebraProperties
    zpl_dump_x: None | int
    zpl_dump_y: None | int
    zpl_dump_width: None | int
    zpl_dump_height: None | int

    def __init__(self, start_block: str = None, end_block: str = None):
        self.start_block = start_block
        self.end_block = end_block
        self.commands = {}
        self._reset_zpl_dump()

    def _reset_zpl_dump(self):
        self.zpl_dump_zpl = None
        self.zpl_dump_props = None
        self.zpl_dump_x = None
        self.zpl_dump_y = None
        self.zpl_dump_width = None
        self.zpl_dump_height = None

    def add_command(self, command: ZplCommandParams | ZplCommandsBlock | str, position: int | str = 0):
        """Adiciona um comando ao bloco.

        Args:
            command (ZplCommandParams | str): Comando ZPL
            position (int | str, optional): Posição do comando
        """
        position = str(position)
        if position not in self.commands:
            self.commands[position] = []
        self.commands[position].append(command)
        self._reset_zpl_dump()
        return self

    def new_command(self, command: ZplCommand, position: int | str = 0) -> ZplCommandParams:
        """Cria um novo comando ao bloco.

        Args:
            command (ZplCommand): Comando ZPL
            position (int | str, optional): Posição do comando

        Returns:
            ZplCommandParams: Comando criado
        """
        cmd_value = ZplCommandParams(command)
        self.add_command(cmd_value, position)
        return cmd_value

    def set_command(self, command: ZplCommandParams | ZplCommandsBlock | str, position: int | str = 0):
        """Define um comando ao bloco.

        Args:
            command (ZplCommandParams | str): Comando ZPL
            position (int | str, optional): Posição do comando
        """
        position = str(position)
        self.commands[position] = []
        self.add_command(command, position)
        return self

    def get_commands(self) -> list[ZplCommandParams | ZplCommandsBlock | str]:
        """Retorna a lista de comandos."""
        return [cmd for order in sorted(self.commands.keys()) for cmd in self.commands[order]]

    def get_commands_by_position(self, position: int | str) -> list[ZplCommandParams | ZplCommandsBlock | str]:
        """Retorna a lista de comandos por posição.

        Args:
            position (int | str): Posição do comando
        """
        return self.commands.get(position, [])

    def add_zpl_blank_line(self, lines: int = 1):
        """Adiciona uma ou mais linhas em branco no código ZPL.
        Funciona somente quando é formado com quebras de linha.

        Args:
            lines (int, optional): Quantidade de linhas em branco
        """
        for _ in range(lines):
            self.add_command('')
        self._reset_zpl_dump()
        return self

    def _format_commands_to_zpl(self, zebra_props: ZebraProperties = None, break_lines: bool = True) -> str:
        """Formata os comandos para o formato ZPL.

        Args:
            zebra_props (ZebraProperties, optional): Propriedades da impressora
            break_lines (bool, optional): Quebra de linha
        """
        lines = []
        for command in self.get_commands():
            if isinstance(command, ZplDump):

                x, y = command.get_origin_position(zebra_props)
                if x >= 0:
                    self.zpl_dump_x = min(x, self.zpl_dump_x)
                if y >= 0:
                    self.zpl_dump_y = min(y, self.zpl_dump_y)

                width, height = command.get_size(zebra_props)
                if width >= 0:
                    self.zpl_dump_width = max(width, self.zpl_dump_width)
                if height >= 0:
                    self.zpl_dump_height = max(height, self.zpl_dump_height)

                new_props = command.get_new_properties(zebra_props)
                zebra_props = new_props or zebra_props

                lines.append(command.dump_zpl(zebra_props, False))
            else:
                lines.append(str(command))
        return '\r\n'.join(lines) if break_lines else ''.join(lines)

    def dump_zpl(self, zebra_props: ZebraProperties = None, break_lines: bool = True) -> str:
        """Formata o bloco de comandos para o formato ZPL.

        Args:
            zebra_props (ZebraProperties, optional): Propriedades da impressora
            break_lines (bool, optional): Quebra de linha
        """
        lines = []
        if self.start_block is not None:
            lines.append(str(self.start_block))
        lines.append(self._format_commands_to_zpl(zebra_props, break_lines))
        if self.end_block is not None:
            lines.append(str(self.end_block))
        zpl_code = '\r\n'.join(lines) if break_lines else ''.join(lines)
        self.zpl_dump_zpl = zpl_code
        return zpl_code
