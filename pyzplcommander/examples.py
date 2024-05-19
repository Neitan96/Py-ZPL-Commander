from pyzplcommander import *


# Exemplo de uso do módulo pyzplcommander
zebra_printer = ZebraNetworkPrinter(host='127.0.0.1', port=9100)

# Criando e imprimindo uma nova etiqueta
with zebra_printer.new_label() as lb:
    lb.font(font=ZplStandardFonts8Dots.FONT_A(), height=18, width=10)
    lb.draw_text(text='Hello, World!', x=20, y=20)
    lb.font(font=ZplStandardFonts8Dots.FONT_B())
    lb.draw_text(text='Simple ZPL label', x=20, y=35)
    lb.add_zpl_blank_line()
    with lb.new_field() as fd:
        fd.position(x=20, y=50)
        fd.font(font=ZplStandardFonts8Dots.FONT_D())
        fd.direction(direction=ZplDirection.VERTICAL(), additional_inter_chars=3)
        fd.data("It's is advanced field builder")

    # Para visualizar o código ZPL gerado use o método format_to_zpl()
    print(lb.format_to_zpl(break_lines=True))
