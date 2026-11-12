"""Estación espacial 3D hecha con los mismos dígitos que las pirámides."""
from pathlib import Path
import random

from PIL import Image, ImageDraw, ImageFont

CARPETA = Path(__file__).resolve().parent
DESTINO = CARPETA / "estacion_3d.png"
RNG = random.Random(73)
W, H = 1000, 620
FUENTE = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 18)


def cara(imagen, puntos, oscuro, claro, paso_x=14, paso_y=20):
    """Rellena una cara con 0/1 y un gradiente de luz lateral."""
    mascara = Image.new("1", (W, H))
    ImageDraw.Draw(mascara).polygon(puntos, fill=1)
    m = mascara.load()
    d = ImageDraw.Draw(imagen)
    xmin = max(0, int(min(p[0] for p in puntos)))
    xmax = min(W, int(max(p[0] for p in puntos)))
    ymin = max(0, int(min(p[1] for p in puntos)))
    ymax = min(H, int(max(p[1] for p in puntos)))
    for y in range(ymin, ymax, paso_y):
        for x in range(xmin, xmax, paso_x):
            if not m[x, y] or RNG.random() < .035:
                continue
            luz = (x - xmin) / max(1, xmax - xmin)
            variacion = RNG.randint(-18, 18)
            color = tuple(max(15, min(255, int(a + (b - a) * luz + variacion)))
                          for a, b in zip(oscuro, claro))
            d.text((x, y), RNG.choice("0011010010110101"), font=FUENTE,
                   fill=color + (255,))


def crear():
    im = Image.new("RGBA", (W, H))
    # Oclusión del mismo azul del cielo: elimina estrellas detrás del cuerpo,
    # sin agregar superficies pintadas de otro color.
    fondo = ImageDraw.Draw(im)
    siluetas = [
        [(35, 192), (300, 152), (300, 330), (35, 370)],
        [(700, 152), (965, 192), (965, 370), (700, 330)],
        [(260, 265), (740, 265), (740, 305), (260, 305)],
        [(225, 230), (290, 240), (320, 300), (290, 360),
         (225, 370), (190, 310)],
        [(775, 230), (810, 310), (775, 370), (710, 360),
         (680, 300), (710, 240)],
        [(370, 230), (390, 135), (440, 90), (560, 90),
         (610, 135), (630, 230)],
        [(330, 230), (670, 230), (730, 315), (670, 400),
         (330, 400), (270, 315)],
        [(410, 395), (590, 395), (565, 530), (435, 530)],
    ]
    for puntos in siluetas:
        fondo.polygon(puntos, fill=(13, 17, 23, 255))
    # Paneles solares en perspectiva: caras superiores claras e inferiores oscuras.
    cara(im, [(35, 192), (300, 152), (300, 330), (35, 370)],
         (45, 92, 113), (134, 201, 215))
    cara(im, [(700, 152), (965, 192), (965, 370), (700, 330)],
         (61, 119, 143), (163, 222, 225))
    for x0, x1, y0, y1 in ((35, 300, 192, 370), (700, 965, 152, 370)):
        for offset in (55, 115, 175):
            cara(im, [(x0 + offset, y0), (x0 + offset + 12, y0),
                      (x0 + offset + 12, y1), (x0 + offset, y1)],
                 (169, 207, 206), (206, 231, 217), 12, 20)

    # Bastidor, módulos laterales y cúpula detrás del casco central.
    cara(im, [(260, 265), (740, 265), (740, 305), (260, 305)],
         (82, 104, 125), (192, 214, 216))
    cara(im, [(225, 230), (290, 240), (320, 300), (290, 360),
              (225, 370), (190, 310)], (60, 71, 101), (178, 159, 187))
    cara(im, [(775, 230), (810, 310), (775, 370), (710, 360),
              (680, 300), (710, 240)], (76, 90, 119), (207, 183, 198))
    cara(im, [(370, 230), (390, 135), (440, 90), (560, 90),
              (610, 135), (630, 230)], (41, 83, 100), (159, 218, 202))

    # Casco hexagonal: lado izquierdo en sombra, lado derecho iluminado.
    cara(im, [(330, 230), (500, 230), (500, 400), (330, 400), (270, 315)],
         (45, 56, 83), (95, 104, 133))
    cara(im, [(500, 230), (670, 230), (730, 315), (670, 400), (500, 400)],
         (180, 177, 187), (249, 232, 200))
    cara(im, [(330, 230), (670, 230), (630, 270), (370, 270)],
         (139, 163, 170), (231, 224, 188))
    cara(im, [(410, 395), (590, 395), (565, 530), (435, 530)],
         (58, 74, 105), (155, 166, 176))
    # Luces doradas y antenas hechas de caracteres, sin trazos sólidos.
    cara(im, [(493, 48), (507, 48), (507, 90), (493, 90)],
         (158, 178, 180), (220, 222, 180))
    cara(im, [(455, 305), (545, 305), (545, 345), (455, 345)],
         (145, 104, 57), (245, 198, 104))
    for x in (410, 590):
        cara(im, [(x, 390), (x + 20, 390), (x + 20, 455), (x, 455)],
             (131, 92, 58), (239, 189, 111))
    im.save(DESTINO)
    print(DESTINO)


if __name__ == "__main__":
    crear()
