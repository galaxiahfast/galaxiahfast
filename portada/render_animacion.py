"""Renderiza un bucle de 10 s con cometas en resolución 2000 × 8000."""
from pathlib import Path
import math
import random
import subprocess

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageFilter


CARPETA = Path(__file__).resolve().parent
BASE = CARPETA / "fondo_binario_2000x8000.png"
VIDEO = CARPETA / "portada_cometas_2000x8000.mp4"
GIF = CARPETA / "portada_cometas_2000x8000.gif"
ESTACION = CARPETA / "estacion_3d.png"
NAVE_USUARIO = CARPETA / "nave_usuario.png"
AVION_USUARIO = CARPETA / "avion_usuario.png"
ANCHO, ALTO = 2000, 8000
FPS, SEGUNDOS = 20, 10
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


FUENTE = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 15)
FUENTE_ESTRELLA = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 13)
RNG = random.Random(1977)
ESTRELLAS = [(RNG.randrange(130, 1870), RNG.randrange(260, 5900),
              RNG.randrange(1, 5), RNG.random() * math.tau,
              RNG.choice("01")) for _ in range(65)]


def dibujar_cometa(d, x, y):
    """Cometa descendente hecho exclusivamente de caracteres binarios."""
    for i in range(66):
        avance = i * 8
        xx = x - avance
        yy = y - avance * .32
        if xx < 0 or xx >= ANCHO:
            continue
        alfa = max(20, int(250 * (1 - i / 66) ** 1.6))
        d.text((xx, yy), "1" if i % 3 else "0", font=FUENTE,
               fill=(210, 228, 247, alfa))
    for dx, dy, digito in ((0, 0, "1"), (9, 4, "0"), (3, 11, "1")):
        d.text((x + dx, y + dy), digito, font=FUENTE,
               fill=(255, 239, 194, 245))


def destello(d, x, y, t, fase=0, dorado=False, tamano=20):
    brillo = max(0, math.sin(math.tau * (3 * t / SEGUNDOS) + fase)) ** 5
    if brillo < .08:
        return
    longitud = int(tamano * brillo)
    alfa = int(70 + 185 * brillo)
    color = (255, 215, 117, alfa) if dorado else (197, 229, 255, alfa)
    halo = (255, 196, 99, 60) if dorado else (120, 190, 245, 60)
    d.line((x - longitud - 5, y, x + longitud + 5, y), fill=halo, width=3)
    d.line((x, y - longitud - 5, x, y + longitud + 5), fill=halo, width=3)
    d.line((x - longitud, y, x + longitud, y), fill=color, width=1)
    d.line((x, y - longitud, x, y + longitud), fill=color, width=1)
    d.point((x, y), fill=(255, 252, 227, 255))


def render_video():
    base = Image.open(BASE).convert("RGBA")
    estacion_3d = Image.open(ESTACION).convert("RGBA")
    nave_fuente = Image.open(NAVE_USUARIO).convert("RGBA")
    naves = []
    margen_luz = 40
    for ancho in (220, 220, 220):
        nave = nave_fuente.copy()
        nave.thumbnail((ancho, 220))
        mascara = Image.new("L", (nave.width + 80, nave.height + 80))
        mascara.paste(nave.getchannel("A"), (margen_luz, margen_luz))
        mascara = mascara.filter(ImageFilter.GaussianBlur(20))
        naves.append((nave, mascara))
    avion_usuario = Image.open(AVION_USUARIO).convert("RGBA")
    avion_usuario.thumbnail((520, 230))
    comando = [FFMPEG, "-y", "-f", "rawvideo", "-pixel_format", "rgb24",
               "-video_size", f"{ANCHO}x{ALTO}", "-framerate", str(FPS),
               "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
               "-crf", "23", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
               str(VIDEO)]
    proceso = subprocess.Popen(comando, stdin=subprocess.PIPE,
                               stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        for fotograma in range(FPS * SEGUNDOS):
            t = fotograma / FPS
            capa = Image.new("RGBA", (ANCHO, ALTO))
            d = ImageDraw.Draw(capa, "RGBA")
            for sx, sy, ciclos, fase, digito in ESTRELLAS:
                pulso = .5 + .5 * math.sin(math.tau * ciclos * 2 * t / SEGUNDOS + fase)
                alfa = int(25 + 220 * pulso ** 4)
                d.text((sx, sy), digito, font=FUENTE_ESTRELLA,
                       fill=(205, 229, 247, alfa))
            for inicio, y0, velocidad in ((.5, 700, 1900),
                                          (2.3, 1730, 1840),
                                          (4.1, 2790, 1960),
                                          (5.9, 3850, 1880),
                                          (7.7, 4850, 1920)):
                tiempo = t - inicio
                x = -550 + velocidad * tiempo
                if -550 < x < ANCHO + 550:
                    y = y0 + .32 * (x + 550)
                    dibujar_cometa(d, x, y)
            for sx, sy, fase, tamano in (
                    (320, 980, .3, 13), (1530, 1160, 1.9, 28),
                    (610, 3060, 3.4, 19), (1740, 4700, 5.1, 34),
                    (910, 1390, 2.1, 9), (260, 2330, 4.8, 24),
                    (1360, 3300, .9, 15), (1150, 5280, 3.8, 27)):
                destello(d, sx, sy, t, fase, tamano=tamano)
            for sx, sy, fase, tamano in (
                    (338, 6720, .4, 12), (899, 6416, 2.0, 20),
                    (1728, 6840, 4.1, 13)):
                destello(d, sx, sy, t, fase, dorado=True, tamano=tamano)

            ex = int((ANCHO - estacion_3d.width) / 2
                     + 8 * math.sin(math.tau * t / SEGUNDOS))
            ey = int(300 + 16 * math.sin(math.tau * t / SEGUNDOS))
            capa.alpha_composite(estacion_3d, (ex, ey))
            # Tres copias del diseño aportado, con recorridos independientes.
            posiciones = (
                (2250 - 430 * (t - .7), 1950 + 100 * math.sin(t * 1.4)),
                (-250 + 400 * (t - 2), 2600 + 75 * math.sin(t * 1.7)),
                (550 + 750 * math.sin(math.tau * t / SEGUNDOS),
                 3020 + 60 * math.sin(math.tau * t / SEGUNDOS)),
            )
            for i, ((nave, mascara), (px, py)) in enumerate(zip(naves, posiciones)):
                nx, ny = int(px), int(py)
                if nx + nave.width < -40 or nx > ANCHO + 40:
                    continue
                luz = .16 + .18 * (1 + math.sin(math.tau * 3 * t / SEGUNDOS + i)) / 2
                halo = Image.new("RGBA", mascara.size, (80, 175, 236, 0))
                halo.putalpha(mascara.point(lambda a: int(a * luz)))
                capa.alpha_composite(halo, (nx - margen_luz, ny - margen_luz))
                capa.alpha_composite(nave, (nx, ny))
            # Avión y cartel originales, de derecha a izquierda.
            ax = int(2250 - 320 * t + 35 * math.sin(math.tau * t / SEGUNDOS))
            ay = int(6140 + 45 * math.sin(math.tau * t / SEGUNDOS))
            capa.alpha_composite(avion_usuario, (ax, ay))
            imagen = Image.alpha_composite(base, capa).convert("RGB")
            proceso.stdin.write(imagen.tobytes())
            if (fotograma + 1) % 10 == 0:
                print(f"Video: {fotograma + 1}/{FPS * SEGUNDOS} fotogramas", flush=True)
    finally:
        proceso.stdin.close()
    error = proceso.stderr.read().decode(errors="replace")
    if proceso.wait() != 0:
        raise RuntimeError(error[-4000:])



def render_gif():
    # La paleta fija mantiene #0D1117 idéntico al fondo de GitHub.
    borde = ("format=rgb24,"
             "drawbox=x=0:y=0:w=32:h=ih:c=0x0d1117:t=fill,"
             "drawbox=x=iw-32:y=0:w=32:h=ih:c=0x0d1117:t=fill,"
             "drawbox=x=0:y=0:w=iw:h=32:c=0x0d1117:t=fill,"
             "drawbox=x=0:y=ih-32:w=iw:h=32:c=0x0d1117:t=fill")
    paleta = CARPETA / "paleta_temporal.png"
    try:
        subprocess.run([FFMPEG, "-y", "-i", str(VIDEO),
                        "-vf", f"{borde},palettegen=max_colors=128:stats_mode=diff",
                        str(paleta)], check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.PIPE)
        p = Image.open(paleta).convert("RGB")
        pix = p.load()
        destino = (13, 17, 23)
        xy = min(((x, y) for y in range(p.height) for x in range(p.width)),
                 key=lambda q: sum((pix[q[0], q[1]][i] - destino[i]) ** 2
                                   for i in range(3)))
        pix[xy] = destino
        # H.264 introduce varios tonos casi idénticos en zonas que eran lisas.
        # Unificarlos evita un rectángulo ligeramente más oscuro en GitHub.
        for yy in range(p.height):
            for xx in range(p.width):
                r, g, b = pix[xx, yy]
                if 8 <= r <= 15 and 13 <= g <= 19 and 19 <= b <= 26:
                    pix[xx, yy] = destino
        p.save(paleta)
        filtro = f"[0:v]{borde}[v];[v][1:v]paletteuse=dither=none"
        subprocess.run([FFMPEG, "-y", "-i", str(VIDEO), "-i", str(paleta),
                        "-filter_complex", filtro, "-loop", "0", str(GIF)],
                       check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.PIPE)
    finally:
        paleta.unlink(missing_ok=True)


def main():
    render_video()
    render_gif()
    print(VIDEO)
    print(GIF)


if __name__ == "__main__":
    main()
