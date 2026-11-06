from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Count
import unicodedata

from pokemon.models import (
    Tipo,
    Profesor,
    Region,
    Entrenador,
    Gimnasio,
    Pokemon,
    BackupEntrenador,
)


PROFESORES = [
    {
        "nombre": "Samuel",
        "apellido": "Oak",
        "especialidad": "Investigación Pokémon",
        "pueblo": "Pueblo Paleta",
    },
    {
        "nombre": "Elm",
        "apellido": "Pokémon",
        "especialidad": "Evolución Pokémon",
        "pueblo": "Ciudad Cerezo",
    },
    {
        "nombre": "Marta",
        "apellido": "Ciprés",
        "especialidad": "Tipos y habilidades Pokémon",
        "pueblo": "Ciudad Luminalia",
    },
    {
        "nombre": "Roberto",
        "apellido": "Encina",
        "especialidad": "Comportamiento Pokémon",
        "pueblo": "Ciudad Porcelana",
    },
    {
        "nombre": "Aurea",
        "apellido": "Serbal",
        "especialidad": "Evoluciones y estadísticas",
        "pueblo": "Pueblo Hojaverde",
    },
]


ENTRENADORES = [
    ("Jefferson", "Alfonso", "Pueblo Paleta", "KANTO", True),
    ("Ash", "Ketchum", "Pueblo Paleta", "KANTO", True),
    ("Misty", "Waterflower", "Ciudad Celeste", "KANTO", True),
    ("Brock", "Harrison", "Ciudad Plateada", "KANTO", True),
    ("Gary", "Oak", "Pueblo Paleta", "KANTO", True),
    ("Luna", "Martínez", "Ciudad Carmín", "KANTO", True),
    ("Daniel", "Rojas", "Ciudad Azafrán", "KANTO", True),
    ("Sofía", "Ramírez", "Ciudad Azulona", "KANTO", True),
    ("Gold", "Harrison", "Pueblo Primavera", "JOHTO", True),
    ("Kris", "Rivera", "Ciudad Cerezo", "JOHTO", True),
    ("Silver", "Oak", "Pueblo Primavera", "JOHTO", False),
    ("Valentina", "Torres", "Ciudad Trigal", "JOHTO", True),
    ("Mateo", "Castro", "Ciudad Iris", "JOHTO", False),
    ("Camila", "Morales", "Ciudad Olivo", "JOHTO", True),
    ("Lucas", "Herrera", "Pueblo Caoba", "JOHTO", False),
]


GIMNASIOS = [
    # Kanto
    ("Brock", "Ciudad Plateada", "Roca", "Medalla Roca", "601000001", "Kanto"),
    ("Misty", "Ciudad Celeste", "Agua", "Medalla Cascada", "601000002", "Kanto"),
    ("Lt. Surge", "Ciudad Carmín", "Eléctrico", "Medalla Trueno", "601000003", "Kanto"),
    ("Erika", "Ciudad Azulona", "Planta", "Medalla Arcoíris", "601000004", "Kanto"),
    ("Koga", "Ciudad Fucsia", "Veneno", "Medalla Alma", "601000005", "Kanto"),
    ("Sabrina", "Ciudad Azafrán", "Psíquico", "Medalla Pantano", "601000006", "Kanto"),
    ("Blaine", "Isla Canela", "Fuego", "Medalla Volcán", "601000007", "Kanto"),
    ("Giovanni", "Ciudad Verde", "Tierra", "Medalla Tierra", "601000008", "Kanto"),

    # Johto
    ("Falkner", "Ciudad Malva", "Volador", "Medalla Céfiro", "601000009", "Johto"),
    ("Bugsy", "Pueblo Azalea", "Bicho", "Medalla Colmena", "601000010", "Johto"),
    ("Whitney", "Ciudad Trigal", "Normal", "Medalla Planicie", "601000011", "Johto"),
    ("Morty", "Ciudad Iris", "Fantasma", "Medalla Niebla", "601000012", "Johto"),
    ("Chuck", "Ciudad Orquídea", "Lucha", "Medalla Tormenta", "601000013", "Johto"),
    ("Jasmine", "Ciudad Olivo", "Acero", "Medalla Mineral", "601000014", "Johto"),
    ("Pryce", "Pueblo Caoba", "Hielo", "Medalla Glaciar", "601000015", "Johto"),
    ("Clair", "Ciudad Endrino", "Dragón", "Medalla Dragón", "601000016", "Johto"),
]


TIPOS_EQUIVALENTES = {
    "roca": ["roca", "rock"],
    "agua": ["agua", "water"],
    "electrico": ["electrico", "eléctrico", "electric"],
    "planta": ["planta", "grass"],
    "veneno": ["veneno", "poison"],
    "psiquico": ["psiquico", "psíquico", "psychic"],
    "fuego": ["fuego", "fire"],
    "tierra": ["tierra", "ground"],
    "volador": ["volador", "flying"],
    "bicho": ["bicho", "bug"],
    "normal": ["normal"],
    "fantasma": ["fantasma", "ghost"],
    "lucha": ["lucha", "fighting"],
    "acero": ["acero", "steel"],
    "hielo": ["hielo", "ice"],
    "dragon": ["dragon", "dragón"],
}


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(
        caracter for caracter in texto
        if not unicodedata.combining(caracter)
    )
    return texto.strip().lower()


class Command(BaseCommand):
    help = (
        "Completa entrenadores, profesores, regiones, gimnasios "
        "y cajas PC sin modificar los Pokémon existentes."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.NOTICE(
                "\nIniciando la carga de información de la Pokédex...\n"
            )
        )

        tipos = self.obtener_tipos()

        # 1. Regiones
        regiones = {}

        for nombre in ["Kanto", "Johto"]:
            region, creada = Region.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "descripcion": (
                        f"Región Pokémon de {nombre}, con ocho gimnasios "
                        "y entrenadores especializados."
                    ),
                    "imagen": "",
                },
            )

            regiones[nombre] = region
            self.mensaje_registro("Región", nombre, creada)

        # 2. Profesores
        profesores = []

        for datos in PROFESORES:
            profesor, creada = Profesor.objects.get_or_create(
                nombre=datos["nombre"],
                apellido=datos["apellido"],
                defaults={
                    "especialidad": datos["especialidad"],
                    "pueblo": datos["pueblo"],
                },
            )

            profesores.append(profesor)
            self.mensaje_registro(
                "Profesor",
                f"{profesor.nombre} {profesor.apellido}",
                creada,
            )

        # 3. Entrenadores
        entrenadores = []

        for indice, datos in enumerate(ENTRENADORES):
            nombre, apellido, pueblo, liga, clasificado = datos

            profesor = profesores[indice % len(profesores)]

            documento = f"ENT-2026-{indice + 1:03d}"

            entrenador, creado = Entrenador.objects.get_or_create(
                documento=documento,
                defaults={
                    "nombre": nombre,
                    "apellido": apellido,
                    "pueblo": pueblo,
                    "cantidad_medallas": 0,
                    "clasificado": clasificado,
                    "liga": liga,
                    "profesor": profesor,
                },
            )

            entrenadores.append(entrenador)

            self.mensaje_registro(
                "Entrenador",
                f"{entrenador.nombre} {entrenador.apellido}",
                creado,
            )

        # 4. Gimnasios
        gimnasios_creados = []

        for indice, datos in enumerate(GIMNASIOS):
            lider, ciudad, nombre_tipo, medalla, telefono, nombre_region = datos

            tipo = tipos.get(normalizar(nombre_tipo))

            if not tipo:
                raise CommandError(
                    f"No se encontró el tipo '{nombre_tipo}' en la tabla "
                    "Tipo. No se han confirmado cambios en la base de datos."
                )

            region = regiones[nombre_region]

            gimnasio, creado = Gimnasio.objects.get_or_create(
                lider=lider,
                ciudad=ciudad,
                region=region,
                defaults={
                    "tipo": tipo,
                    "medalla": medalla,
                    "telefono": telefono,
                },
            )

            gimnasios_creados.append(gimnasio)

            self.mensaje_registro(
                "Gimnasio",
                f"{lider} - {ciudad}",
                creado,
            )

            # Relaciona cada gimnasio con un entrenador.
            entrenador = entrenadores[indice % len(entrenadores)]
            entrenador.gimnasios.add(gimnasio)

        # Actualiza el contador solo cuando está en cero.
        for entrenador in entrenadores:
            cantidad = entrenador.gimnasios.count()

            if entrenador.cantidad_medallas == 0 and cantidad > 0:
                entrenador.cantidad_medallas = cantidad
                entrenador.save(update_fields=["cantidad_medallas"])

        # 5. Cajas PC
        backups = []

        for entrenador in entrenadores:
            nombre_caja = (
                f"Caja principal - {entrenador.nombre} "
                f"{entrenador.apellido}"
            )

            backup, creado = BackupEntrenador.objects.get_or_create(
                nombre=nombre_caja,
                entrenador=entrenador,
                defaults={
                    "profesor": entrenador.profesor,
                    "items": "Caja principal del entrenador.",
                },
            )

            backups.append(backup)

            self.mensaje_registro(
                "Caja PC",
                nombre_caja,
                creado,
            )

        # 6. Distribuye los Pokémon existentes en las cajas.
        # No modifica ningún campo de la tabla Pokemon.
        pokemon_en_cajas = set(
            BackupEntrenador.objects.values_list(
                "pokemones__id",
                flat=True,
            ).exclude(pokemones__id__isnull=True)
        )

        pokemon_disponibles = list(
            Pokemon.objects.exclude(
                id__in=pokemon_en_cajas
            ).order_by("numero")
        )

        for indice, pokemon in enumerate(pokemon_disponibles):
            caja = backups[indice % len(backups)]
            caja.pokemones.add(pokemon)

        # 7. Resumen
        self.stdout.write("\n")
        self.stdout.write(self.style.SUCCESS("Carga finalizada.\n"))

        self.stdout.write(
            f"Pokémon registrados: {Pokemon.objects.count()}"
        )
        self.stdout.write(
            f"Tipos existentes: {Tipo.objects.count()}"
        )
        self.stdout.write(
            f"Profesores: {Profesor.objects.count()}"
        )
        self.stdout.write(
            f"Regiones: {Region.objects.count()}"
        )
        self.stdout.write(
            f"Entrenadores: {Entrenador.objects.count()}"
        )
        self.stdout.write(
            f"Gimnasios: {Gimnasio.objects.count()}"
        )
        self.stdout.write(
            f"Cajas PC: {BackupEntrenador.objects.count()}"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "\nLos Pokémon existentes no fueron modificados."
            )
        )

    def obtener_tipos(self):
        """
        Busca los tipos existentes. No crea ni modifica tipos.
        """

        tipos_existentes = list(Tipo.objects.all())
        resultado = {}

        necesarios = {
            normalizar(datos[2])
            for datos in GIMNASIOS
        }

        for tipo_necesario in necesarios:
            equivalentes = TIPOS_EQUIVALENTES.get(
                tipo_necesario,
                [tipo_necesario],
            )

            encontrado = None

            for tipo in tipos_existentes:
                nombre_normalizado = normalizar(tipo.nombre)

                if nombre_normalizado in equivalentes:
                    encontrado = tipo
                    break

            if encontrado is None:
                raise CommandError(
                    f"No existe el tipo '{tipo_necesario}' en la tabla "
                    "Tipo. Revisa los tipos registrados antes de continuar."
                )

            resultado[tipo_necesario] = encontrado

        return resultado

    def mensaje_registro(self, categoria, nombre, creado):
        if creado:
            self.stdout.write(
                self.style.SUCCESS(f"[CREADO] {categoria}: {nombre}")
            )
        else:
            self.stdout.write(
                f"[EXISTENTE] {categoria}: {nombre}"
            )