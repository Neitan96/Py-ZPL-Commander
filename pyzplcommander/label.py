from __future__ import annotations

from pyzplcommander.core import ZplCommandsBlock, ZplCommandSender, ZplCommandParams
from pyzplcommander.commands import ZplCommands


class ZplLabelField(ZplCommandsBlock):
    """Classe para criação de campos de texto em etiquetas ZPL."""

    def __init__(self):
        super().__init__(end_block=str(ZplCommands.FIELD_SEPARATOR))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def data(self, data: str):
        """Define o texto do campo.

        Args:
            data (str): Texto.
        """
        self.add_command(ZplCommands.FIELD_DATA(data))
        return self

    def position(self, x: int, y: int):
        """Define a posição do campo.

        Args:
            x (int): Coordenada X.
            y (int): Coordenada Y.
        """
        self.add_command(ZplCommands.FIELD_ORIGIN(x, y))
        return self

    def font(self, font: str, orientation: str | None = None, height: int | None = None, width: int | None = None):
        """Define a fonte do campo.

        Args:
            font (str): Nome da fonte.
            orientation (str, optional): Orientação do texto. Defaults to None.
            height (int, optional): Altura da fonte. Defaults to None.
            width (int, optional): Largura da fonte. Defaults to None.
        """
        self.add_command(ZplCommands.FIELD_FONT(font, orientation, height, width))
        return self

    def direction(self, direction: str, additional_inter_chars: int | None = None):
        """Define a direção do texto.

        Args:
            direction (str): Direção do texto, 'H'=horizontal, 'V'=vertical, 'R'=reverso.
            additional_inter_chars (int, optional): Espaço adicional entre caracteres. Defaults to None.
        """
        self.add_command(ZplCommands.FIELD_DIRECTION(direction, additional_inter_chars))
        return self

    def orientation(self, orientation: str):
        """Define a orientação do texto.

        Args:
            orientation (str): Orientação do texto, 'N'=normal, 'R'=rotação de 90º,
                                'I'=invertido, 'B'=rotação de 90º invertido.
        """
        self.add_command(ZplCommands.FIELD_ORIENTATION(orientation))
        return self

    def multi_line_block(self, width_line: int = None, max_lines: int = None, space_between_lines: int = None,
                         text_justification: any = None, indent_seconds_line: int = None):
        """Define um bloco de texto com múltiplas linhas.

        Args:
            width_line (int): Largura da linha.
            max_lines (int): Número máximo de linhas.
            space_between_lines (int): Espaço entre as linhas.
            text_justification (str): Justificação do texto.
            indent_seconds_line (int): Recuo da segunda linha.
        """
        self.add_command(ZplCommands.FIELD_BLOCK(width_line, max_lines, space_between_lines,
                                                 text_justification, indent_seconds_line))
        return self


class ZplLabel(ZplCommandsBlock):
    """Classe para criação de etiquetas ZPL.

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
        self.send_to(self.printer)

    def new_field(self, x: int = None, y: int = None, data: str = None):
        """Cria um novo campo de texto.

        Args:
            x (int, optional): Coordenada X. Defaults to None.
            y (int, optional): Coordenada Y. Defaults to None.
            data (str, optional): Texto. Defaults to None.
        """
        field = ZplLabelField()
        if x is not None or y is not None:
            field.position(x, y)
        if data:
            field.data(data)
        self.add_command(field)
        return field

    def font(self, font: str, height: int | None = None, width: int | None = None):
        """Define a fonte padrão para os próximos campos de texto.

        Args:
            font (str): Nome da fonte.
            height (int, optional): Altura da fonte. Defaults to None.
            width (int, optional): Largura da fonte. Defaults to None.
        """
        self.add_command(ZplCommands.LABEL_FONT_DEFAULT(font, height, width))
        return self

    def comment(self, comment: str):
        """Adiciona um comentário ao bloco de comandos.

        Args:
            comment (str): Comentário.
        """
        self.add_command(ZplCommands.FIELD_COMMENT(comment))
        return self
