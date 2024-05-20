from __future__ import annotations
from enum import Enum
from pyzplcommander.core import ZplCommand, ZplCommandParams


class ZplCommands(Enum):
    """ Lista de comandos ZPL."""

    def __str__(self):
        return str(self.value)

    def instance_params(self, params: list[str | any] = None) -> ZplCommandParams:
        return self.value(*params)

    def __call__(self, *params) -> ZplCommandParams:
        return self.value(*params)

    # Propriedades de impressão
    PRINTING_DARKNESS = ZplCommand(
        command='~SD',
        description='Define a escuridão da impressão',
        params_description=['darkness'],
        params_required=1
    )

    # Propriedades de campos
    FIELD_COMMENT = ZplCommand(
        command='^FX',
        description='Comentário',
        params_description=['comment'],
        params_required=1
    )
    FIELD_ORIGIN = ZplCommand(
        command='^FO',
        description='Define a posição de origem do campo',
        params_description=['x', 'y', 'justification'],
        params_required=0
    )
    FIELD_DATA = ZplCommand(
        command='^FD',
        description='Define os dados do campo',
        params_description=['data'],
        params_required=1
    )
    FIELD_SEPARATOR = ZplCommand(
        command='^FS',
        description='Finaliza o campo atual',
        params_required=0
    )
    FIELD_FONT = ZplCommand(
        command='^A',
        description='Define a fonte',
        params_description=['font', 'orientation', 'height', 'width'],
        params_required=1
    )
    FIELD_FONT_RESOURCES = ZplCommand(
        command='^A@',
        description='Define a fonte a partir dos recursos da impressora',
        params_description=['orientation', 'height', 'width', 'font_address'],
        params_required=1
    )
    FIELD_ORIENTATION = ZplCommand(
        command='^FW',
        description='Define a orientação do campo',
        params_description=['orientation', 'justification'],
        params_required=1
    )
    FIELD_DIRECTION = ZplCommand(
        command='^FP',
        description='Define a direção do campo',
        params_description=['direction', 'additional_inter_chars'],
        params_default=['H', '0'],
        params_required=1
    )
    FIELD_BLOCK = ZplCommand(
        command='^FB',
        description='Define um bloco de texto multi-linha',
        params_description=['width_line', 'max_lines', 'space_between_lines', 'text_justification',
                            'indent_seconds_line'],
        params_required=0
    )
    FIELD_HEX_INDICATOR = ZplCommand(
        command='^FH',
        description='Indicador de dados hexadecimal',
        params_description=['indicator'],
        params_default=['_'],
        params_required=1
    )
    FIELD_CLOCK = ZplCommand(
        command='^FC',
        description='Ativa a impressão de data e hora',
        params_description=['char_indicator_1', 'char_indicator_2', 'char_indicator_3'],
        params_default=['%', '', ''],
        params_required=0
    )

    # Propriedades da etiqueta

    LABEL_START_BLOCK = ZplCommand(
        command='^XA',
        description='Inicia um bloco de impressão'
    )
    LABEL_END_BLOCK = ZplCommand(
        command='^XZ',
        description='Finaliza um bloco de impressão'
    )
    LABEL_HOME = ZplCommand(
        command='^LH',
        description='Define a posição inicial da etiqueta',
        params_description=['x', 'y'],
        params_required=2
    )
    LABEL_QUANTITY = ZplCommand(
        command='^PQ',
        description='Define a quantidade de etiquetas a serem impressas',
        params_description=['quantity', 'pause', 'replicates', 'override_pause', 'cut_on_error'],
        params_default=['1', '0', '0', 'N', 'Y'],
    )
    LABEL_FONT_DEFAULT = ZplCommand(
        command='^CF',
        description='Define a fonte padrão',
        params_description=['font', 'height', 'width'],
        params_required=1
    )
    LABEL_LENGTH = ZplCommand(
        command='^LL',
        description='Define o comprimento da etiqueta',
        params_description=['length'],
        params_required=1
    )
    LABEL_ORIENTATION = ZplCommand(
        command='^PO',
        description='Define a orientação da etiqueta',
        params_description=['orientation'],
        params_default=['N'],
        params_required=1
    )
    CHANGE_ENCODING = ZplCommand(
        command='^CI',
        description='Define a codificação de fonte',
        params_description=['encoding'],
        params_default=['0'],
        params_required=1
    )

    # Controles da impressora

    PRINTER_PAUSE = ZplCommand(
        command='~PP',
        description='Pausa a impressora'
    )
    PRINTER_FEED = ZplCommand(
        command='^FF',
        description='Avança a etiqueta',
        params_description=['number_dots'],
        params_required=1
    )

    # Gráficos

    GRAPHIC_BOX = ZplCommand(
        command='^GB',
        description='Desenha uma caixa',
        params_description=['width', 'height', 'border_thickness', 'line_color', 'rounding'],
        params_default=['3', '3', '1', 'B', '0'],
        params_required=0
    )
    GRAPHIC_CIRCLE = ZplCommand(
        command='^GC',
        description='Desenha um círculo',
        params_description=['diameter', 'border_thickness', 'line_color'],
        params_default=['3', '1', 'B'],
        params_required=0
    )
    GRAPHIC_DIAGONAL = ZplCommand(
        command='^GD',
        description='Desenha uma linha diagonal',
        params_description=['width', 'height', 'border_thickness', 'line_color', 'diagonal_orientation'],
        params_default=['3', '3', '1', 'B', 'R'],
        params_required=0
    )
    GRAPHIC_ELLIPSE = ZplCommand(
        command='^GE',
        description='Desenha uma elipse',
        params_description=['width', 'height', 'border_thickness', 'line_color'],
        params_default=['3', '3', '1', 'B'],
        params_required=0
    )
    GRAPHIC_SYMBOL = ZplCommand(
        command='^GS',
        description='Seleciona um símbolo',
        params_description=['orientation', 'height', 'width'],
        params_default=['N', '^CF', '^CF'],
        params_required=0
    )

    # Status e funções da impressora

    PRINTER_STATUS = ZplCommand(
        command='~HS',
        description='Solicita o status da impressora'
    )
    PRINT_HEAD_TEST = ZplCommand(
        command='^JT',
        description='Teste de cabeçote de impressão'
    )

    # Configurações do ZPL

    ZPL_CMD_PREFIX = ZplCommand(
        command='~CC',
        description='Define o prefixo de comandos ZPL',
        params_description=['prefix'],
        params_required=1
    )
    ZPL_CONTROL_PREFIX = ZplCommand(
        command='~CT',
        description='Define o prefixo de controle ZPL',
        params_description=['prefix'],
        params_required=1
    )
    ZPL_PARAM_DELIMITER = ZplCommand(
        command='~CD',
        description='Define o delimitador de parâmetros ZPL',
        params_description=['delimiter'],
        params_required=1
    )

    # Códigos de barras
    BARCODE_CODE_11 = ZplCommand(
        command='^B1',
        description='Código de barras Code 11',
        params_description=['orientation', 'print_check_digit', 'height', 'interpretation_line',
                            'interpretation_line_above'],
        params_default=['^FW', 'N', '^BY', 'Y', 'N'],
        params_required=0
    )
    BARCODE_INTERLEAVED_2_OF_5 = ZplCommand(
        command='^B2',
        description='Código de barras Interleaved 2 of 5',
        params_description=['orientation', 'height', 'interpretation_line', 'interpretation_line_above',
                            'print_check_digit'],
        params_default=['^FW', '^BY', 'Y', 'N', 'N'],
        params_required=0
    )
    BARCODE_CODE_39 = ZplCommand(
        command='^B3',
        description='Código de barras Code 39',
        params_description=['orientation', 'print_check_digit', 'height', 'interpretation_line',
                            'interpretation_line_above'],
        params_default=['^FW', 'N', '^BY', 'Y', 'N'],
        params_required=0
    )
    BARCODE_CODE_49 = ZplCommand(
        command='^B4',
        description='Código de barras Code 49',
        params_description=['orientation', 'height', 'interpretation_line', 'starting_mode'],
        params_default=['^FW', '^BY', 'Y', 'A'],
        params_required=0
    )
    BARCODE_PLANET_CODE = ZplCommand(
        command='^B5',
        description='Código de barras Planet Code',
        params_description=['orientation', 'height', 'interpretation_line', 'interpretation_line_above'],
        params_default=['^FW', '^BY', 'N', 'N'],
        params_required=0
    )
    BARCODE_PD417 = ZplCommand(
        command='^B7',
        description='Código de barras PDF417',
        params_description=['orientation', 'height_individual_row', 'security_level', 'columns', 'rows', 'truncate'],
        params_default=['^FW', '^BY', '0', '1:2', '1:2', 'N'],
        params_required=0
    )
    BARCODE_EAN_8 = ZplCommand(
        command='^B8',
        description='Código de barras EAN-8',
        params_description=['orientation', 'height', 'interpretation_line', 'interpretation_line_above'],
        params_default=['^FW', '^BY', 'Y', 'N'],
        params_required=0
    )
    BARCODE_UPC_E = ZplCommand(
        command='^B9',
        description='Código de barras UPC-E',
        params_description=['orientation', 'height', 'interpretation_line', 'interpretation_line_above',
                            'print_check_digit'],
        params_default=['^FW', '^BY', 'Y', 'N', 'Y'],
        params_required=0
    )
    BARCODE_CODE_93 = ZplCommand(
        command='^BA',
        description='Código de barras Code 93',
        params_description=['orientation', 'height', 'interpretation_line', 'interpretation_line_above',
                            'print_check_digit'],
        params_default=['^FW', '^BY', 'Y', 'N', 'N'],
        params_required=0
    )
    BARCODE_CODABLOCK = ZplCommand(
        command='^BB',
        description='Código de barras Codablock',
        params_description=['orientation', 'height', 'security_level', 'characters_per_row', 'rows', 'mode'],
        params_default=['N', '8', 'Y', '', '', 'F'],
        params_required=0
    )
    BARCODE_CODE_128 = ZplCommand(
        command='^BC',
        description='Código de barras Code 128',
        params_description=['orientation', 'height', 'interpretation_line', 'interpretation_line_above',
                            'print_check_digit', 'mode'],
        params_default=['^FW', '^BY', 'Y', 'N', 'N', 'N'],
        params_required=0
    )
    BARCODE_UPS_MAXICODE = ZplCommand(
        command='^BD',
        description='Código de barras UPS MaxiCode',
        params_description=['mode', 'symbol_number', 'number_of_symbols'],
        params_default=['2', '1', '1'],
        params_required=0
    )
    BARCODE_EAN_13 = ZplCommand(
        command='^BE',
        description='Código de barras EAN-13',
        params_description=['orientation', 'height', 'interpretation_line', 'interpretation_line_above'],
        params_default=['^FW', '^BY', 'Y', 'N'],
        params_required=0
    )
    BARCODE_MICRO_PDF417 = ZplCommand(
        command='^BF',
        description='Código de barras Micro PDF417',
        params_description=['orientation', 'height', 'mode'],
        params_default=['^FW', '^BY', '0'],
        params_required=0
    )
    BARCODE_INDUSTRIAL_2_OF_5 = ZplCommand(
        command='^BI',
        description='Código de barras Industrial 2 of 5',
        params_description=['orientation', 'height', 'interpretation_line', 'interpretation_line_above'],
        params_default=['^FW', '^BY', 'Y', 'N'],
        params_required=0
    )
    BARCODE_STANDARD_2_OF_5 = ZplCommand(
        command='^BJ',
        description='Código de barras Standard 2 of 5',
        params_description=['orientation', 'height', 'interpretation_line', 'interpretation_line_above'],
        params_default=['^FW', '^BY', 'Y', 'N'],
        params_required=0
    )
    BARCODE_ANSI_CODABAR = ZplCommand(
        command='^BK',
        description='Código de barras ANSI Codabar',
        params_description=['orientation', 'print_check_digit', 'height', 'interpretation_line',
                            'interpretation_line_above', 'start_stop_character', 'designate_stop_character'],
        params_default=['^FW', 'N', '^BY', 'Y', 'N', 'A', 'A'],
        params_required=0
    )
    BARCODE_LOGMARS = ZplCommand(
        command='^BL',
        description='Código de barras LOGMARS',
        params_description=['orientation', 'height', 'interpretation_line_above'],
        params_default=['^FW', '^BY', 'N'],
        params_required=0
    )
    BARCODE_MSI = ZplCommand(
        command='^BM',
        description='Código de barras MSI',
        params_description=['orientation', 'check_digit_selection', 'height', 'interpretation_line',
                            'interpretation_line_above', 'check_digit_in_interpretation_line'],
        params_default=['^FW', 'B', '^BY', 'Y', 'N', 'N'],
        params_required=0
    )
    BARCODE_PLESSEY_CODE = ZplCommand(
        command='^BP',
        description='Código de barras Plessey Code',
        params_description=['orientation', 'print_check_digit', 'height', 'interpretation_line',
                            'interpretation_line_above'],
        params_default=['^FW', 'N', '^BY', 'Y', 'N'],
        params_required=0
    )
    BARCODE_QR_CODE = ZplCommand(
        command='^BQ',
        description='Código de barras QR Code',
        params_description=['orientation', 'model', 'magnification_factor', 'error_correction', 'mask_value'],
        params_default=['^FW', '2', '1', 'H', '7'],
        params_required=0
    )
    BARCODE_GS1_DATABAR = ZplCommand(
        command='^BR',
        description='Código de barras GS1 DataBar',
        params_description=['orientation', 'symbology_type', 'magnification_factor', 'separator_height',
                            'height', 'segment_width'],
        params_default=['R', '1', '6,3,2', '1', '25', '22'],
        params_required=0
    )
    BARCODE_UPC_EAN_EXTENSION = ZplCommand(
        command='^BS',
        description='Código de barras UPC/EAN Extension',
        params_description=['orientation', 'height', 'interpretation_line', 'interpretation_line_above'],
        params_default=['^FW', '^BY', 'Y', 'N'],
        params_required=0
    )
    BARCODE_TLC39 = ZplCommand(
        command='^BT',
        description='Código de barras TLC39',
        params_description=['orientation', 'width', 'wide_bar_width', 'height_barcode', 'height_row',
                            'narrow_bar_width'],
        params_default=['^FW', '4', '2.0', '120,60,40', '8,4', '4,2'],
        params_required=0
    )
    BARCODE_UPC_A = ZplCommand(
        command='^BU',
        description='Código de barras UPC-A',
        params_description=['orientation', 'height', 'interpretation_line', 'interpretation_line_above',
                            'print_check_digit'],
        params_default=['^FW', '^BY', 'Y', 'N', 'Y'],
        params_required=0
    )
    BARCODE_DATA_MATRIX = ZplCommand(
        command='^BX',
        description='Código de barras Data Matrix',
        params_description=['orientation', 'height', 'quality_level', 'columns_to_encode', 'rows_to_encode',
                            'format_id', 'escape_sequence', 'aspect_ratio'],
        params_default=['^FW', '^BY', '0', '', '', '6', '', '1'],
        params_required=0
    )
    BARCODE_POSTAL_CODE = ZplCommand(
        command='^BY',
        description='Código de barras Postal Code',
        params_description=['orientation', 'height', 'interpretation_line', 'interpretation_line_above',
                            'postal_code_type'],
        params_default=['^FW', '^BY', 'N', 'N', '0'],
        params_required=0
    )
    BARCODE_AZTEC_CODE = ZplCommand(
        command='^BZ',
        description='Código de barras Aztec Code',
        params_description=['orientation', 'magnification_factor', 'extended_channel', 'error control', 'menu symbol',
                            'number_of_symbols', 'id_field'],
        params_default=['^FW', '1', 'N', '0', 'N', '1', ''],
        params_required=0
    )
