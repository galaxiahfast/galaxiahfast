"""Renderiza un bucle de 10 s con cometas en resolución 2000 × 8000."""
from pathlib import Path
import math
import subprocess

import imageio_ffmpeg
from PIL import Image, ImageDraw


CARPETA = Path(__file__).resolve().parent
BASE = CARPETA / "fondo_binario_2000x8000.png"
VIDEO = CARPETA / "portada_cometas_2000x8000.mp4"
GIF = CARPETA / "portada_cometas_2000x8000.gif"
ANCHO, ALTO = 2000, 8000
FPS, SEGUNDOS = 5, 10
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def dibujar_cometa(d, x, y, longitud, intensidad):
    # Cola azul dorada y núcleo brillante. Sale del cuadro al principio y al final.
    for anchura, alpha in ((26, 18), (13, 32), (5, 100)):
        d.line((x - longitud, y + longitud * .22, x, y),
               fill=(170, 202, 229, int(alpha * intensidad)), width=anchura)
    for radio, alpha in ((20, 35), (10, 100), (4, 250)):
        d.ellipse((x - radio, y - radio, x + radio, y + radio),
                  fill=(255, 233, 185, int(alpha * intensidad)))


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
            for inicio, y0, velocidad, largo in ((.7, 1070, 1480, 330),
                                                 (3.8, 2850, 1560, 430),
                                                 (6.8, 4350, 1450, 380)):
                tiempo = t - inicio
                x = -largo + velocidad * tiempo
                if -largo < x < ANCHO + largo:
                    y = y0 - 70 * tiempo
                    entrada = min(1, max(0, (x + largo) / 200))
                    salida = min(1, max(0, (ANCHO + largo - x) / 200))
                    dibujar_cometa(d, x, y, largo, entrada * salida)
            # Un brillo suave y periódico sobre la punta central.
            brillo = int(13 + 12 * (1 + math.sin(2 * math.pi * t / SEGUNDOS)))
            d.ellipse((845, 6355, 900, 6410), fill=(255, 205, 100, brillo))
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
