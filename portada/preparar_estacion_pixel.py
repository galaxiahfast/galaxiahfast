"""Convierte la estación pixelada aportada a un PNG transparente."""
from pathlib import Path
from PIL import Image

CARPETA = Path(__file__).resolve().parent
FUENTE = CARPETA / "estacion_pixel_referencia.webp"
DESTINO = CARPETA / "estacion_pixel.png"


def main():
    origen = Image.open(FUENTE).convert("RGB")
    salida = Image.new("RGBA", origen.size)
    src, dst = origen.load(), salida.load()
    for y in range(origen.height):
        for x in range(origen.width):
            r, g, b = src[x, y]
            tinta = 255 - min(r, g, b)
            alfa = max(0, min(255, (tinta - 5) * 12))
            dst[x, y] = (r, g, b, alfa)
    salida.crop(salida.getbbox()).save(DESTINO)
    print(DESTINO)


if __name__ == "__main__":
    main()
