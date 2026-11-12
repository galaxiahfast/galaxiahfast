"""Renderiza un bucle de 10 s con cometas en resolución 2000 × 8000."""
from pathlib import Path
import math
import random
import subprocess

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont


CARPETA = Path(__file__).resolve().parent
BASE = CARPETA / "fondo_binario_2000x8000.png"
VIDEO = CARPETA / "portada_cometas_2000x8000.mp4"
GIF = CARPETA / "portada_cometas_2000x8000.gif"
ANCHO, ALTO = 2000, 8000
FPS, SEGUNDOS = 5, 10
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


FUENTE = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 15)
FUENTE_ESTRELLA = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 13)
FUENTE_BOLA = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 13)
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


def dibujar_bola(d, t):
    """Bola de ramas rodando por la arena, formada por 0 y 1."""
    cx = -110 + 222 * t
    cy = 7800 + 22 * math.sin(cx / 180)
    giro = t * 3.2
    for i in range(100):
        angulo = math.tau * i / 100 + giro
        radio = 49 + 10 * math.sin(i * 2.7)
        x = cx + radio * math.cos(angulo)
        y = cy + radio * math.sin(angulo)
        if 0 <= x < ANCHO:
            d.text((x, y), "1" if i % 2 else "0", font=FUENTE_BOLA,
                   fill=(176, 157, 119, 230))
    for i in range(32):
        angulo = math.tau * i / 32 - giro * .8
        radio = 14 + (i % 4) * 8
        x = cx + radio * math.cos(angulo)
        y = cy + radio * math.sin(angulo)
        if 0 <= x < ANCHO:
            d.text((x, y), "01"[i % 2], font=FUENTE_BOLA,
                   fill=(142, 132, 110, 200))


def main():
    base = Image.open(BASE).convert("RGBA")
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
                pulso = .5 + .5 * math.sin(math.tau * ciclos * t / SEGUNDOS + fase)
                alfa = int(25 + 220 * pulso ** 4)
                d.text((sx, sy), digito, font=FUENTE_ESTRELLA,
                       fill=(205, 229, 247, alfa))
            for inicio, y0, velocidad in ((.7, 1030, 1180),
                                          (3.8, 2640, 1250),
                                          (6.8, 4060, 1160)):
                tiempo = t - inicio
                x = -550 + velocidad * tiempo
                if -550 < x < ANCHO + 550:
                    y = y0 + .32 * (x + 550)
                    dibujar_cometa(d, x, y)
            dibujar_bola(d, t)
            imagen = Image.alpha_composite(base, capa).convert("RGB")
            proceso.stdin.write(imagen.tobytes())
            if (fotograma + 1) % 10 == 0:
                print(f"Video: {fotograma + 1}/{FPS * SEGUNDOS} fotogramas", flush=True)
    finally:
        proceso.stdin.close()
    error = proceso.stderr.read().decode(errors="replace")
    if proceso.wait() != 0:
        raise RuntimeError(error[-4000:])

    # Paleta compartida y compresión de cambios entre fotogramas.
    filtro = "fps=5,split[a][b];[a]palettegen=max_colors=64:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle"
    comando_gif = [FFMPEG, "-y", "-i", str(VIDEO), "-filter_complex", filtro,
                   "-loop", "0", str(GIF)]
    subprocess.run(comando_gif, check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.PIPE)
    print(VIDEO)
    print(GIF)


if __name__ == "__main__":
    main()
