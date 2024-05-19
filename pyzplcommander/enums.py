from enum import Enum


class EnumBase(Enum):
    """Classe base para enumerações."""
    def __str__(self):
        return str(self.value)

    def __call__(self):
        return str(self.value)


class GraphicSymbol(EnumBase):
    """Símbolos gráficos."""
    REGISTERED_TRADE_MARK = 'A'
    COPYRIGHT = 'B'
    TRADE_MARK = 'C'
    UNDERWRITERS_LABORATORIES_INC = 'D'
    CANADIAN_STANDARDS_ASSOCIATION = 'E'


class ZplPrintOrientation(EnumBase):
    """Orientação de campo."""
    NORMAL = 'N'  # Normal
    INVERT = 'I'  # Invertido


class DiagonalOrientation(EnumBase):
    """Orientação diagonal."""
    RIGHT = 'R'  # Direita
    LEFT = 'L'  # Esquerda


class ZplOrientation(EnumBase):
    """Orientação de campo."""
    NORMAL = 'N'  # 0 graus
    ROTATE_90 = 'R'  # 90 graus
    ROTATE_180 = 'I'  # 180 graus
    ROTATE_270 = 'B'  # 270 graus


class ZplDirection(EnumBase):
    """Direção do texto."""
    VERTICAL = 'V'  # Vertical
    HORIZONTAL = 'H'  # Horizontal
    REVERSE = 'R'  # Reverso


class ZplJustification(EnumBase):
    """Justificação de texto."""
    LEFT = 'L'  # Esquerda
    CENTER = 'C'  # Centralizado
    RIGHT = 'R'  # Direita
    JUSTIFIED = 'J'  # Justificado


class ZplFont:
    """Fonte ZPL."""

    def __init__(self, name: str, min_height: int, min_width: int, font_type: str):
        self.name = name
        self.min_height = min_height
        self.min_width = min_width
        self.type = font_type

    def __str__(self):
        return self.name


class ZplCharSets(EnumBase):
    """Conjuntos de caracteres de texto."""
    USA_1 = '0'  # USA 1
    USA_2 = '1'  # USA 2
    EUROPE = '2'  # Europe
    HOLLAND = '3'  # Holland
    DENMARK_NORWAY = '4'  # Denmark/Norway
    SWEDEN_FINLAND = '5'  # Sweden/Finland
    GERMANY = '6'  # Germany
    FRANCE_1 = '7'  # France 1
    FRANCE_2 = '8'  # France 2
    ITALY = '9'  # Italy
    SPAIN = '10'  # Spain
    SINGLE_BYTE = '11'  # Single byte
    SINGLE_BYTE_JAPAN = '12'  # Single byte Japan
    ZEBRA_CODE_850 = '13'  # Zebra Code Page 850
    DOUBLE_BYTE = '14'  # Double byte, only firmware .14+
    SHIFT_JIS = '15'  # Shift JIS, only firmware .14+
    EUC_JP_CN = '16'  # EUC-JP, only firmware .14+
    BIG_ENDIAN = '17'  # Big 5, only firmware .14+
    SINGLE_BYTE_ASIAN = '24'  # Single byte Asian, only firmware .14+
    MULTIBYTE_ASIAN = '26'  # Multibyte Asian, only firmware .14+
    ZEBRA_CODE_1252 = '27'  # Zebra Code Page 1252, only firmware .14+
    UTF_8 = '28'  # UTF-8, only firmware .14+
    UTF_16_BIG_ENDIAN = '29'  # UTF-16, only firmware .14+
    UTF_16_LITTLE_ENDIAN = '30'  # UTF-16, only firmware .14+
    ZEBRA_CODE_1250 = '31'  # Zebra Code Page 1250, only firmware .16+
    ZEBRA_CODE_1251 = '33'  # Zebra Code Page 1251, only firmware .16+
    ZEBRA_CODE_1253 = '34'  # Zebra Code Page 1253, only firmware .16+
    ZEBRA_CODE_1254 = '35'  # Zebra Code Page 1254, only firmware .16+
    ZEBRA_CODE_1255 = '36'  # Zebra Code Page 1255, only firmware .16+


class ZplStandardFonts6Dots(EnumBase):
    """Fontes padrão de 6 pontos."""
    FONT_A = ZplFont('A', 9, 5, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_B = ZplFont('B', 11, 7, 'U')  # Uppercase
    FONT_D = ZplFont('D', 18, 10, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_E = ZplFont('E', 21, 10, 'OCR-B')  # OCR-B, Uppercase, Lowercase, Digits
    FONT_F = ZplFont('F', 26, 13, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_G = ZplFont('G', 60, 40, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_H = ZplFont('H', 17, 11, 'OCR-A')  # OCR-A, Uppercase only
    FONT_GS = ZplFont('GS', 24, 24, 'SYMBOL')  # Symbol
    FONT_0 = ZplFont('0', 15, 12, 'U-L-D')  # Uppercase, Lowercase, Digits


class ZplStandardFonts8Dots(EnumBase):
    """Fontes padrão de 8 pontos, 203 DPI."""
    FONT_A = ZplFont('A', 9, 5, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_B = ZplFont('B', 11, 7, 'U')  # Uppercase
    FONT_D = ZplFont('D', 18, 10, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_E = ZplFont('E', 28, 15, 'OCR-B')  # OCR-B, Uppercase, Lowercase, Digits
    FONT_F = ZplFont('F', 26, 13, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_G = ZplFont('G', 60, 40, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_H = ZplFont('H', 21, 13, 'OCR-A')  # OCR-A, Uppercase only
    FONT_GS = ZplFont('GS', 24, 24, 'SYMBOL')  # Symbol
    FONT_P = ZplFont('P', 20, 18, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_Q = ZplFont('Q', 28, 24, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_R = ZplFont('R', 35, 31, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_S = ZplFont('S', 40, 35, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_T = ZplFont('T', 48, 42, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_U = ZplFont('U', 59, 53, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_V = ZplFont('V', 80, 71, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_0 = ZplFont('0', 15, 12, 'U-L-D')  # Uppercase, Lowercase, Digits


class ZplStandardFonts12Dots(EnumBase):
    """Fontes padrão de 12 pontos, 300 DPI."""
    FONT_A = ZplFont('A', 9, 5, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_B = ZplFont('B', 11, 7, 'U')  # Uppercase
    FONT_D = ZplFont('D', 18, 10, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_E = ZplFont('E', 42, 20, 'OCR-B')  # OCR-B, Uppercase, Lowercase, Digits
    FONT_F = ZplFont('F', 26, 13, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_G = ZplFont('G', 60, 40, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_H = ZplFont('H', 34, 22, 'OCR-A')  # OCR-A, Uppercase only
    FONT_GS = ZplFont('GS', 24, 24, 'SYMBOL')  # Symbol
    FONT_P = ZplFont('P', 20, 18, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_Q = ZplFont('Q', 28, 24, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_R = ZplFont('R', 35, 31, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_S = ZplFont('S', 40, 35, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_T = ZplFont('T', 48, 42, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_U = ZplFont('U', 59, 53, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_V = ZplFont('V', 80, 71, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_0 = ZplFont('0', 15, 12, 'U-L-D')  # Uppercase, Lowercase, Digits


class ZplStandardFonts24Dots(EnumBase):
    """Fontes padrão de 24 pontos, 600 DPI."""
    FONT_A = ZplFont('A', 9, 5, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_B = ZplFont('B', 11, 7, 'U')  # Uppercase
    FONT_D = ZplFont('D', 18, 10, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_E = ZplFont('E', 42, 20, 'OCR-B')  # OCR-B, Uppercase, Lowercase, Digits
    FONT_F = ZplFont('F', 26, 13, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_G = ZplFont('G', 60, 40, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_H = ZplFont('H', 34, 22, 'OCR-A')  # OCR-A, Uppercase only
    FONT_GS = ZplFont('GS', 24, 24, 'SYMBOL')  # Symbol
    FONT_P = ZplFont('P', 20, 18, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_Q = ZplFont('Q', 28, 24, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_R = ZplFont('R', 35, 31, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_S = ZplFont('S', 40, 35, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_T = ZplFont('T', 48, 42, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_U = ZplFont('U', 59, 53, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_V = ZplFont('V', 80, 71, 'U-L-D')  # Uppercase, Lowercase, Digits
    FONT_0 = ZplFont('0', 15, 12, 'U-L-D')  # Uppercase, Lowercase, Digits
