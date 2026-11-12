"""Prepara el avión aportado y ensancha solamente el cartel."""
from pathlib import Path
from PIL import Image

CARPETA = Path(__file__).resolve().parent
FUENTE = CARPETA / "avion_referencia.png"
DESTINO = CARPETA / "avion_usuario.png"


def main():
    origen = Image.open(FUENTE).convert("RGB")
    corte = 510
    izquierda = origen.crop((0, 0, corte, origen.height))
    cartel = origen.crop((corte, 0, origen.width, origen.height))
    cartel = cartel.resize((int(cartel.width * 1.35), cartel.height),
                           Image.Resampling.LANCZOS)
    ancho = izquierda.width + cartel.width
    imagen = Image.new("RGB", (ancho, origen.height), (255, 255, 255))
    imagen.paste(izquierda, (0, 0))
    imagen.paste(cartel, (corte, 0))

    salida = Image.new("RGBA", imagen.size)
    src, dst = imagen.load(), salida.load()
    for y in range(imagen.height):
        for x in range(imagen.width):
            r, g, b = src[x, y]
            tinta = 255 - min(r, g, b)
            alfa = max(0, min(255, (tinta - 10) * 9))
            dst[x, y] = (r, g, b, alfa)
    salida.crop(salida.getbbox()).save(DESTINO)
    print(DESTINO)


if __name__ == "__main__":
    main()
