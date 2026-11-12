"""Sprites de avión, naves y estación dibujados solo con 1 y 0."""
from PIL import Image, ImageDraw, ImageFont

FUENTE = r"C:\Windows\Fonts\consola.ttf"

AVION = (
    "            00000000                 ",
    "         00000000000000              ",
    "         0     11     0         11   ",
    " 1    1111111111111111111111111111   ",
    " 1  1111111111111111111111111111111  ",
    " 1    1111111111111111111111111111   ",
    "         0     11     0         11   ",
    "         00000000000000              ",
    "            00000000                 ",
)

NAVE = (
    "      010      ",
    "  0011111100  ",
    "00111111111100",
    "  0011111100  ",
    "      010      ",
)


def sprite(d, patron, x, y, tamano, color_1, color_0):
    f = ImageFont.truetype(FUENTE, tamano)
    paso = tamano * .61
    for fila, linea in enumerate(patron):
        for columna, cifra in enumerate(linea):
            if cifra in "01":
                d.text((x + columna * paso, y + fila * tamano), cifra,
                       font=f, fill=color_1 if cifra == "1" else color_0)


def avion(d, x, y):
    sprite(d, AVION, x, y, 12, (238, 195, 124, 255), (133, 191, 211, 255))


def nave(d, x, y, tamano=10):
    sprite(d, NAVE, x, y, tamano, (155, 225, 227, 255), (93, 165, 193, 255))


def estacion(d, x, y):
    # Paneles solares a ambos lados y núcleo central.
    f = ImageFont.truetype(FUENTE, 12)
    for lado in (-1, 1):
        for fila in range(12):
            for columna in range(13):
                px = x + lado * (98 + columna * 12)
                py = y + fila * 12
                d.text((px, py), "01"[(fila + columna) % 2], font=f,
                       fill=(83, 155, 190, 225))
        for columna in range(7):
            px = x + lado * (15 + columna * 12)
            d.text((px, y + 67), "1", font=f, fill=(178, 210, 220, 255))
    nucleo = (
        "  00111100  ",
        " 0111111110 ",
        "001111111100",
        "001111111100",
        " 0111111110 ",
        "  00111100  ",
    )
    sprite(d, nucleo, x - 38, y + 35, 11,
           (208, 224, 218, 255), (102, 165, 186, 255))


if __name__ == "__main__":
    im = Image.new("RGB", (520, 160), (13, 17, 23))
    avion(ImageDraw.Draw(im), 40, 25)
    im.save("avion_diseno.png")
