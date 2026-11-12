"""Reconstruye la estación aportada como caracteres binarios transparentes."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CARPETA = Path(__file__).resolve().parent
FUENTE = CARPETA / "estacion_referencia.png"
DESTINO = CARPETA / "estacion_binaria.png"


def main():
    imagen = Image.open(FUENTE).convert("RGB")
    salida = Image.new("RGBA", imagen.size)
    dibujo = ImageDraw.Draw(salida)
    fuente = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 9)
    ancho, alto = 8, 10
    for y in range(0, imagen.height - alto, alto):
        for x in range(0, imagen.width - ancho, ancho):
            muestra = imagen.crop((x, y, x + ancho, y + alto))
            pixeles = [p for p in muestra.get_flattened_data()
                       if 255 - min(p) > 40]
            if len(pixeles) < 5:
                continue
            pixeles.sort(key=lambda p: min(p))
            oscuros = pixeles[:max(1, len(pixeles) // 3)]
            r, g, b = (sum(p[i] for p in oscuros) // len(oscuros)
                       for i in range(3))
            cifra = "0" if (x // ancho + y // alto) % 3 else "1"
            escala = max(1, 190 / max(1, r, g, b))
            color = tuple(min(255, int(c * escala)) for c in (r, g, b))
            dibujo.text((x, y), cifra, font=fuente, fill=color + (255,))
    caja = salida.getbbox()
    salida = salida.crop(caja)
    salida.save(DESTINO)
    print(DESTINO, salida.size)


if __name__ == "__main__":
    main()
