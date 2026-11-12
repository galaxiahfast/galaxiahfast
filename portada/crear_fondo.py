"""Genera un cielo azul nocturno y pirámides hechas de unos y ceros."""

from pathlib import Path
import math
import random

from PIL import Image, ImageDraw, ImageFont, ImageChops


ANCHO, ALTO = 2000, 8000
AZUL = (13, 17, 23)  # Color de la segunda referencia.
DESTINO = Path(__file__).resolve().parent / "fondo_binario_2000x8000.png"
RNG = random.Random(2026)


def fuente(tamano):
    rutas = [
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\lucon.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]
    for ruta in rutas:
        if Path(ruta).exists():
            return ImageFont.truetype(ruta, tamano)
    return ImageFont.load_default()


def piramide(imagen, punta, izquierda, derecha, base, quiebre=0.52, delante=False):
    """Construye dos caras visibles, con una arista frontal en perspectiva."""
    px, py = punta
    frontal = int(izquierda + (derecha - izquierda) * quiebre)
    d = ImageDraw.Draw(imagen, "RGBA")
    if delante:
        # El cuerpo opaco oculta los caracteres de las pirámides posteriores.
        d.polygon([(px, py), (izquierda, base), (derecha, base)],
                  fill=(12, 17, 23, 255))
    f = fuente(18)

    # Cada fila sigue los límites de ambas caras. Los caracteres crecen hacia la base.
    for y in range(py + 6, base - 7, 18):
        t = (y - py) / (base - py)
        lx = px + (izquierda - px) * t
        cx = px + (frontal - px) * t
        rx = px + (derecha - px) * t
        for cara, inicio, fin in ((0, lx, cx), (1, cx, rx)):
            for x in range(int(inicio) + 3, int(fin) - 5, 12):
                if RNG.random() < .035:
                    continue
                brillo = RNG.randint(55, 125) if cara == 0 else RNG.randint(147, 233)
                # El borde de luz y las filas de bloques hacen legible el volumen.
                if cara == 1 and x - cx < 28 * t:
                    brillo = min(250, brillo + 25)
                if RNG.random() < .035:
                    brillo = 250
                if y - py < 210:
                    fuerza = 1 - (y - py) / 210
                    reflejo = 1.0 if cara == 1 else .56
                    dorado = int(110 + 145 * fuerza * reflejo)
                    color = (min(255, dorado + 12), min(255, int(dorado * .83)),
                             int(dorado * .38), 255)
                elif cara == 1 and RNG.random() < .035:
                    # Chispas aisladas del mismo reflejo sobre la cara iluminada.
                    color = (min(255, brillo + 42), min(255, brillo + 20),
                             max(30, brillo - 30), 255)
                else:
                    color = (brillo, min(255, brillo + 9), min(255, brillo + 19), 255)
                d.text((x, y), RNG.choice("0011010010110101"), font=f, fill=color)


def crear():
    imagen = Image.new("RGBA", (ANCHO, ALTO), AZUL + (255,))
    d = ImageDraw.Draw(imagen, "RGBA")

    # Nebulosas tenues hechas de muchas estrellas pequeñas.
    for _ in range(145000):
        x = RNG.randrange(ANCHO)
        y = RNG.randrange(ALTO)
        banda = math.exp(-((x - (950 + 270 * math.sin(y / 850))) / 420) ** 2)
        if RNG.random() > 0.22 + 0.65 * banda:
            continue
        intensidad = RNG.randint(42, 124)
        radio = 1 if RNG.random() < 0.96 else 2
        d.ellipse((x, y, x + radio, y + radio), fill=(145, 183, 218, intensidad))

    for _ in range(520):
        x, y = RNG.randrange(ANCHO), RNG.randrange(ALTO)
        brillo = RNG.randint(95, 210)
        radio = RNG.choice((2, 2, 3, 4))
        d.ellipse((x - radio, y - radio, x + radio, y + radio),
                  fill=(190, 219, 240, brillo))
        if radio == 4 and RNG.random() < 0.2:
            d.line((x - 15, y, x + 15, y), fill=(147, 193, 230, 65))
            d.line((x, y - 15, x, y + 15), fill=(147, 193, 230, 65))

    # Horizonte y tres pirámides, concentradas en el tramo inferior.
    piramide(imagen, (320, 6690), -230, 800, 7350, .56)
    piramide(imagen, (1710, 6810), 1270, 2230, 7370, .53)

    # Ola intermedia: oculta las bases laterales y queda detrás de la principal.
    d = ImageDraw.Draw(imagen, "RGBA")
    def ola_intermedia(x):
        return 7190 + 72 * math.sin(x / 255 + .7) + 34 * math.sin(x / 95)

    perfil = [(x, int(ola_intermedia(x))) for x in range(0, ANCHO + 1, 8)]
    d.polygon(perfil + [(ANCHO, 7520), (0, 7520)], fill=(10, 17, 24, 255))
    f_ola = fuente(10)
    for fila in range(22):
        for x in range(0, ANCHO, 9):
            y = ola_intermedia(x) + 4 + fila * 12
            if y >= 7520 or RNG.random() < .07:
                continue
            tono = max(48, int(145 - fila * 3 + 22 * math.sin(x / 260 + fila * .12)
                                + RNG.randint(-31, 20)))
            d.text((x, int(y)), RNG.choice("0011010010110101"), font=f_ola,
                   fill=(tono, min(255, tono + 11), min(255, tono + 19), 255))

    piramide(imagen, (870, 6380), 70, 1900, 7400, .53, delante=True)

    d = ImageDraw.Draw(imagen, "RGBA")
    # Arena en planos diagonales, como surcos que atraviesan el primer plano.
    horizonte = [(x, int(7290 + 42 * math.sin(x / 270) + .035 * x))
                 for x in range(0, ANCHO + 1, 10)]
    d.polygon(horizonte + [(ANCHO, ALTO), (0, ALTO)], fill=(9, 15, 21, 255))
    # Una trama tenue continua llena los huecos entre las franjas diagonales.
    f_base = fuente(10)
    for y in range(7220, ALTO - 10, 11):
        for x in range(0, ANCHO, 10):
            if y < 7290 + 42 * math.sin(x / 270) + .035 * x:
                continue
            tono = max(35, int(74 - max(0, y - 7620) * .075
                               + 11 * math.sin(x / 230 + y / 85)
                               + RNG.randint(-14, 13)))
            d.text((x, y), RNG.choice("0011010010110101"), font=f_base,
                   fill=(tono, min(255, tono + 8), min(255, tono + 15), 255))
    for plano in range(3):
        f_arena = fuente((9, 12, 15)[plano])
        paso_x = (9, 11, 14)[plano]
        numero_surcos = (25, 19, 16)[plano]
        for surco in range(numero_surcos):
            for x in range(-20, ANCHO + 20, paso_x):
                # Cada plano cruza el encuadre con distinta inclinación.
                if plano == 0:
                    y = 7270 + surco * 12 + .13 * x + 38 * math.sin(x / 230 + surco * .08)
                elif plano == 1:
                    y = 7410 + surco * 17 - .11 * x + 55 * math.sin(x / 300 + 1.2)
                else:
                    y = 7515 + surco * 25 + .16 * x + 65 * math.sin(x / 270 + 2.1)
                if y < 7290 + 42 * math.sin(x / 270) + .035 * x or y >= ALTO - 15:
                    continue
                if RNG.random() < .09:
                    continue
                brillo_cresta = 38 * math.exp(-surco / 8)
                lateral = 20 * math.sin(x / 310 + plano * 1.5)
                desvanecer = max(0, y - 7740) * .18
                tono = int(87 + brillo_cresta + lateral - desvanecer + RNG.randint(-24, 20))
                tono = max(32, min(180, tono))
                if surco < 5 and RNG.random() < .025:
                    color = (min(255, tono + 65), min(255, tono + 38), tono, 255)
                else:
                    color = (tono, min(255, tono + 10), min(255, tono + 18), 255)
                d.text((x, int(y)), RNG.choice("0011010010110101"), font=f_arena,
                       fill=color)

    # Cactus discretos, también dibujados con 1 y 0.
    patron = (
        "    10    ",
        "    01    ",
        "  1 10 0  ",
        "  0 01 1  ",
        "  111011  ",
        "    10    ",
        "    01    ",
        "    10    ",
    )
    for cx, cy, escala, tono_cactus in (
            (280, 7370, 6, 115), (650, 7380, 5, 109),
            (1510, 7400, 6, 119), (1080, 7450, 7, 135),
            (460, 7530, 8, 148), (1320, 7600, 9, 160),
            (790, 7720, 11, 179), (1690, 7780, 12, 190)):
        f_cactus = fuente(escala)
        for fila, linea in enumerate(patron):
            for columna, digito in enumerate(linea):
                if digito != " ":
                    d.text((cx + columna * escala * .62, cy + fila * escala),
                           digito, font=f_cactus,
                           fill=(tono_cactus, min(255, tono_cactus + 18),
                                 max(0, tono_cactus - 20), 255),
                           stroke_width=1, stroke_fill=(5, 15, 14, 255))
    # Desvanecimiento suave en los cuatro bordes hacia el azul original.
    margen_x, margen_y = 240, 360
    horizontal = Image.new("L", (ANCHO, 1))
    horizontal.putdata([
        int(255 * min(1, x / margen_x, (ANCHO - 1 - x) / margen_x))
        for x in range(ANCHO)
    ])
    vertical = Image.new("L", (1, ALTO))
    vertical.putdata([
        int(255 * min(1, y / margen_y, (ALTO - 1 - y) / margen_y))
        for y in range(ALTO)
    ])
    mascara = ImageChops.multiply(horizontal.resize((ANCHO, ALTO)),
                                 vertical.resize((ANCHO, ALTO)))
    resultado = Image.composite(imagen.convert("RGB"),
                               Image.new("RGB", (ANCHO, ALTO), AZUL), mascara)
    resultado.save(DESTINO, optimize=True)
    print(DESTINO)


if __name__ == "__main__":
    crear()
