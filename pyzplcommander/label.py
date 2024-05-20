from __future__ import annotations
from typing import Literal

from pyzplcommander.core import ZplCommandsBlock, ZplCommandSender
from pyzplcommander.commands import ZplCommands


class ZplLabelField(ZplCommandsBlock):
    """Classe para criação de campos de texto em etiquetas ZPL."""

    hex_indicator_char = '_'

    def __init__(self):
        super().__init__(end_block=str(ZplCommands.FIELD_SEPARATOR))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def hex_indicator(self, hex_indicator: str):
        """Define o caractere de escape hexadecimal para caracteres especiais.

        Note:
            Comando ZPL: ^FH

        Args:
            hex_indicator (str): Caractere de escape hexadecimal.
        """
        self.hex_indicator_char = hex_indicator
        self.add_command(ZplCommands.FIELD_HEX_INDICATOR(hex_indicator))
        return self

    def enable_clock(self, char_indicator_1: str = None, char_indicator_2: str = None, char_indicator_3: str = None):
        """Habilita a formatação de data e hora no campo de texto.
        A formatação de data e hora é feita utilizando os caracteres especiais de formatação, sendo os caracteres
        passados como argumento, por padrão o caractere de formatação é o '%'.

        Referência dos caracteres de formatação:
        - pyzplcommander.enums.ZplRTCChars

        Tabela de caracteres de formatação:
        - %a = Nome abreviado do dia da semana
        - %A = Nome completo do dia da semana
        - %b = Nome abreviado do mês
        - %B = Nome completo do mês
        - %d = Dia do mês 01-31
        - %H = Hora do dia 00-23
        - %I = Hora do dia 01-12
        - %j = Dia do ano 001-366
        - %m = Mês do ano 01-12
        - %M = Minuto 00-59
        - %p = AM/PM
        - %S = Segundo 00-59
        - %U = Semana do ano, domingo como primeiro dia da semana 00-53
        - %W = Semana do ano, segunda-feira como primeiro dia da semana 00-53
        - %w = Dia da semana 0-6 (0 = domingo)
        - %y = Ano com dois dígitos
        - %Y = Ano com quatro dígitos

        Note:
            Comando ZPL: ^FC

        Args:
            char_indicator_1 (str, optional): Caractere de formatação de data e hora 1.
            char_indicator_2 (str, optional): Caractere de formatação de data e hora 2.
            char_indicator_3 (str, optional): Caractere de formatação de data e hora 3.
        """
        self.add_command(ZplCommands.FIELD_CLOCK(char_indicator_1, char_indicator_2, char_indicator_3))
        return self

    def data(self, data: str):
        """Define o texto/data do campo.
        Caso o texto/data contenha caracteres especiais, é necessário realizar o escape dos mesmos,
        conforme a tabela de caracteres especiais do ZPL utilizando tabela hexadecimal.

        Caracteres especiais que é feito o escape:
        _ \\ ^ ~ # $ & | { } [ ] : ; , . < > = - + ! " ( ) * % / ? @ ` '

        Note:
            Comando ZPL: ^FD

        Args:
            data (str): Texto/Data de até 3072 bytes.
        """

        special_chars = {
            '_': self.hex_indicator_char+'5F',
            '\\': self.hex_indicator_char+'5C',
            '^': self.hex_indicator_char+'5E',
            '~': self.hex_indicator_char+'7E',
            '#': self.hex_indicator_char+'23',
            '$': self.hex_indicator_char+'24',
            '&': self.hex_indicator_char+'26',
            '|': self.hex_indicator_char+'7C',
            '{': self.hex_indicator_char+'7B',
            '}': self.hex_indicator_char+'7D',
            '[': self.hex_indicator_char+'5B',
            ']': self.hex_indicator_char+'5D',
            ':': self.hex_indicator_char+'3A',
            ';': self.hex_indicator_char+'3B',
            ',': self.hex_indicator_char+'2C',
            '.': self.hex_indicator_char+'2E',
            '<': self.hex_indicator_char+'3C',
            '>': self.hex_indicator_char+'3E',
            '=': self.hex_indicator_char+'3D',
            '-': self.hex_indicator_char+'2D',
            '+': self.hex_indicator_char+'2B',
            '!': self.hex_indicator_char+'21',
            '"': self.hex_indicator_char+'22',
            '(': self.hex_indicator_char+'28',
            ')': self.hex_indicator_char+'29',
            '*': self.hex_indicator_char+'2A',
            '%': self.hex_indicator_char+'25',
            '/': self.hex_indicator_char+'2F',
            '?': self.hex_indicator_char+'3F',
            '@': self.hex_indicator_char+'40',
            '`': self.hex_indicator_char+'60',
            "'": self.hex_indicator_char+'27'
        }

        if any(char in data for char in special_chars):
            data = ''.join(special_chars.get(i, i) for i in data)

        self.set_command(ZplCommands.FIELD_DATA(data), 'data')
        return self

    def position(self, x: int = None, y: int = None, justification: Literal['0', '1', '2'] = None):
        """Define a posição do campo.
        A posição do campo é relativa à posição inicial da etiqueta, definido pelo comando ^LH.

        Note:
            Comando ZPL: ^FO
            A justificação do campo é suportada somente para firmware .14+.

        Args:
            x (int): Coordenada X em pontos(0-32000).
            y (int): Coordenada Y em pontos(0-32000).
            justification (str): Justificação do campo, suporte somente para firmware .14+, valores possíveis:
                                    '0'=Esquerda, '1'=Direita, '2'=Auto justificado.
        """
        self.add_command(ZplCommands.FIELD_ORIGIN(x, y, justification))
        return self

    def font(self, font: str = None, orientation: Literal['N', 'I', 'R', 'B'] = None,
             height: int | None = None, width: int | None = None):
        """Define a fonte do campo atual.
        A altura e largura da fonte precisa ser proporcional a largura e altura mínima da fonte,
        caso contrário, a impressora irá arredondar para o valor mais próximo.

        Referência das fontes padrão:
        - pyzplcommander.enums.ZplStandardFonts6Dots
        - pyzplcommander.enums.ZplStandardFonts8Dots
        - pyzplcommander.enums.ZplStandardFonts12Dots
        - pyzplcommander.enums.ZplStandardFonts24Dots

        Note:
            Comando ZPL: ^CF

        Args:
            font (str): Nome da fonte, caso não seja informado, será utilizada a fonte padrão definida pelo comando ^CF.
            orientation (str, optional): Orientação do texto, valores possíveis:
                                        'N'=normal, 'I'=rotação de 90º, 'R'=rotação de 180º, 'B'=rotação de 270º.
            height (int, optional): Altura da fonte em pontos(10-32000).
            width (int, optional): Largura da fonte em pontos(10-32000).
        """
        self.add_command(ZplCommands.FIELD_FONT(font, orientation, height, width))
        return self

    def direction(self, direction: Literal['H', 'V', 'R'], additional_inter_chars: int | None = None):
        """Define a direção do texto e o espaço adicional entre os caracteres.

        Note:
            Comando ZPL: ^FP

        Args:
            direction (str): Direção do texto, valores possíveis:
                                'H'=horizontal, 'V'=vertical, 'R'=reverso.
            additional_inter_chars (int, optional): Espaço adicional entre caracteres em pontos(0-9999).
        """
        self.add_command(ZplCommands.FIELD_DIRECTION(direction, additional_inter_chars))
        return self

    def orientation(self, orientation: Literal['N', 'R', 'I', 'B'], justification: Literal['0', '1', '2'] = None):
        """Define a orientação do texto.

        Note:
            Comando ZPL: ^FW

        Args:
            orientation (str): Orientação do texto, valores possíveis:
                                'N'=normal, 'I'=rotação de 90º, 'R'=rotação de 180º, 'B'=rotação de 270º.
            justification (str, optional): Justificação do texto, suporte somente para firmware .14+, valores possíveis:
                                            '0'=Esquerda, '1'=Direita, '2'=Auto justificado.
        """
        self.add_command(ZplCommands.FIELD_ORIENTATION(orientation, justification))
        return self

    def multi_line_block(self, width_line: int = None, max_lines: int = None, space_between_lines: int = None,
                         text_justification: Literal['L', 'C', 'R', 'J'] = None, indent_seconds_line: int = None):
        """Define um bloco de texto com múltiplas linhas.

        Note:
            Comando ZPL: ^FB

        Args:
            width_line (int): Largura da linha em pontos.
            max_lines (int): Número máximo de linhas(1-9999).
            space_between_lines (int): Espaço entre as linhas((-9999)-9999).
            text_justification (str): Justificação do texto, valores possíveis:
                                        'L'=Left, 'C'=Center, 'R'=Right, 'J'=Justified.
            indent_seconds_line (int): Recuo da segunda linha.
        """
        self.add_command(ZplCommands.FIELD_BLOCK(width_line, max_lines, space_between_lines,
                                                 text_justification, indent_seconds_line))
        return self


class ZplLabel(ZplCommandsBlock):
    """Classe de construtor para criação de etiquetas ZPL.

    Note:
        Comando ZPL: ^XA
        Comando finalizador: ^XZ

    Args:
        printer (ZplCommandSender): Instância de ZplCommandSender para envio dos comandos.
    """

    printer: ZplCommandSender

    def __init__(self, printer: ZplCommandSender):
        super().__init__(
            start_block=str(ZplCommands.LABEL_START_BLOCK),
            end_block=str(ZplCommands.LABEL_END_BLOCK)
        )
        self.printer = printer

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Envia os comandos da etiqueta criada para a impressora."""
        if self.printer is not None:
            self.send_to(self.printer)

    def new_field(self, x: int = None, y: int = None, data: str = None):
        """Instancia um construtor de campo de texto.

        Note:
            Comando ZPL: ^FO
            Comando finalizador: ^FS

        Args:
            x (int, optional): Coordenada X em pontos(0-32000), definido com o comando ^FO.
            y (int, optional): Coordenada Y em pontos(0-32000), definido com o comando ^FO.
            data (str, optional): Texto/Data de até 3072 bytes, definido com o comando ^FD.
        """
        field = ZplLabelField()
        if x is not None or y is not None:
            field.position(x, y)
        if data:
            field.data(data)
        self.add_command(field)
        return field

    def draw_text(self, text: str, x: int = None, y: int = None, font: str = None,
                  height: int = None, width: int = None, orientation: Literal['N', 'R', 'I', 'B'] = None):
        """Adiciona um campo de texto à etiqueta.

        Args:
            text (str): Texto/Data de até 3072 bytes.
            x (int, optional): Coordenada X em pontos(0-32000), definido com o comando ^FO.
            y (int, optional): Coordenada Y em pontos(0-32000), definido com o comando ^FO.
            font (str, optional): Nome da fonte, caso não seja informado, será utilizada a fonte padrão atual.
            height (int, optional): Altura da fonte em pontos(10-32000).
            width (int, optional): Largura da fonte em pontos(10-32000).
            orientation (str, optional): Orientação do texto, valores possíveis:
                                        'N'=normal, 'I'=rotação de 90º, 'R'=rotação de 180º, 'B'=rotação de 270º.
        """
        field = ZplLabelField()
        if x or y:
            field.position(x, y)
        if font or height or width or orientation:
            field.font(font, orientation, height, width)
        field.data(text)
        self.add_command(field)

    def encode_font(self, encode_enum: str | int):
        """Define o charset da fonte para os próximos campos de texto.
        O charset é utilizado para converter os caracteres especiais para os caracteres correspondentes
        na fonte selecionada.

        Firmware .14- suporta os seguintes charsets de 0 a 12.
        Firmware .14+ suporta os seguintes charsets de 0 a 30.
        Firmware .16+ suporta os seguintes charsets de 0 a 36.

        Referência dos charsets:
        - pyzplcommander.enums.ZplCharSets

        Note:
            Comando ZPL: ^CI

        Args:
            encode_enum (str): Enumeração do charset.
        """
        self.add_command(ZplCommands.CHANGE_ENCODING(encode_enum))
        return self

    def font(self, font: str, height: int | None = None, width: int | None = None):
        """Define a fonte padrão para os próximos campos de texto.
        A fonte padrão é utilizada para os campos de texto que não possuem uma fonte definida,
        a altura e largura da fonte precisa ser proporcional a largura e altura mínima da fonte,
        caso contrário, a impressora irá arredondar para o valor mais próximo.

        Referência das fontes padrão:
        - pyzplcommander.enums.ZplStandardFonts6Dots
        - pyzplcommander.enums.ZplStandardFonts8Dots
        - pyzplcommander.enums.ZplStandardFonts12Dots
        - pyzplcommander.enums.ZplStandardFonts24Dots

        Note:
            Comando ZPL: ^CF

        Args:
            font (str): Nome da fonte.
            height (int, optional): Altura da fonte em pontos(0-32000). Defaults to None.
            width (int, optional): Largura da fonte em pontos(0-32000). Defaults to None.
        """
        self.add_command(ZplCommands.LABEL_FONT_DEFAULT(font, height, width))
        return self

    def comment(self, comment: str):
        """Adiciona um comentário ao bloco de comandos.
        Conforme a documentação ZPL, o comentário é ignorado pelo interpretador.

        Note:
            Comando ZPL: ^FX
            Comando finalizador: ^FS

        Args:
            comment (str): Comentário de até 255 caracteres.
        """
        comment = ZplCommands.FIELD_COMMENT(comment)
        self.add_command(ZplCommandsBlock(end_block=str(ZplCommands.FIELD_SEPARATOR)).add_command(comment))
        return self
