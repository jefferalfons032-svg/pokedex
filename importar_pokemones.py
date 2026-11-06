
import os
import django
import json
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configuracion.settings")
django.setup()

from pokemon.models import Pokemon, Tipo, Habilidad

API = "https://pokeapi.co/api/v2"

TIPOS = {
    "normal": ("Normal", "#A8A878"),
    "fire": ("Fuego", "#F08030"),
    "water": ("Agua", "#6890F0"),
    "electric": ("Eléctrico", "#F8D030"),
    "grass": ("Planta", "#78C850"),
    "ice": ("Hielo", "#98D8D8"),
    "fighting": ("Lucha", "#C03028"),
    "poison": ("Veneno", "#A040A0"),
    "ground": ("Tierra", "#E0C068"),
    "flying": ("Volador", "#A890F0"),
    "psychic": ("Psíquico", "#F85888"),
    "bug": ("Bicho", "#A8B820"),
    "rock": ("Roca", "#B8A038"),
    "ghost": ("Fantasma", "#705898"),
    "dragon": ("Dragón", "#7038F8"),
    "dark": ("Siniestro", "#705848"),
    "steel": ("Acero", "#B8B8D0"),
    "fairy": ("Hada", "#EE99AC"),
}

def consultar(url):
    for intento in range(4):
        try:
            solicitud = urllib.request.Request(
                url,
                headers={"User-Agent": "PokemonPokedexDjango/1.0"}
            )
            with urllib.request.urlopen(solicitud, timeout=40) as respuesta:
                return json.loads(respuesta.read().decode("utf-8"))
        except Exception:
            if intento == 3:
                raise
    return None


def obtener_pokemon(numero):
    datos = consultar(f"{API}/pokemon/{numero}/")
    especie = consultar(datos["species"]["url"])

    nombres = especie.get("names", [])
    nombre_es = next(
        (n["name"] for n in nombres if n["language"]["name"] == "es"),
        especie["name"]
    )

    estadisticas = {
        s["stat"]["name"]: s["base_stat"]
        for s in datos["stats"]
    }

    imagen = (
        datos["sprites"]["other"]["official-artwork"]["front_default"]
        or datos["sprites"]["front_default"]
        or ""
    )

    return {
        "numero": numero,
        "nombre": nombre_es,
        "imagen": imagen,
        "altura": datos["height"],
        "peso": datos["weight"],
        "experiencia": datos["base_experience"] or 0,
        "tipos": [t["type"]["name"] for t in datos["types"]],
        "habilidades": [
            h["ability"]["name"] for h in datos["abilities"]
        ],
        "hp": estadisticas.get("hp", 0),
        "ataque": estadisticas.get("attack", 0),
        "defensa": estadisticas.get("defense", 0),
        "ataque_especial": estadisticas.get("special-attack", 0),
        "defensa_especial": estadisticas.get("special-defense", 0),
        "velocidad": estadisticas.get("speed", 0),
        "legendario": (
            especie.get("is_legendary", False)
            or especie.get("is_mythical", False)
        ),
        "cadena": especie["evolution_chain"]["url"],
    }


def obtener_evoluciones(url):
    cadena = consultar(url)
    relaciones = []

    def recorrer(nodo, numero_anterior=None):
        especie_url = nodo["species"]["url"]
        numero = int(especie_url.rstrip("/").split("/")[-1])

        if numero_anterior is not None:
            relaciones.append((numero_anterior, numero))

        for evolucion in nodo.get("evolves_to", []):
            recorrer(evolucion, numero)

    recorrer(cadena["chain"])
    return relaciones


print("=" * 55)
print("       IMPORTADOR DE POKEMON - POKEDEX")
print("=" * 55)

actuales = Pokemon.objects.count()
print(f"Pokémon actuales: {actuales}")

# Importar 1.000 Pokémon nuevos, empezando por el número 26.
numeros = [
    n for n in range(26, 2000)
    if not Pokemon.objects.filter(numero=n).exists()
][:1000]

if len(numeros) != 1000:
    raise Exception("No se encontraron 1.000 números nuevos disponibles.")

print("Descargando información de 1.000 Pokémon...")

resultados = {}

with ThreadPoolExecutor(max_workers=8) as executor:
    tareas = {
        executor.submit(obtener_pokemon, n): n
        for n in numeros
    }

    completados = 0

    for tarea in as_completed(tareas):
        numero = tareas[tarea]
        resultados[numero] = tarea.result()
        completados += 1

        if completados % 50 == 0:
            print(f"Descargados: {completados}/1000")

print("Descargando cadenas de evolución...")

cadenas = set(
    datos["cadena"] for datos in resultados.values()
)

relaciones = []

with ThreadPoolExecutor(max_workers=8) as executor:
    tareas = [
        executor.submit(obtener_evoluciones, url)
        for url in cadenas
    ]

    for tarea in as_completed(tareas):
        relaciones.extend(tarea.result())

print("Guardando información en PostgreSQL...")

with transaction.atomic():

    tipos_db = {}

    for clave, (nombre, color) in TIPOS.items():
        tipo, _ = Tipo.objects.get_or_create(
            nombre=nombre,
            defaults={"color": color}
        )
        tipos_db[clave] = tipo

    habilidades_db = {}

    for datos in resultados.values():
        for nombre in datos["habilidades"]:
            habilidad, _ = Habilidad.objects.get_or_create(
                nombre=nombre.replace("-", " ").title()
            )
            habilidades_db[nombre] = habilidad

    pokemones_db = {}

    for numero in numeros:
        datos = resultados[numero]

        pokemon, creado = Pokemon.objects.get_or_create(
            numero=numero,
            defaults={
                "nombre": datos["nombre"],
                "imagen": datos["imagen"],
                "imagen_oficial": datos["imagen"],
                "altura": datos["altura"],
                "peso": datos["peso"],
                "experiencia_base": datos["experiencia"],
                "hp": datos["hp"],
                "ataque": datos["ataque"],
                "defensa": datos["defensa"],
                "ataque_especial": datos["ataque_especial"],
                "defensa_especial": datos["defensa_especial"],
                "velocidad": datos["velocidad"],
                "es_legendario": datos["legendario"],
            }
        )

        if not creado:
            raise Exception(
                f"El Pokémon #{numero} ya existía. Se canceló la operación."
            )

        pokemon.tipos.set([
            tipos_db[t] for t in datos["tipos"]
        ])

        pokemon.habilidades.set([
            habilidades_db[h] for h in datos["habilidades"]
        ])

        pokemones_db[numero] = pokemon

    for origen, destino in relaciones:
        if origen in pokemones_db and destino in pokemones_db:
            pokemones_db[origen].evoluciones.add(
                pokemones_db[destino]
            )

print("=" * 55)
print("IMPORTACIÓN FINALIZADA")
print(f"Pokémon anteriores: {actuales}")
print(f"Pokémon agregados: {len(pokemones_db)}")
print(f"Total en la base de datos: {Pokemon.objects.count()}")
print("=" * 55)
