from enum import Enum


class ZplPrintOrientation(Enum):
    """Orientação de campo."""
    NORMAL = 'N'  # Normal
    INVERT = 'I'  # Invertido


class ZplOrientation(Enum):
    """Orientação de campo."""
    NORMAL = 'N'  # 0 graus
    ROTATE_90 = 'R'  # 90 graus
    ROTATE_180 = 'I'  # 180 graus
    ROTATE_270 = 'B'  # 270 graus


class ZplDirection(Enum):
    """Direção do texto."""
    VERTICAL = 'V'  # Vertical
    HORIZONTAL = 'H'  # Horizontal
    REVERSE = 'R'  # Reverso


class ZplJustification(Enum):
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


class ZplStandardFonts6Dots(Enum):
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


class ZplStandardFonts8Dots(Enum):
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


class ZplStandardFonts12Dots(Enum):
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


class ZplStandardFonts24Dots(Enum):
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
