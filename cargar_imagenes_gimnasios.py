
import json
import re
import time
import unicodedata
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import os
import django

from django.core.files.base import ContentFile


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configuracion.settings")
django.setup()

from pokemon.models import Gimnasio


API = "https://archives.bulbagarden.net/w/api.php"

# Ciudad de tu base de datos: nombre utilizado en los archivos oficiales.
GIMNASIOS = {
    "Ciudad Plateada": ("Pewter", "Kanto"),
    "Ciudad Celeste": ("Cerulean", "Kanto"),
    "Ciudad Carmín": ("Vermilion", "Kanto"),
    "Ciudad Azulona": ("Celadon", "Kanto"),
    "Ciudad Fucsia": ("Fuchsia", "Kanto"),
    "Ciudad Azafrán": ("Saffron", "Kanto"),
    "Isla Canela": ("Cinnabar", "Kanto"),
    "Ciudad Verde": ("Viridian", "Kanto"),

    "Ciudad Malva": ("Violet", "Johto"),
    "Pueblo Azalea": ("Azalea", "Johto"),
    "Ciudad Trigal": ("Goldenrod", "Johto"),
    "Ciudad Iris": ("Ecruteak", "Johto"),
    "Ciudad Orquídea": ("Cianwood", "Johto"),
    "Ciudad Olivo": ("Olivine", "Johto"),
    "Pueblo Caoba": ("Mahogany", "Johto"),
    "Ciudad Endrino": ("Blackthorn", "Johto"),
}


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", texto.lower())


def consultar_api(parametros):
    parametros["format"] = "json"

    url = API + "?" + urlencode(parametros)

    solicitud = Request(
        url,
        headers={
            "User-Agent": "PokedexDjango/1.0 (automatic gym image loader)"
        }
    )

    with urlopen(solicitud, timeout=45) as respuesta:
        return json.loads(respuesta.read().decode("utf-8"))


def obtener_archivos(categoria):
    archivos = []
    continuation = {}

    while True:
        parametros = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": f"Category:{categoria}",
            "cmtype": "file",
            "cmlimit": "500",
        }

        parametros.update(continuation)

        datos = consultar_api(parametros)

        miembros = datos.get("query", {}).get("categorymembers", [])

        archivos.extend(
            miembro["title"]
            for miembro in miembros
        )

        continuation = datos.get("continue", {})

        if not continuation:
            break

    return archivos


def elegir_imagen(archivos, ciudad, region):
    candidatos = []

    ciudad_normalizada = normalizar(ciudad)

    for archivo in archivos:
        nombre = archivo.replace("File:", "")
        nombre_normalizado = normalizar(nombre)

        if ciudad_normalizada not in nombre_normalizado:
            continue

        if "gym" not in nombre_normalizado:
            continue

        if not nombre.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            continue

        # Solo imágenes de edificios, mapas o interiores.
        if any(
            palabra in nombre_normalizado
            for palabra in ["leader", "trainer", "character", "badge"]
        ):
            continue

        puntos = 0

        if "exterior" in nombre_normalizado:
            puntos += 100

        if "screenshot" in nombre_normalizado:
            puntos += 30

        if "interior" in nombre_normalizado:
            puntos += 20

        if region == "Kanto" and "lgpe" in nombre_normalizado:
            puntos += 50

        if region == "Johto" and "hgss" in nombre_normalizado:
            puntos += 50

        if "gsc" in nombre_normalizado:
            puntos += 10

        candidatos.append((puntos, archivo))

    if not candidatos:
        return None

    candidatos.sort(reverse=True)

    return candidatos[0][1]


def obtener_url_imagen(titulo):
    datos = consultar_api({
        "action": "query",
        "titles": titulo,
        "prop": "imageinfo",
        "iiprop": "url",
    })

    paginas = datos.get("query", {}).get("pages", {})

    for pagina in paginas.values():
        imagenes = pagina.get("imageinfo", [])

        if imagenes:
            return imagenes[0]["url"]

    return None


def descargar_imagen(url):
    solicitud = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 Pokedex Django"
        }
    )

    with urlopen(solicitud, timeout=60) as respuesta:
        contenido = respuesta.read()

    if not contenido.startswith(b"\x89PNG\r\n\x1a\n") and not contenido.startswith(b"\xff\xd8"):
        raise ValueError("El archivo recibido no es una imagen PNG o JPG válida.")

    return contenido


def ejecutar():
    print("\n========================================")
    print(" DESCARGA AUTOMÁTICA DE GIMNASIOS")
    print("========================================\n")

    print("Consultando imágenes oficiales de Kanto...")
    kanto = obtener_archivos("Kanto maps")

    print("Consultando imágenes oficiales de Johto...")
    johto = obtener_archivos("Johto maps")

    resultados = {
        "Kanto": kanto,
        "Johto": johto,
    }

    exitos = 0
    errores = []

    for ciudad, (nombre_ingles, region) in GIMNASIOS.items():

        print(f"\nBuscando: {ciudad} ({region})")

        gimnasio = Gimnasio.objects.filter(
            ciudad__iexact=ciudad
        ).first()

        if not gimnasio:
            print("  No existe este gimnasio en la base de datos.")
            errores.append(ciudad)
            continue

        archivo = elegir_imagen(
            resultados[region],
            nombre_ingles,
            region
        )

        if not archivo:
            print("  No se encontró una imagen adecuada.")
            errores.append(ciudad)
            continue

        try:
            url = obtener_url_imagen(archivo)

            if not url:
                raise ValueError("No se encontró la dirección de la imagen.")

            contenido = descargar_imagen(url)

            extension = ".png" if contenido.startswith(b"\x89PNG") else ".jpg"

            nombre_archivo = f"gimnasio_{gimnasio.pk}{extension}"

            # Reemplaza la imagen anterior del líder por la del edificio.
            gimnasio.imagen_archivo.save(
                nombre_archivo,
                ContentFile(contenido),
                save=True
            )

            print(f"  Imagen instalada: {nombre_archivo}")
            print(f"  Fuente: {archivo}")

            exitos += 1

            time.sleep(0.4)

        except Exception as error:
            print(f"  Error: {error}")
            errores.append(ciudad)

    print("\n========================================")
    print(" RESULTADO")
    print("========================================")
    print(f"Imágenes instaladas: {exitos}/16")

    if errores:
        print("\nGimnasios pendientes:")
        for ciudad in errores:
            print(" -", ciudad)

    else:
        print("\n¡Los 16 gimnasios tienen imágenes asignadas!")

    print("\nCarpeta: media/gimnasios/")


if __name__ == "__main__":
    ejecutar()
