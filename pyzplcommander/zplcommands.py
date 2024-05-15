from enum import Enum
from collections import namedtuple


class ZplBool(Enum):
    YES = 'Y'
    NO = 'N'


class ZplOrientation(Enum):
    NORMAL = 'N'
    ROTATE_90 = 'R'
    ROTATE_180 = 'I'
    ROTATE_270 = 'B'


class ZplDirection(Enum):
    VERTICAL = 'V'
    HORIZONTAL = 'H'
    REVERSE = 'R'


class ZplJustification(Enum):
    LEFT = 'L'
    CENTER = 'C'
    RIGHT = 'R'
    JUSTIFIED = 'J'


zpl_font_text = namedtuple('zpl_font', ['name', 'min_height', 'min_width', 'type'])


class ZplStandardFonts(Enum):
    FONT_A = zpl_font_text('A', 9, 5, 'U-L-D')
    FONT_B = zpl_font_text('B', 11, 7, 'U')
    FONT_D = zpl_font_text('D', 18, 10, 'U-L-D')
    FONT_E = zpl_font_text('E', 18, 10, 'OCR-B')
    FONT_F = zpl_font_text('F', 26, 13, 'U-L-D')
    FONT_G = zpl_font_text('G', 60, 40, 'U-L-D')
    FONT_H = zpl_font_text('H', 21, 13, 'OCR-A')
    FONT_0 = zpl_font_text('0', 15, 12, 'U-L-D')
    FONT_GS = zpl_font_text('GS', 24, 24, 'SYMBOL')
    FONT_P = zpl_font_text('P', 20, 18, 'U-L-D')
    FONT_Q = zpl_font_text('Q', 28, 24, 'U-L-D')
    FONT_R = zpl_font_text('R', 35, 31, 'U-L-D')
    FONT_S = zpl_font_text('S', 40, 35, 'U-L-D')
    FONT_T = zpl_font_text('T', 48, 42, 'U-L-D')
    FONT_U = zpl_font_text('U', 59, 53, 'U-L-D')
    FONT_V = zpl_font_text('V', 80, 71, 'U-L-D')


zpl_command = namedtuple('zpl_command', ['command', 'description', 'parameters'])


class ZplCommands(Enum):

    # Propriedades de impressão
    PRINTING_DARKNESS = zpl_command('~SD', 'Ajusta a escuridão da impressão', ['darkness_level'])

    # Propriedades da etiqueta
    LABEL_START_BLOCK = zpl_command('^XA', 'Inicia um bloco de etiqueta', [])
    LABEL_END_BLOCK = zpl_command('^XZ', 'Final do bloco de etiqueta', [])

    LABEL_FONT_DEFAULT = zpl_command('^CF', 'Altera a fonte de texto padrão', ['font', 'height', 'width'])
    LABEL_LENGTH = zpl_command('^LL', 'Define o comprimento da etiqueta', ['length'])
    LABEL_ORIENTATION = zpl_command('^PO', 'Define a orientação da etiqueta', ['orientation'])
    LABEL_HOME = zpl_command('^LH', 'Define a origem da etiqueta', ['x', 'y'])

    # Campos de valores
    FIELD_COMMENT = zpl_command('^FX', 'Adiciona um comentário ao ZPL', ['text'])
    FIELD_DATA = zpl_command('^FD', 'Define um campo de dados', ['text'])
    FIELD_SEPARATOR = zpl_command('^FS', 'Finaliza um campo', [])
    FIELD_ORIGIN = zpl_command('^FO', 'Define a posição de um campo', ['x', 'y'])
    FIELD_FONT = zpl_command('^A', 'Define fonte de texto', ['font', 'orientation', 'height', 'width'])
    FIELD_FONT_RESOURCES = zpl_command('^A@', 'Define fonte de texto armazenada', [
        'orientation', 'height', 'width', 'location'
    ])
    FIELD_DIRECTION = zpl_command('^FP', 'Permite impressão na vertical e reverso', [
        'direction', 'additional inter-character'
    ])
    FIELD_BLOCK = zpl_command('^FB', 'Campo em bloco para quebras de linhas', [
        'width', 'number of lines', 'space between lines', 'text justification', 'hanging indent seconds lines'
    ])

    # Controles da impressora
    PRINTER_PAUSE = zpl_command('~PP', 'Pausa após impressão', ['pause_length'])
    PRINTER_FEED = zpl_command('^PF', 'Avança a etiqueta', ['number of dots rows to slew'])

    # Status e funções da impressora
    PRINTER_STATUS = zpl_command('~HS', 'Obtém o status da impressora', [])

    # Configurações do ZPL
    ZPL_CONTROL_PREFIX = zpl_command('~CC', 'Configura o prefixo de controle', ['prefix'])
    ZPL_PARAM_DELIMITER = zpl_command('~CD', 'Configura o delimitador de parâmetros', ['delimiter'])
    ZPL_CMD_PREFIX = zpl_command('~CT', 'Configura o prefixo de comandos', ['prefix'])


zpl_barcode = namedtuple('zpl_barcode', ['command', 'type', 'group', 'params'])


class ZplBarcode(Enum):
    CODE_11 = zpl_barcode('^B1', 'Code 11 (USD-8)', 'NUMERIC', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'check digit (Y,N), Default: N',
        'height (1-32000), Default: ^BY',
        'interpretation line (Y,N), Default: Y',
        'interpretation line above code (Y,N), Default: N'
    ])
    INTERLEAVED_2_OF_5 = zpl_barcode('^B2', 'Interleaved 2 of 5', 'NUMERIC', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'height (1-32000), Default: ^BY',
        'interpretation line (Y,N), Default: Y',
        'interpretation line above code (Y,N), Default: N',
        'print mod 10 check digit (Y,N), Default: N'
    ])
    CODE_39 = zpl_barcode('^B3', 'Code 39', 'ALPHANUMERIC', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'mod 43 check digit (Y,N), Default: N',
        'height (0-32000), Default: ^BY',
        'interpretation line (Y,N), Default: Y',
        'interpretation line above code (Y,N), Default: N'
    ])
    CODE_49 = zpl_barcode('^B4', 'Code 49', 'TWO-DIMENSIONAL', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'height multiplier of individual rows (1-height of label), Default: ^BY',
        'interpretation line (Y,N), Default: Y',
        'starting mode ('
        '0=regular alphanumeric, 1=multiple read alphanumeric, '
        '2=regular numeric, 3=group alphanumeric, '
        '4=regular alphanumeric shift 1, 5=regular alphanumeric shift 2, '
        'A=automatic mode), Default: A'
    ])
    PLANET_CODE = zpl_barcode('^B5', 'Planet Code', 'NUMERIC', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'height (1-9999), Default: ^BY',
        'interpretation line (Y,N), Default: Y',
        'interpretation line above code (Y,N), Default: N'
    ])
    PDF417 = zpl_barcode('^B7', 'PDF417', 'TWO-DIMENSIONAL', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'height multiplier of individual rows (0-height of label), Default: ^BY',
        'security level (1-8), Default: 0',
        'number of data columns to encode (1-30), Default: 1:2',
        'number of rows to encode (3-90), Default: 1:2',
        'truncate right row indicators and stop pattern (Y,N), Default: N'
    ])
    EAN_8 = zpl_barcode('^B8', 'EAN-8', 'RETAIL LABELING', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'height (1-32000), Default: ^BY',
        'interpretation line (Y,N), Default: Y',
        'interpretation line above code (Y,N), Default: N'
    ])
    UPC_E = zpl_barcode('^B9', 'UPC-E', 'RETAIL LABELING', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'height (1-32000), Default: ^BY',
        'interpretation line (Y,N), Default: Y',
        'interpretation line above code (Y,N), Default: N',
        'print check digit (Y,N), Default: Y'
    ])
    CODE_93 = zpl_barcode('^BA', 'Code 93', 'ALPHANUMERIC', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'height (1-32000), Default: ^BY',
        'interpretation line (Y,N), Default: Y',
        'interpretation line above code (Y,N), Default: N',
        'print check digit (Y,N), Default: N'
    ])
    CODABLOCK = zpl_barcode('^BB', 'CODABLOCK', 'TWO-DIMENSIONAL', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'height (2-32000), Default: 8',
        'security level (1-8), Default: 0',
        'number of characters per row (2-62)',
        'number of rows to encode (CODABLOCK A:1-22 | CODABLOCK E-F:2-4)',
        'mode (A=Code 39, F=Code128, E=Code128 auto FNC1), Default: F'
    ])
    CODE_128 = zpl_barcode('^BC', 'Code 128', 'ALPHANUMERIC', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'height (1-32000), Default: ^BY',
        'interpretation line (Y,N), Default: Y',
        'interpretation line above code (Y,N), Default: N',
        'ucc check digit (Y,N), Default: N',
        'mode (N=no selected mode, U=ucc case mode, A=automatic mode, D=ucc/ean mode), Default: N'
    ])
    UPS_MAXICODE = zpl_barcode('^BD', 'UPS MaxiCode', 'TWO-DIMENSIONAL', [
        'mode (2=numeric postal code, 3=alphanumeric postal code,'
        '4=standard mode, 5=full eec, 6= reader program), Default: 3',
        'symbol number (1-8), Default: 1',
        'total symbols (1-8), Default: 1'
    ])
    EAN_13 = zpl_barcode('^BE', 'EAN-13', 'RETAIL LABELING', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'height (1-32000), Default: ^BY',
        'interpretation line (Y,N), Default: Y',
        'interpretation line above code (Y,N), Default: N'
    ])
    MICRO_PDF417 = zpl_barcode('^BF', 'Micro PDF417', 'TWO-DIMENSIONAL', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'height (0-9999), Default: ^BY',
        'mode (0-33), Default: 0'
    ])
    INDUSTRIAL_2_OF_5 = zpl_barcode('^BI', 'Industrial 2 of 5', 'NUMERIC', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'height (1-32000), Default: ^BY',
        'interpretation line (Y,N), Default: Y',
        'interpretation line above code (Y,N), Default: N'
    ])
    STANDARD_2_OF_5 = zpl_barcode('^BJ', 'Standard 2 of 5', 'NUMERIC', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'height (1-32000), Default: ^BY',
        'interpretation line (Y,N), Default: Y',
        'interpretation line above code (Y,N), Default: N'
    ])
    ANSI_CODABAR = zpl_barcode('^BK', 'ANSI Codabar', 'ALPHANUMERIC', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'check digit (Y,N), Default: N',
        'height (1-32000), Default: ^BY',
        'interpretation line (Y,N), Default: Y',
        'interpretation line above code (Y,N), Default: N'
        'designates a start character (A,B,C,D), Default: A',
        'designates a stop character (A,B,C,D), Default: A'
    ])
    LOGMARS = zpl_barcode('^BL', 'LOGMARS', 'ALPHANUMERIC', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'height (1-32000), Default: ^BY',
        'interpretation line above code (Y,N), Default: N'
    ])
    MSI = zpl_barcode('^BM', 'MSI', 'NUMERIC', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'check digit (Y,N), Default: N',
        'height (1-32000), Default: ^BY',
        'interpretation line (Y,N), Default: Y',
        'interpretation line above code (Y,N), Default: N',
        'inserts digit into the interpretation line (Y,N), Default: N'
    ])
    AZTEC_CODE = zpl_barcode('^BO', 'Aztec Code', 'TWO-DIMENSIONAL', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'magnification factor (1-10), Default: 1',
        'extended channel interpretation (Y,N), Default: N',
        'error control and symbol size (1-300), Default: 0',
        'menu symbol (Y,N), Default: N',
        'number of symbols (1-26), Default: 1',
        'ID field for structured append (text 24 characters max), Default: 0'
    ])
    PLESSEY_CODE = zpl_barcode('^BP', 'Plessey Code', 'ALPHANUMERIC', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'print check digit (Y,N), Default: N',
        'height (1-32000), Default: ^BY',
        'interpretation line (Y,N), Default: Y',
        'interpretation line above code (Y,N), Default: N'
    ])
    QR_CODE = zpl_barcode('^BQ', 'QR Code', 'TWO-DIMENSIONAL', [
        'field orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'model (1-2), Default: 2',
        'magnification factor (1-10), Default: 1',
        'error correction (h=ultra high, q=high, m=medium, l=low), Default: H',
        'mask value (0-7), Default: 7'
    ])
    GS1_DATABAR = zpl_barcode('^BS', 'GS1 DataBar', 'TWO-DIMENSIONAL', [
        'orientation (N=Normal, R=rotated, I=inverted, B=bottom up), Default: R',
        'symbology type (1=omnidirectional, 2=truncated, 3=stacked, 4=stacked omnidirectional,'
        '5=limited, 6=expanded, 7=upc-a, 8=upc-e, 9=ean-13, 11=ucc-128 ab, 12=ucc-128 c) Default: 1',
        'magnification factor (1-10), Default: 1',
        'separator height (1-2), Default: 1',
        'bar code height (1-32000), Default: 25',
        'the segment width (2-22), Default: 22',
    ])
    UPC_EAN_EXTENSION = zpl_barcode('^BS', 'UPC/EAN Extension', 'RETAIL LABELING', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'height (1-32000), Default: ^BY',
        'interpretation line (Y,N), Default: Y',
        'interpretation line above code (Y,N), Default: N'
    ])
    TLC39 = zpl_barcode('^BT', 'TLC39', 'ALPHANUMERIC', [
        'orientation (N=Normal, R=rotated, I=inverted, B=bottom up)',
        'width of the code 39 bar code (1-10)',
        'wide to narrow ratio (2.0-3.0), Default: 2.0',
        'height of the bar code (1-9999)',
        'row height of the micro pdf417 bar code (1-255)',
        'narrow bar width of the code 39 bar code (1-10)'
    ])
    UPC_A = zpl_barcode('^BU', 'UPC-A', 'RETAIL LABELING', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'height (1-9999), Default: ^BY',
        'interpretation line (Y,N), Default: Y',
        'interpretation line above code (Y,N), Default: N',
        'print check digit (Y,N), Default: Y'
    ])
    DATA_MATRIX = zpl_barcode('^BX', 'Data Matrix', 'TWO-DIMENSIONAL', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'height of individual symbol (1-width of label), Default: ^BY',
        'quality level (0, 50, 80, 100, 140, 200), Default: 0',
        'columns to encode (9-49)',
        'rows to encode (9-49)',
        'format id (1-6), Default: 6',
        'escape sequence control (any character), Default: ~',
        'aspect ratio (1-2), Default: 1'
    ])
    POSTAL_CODE = zpl_barcode('^BZ', 'Postal Code', 'ALPHANUMERIC', [
        'orientation (N=Normal, R=90 degrees, I=180 degrees, B=270 degrees), Default: ^FW',
        'height (1-32000), Default: ^BY',
        'interpretation line (Y,N), Default: Y',
        'interpretation line above code (Y,N), Default: N',
        'postal code type (0-3), Default: 0'
    ])
