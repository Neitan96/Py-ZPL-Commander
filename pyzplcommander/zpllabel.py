from __future__ import annotations
from pyzplcommander.zplcore import ZplCommandsDump, ZplCommandSender
from pyzplcommander.zplcommands import ZplCommands, ZplStandardFonts, ZplOrientation, ZplDirection, ZplJustification
from pyzplcommander.zplcommands import ZplBarcode, zpl_barcode


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

    def set_barcode(self, barcode_type: ZplBarcode, barcode_value: str, params: list[str] = None) -> ZplLabelField:
        # TODO - Validação de valores para cada tipo de código de barras
        self.set_command(barcode_type.value.command, params, position=10)
        self.set_command(barcode_value, position=11)
        return self

    def set_barcode_code_11(self, barcode_value: str, orientation: str | ZplOrientation, check_digit: bool = None,
                            height: int = None, interp_line: bool = None,
                            interp_line_above_code: bool = None) -> ZplLabelField:

        if isinstance(orientation, ZplOrientation):
            orientation = orientation.value

        self.set_barcode(
            ZplBarcode.CODE_11, barcode_value,
            [orientation, check_digit, height, interp_line, interp_line_above_code]
        )
        return self

    def set_barcode_interleaved_2_of_5(self, barcode_value: str, orientation: str | ZplOrientation,
                                       height: int = None, interp_line: bool = None,
                                       interp_line_above_code: bool = None,
                                       mod10_check_digit: bool = None) -> ZplLabelField:

        if isinstance(orientation, ZplOrientation):
            orientation = orientation.value

        self.set_barcode(
            ZplBarcode.CODE_11, barcode_value,
            [orientation, height, interp_line, interp_line_above_code, mod10_check_digit]
        )
        return self


class ZplLabel(ZplCommandsDump):

    def __init__(self, printer: ZplCommandSender | str = None):
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
