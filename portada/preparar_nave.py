"""Quita el blanco exterior sin redibujar la nave aportada."""
from pathlib import Path
from PIL import Image

CARPETA = Path(__file__).resolve().parent
FUENTE = CARPETA / "nave_referencia.png"
DESTINO = CARPETA / "nave_usuario.png"


def main():
    origen = Image.open(FUENTE).convert("RGB")
    salida = Image.new("RGBA", origen.size)
    src, dst = origen.load(), salida.load()
    for y in range(origen.height):
        for x in range(origen.width):
            r, g, b = src[x, y]
            tinta = 255 - min(r, g, b)
            alfa = max(0, min(255, (tinta - 10) * 9))
            dst[x, y] = (r, g, b, alfa)
    caja = salida.getbbox()
    salida.crop(caja).save(DESTINO)
    print(DESTINO, caja)


if __name__ == "__main__":
    main()
