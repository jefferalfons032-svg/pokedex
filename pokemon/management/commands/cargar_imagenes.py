
from urllib.request import Request, urlopen
from urllib.parse import quote
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from pokemon.models import Entrenador, Profesor, Gimnasio, Region


BASE_TRAINERS = (
    "https://play.pokemonshowdown.com/sprites/trainers/"
)

IMAGENES_ENTRENADORES = {
    "red": ["red.png"],
    "ash": ["ash.png", "red.png"],
    "misty": ["misty.png"],
    "brock": ["brock.png"],
    "gary": ["blue.png"],
    "gold": ["ethan.png"],
    "kris": ["kris.png"],
    "silver": ["silver.png"],
    "luna": ["acetrainerf-gen6.png"],
    "daniel": ["acetrainer-gen6.png"],
    "sofia": ["risingstarf.png"],
    "valentina": ["risingstarf-gen6.png"],
    "mateo": ["acetrainer-gen4.png"],
    "camila": ["risingstarf-gen6.png"],
    "lucas": ["acetrainer-gen3.png"],
}

IMAGENES_PROFESORES = {
    "oak": ["oak.png"],
    "elm": ["elm.png"],
    "cipres": ["sycamore.png"],
    "encina": ["birch.png"],
    "serbal": ["rowan.png"],
}

IMAGENES_LIDERES = {
    "brock": ["brock.png"],
    "misty": ["misty.png"],
    "surge": ["surge.png"],
    "erika": ["erika.png"],
    "koga": ["koga.png"],
    "sabrina": ["sabrina.png"],
    "blaine": ["blaine.png"],
    "giovanni": ["giovanni.png"],
    "falkner": ["falkner.png"],
    "bugsy": ["bugsy.png"],
    "whitney": ["whitney.png"],
    "morty": ["morty.png"],
    "chuck": ["chuck.png"],
    "jasmine": ["jasmine.png"],
    "pryce": ["pryce.png"],
    "clair": ["clair.png"],
}

IMAGENES_REGIONES = {
    "kanto": "Kanto_Map.png",
    "johto": "Johto_Map.png",
}


class Command(BaseCommand):
    help = (
        "Descarga imágenes para entrenadores, profesores, "
        "gimnasios y regiones."
    )

    def descargar(self, url):
        solicitud = Request(
            url,
            headers={
                "User-Agent": "PokedexEscolar/1.0"
            }
        )

        with urlopen(solicitud, timeout=30) as respuesta:
            contenido = respuesta.read()

        # Comprobar que realmente se recibió una imagen.
        formatos_validos = (
            b"\x89PNG\r\n\x1a\n",
            b"\xff\xd8\xff",
            b"GIF87a",
            b"GIF89a",
            b"RIFF",
        )

        if not any(
            contenido.startswith(formato)
            for formato in formatos_validos
        ):
            raise ValueError(
                "La dirección no devolvió una imagen válida."
            )

        return contenido

    def descargar_opciones(self, archivos):
        ultimo_error = None

        for archivo in archivos:
            url = BASE_TRAINERS + archivo

            try:
                contenido = self.descargar(url)
                return contenido, archivo

            except Exception as error:
                ultimo_error = error

        raise ValueError(
            f"No se encontró una imagen válida. "
            f"Último error: {ultimo_error}"
        )

    def guardar_archivo(self, objeto, campo, contenido, nombre):
        archivo = ContentFile(contenido)

        getattr(objeto, campo).save(
            nombre,
            archivo,
            save=False
        )

        objeto.save(update_fields=[campo])

    def guardar_desde_urls(
        self,
        objeto,
        campo,
        urls,
        nombre_archivo
    ):
        imagen_actual = getattr(objeto, campo)

        if imagen_actual:
            self.stdout.write(
                self.style.WARNING(
                    f"Ya tiene imagen: {objeto}"
                )
            )
            return

        ultimo_error = None

        for url in urls:
            try:
                contenido = self.descargar(url)

                self.guardar_archivo(
                    objeto,
                    campo,
                    contenido,
                    nombre_archivo
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Imagen guardada: {objeto}"
                    )
                )
                return

            except Exception as error:
                ultimo_error = error

        raise ValueError(
            f"No se pudo descargar la imagen: {ultimo_error}"
        )

    def reemplazar_jefferson_por_red(self):
        entrenador = Entrenador.objects.filter(
            nombre__iexact="Jefferson",
            apellido__icontains="Alfonso"
        ).first()

        if not entrenador:
            entrenador = Entrenador.objects.filter(
                nombre__icontains="Jefferson"
            ).first()

        if not entrenador:
            self.stdout.write(
                self.style.WARNING(
                    "No se encontró el registro de Jefferson. "
                    "No se modificó ningún entrenador."
                )
            )
            return

        # Se conserva el ID para mantener las relaciones del PC.
        entrenador.nombre = "Red"
        entrenador.apellido = "Pokémon"
        entrenador.documento = f"RED-{entrenador.pk:04d}"
        entrenador.pueblo = "Pueblo Paleta"
        entrenador.cantidad_medallas = 8
        entrenador.clasificado = True
        entrenador.liga = "KANTO"

        profesor_oak = Profesor.objects.filter(
            apellido__icontains="Oak"
        ).first()

        if profesor_oak:
            entrenador.profesor = profesor_oak

        entrenador.save()

        self.stdout.write(
            self.style.SUCCESS(
                "Entrenador actualizado: Red. "
                "Se conservaron su ID y sus relaciones."
            )
        )

    def buscar_archivo(self, nombre, mapa):
        for clave, archivos in mapa.items():
            if clave in nombre:
                return archivos

        return ["acetrainer-gen1.png"]

    def cargar_entrenadores(self):
        self.stdout.write(
            self.style.WARNING(
                "\nCargando imágenes de entrenadores..."
            )
        )

        for entrenador in Entrenador.objects.all():
            if entrenador.imagen_archivo:
                self.stdout.write(
                    f"Ya tiene imagen: {entrenador}"
                )
                continue

            nombre = slugify(entrenador.nombre)

            archivos = IMAGENES_ENTRENADORES.get(
                nombre,
                ["acetrainer-gen1.png"]
            )

            try:
                contenido, archivo = self.descargar_opciones(
                    archivos
                )

                self.guardar_archivo(
                    entrenador,
                    "imagen_archivo",
                    contenido,
                    f"entrenador_{entrenador.pk}.png"
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"{entrenador}: {archivo}"
                    )
                )

            except Exception as error:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error con {entrenador}: {error}"
                    )
                )

    def cargar_profesores(self):
        self.stdout.write(
            self.style.WARNING(
                "\nCargando imágenes de profesores..."
            )
        )

        for profesor in Profesor.objects.all():
            if profesor.imagen_archivo:
                continue

            nombre = slugify(
                f"{profesor.nombre} {profesor.apellido}"
            )

            archivos = self.buscar_archivo(
                nombre,
                IMAGENES_PROFESORES
            )

            try:
                contenido, archivo = self.descargar_opciones(
                    archivos
                )

                self.guardar_archivo(
                    profesor,
                    "imagen_archivo",
                    contenido,
                    f"profesor_{profesor.pk}.png"
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"{profesor}: {archivo}"
                    )
                )

            except Exception as error:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error con {profesor}: {error}"
                    )
                )

    def cargar_gimnasios(self):
        self.stdout.write(
            self.style.WARNING(
                "\nCargando imágenes de gimnasios..."
            )
        )

        for gimnasio in Gimnasio.objects.all():
            if gimnasio.imagen_archivo:
                continue

            nombre = slugify(gimnasio.lider)

            archivos = self.buscar_archivo(
                nombre,
                IMAGENES_LIDERES
            )

            try:
                contenido, archivo = self.descargar_opciones(
                    archivos
                )

                self.guardar_archivo(
                    gimnasio,
                    "imagen_archivo",
                    contenido,
                    f"gimnasio_{gimnasio.pk}.png"
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Gimnasio {gimnasio.ciudad}: {archivo}"
                    )
                )

            except Exception as error:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error con gimnasio "
                        f"{gimnasio.ciudad}: {error}"
                    )
                )

    def cargar_regiones(self):
        self.stdout.write(
            self.style.WARNING(
                "\nCargando imágenes de regiones..."
            )
        )

        for region in Region.objects.all():
            if region.imagen_archivo:
                continue

            nombre = slugify(region.nombre)
            archivo = IMAGENES_REGIONES.get(nombre)

            if not archivo:
                self.stdout.write(
                    self.style.WARNING(
                        f"No hay mapa configurado para {region}."
                    )
                )
                continue

            url = (
                "https://commons.wikimedia.org/wiki/"
                "Special:FilePath/"
                + quote(archivo)
            )

            try:
                self.guardar_desde_urls(
                    region,
                    "imagen_archivo",
                    [url],
                    f"region_{region.pk}.png"
                )

            except Exception as error:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error con región {region}: {error}"
                    )
                )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                "INICIANDO CARGA DE IMÁGENES"
            )
        )

        self.reemplazar_jefferson_por_red()

        self.cargar_entrenadores()
        self.cargar_profesores()
        self.cargar_gimnasios()
        self.cargar_regiones()

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "PROCESO FINALIZADO."
            )
        )
