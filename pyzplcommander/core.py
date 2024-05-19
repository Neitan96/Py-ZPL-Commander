from __future__ import annotations
from abc import ABC, abstractmethod


class ZplCommandSender(ABC):
    """ZplCommandSender é uma classe abstrata para classes que enviam comandos ZPL."""

    @abstractmethod
    def send_command(self, command: str, get_response: bool = False) -> None | str:
        """Envia um comando ZPL.

        Args:
            command (str): Comando ZPL
            get_response (bool, optional): Obter resposta do comando
        """
        pass

    def send_commands(self, commands: list[str], get_response: bool = False) -> list[str] | None:
        """Envia uma lista de comandos ZPL.

        Args:
            commands (list[str]): Lista de comandos ZPL
            get_response (bool, optional): Obter resposta do comando
        """
        results = []
        for command in commands:
            results.append(self.send_command(command, get_response))

        if get_response:
            return results


class ZplCommand:
    """ZplCommand é uma classe para representar um comando ZPL.

    Contém informações sobre o comando, como descrição, parâmetros, valores, etc.

    Args:
        command (str): O comando ZPL em si, ex: '^FO'
        description (str, optional): Descrição do comando
        params_description (list[str], optional): Lista de descrições dos parâmetros
        params_default (list[str], optional): Lista de valores padrão dos parâmetros
        params_required (int, optional): Quantidade de parâmetros obrigatórios
        command_response (bool, optional): Se o comando retorna uma resposta
    """

    command: str
    description: str
    params_description: list[str]
    params_default: list[str]
    params_required: int
    command_response: bool

    def __init__(self, command: str, description: str = None,
                 params_description: list[str] = None, params_default: list[str] = None,
                 params_required: int = 0, command_response: bool = False):
        self.command = command
        self.description = description
        self.params_description = params_description
        self.params_default = params_default
        self.params_required = params_required
        self.command_response = command_response

    def send_to(self, sender: ZplCommandSender, get_response: bool = False) -> None | str:
        """Envia o comando ZPL.

        Args:
            sender (ZplCommandSender): Objeto que envia o comando
            get_response (bool, optional): Obter resposta do comando
        """
        return sender.send_command(str(self), get_response)

    def get_param_index(self, param: str) -> int:
        """Retorna o índice do parâmetro pelo nome do parâmetro.

        Args:
            param (str): Nome do parâmetro
        """
        if param is None or self.params_description is None:
            return -1
        return self.params_description.index(param)

    def instance_params(self, params: list[str | any] = None) -> ZplCommandParams:
        """Cria um novo comando com parâmetros.

        Args:
            params (list[str], optional): Lista de parâmetros
        """
        return self(params)

    def __call__(self, *params) -> ZplCommandParams:
        """Cria um novo comando com parâmetros.

        Args:
            params: Parâmetros
        """
        params = params[0] if len(params) == 1 and isinstance(params[0], list) else list(params)
        return ZplCommandParams(self, params)

    def __str__(self):
        """Retorna o comando ZPL."""
        return self.command

    def __repr__(self):
        return f'<ZplCommand: {self.command}, Description: {self.description}>, Params: {self.params_description}>'


class ZplCommandParams:
    """ZplCommandParams é uma classe para representar um comando ZPL com parâmetros.

    Args:
        command (ZplCommand | str): Comando ZPL
        params (list[str], optional): Lista de parâmetros
    """

    command: ZplCommand | str
    params: list[str | None]

    def __init__(self, command: ZplCommand | str, params: list[str | any] = None):
        self.command = command
        self.params = [str(param) for param in params]

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

        return ','.join(map(lambda x: None if x is None else str(x), params[:last_value+1]))

    def format_to_zpl(self) -> str:
        """Formata o comando com os parâmetros e valor para o formato ZPL."""
        return str(self)

    def __str__(self):
        """Formata o comando com os parâmetros e valor para o formato ZPL."""
        return str(self.command)+self.format_params_to_zpl(self.params)

    def __repr__(self):
        return f'<ZplCommandValue: {self.command}, Params: {self.params}>'


class ZplCommandsBlock:
    """ZplCommandsBlock é uma classe para representar um bloco de comandos ZPL.

    Args:
        start_block (ZplCommandValue, optional): Comando de início do bloco
        end_block (ZplCommandValue, optional): Comando de fim do bloco
    """

    start_block: str
    end_block: str
    commands: dict[int, list[ZplCommandParams | str]]

    def __init__(self, start_block: str = None, end_block: str = None):
        self.start_block = start_block
        self.end_block = end_block
        self.commands = {}

    def send_to(self, sender: ZplCommandSender, get_response: bool = False) -> None | str:
        """Envia o comando ZPL.

        Args:
            sender (ZplCommandSender): Objeto que envia o comando
            get_response (bool, optional): Obter resposta do comando
        """
        return sender.send_command(str(self), get_response)

    def add_command(self, command: ZplCommandParams | ZplCommandsBlock | str, position: int = 0):
        """Adiciona um comando ao bloco.

        Args:
            command (ZplCommandParams | str): Comando ZPL
            position (int, optional): Posição do comando
        """
        if position not in self.commands:
            self.commands[position] = []
        self.commands[position].append(command)

    def new_command(self, command: ZplCommand, position: int = 0) -> ZplCommandParams:
        """Cria um novo comando ao bloco.

        Args:
            command (ZplCommand): Comando ZPL
            position (int, optional): Posição do comando

        Returns:
            ZplCommandParams: Comando criado
        """
        cmd_value = ZplCommandParams(command)
        self.add_command(cmd_value, position)
        return cmd_value

    def set_command(self, command: ZplCommandParams | ZplCommandsBlock | str, position: int = 0):
        """Define um comando ao bloco.

        Args:
            command (ZplCommandParams | str): Comando ZPL
            position (int, optional): Posição do comando
        """
        self.commands[position] = []
        self.add_command(command, position)

    def get_commands(self) -> list[ZplCommandParams | ZplCommandsBlock | str]:
        """Retorna a lista de comandos."""
        return [cmd for order in sorted(self.commands.keys()) for cmd in self.commands[order]]

    def get_commands_by_position(self, position: int) -> list[ZplCommandParams | ZplCommandsBlock | str]:
        """Retorna a lista de comandos por posição.

        Args:
            position (int): Posição do comando
        """
        return self.commands.get(position, [])

    def __str__(self):
        """Retorna o bloco de comandos."""
        return self.format_to_zpl(True)

    def __repr__(self):
        return (f'<ZplCommandsBlock: Start: {str(self.start_block)}, End: {str(self.end_block)}, '
                f'Commands: {str(self.commands)}>')

    def format_to_zpl(self, break_lines: bool = True) -> str:
        """Formata o bloco de comandos para o formato ZPL.

        Args:
            break_lines (bool, optional): Quebra de linha
        """
        lines = []
        if self.start_block is not None:
            lines.append(str(self.start_block))
        lines.extend(self.get_commands())
        if self.end_block is not None:
            lines.append(str(self.end_block))
        return '\r\n'.join(lines) if break_lines else ''.join(lines)
