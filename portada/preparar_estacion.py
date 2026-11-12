"""Prepara la estación binaria aportada por el usuario para el cielo azul."""
from pathlib import Path
from PIL import Image

CARPETA = Path(__file__).resolve().parent
FUENTE = CARPETA / "estacion_referencia.png"
DESTINO = CARPETA / "estacion_binaria.png"


def main():
    imagen = Image.open(FUENTE).convert("RGB")
    pixeles = imagen.load()
    salida = Image.new("RGBA", imagen.size)
    dst = salida.load()
    for y in range(imagen.height):
        for x in range(imagen.width):
            r, g, b = pixeles[x, y]
            oscuridad = 255 - min(r, g, b)
            alfa = min(255, max(0, (oscuridad - 5) * 3))
            dst[x, y] = (r, g, b, alfa)
    caja = salida.getbbox()
    salida = salida.crop(caja)
    salida.save(DESTINO)
    print(DESTINO, salida.size)


if __name__ == "__main__":
    main()
