
import json

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from django.contrib import messages
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Count
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from .models import (
    Pokemon,
    Tipo,
    Habilidad,
    Profesor,
    Region,
    Entrenador,
    Gimnasio,
    BackupEntrenador,
)

from .forms import (
    PokemonForm,
    TipoForm,
    HabilidadForm,
    ProfesorForm,
    RegionForm,
    EntrenadorForm,
    GimnasioForm,
    BackupEntrenadorForm,
)


# =====================================================
# CONFIGURACIÓN DE POKEAPI
# =====================================================

POKEAPI_URL = "https://pokeapi.co/api/v2"
TIEMPO_CACHE = 60 * 60 * 12


# =====================================================
# TRADUCCIONES DE HABILIDADES
# =====================================================

NOMBRES_HABILIDADES_ES = {
    "overgrow": "Espesura",
    "chlorophyll": "Clorofila",
    "blaze": "Mar llamas",
    "torrent": "Torrente",
    "swarm": "Enjambre",
    "keen-eye": "Vista lince",
    "tangled-feet": "Tumbos",
    "big-pecks": "Sacapecho",
    "intimidate": "Intimidación",
    "static": "Electricidad estática",
    "lightning-rod": "Pararrayos",
    "sand-veil": "Velo arena",
    "poison-point": "Punto tóxico",
    "rivalry": "Rivalidad",
    "cute-charm": "Gran encanto",
    "magic-guard": "Muro mágico",
    "flash-fire": "Absorbe fuego",
    "water-absorb": "Absorbe agua",
    "volt-absorb": "Absorbe electricidad",
    "levitate": "Levitación",
    "pressure": "Presión",
    "inner-focus": "Foco interno",
    "synchronize": "Sincronía",
    "clear-body": "Cuerpo puro",
    "natural-cure": "Cura natural",
    "serene-grace": "Dicha",
    "swift-swim": "Nado rápido",
    "rain-dish": "Cura lluvia",
    "drought": "Sequía",
    "drizzle": "Llovizna",
    "sand-stream": "Chorro arena",
    "snow-warning": "Nevada",
    "speed-boost": "Impulso",
    "adaptability": "Adaptable",
    "technician": "Experto",
    "mold-breaker": "Rompemoldes",
    "multiscale": "Compensación",
    "sturdy": "Robustez",
    "huge-power": "Potencia",
    "pure-power": "Energía pura",
    "guts": "Agallas",
    "quick-feet": "Pies rápidos",
    "flame-body": "Cuerpo llama",
    "magma-armor": "Escudo magma",
    "thick-fat": "Sebo",
    "own-tempo": "Ritmo propio",
    "limber": "Flexibilidad",
    "water-veil": "Velo agua",
    "insomnia": "Insomnio",
    "vital-spirit": "Espíritu vital",
    "early-bird": "Madrugar",
    "run-away": "Fuga",
    "pickup": "Recogida",
    "compound-eyes": "Ojo compuesto",
    "hustle": "Entusiasmo",
    "marvel-scale": "Escama especial",
    "immunity": "Inmunidad",
    "oblivious": "Despiste",
    "cloud-nine": "Aclimatación",
    "air-lock": "Bucle aire",
    "trace": "Rastro",
    "download": "Descarga",
    "forecast": "Predicción",
    "color-change": "Cambio color",
    "wonder-guard": "Superguarda",
    "effect-spore": "Efecto espora",
    "rough-skin": "Piel tosca",
    "iron-fist": "Puño férreo",
    "scrappy": "Intrépido",
    "unaware": "Ignorante",
    "simple": "Simple",
    "prankster": "Bromista",
    "defiant": "Competitivo",
    "contrary": "Respondón",
    "infiltrator": "Allanamiento",
    "moxie": "Autoestima",
    "protean": "Mutatipo",
    "libero": "Líbero",
    "disguise": "Disfraz",
    "battle-armor": "Armadura batalla",
    "shell-armor": "Caparazón",
    "super-luck": "Afortunado",
    "sniper": "Francotirador",
    "skill-link": "Encadenado",
    "reckless": "Audaz",
    "aftermath": "Resquicio",
    "healer": "Alma cura",
    "friend-guard": "Compiescolta",
    "weak-armor": "Armadura frágil",
    "regenerator": "Regeneración",
    "magic-bounce": "Espejo mágico",
    "bulletproof": "Antibalas",
    "competitive": "Tenacidad",
    "tough-claws": "Garra dura",
    "pixilate": "Piel feérica",
    "refrigerate": "Piel helada",
    "aerilate": "Piel celeste",
    "galvanize": "Piel eléctrica",
    "liquid-voice": "Voz fluida",
    "stamina": "Firmeza",
    "beast-boost": "Ultraimpulso",
}


# =====================================================
# DESCRIPCIONES DE HABILIDADES
# =====================================================

DESCRIPCIONES_HABILIDADES_ES = {
    "overgrow": (
        "Potencia los movimientos de tipo Planta cuando los PS "
        "del Pokémon son bajos."
    ),
    "chlorophyll": (
        "Aumenta la velocidad del Pokémon cuando hace sol."
    ),
    "blaze": (
        "Potencia los movimientos de tipo Fuego cuando los PS "
        "del Pokémon son bajos."
    ),
    "torrent": (
        "Potencia los movimientos de tipo Agua cuando los PS "
        "del Pokémon son bajos."
    ),
    "swarm": (
        "Potencia los movimientos de tipo Bicho cuando los PS "
        "del Pokémon son bajos."
    ),
    "intimidate": (
        "Al entrar en combate, reduce el Ataque de los rivales."
    ),
    "static": (
        "Puede paralizar al Pokémon que entre en contacto físico."
    ),
    "lightning-rod": (
        "Atrae los movimientos eléctricos y aumenta el Ataque Especial."
    ),
    "levitate": (
        "El Pokémon es inmune a los movimientos de tipo Tierra."
    ),
    "pressure": (
        "Hace que el rival consuma más PP al utilizar sus movimientos."
    ),
    "natural-cure": (
        "Cura los problemas de estado cuando el Pokémon se retira "
        "del combate."
    ),
    "speed-boost": (
        "Aumenta la Velocidad del Pokémon al final de cada turno."
    ),
    "flash-fire": (
        "Absorbe los movimientos de tipo Fuego y potencia sus propios "
        "movimientos de ese tipo."
    ),
    "water-absorb": (
        "Recupera PS cuando recibe un movimiento de tipo Agua."
    ),
    "volt-absorb": (
        "Recupera PS cuando recibe un movimiento de tipo Eléctrico."
    ),
    "sturdy": (
        "Evita que el Pokémon debilitado por un golpe pierda todos "
        "sus PS de una sola vez si estaba con todos sus PS."
    ),
    "guts": (
        "Aumenta el Ataque cuando el Pokémon sufre un problema de estado."
    ),
    "thick-fat": (
        "Reduce el daño recibido de movimientos de tipo Fuego y Hielo."
    ),
    "adaptability": (
        "Aumenta la potencia de los movimientos que comparten tipo "
        "con el Pokémon."
    ),
    "technician": (
        "Aumenta la potencia de los movimientos de poca fuerza."
    ),
    "mold-breaker": (
        "Permite que los movimientos ignoren ciertas habilidades "
        "del objetivo."
    ),
    "multiscale": (
        "Reduce el daño recibido cuando el Pokémon tiene todos sus PS."
    ),
    "prankster": (
        "Aumenta la prioridad de los movimientos que no causan daño."
    ),
    "regenerator": (
        "Recupera parte de los PS cuando el Pokémon se retira del combate."
    ),
    "magic-guard": (
        "Evita el daño indirecto que no provenga de un movimiento directo."
    ),
    "immunity": (
        "Evita que el Pokémon pueda ser envenenado."
    ),
    "insomnia": (
        "Evita que el Pokémon se duerma."
    ),
    "synchronize": (
        "Puede transmitir al rival ciertos problemas de estado "
        "que afecten al Pokémon."
    ),
    "serene-grace": (
        "Aumenta la probabilidad de que se produzcan efectos secundarios "
        "de los movimientos."
    ),
    "swift-swim": (
        "Aumenta la Velocidad del Pokémon cuando llueve."
    ),
    "rain-dish": (
        "Recupera una pequeña cantidad de PS cuando está lloviendo."
    ),
    "drought": (
        "Provoca un clima soleado al entrar en combate."
    ),
    "drizzle": (
        "Provoca lluvia al entrar en combate."
    ),
    "sand-stream": (
        "Provoca una tormenta de arena al entrar en combate."
    ),
    "snow-warning": (
        "Provoca granizo o nieve al entrar en combate, según la generación."
    ),
}


# =====================================================
# TRADUCCIONES DE NOMBRES DE POKÉMON
# =====================================================

NOMBRES_POKEMON_ES = {
    "bulbasaur": "Bulbasaur",
    "ivysaur": "Ivysaur",
    "venusaur": "Venusaur",
    "charmander": "Charmander",
    "charmeleon": "Charmeleon",
    "charizard": "Charizard",
    "squirtle": "Squirtle",
    "wartortle": "Wartortle",
    "blastoise": "Blastoise",
    "caterpie": "Caterpie",
    "metapod": "Metapod",
    "butterfree": "Butterfree",
    "weedle": "Weedle",
    "kakuna": "Kakuna",
    "beedrill": "Beedrill",
    "pidgey": "Pidgey",
    "pidgeotto": "Pidgeotto",
    "pidgeot": "Pidgeot",
    "rattata": "Rattata",
    "raticate": "Raticate",
    "pikachu": "Pikachu",
    "raichu": "Raichu",
    "sandshrew": "Sandshrew",
    "sandslash": "Sandslash",
    "nidoran-f": "Nidoran hembra",
    "nidoran-m": "Nidoran macho",
    "clefairy": "Clefairy",
    "clefable": "Clefable",
    "vulpix": "Vulpix",
    "ninetales": "Ninetales",
    "jigglypuff": "Jigglypuff",
    "wigglytuff": "Wigglytuff",
    "zubat": "Zubat",
    "golbat": "Golbat",
    "oddish": "Oddish",
    "gloom": "Gloom",
    "vileplume": "Vileplume",
    "paras": "Paras",
    "parasect": "Parasect",
    "venonat": "Venonat",
    "venomoth": "Venomoth",
    "diglett": "Diglett",
    "dugtrio": "Dugtrio",
    "meowth": "Meowth",
    "persian": "Persian",
    "psyduck": "Psyduck",
    "golduck": "Golduck",
    "mankey": "Mankey",
    "primeape": "Primeape",
    "growlithe": "Growlithe",
    "arcanine": "Arcanine",
    "poliwag": "Poliwag",
    "poliwhirl": "Poliwhirl",
    "poliwrath": "Poliwrath",
    "abra": "Abra",
    "kadabra": "Kadabra",
    "alakazam": "Alakazam",
    "machop": "Machop",
    "machoke": "Machoke",
    "machamp": "Machamp",
    "bellsprout": "Bellsprout",
    "weepinbell": "Weepinbell",
    "victreebel": "Victreebel",
    "tentacool": "Tentacool",
    "tentacruel": "Tentacruel",
    "geodude": "Geodude",
    "graveler": "Graveler",
    "golem": "Golem",
    "ponyta": "Ponyta",
    "rapidash": "Rapidash",
    "slowpoke": "Slowpoke",
    "slowbro": "Slowbro",
    "magnemite": "Magnemite",
    "magneton": "Magneton",
    "farfetchd": "Farfetch'd",
    "doduo": "Doduo",
    "dodrio": "Dodrio",
    "seel": "Seel",
    "dewgong": "Dewgong",
    "grimer": "Grimer",
    "muk": "Muk",
    "shellder": "Shellder",
    "cloyster": "Cloyster",
    "gastly": "Gastly",
    "haunter": "Haunter",
    "gengar": "Gengar",
    "onix": "Onix",
    "drowzee": "Drowzee",
    "hypno": "Hypno",
    "krabby": "Krabby",
    "kingler": "Kingler",
    "voltorb": "Voltorb",
    "electrode": "Electrode",
    "exeggcute": "Exeggcute",
    "exeggutor": "Exeggutor",
    "cubone": "Cubone",
    "marowak": "Marowak",
    "hitmonlee": "Hitmonlee",
    "hitmonchan": "Hitmonchan",
    "lickitung": "Lickitung",
    "koffing": "Koffing",
    "weezing": "Weezing",
    "rhyhorn": "Rhyhorn",
    "rhydon": "Rhydon",
    "chansey": "Chansey",
    "tangela": "Tangela",
    "kangaskhan": "Kangaskhan",
    "horsea": "Horsea",
    "seadra": "Seadra",
    "goldeen": "Goldeen",
    "seaking": "Seaking",
    "staryu": "Staryu",
    "starmie": "Starmie",
    "mr-mime": "Mr. Mime",
    "scyther": "Scyther",
    "jynx": "Jynx",
    "electabuzz": "Electabuzz",
    "magmar": "Magmar",
    "pinsir": "Pinsir",
    "tauros": "Tauros",
    "magikarp": "Magikarp",
    "gyarados": "Gyarados",
    "lapras": "Lapras",
    "ditto": "Ditto",
    "eevee": "Eevee",
    "vaporeon": "Vaporeon",
    "jolteon": "Jolteon",
    "flareon": "Flareon",
    "porygon": "Porygon",
    "omanyte": "Omanyte",
    "omastar": "Omastar",
    "kabuto": "Kabuto",
    "kabutops": "Kabutops",
    "aerodactyl": "Aerodactyl",
    "snorlax": "Snorlax",
    "articuno": "Articuno",
    "zapdos": "Zapdos",
    "moltres": "Moltres",
    "dratini": "Dratini",
    "dragonair": "Dragonair",
    "dragonite": "Dragonite",
    "mewtwo": "Mewtwo",
    "mew": "Mew",
}

# =====================================================
# CONSULTAR INFORMACIÓN DE POKEAPI
# =====================================================

def consultar_pokeapi(url):
    """
    Consulta PokéAPI y almacena cada respuesta en caché.
    El timeout reducido evita que una consulta fallida
    mantenga detenida la página durante demasiado tiempo.
    """

    if not url:
        return None

    clave = f"pokedex_api_v3_{url}"
    resultado = cache.get(clave)

    if resultado is not None:
        return resultado

    try:
        solicitud = Request(
            url,
            headers={"User-Agent": "Pokedex-Django/3.0"},
        )

        with urlopen(solicitud, timeout=2.5) as respuesta:
            resultado = json.loads(
                respuesta.read().decode("utf-8")
            )

        cache.set(clave, resultado, TIEMPO_CACHE)
        return resultado

    except (
        URLError,
        HTTPError,
        TimeoutError,
        ValueError,
        OSError,
    ):
        return None


# =====================================================
# OBTENER NÚMERO DE ESPECIE
# =====================================================

def obtener_numero_especie(url):
    if not url:
        return None

    try:
        return int(url.rstrip("/").split("/")[-1])
    except (ValueError, IndexError, AttributeError):
        return None


# =====================================================
# OBTENER IMÁGENES
# =====================================================

def obtener_imagen_api(numero):
    if not numero:
        return ""

    return (
        "https://raw.githubusercontent.com/PokeAPI/"
        "sprites/master/sprites/pokemon/other/"
        f"official-artwork/{numero}.png"
    )


def obtener_sprite_api(numero):
    if not numero:
        return ""

    return (
        "https://raw.githubusercontent.com/PokeAPI/"
        f"sprites/master/sprites/pokemon/{numero}.png"
    )


# =====================================================
# TRADUCIR NOMBRES
# =====================================================

def obtener_nombre_localizado(datos, nombre_original, idioma="es"):
    for elemento in datos.get("names", []):
        idioma_dato = elemento.get(
            "language", {}
        ).get("name")

        if idioma_dato == idioma:
            nombre = elemento.get("name")

            if nombre:
                return nombre

    return (
        nombre_original
        .replace("-", " ")
        .replace("_", " ")
        .title()
    )


def obtener_nombre_habilidad_es(nombre, datos=None):
    if datos:
        nombre_localizado = obtener_nombre_localizado(
            datos,
            nombre,
            "es",
        )

        if nombre_localizado:
            return nombre_localizado

    return NOMBRES_HABILIDADES_ES.get(
        nombre,
        nombre.replace("-", " ").title(),
    )


def obtener_nombre_especie_es(especie):
    nombre_original = especie.get("name", "")

    return NOMBRES_POKEMON_ES.get(
        nombre_original,
        nombre_original.replace("-", " ").title(),
    )


# =====================================================
# DESCRIPCIONES DE HABILIDADES
# =====================================================

def obtener_descripcion_habilidad(datos, nombre):
    """
    No consulta PokéAPI por cada habilidad.
    Utiliza las descripciones locales para acelerar la ficha.
    """

    return DESCRIPCIONES_HABILIDADES_ES.get(
        nombre,
        "Descripción no disponible en español para esta habilidad.",
    )


# =====================================================
# OBTENER HABILIDADES
# =====================================================

def obtener_habilidades_api(datos_pokemon):
    resultado = []

    for elemento in datos_pokemon.get("abilities", []):
        habilidad = elemento.get("ability", {})
        nombre_original = habilidad.get("name", "")

        if not nombre_original:
            continue

        resultado.append({
            "nombre": obtener_nombre_habilidad_es(
                nombre_original
            ),
            "nombre_original": nombre_original,
            "descripcion": obtener_descripcion_habilidad(
                None,
                nombre_original,
            ),
            "oculta": elemento.get("is_hidden", False),
        })

    return resultado


# =====================================================
# IDENTIFICAR UNA ESPECIE POR SU ID
# =====================================================

def obtener_id_especie_nodo(nodo):
    especie = nodo.get("species", {})

    return obtener_numero_especie(
        especie.get("url", "")
    )


# =====================================================
# BUSCAR LA RUTA EVOLUTIVA POR ID
# =====================================================

def buscar_ruta_evolutiva(nodo, numero_especie, ruta=None):
    """
    Encuentra la ruta hasta una especie utilizando su ID.
    Esto evita errores con formas especiales y nombres distintos.
    """

    if ruta is None:
        ruta = []

    nueva_ruta = ruta + [nodo]

    if obtener_id_especie_nodo(nodo) == numero_especie:
        return nueva_ruta

    for siguiente in nodo.get("evolves_to", []):
        resultado = buscar_ruta_evolutiva(
            siguiente,
            numero_especie,
            nueva_ruta,
        )

        if resultado:
            return resultado

    return None


# =====================================================
# CONSTRUIR UNA TARJETA DE EVOLUCIÓN
# =====================================================

def construir_dato_evolucion(nodo):
    especie = nodo.get("species", {})
    numero = obtener_id_especie_nodo(nodo)

    if not numero:
        return None

    nombre_original = especie.get("name", "")

    return {
        "numero": numero,
        "nombre": obtener_nombre_especie_es(especie),
        "nombre_original": nombre_original,
        "imagen": obtener_imagen_api(numero),
        "imagen_alternativa": obtener_sprite_api(numero),
    }


# =====================================================
# OBTENER TODAS LAS EVOLUCIONES POSTERIORES
# =====================================================

def obtener_descendientes(nodo):
    """
    Recorre todas las ramas y todos los niveles posteriores.
    Ejemplo: Eevee puede mostrar sus diferentes evoluciones.
    """

    resultado = []
    visitados = set()

    def recorrer(nodo_actual):
        for siguiente in nodo_actual.get("evolves_to", []):
            dato = construir_dato_evolucion(siguiente)

            if dato and dato["numero"] not in visitados:
                visitados.add(dato["numero"])
                resultado.append(dato)

            recorrer(siguiente)

    recorrer(nodo)

    return resultado


# =====================================================
# OBTENER TODAS LAS EVOLUCIONES ANTERIORES
# =====================================================

def obtener_anteriores(ruta):
    resultado = []
    visitados = set()

    for nodo in ruta[:-1]:
        dato = construir_dato_evolucion(nodo)

        if dato and dato["numero"] not in visitados:
            visitados.add(dato["numero"])
            resultado.append(dato)

    return resultado


# =====================================================
# OBTENER DATOS COMPLETOS DEL POKÉMON
# =====================================================

def obtener_datos_completos_api(numero, nombre):
    """
    Recupera la ficha completa y la guarda en caché.

    Consultas necesarias en una primera carga:
    1. Datos del Pokémon.
    2. Datos de su especie.
    3. Cadena evolutiva.

    Las siguientes visitas reutilizan el resultado almacenado.
    """

    clave_detalle = f"pokedex_detalle_completo_v3_{numero}"
    datos_guardados = cache.get(clave_detalle)

    if datos_guardados is not None:
        return datos_guardados

    resultado_vacio = {
        "imagen_api": "",
        "imagen_alternativa_api": "",
        "habilidades_api": [],
        "evoluciones_anteriores_api": [],
        "evoluciones_siguientes_api": [],
    }

    datos_pokemon = consultar_pokeapi(
        f"{POKEAPI_URL}/pokemon/{numero}/"
    )

    if not datos_pokemon:
        nombre_api = nombre.lower().replace(" ", "-")

        datos_pokemon = consultar_pokeapi(
            f"{POKEAPI_URL}/pokemon/{nombre_api}/"
        )

    if not datos_pokemon:
        return resultado_vacio

    # -------------------------------------------------
    # IMÁGENES DEL POKÉMON
    # -------------------------------------------------

    numero_api = datos_pokemon.get("id", numero)

    sprites = datos_pokemon.get("sprites", {})
    otros_sprites = sprites.get("other", {})

    imagen = (
        otros_sprites
        .get("official-artwork", {})
        .get("front_default")
    )

    imagen_alternativa = sprites.get("front_default")

    if not imagen:
        imagen = obtener_imagen_api(numero_api)

    if not imagen_alternativa:
        imagen_alternativa = obtener_sprite_api(numero_api)

    # -------------------------------------------------
    # HABILIDADES
    # -------------------------------------------------

    habilidades = obtener_habilidades_api(datos_pokemon)

    # -------------------------------------------------
    # EVOLUCIONES
    # -------------------------------------------------

    anteriores = []
    siguientes = []

    especie = datos_pokemon.get("species", {})
    especie_url = especie.get("url", "")

    numero_especie = obtener_numero_especie(especie_url)

    if especie_url and numero_especie:
        datos_especie = consultar_pokeapi(especie_url)

        if datos_especie:
            cadena_url = (
                datos_especie
                .get("evolution_chain", {})
                .get("url", "")
            )

            if cadena_url:
                cadena = consultar_pokeapi(cadena_url)

                if cadena:
                    raiz = cadena.get("chain", {})

                    ruta = buscar_ruta_evolutiva(
                        raiz,
                        numero_especie,
                    )

                    if ruta:
                        anteriores = obtener_anteriores(ruta)

                        siguientes = obtener_descendientes(
                            ruta[-1]
                        )

    resultado = {
        "imagen_api": imagen or "",
        "imagen_alternativa_api": imagen_alternativa or "",
        "habilidades_api": habilidades,
        "evoluciones_anteriores_api": anteriores,
        "evoluciones_siguientes_api": siguientes,
    }

    # Guarda la ficha completa durante doce horas.
    cache.set(
        clave_detalle,
        resultado,
        TIEMPO_CACHE,
    )

    return resultado

# =====================================================
# POKEDEX PRINCIPAL
# =====================================================

def inicio(request):
    busqueda = request.GET.get("buscar", "").strip()
    tipo_seleccionado = request.GET.get("tipo", "").strip()

    pokemones = (
        Pokemon.objects
        .prefetch_related("tipos", "habilidades")
        .order_by("numero")
    )

    if busqueda:
        filtro = Q(nombre__icontains=busqueda)

        if busqueda.isdigit():
            filtro |= Q(numero=int(busqueda))

        pokemones = pokemones.filter(filtro)

    if tipo_seleccionado:
        pokemones = pokemones.filter(
            tipos__nombre__iexact=tipo_seleccionado
        ).distinct()

    paginator = Paginator(pokemones, 24)
    pagina = paginator.get_page(request.GET.get("pagina"))

    contexto = {
        "pagina": pagina,
        "tipos": Tipo.objects.order_by("nombre"),
        "buscar": busqueda,
        "tipo_seleccionado": tipo_seleccionado,
    }

    return render(request, "pokemon/inicio.html", contexto)


# =====================================================
# DETALLE DE UN POKÉMON
# =====================================================

def detalle(request, numero):
    pokemon = get_object_or_404(
        Pokemon.objects
        .select_related("entrenador")
        .prefetch_related(
            "tipos",
            "habilidades",
            "evoluciones",
            "evoluciona_desde",
        ),
        numero=numero,
    )

    # Datos de PokéAPI. La función ya tiene caché.
    datos_api = obtener_datos_completos_api(
        pokemon.numero,
        pokemon.nombre,
    )

    # -------------------------------------------------
    # ESTADÍSTICAS
    # -------------------------------------------------

    estadisticas = [
        {
            "nombre": "Salud",
            "abreviatura": "HP",
            "valor": pokemon.hp,
        },
        {
            "nombre": "Ataque",
            "abreviatura": "ATK",
            "valor": pokemon.ataque,
        },
        {
            "nombre": "Defensa",
            "abreviatura": "DEF",
            "valor": pokemon.defensa,
        },
        {
            "nombre": "Ataque especial",
            "abreviatura": "AT. ESP",
            "valor": pokemon.ataque_especial,
        },
        {
            "nombre": "Defensa especial",
            "abreviatura": "DEF. ESP",
            "valor": pokemon.defensa_especial,
        },
        {
            "nombre": "Velocidad",
            "abreviatura": "VEL",
            "valor": pokemon.velocidad,
        },
    ]

    for estadistica in estadisticas:
        valor = estadistica["valor"] or 0

        estadistica["porcentaje"] = min(
            max(valor, 0) / 255 * 100,
            100,
        )

    # -------------------------------------------------
    # ALTURA Y PESO
    # -------------------------------------------------

    altura_metros = (
        pokemon.altura / 10
        if pokemon.altura is not None
        else None
    )

    peso_kg = (
        pokemon.peso / 10
        if pokemon.peso is not None
        else None
    )

    # -------------------------------------------------
    # EVOLUCIONES DE RESPALDO DESDE LA BASE DE DATOS
    # -------------------------------------------------

    evoluciones_anteriores = datos_api.get(
        "evoluciones_anteriores_api",
        [],
    )

    evoluciones_siguientes = datos_api.get(
        "evoluciones_siguientes_api",
        [],
    )

    # Si PokéAPI no responde, se utilizan las relaciones
    # que ya estén guardadas en la base de datos.
    if not evoluciones_anteriores:
        for anterior in pokemon.evoluciona_desde.all():
            evoluciones_anteriores.append({
                "numero": anterior.numero,
                "nombre": anterior.nombre,
                "imagen": anterior.url_imagen or "",
                "imagen_alternativa": "",
            })

    if not evoluciones_siguientes:
        for siguiente in pokemon.evoluciones.all():
            evoluciones_siguientes.append({
                "numero": siguiente.numero,
                "nombre": siguiente.nombre,
                "imagen": siguiente.url_imagen or "",
                "imagen_alternativa": "",
            })

    # -------------------------------------------------
    # ENTRENADOR
    # -------------------------------------------------

    entrenador = pokemon.entrenador

    cantidad_pokemones_entrenador = 0
    cantidad_medallas_entrenador = 0

    if entrenador:
        cantidad_pokemones_entrenador = (
            entrenador.pokemones.count()
        )

        cantidad_medallas_entrenador = (
            entrenador.gimnasios.count()
        )

    # -------------------------------------------------
    # CONTEXTO
    # -------------------------------------------------

    contexto = {
        "pokemon": pokemon,

        "estadisticas": estadisticas,
        "altura_metros": altura_metros,
        "peso_kg": peso_kg,

        "imagen_api": datos_api.get(
            "imagen_api",
            "",
        ),

        "imagen_alternativa_api": datos_api.get(
            "imagen_alternativa_api",
            "",
        ),

        "habilidades_api": datos_api.get(
            "habilidades_api",
            [],
        ),

        "evoluciones_anteriores_api": evoluciones_anteriores,
        "evoluciones_siguientes_api": evoluciones_siguientes,

        "entrenador": entrenador,

        "cantidad_pokemones_entrenador": (
            cantidad_pokemones_entrenador
        ),

        "cantidad_medallas_entrenador": (
            cantidad_medallas_entrenador
        ),
    }

    return render(
        request,
        "pokemon/detalle.html",
        contexto,
    )

# =====================================================
# LISTADO DE POKÉMON
# =====================================================

def pokemon_lista(request):
    busqueda = request.GET.get("buscar", "").strip()

    pokemones = (
        Pokemon.objects
        .prefetch_related("tipos", "habilidades")
        .order_by("numero")
    )

    if busqueda:
        filtro = Q(nombre__icontains=busqueda)

        if busqueda.isdigit():
            filtro |= Q(numero=int(busqueda))

        pokemones = pokemones.filter(filtro).distinct()

    pagina = Paginator(
        pokemones,
        15,
    ).get_page(
        request.GET.get("pagina")
    )

    return render(
        request,
        "pokemon/pokemon_lista.html",
        {
            "pagina": pagina,
            "buscar": busqueda,
            "total_pokemones": Pokemon.objects.count(),
        },
    )


# =====================================================
# CREAR POKÉMON
# =====================================================

def pokemon_crear(request):
    formulario = PokemonForm(
        request.POST or None,
        request.FILES or None,
    )

    if request.method == "POST" and formulario.is_valid():
        pokemon = formulario.save()

        messages.success(
            request,
            f"{pokemon.nombre} fue registrado correctamente.",
        )

        return redirect("pokemon_lista")

    return render(
        request,
        "pokemon/pokemon_formulario.html",
        {
            "formulario": formulario,
            "titulo": "Registrar Pokémon",
            "accion": "Guardar Pokémon",
        },
    )


# =====================================================
# EDITAR POKÉMON
# =====================================================

def pokemon_editar(request, numero):
    pokemon = get_object_or_404(
        Pokemon,
        numero=numero,
    )

    formulario = PokemonForm(
        request.POST or None,
        request.FILES or None,
        instance=pokemon,
    )

    if request.method == "POST" and formulario.is_valid():
        pokemon = formulario.save()

        messages.success(
            request,
            f"{pokemon.nombre} fue actualizado correctamente.",
        )

        return redirect("pokemon_lista")

    return render(
        request,
        "pokemon/pokemon_formulario.html",
        {
            "formulario": formulario,
            "titulo": f"Editar {pokemon.nombre}",
            "accion": "Guardar cambios",
            "pokemon": pokemon,
        },
    )


# =====================================================
# ELIMINAR POKÉMON
# =====================================================

def pokemon_eliminar(request, numero):
    pokemon = get_object_or_404(
        Pokemon,
        numero=numero,
    )

    if request.method == "POST":
        nombre = pokemon.nombre
        pokemon.delete()

        messages.success(
            request,
            f"{nombre} fue eliminado correctamente.",
        )

        return redirect("pokemon_lista")

    return render(
        request,
        "pokemon/pokemon_confirmar_eliminar.html",
        {
            "pokemon": pokemon,
        },
    )


# =====================================================
# CONFIGURACIÓN DE LOS MÓDULOS
# =====================================================

MODULOS = {
    "tipos": {
        "modelo": Tipo,
        "formulario": TipoForm,
        "titulo": "Tipos elementales",
        "campo": "nombre",
    },

    "habilidades": {
        "modelo": Habilidad,
        "formulario": HabilidadForm,
        "titulo": "Habilidades",
        "campo": "nombre",
    },

    "profesores": {
        "modelo": Profesor,
        "formulario": ProfesorForm,
        "titulo": "Profesores",
        "campo": "nombre",
    },

    "regiones": {
        "modelo": Region,
        "formulario": RegionForm,
        "titulo": "Regiones",
        "campo": "nombre",
    },

    "entrenadores": {
        "modelo": Entrenador,
        "formulario": EntrenadorForm,
        "titulo": "Entrenadores",
        "campo": "nombre",
    },

    "gimnasios": {
        "modelo": Gimnasio,
        "formulario": GimnasioForm,
        "titulo": "Gimnasios",
        "campo": "lider",
    },

    "backups": {
        "modelo": BackupEntrenador,
        "formulario": BackupEntrenadorForm,
        "titulo": "Cajas del PC Pokémon",
        "campo": "nombre",
    },
}


# =====================================================
# LISTAR LOS MÓDULOS
# =====================================================

def modulo_lista(request, modulo):
    configuracion = MODULOS.get(modulo)

    if configuracion is None:
        messages.error(
            request,
            "El módulo solicitado no existe.",
        )
        return redirect("inicio")

    modelo = configuracion["modelo"]
    registros = modelo.objects.all()

    if modulo == "backups":
        registros = (
            registros
            .select_related("entrenador", "profesor")
            .prefetch_related(
                "pokemones__tipos",
                "pokemones__habilidades",
            )
        )

    elif modulo == "entrenadores":
        registros = (
            registros
            .select_related("profesor")
            .prefetch_related(
                "gimnasios",
                "pokemones__tipos",
                "respaldos__pokemones",
            )
        )

    elif modulo == "gimnasios":
        registros = registros.select_related(
            "tipo",
            "region",
        )

    registros = registros.order_by(
        configuracion["campo"]
    )

    busqueda = request.GET.get("buscar", "").strip()

    if busqueda:
        registros = registros.filter(
            **{
                f'{configuracion["campo"]}__icontains': busqueda
            }
        )

    total = registros.count()

    pagina = Paginator(
        registros,
        15,
    ).get_page(
        request.GET.get("pagina")
    )

    return render(
        request,
        "pokemon/modulo_lista.html",
        {
            "modulo": modulo,
            "titulo": configuracion["titulo"],
            "pagina": pagina,
            "buscar": busqueda,
            "total": total,
        },
    )


# =====================================================
# CREAR REGISTROS DE LOS MÓDULOS
# =====================================================

def modulo_crear(request, modulo):
    configuracion = MODULOS.get(modulo)

    if configuracion is None:
        messages.error(
            request,
            "El módulo solicitado no existe.",
        )
        return redirect("inicio")

    formulario = configuracion["formulario"](
        request.POST or None,
        request.FILES or None,
    )

    if request.method == "POST" and formulario.is_valid():
        registro = formulario.save()

        messages.success(
            request,
            f"{configuracion['titulo']}: registro creado correctamente.",
        )

        if modulo == "backups":
            return redirect(
                "pc_caja",
                caja_id=registro.pk,
            )

        return redirect(
            "modulo_lista",
            modulo=modulo,
        )

    return render(
        request,
        "pokemon/modulo_formulario.html",
        {
            "formulario": formulario,
            "titulo": f"Crear registro: {configuracion['titulo']}",
            "modulo": modulo,
            "accion": "Crear registro",
        },
    )


# =====================================================
# EDITAR REGISTROS DE LOS MÓDULOS
# =====================================================

def modulo_editar(request, modulo, pk):
    configuracion = MODULOS.get(modulo)

    if configuracion is None:
        messages.error(
            request,
            "El módulo solicitado no existe.",
        )
        return redirect("inicio")

    registro = get_object_or_404(
        configuracion["modelo"],
        pk=pk,
    )

    formulario = configuracion["formulario"](
        request.POST or None,
        request.FILES or None,
        instance=registro,
    )

    if request.method == "POST" and formulario.is_valid():
        formulario.save()

        messages.success(
            request,
            "Registro actualizado correctamente.",
        )

        return redirect(
            "modulo_lista",
            modulo=modulo,
        )

    return render(
        request,
        "pokemon/modulo_formulario.html",
        {
            "formulario": formulario,
            "titulo": f"Editar: {registro}",
            "modulo": modulo,
            "accion": "Guardar cambios",
        },
    )


# =====================================================
# ELIMINAR REGISTROS DE LOS MÓDULOS
# =====================================================

def modulo_eliminar(request, modulo, pk):
    configuracion = MODULOS.get(modulo)

    if configuracion is None:
        messages.error(
            request,
            "El módulo solicitado no existe.",
        )
        return redirect("inicio")

    registro = get_object_or_404(
        configuracion["modelo"],
        pk=pk,
    )

    if request.method == "POST":
        registro.delete()

        messages.success(
            request,
            "Registro eliminado correctamente.",
        )

        return redirect(
            "modulo_lista",
            modulo=modulo,
        )

    return render(
        request,
        "pokemon/modulo_confirmar_eliminar.html",
        {
            "registro": registro,
            "modulo": modulo,
        },
    )


# =====================================================
# PC POKÉMON - PERFIL DEL ENTRENADOR
# =====================================================

def pc_entrenador(request, entrenador_id):
    entrenador = get_object_or_404(
        Entrenador.objects
        .select_related("profesor")
        .prefetch_related(
            "gimnasios__tipo",
            "gimnasios__region",
            "pokemones__tipos",
            "pokemones__habilidades",
            "respaldos__pokemones",
        ),
        pk=entrenador_id,
    )

    cajas = list(
        entrenador.respaldos
        .annotate(
            total_guardados=Count(
                "pokemones",
                distinct=True,
            )
        )
        .order_by("-fecha_creacion")
    )

    medallas = entrenador.gimnasios.select_related(
        "tipo",
        "region",
    )

    pokemones_equipo = (
        entrenador.pokemones
        .exclude(respaldos__isnull=False)
        .prefetch_related(
            "tipos",
            "habilidades",
            "evoluciones",
        )
        .order_by("numero")
        .distinct()
    )

    total_en_pc = sum(
        caja.total_guardados
        for caja in cajas
    )

    profesores = Profesor.objects.order_by(
        "nombre",
        "apellido",
    )

    return render(
        request,
        "pokemon/pc_entrenador.html",
        {
            "entrenador": entrenador,
            "cajas": cajas,
            "medallas": medallas,
            "pokemones_equipo": pokemones_equipo,
            "total_en_pc": total_en_pc,
            "profesores": profesores,
        },
    )


# =====================================================
# PC POKÉMON - ADMINISTRAR UNA CAJA
# =====================================================

def pc_caja(request, caja_id):
    caja = get_object_or_404(
        BackupEntrenador.objects
        .select_related(
            "entrenador__profesor",
            "profesor",
        )
        .prefetch_related(
            "pokemones__tipos",
            "pokemones__habilidades",
            "pokemones__evoluciones",
        ),
        pk=caja_id,
    )

    entrenador = caja.entrenador

    if request.method == "POST":
        accion = request.POST.get(
            "accion",
            "",
        ).strip()

        pokemon_id = request.POST.get(
            "pokemon_id",
            "",
        ).strip()

        if not pokemon_id.isdigit():
            messages.error(
                request,
                "No se recibió un Pokémon válido.",
            )
            return redirect(
                "pc_caja",
                caja_id=caja.pk,
            )

        with transaction.atomic():
            pokemon = get_object_or_404(
                Pokemon.objects.select_for_update(),
                pk=int(pokemon_id),
            )

            if accion == "guardar":

                if pokemon.entrenador_id not in (
                    None,
                    entrenador.pk,
                ):
                    messages.error(
                        request,
                        "Este Pokémon pertenece a otro entrenador.",
                    )
                    return redirect(
                        "pc_caja",
                        caja_id=caja.pk,
                    )

                ya_guardado = (
                    BackupEntrenador.objects
                    .filter(pokemones=pokemon)
                    .exclude(pk=caja.pk)
                    .exists()
                )

                if ya_guardado:
                    messages.warning(
                        request,
                        "Este Pokémon ya está guardado en otra caja.",
                    )
                    return redirect(
                        "pc_caja",
                        caja_id=caja.pk,
                    )

                if caja.pokemones.filter(
                    pk=pokemon.pk
                ).exists():
                    messages.warning(
                        request,
                        "Este Pokémon ya está en esta caja.",
                    )
                    return redirect(
                        "pc_caja",
                        caja_id=caja.pk,
                    )

                pokemon.entrenador = None
                pokemon.save(
                    update_fields=["entrenador"]
                )

                caja.pokemones.add(pokemon)

                messages.success(
                    request,
                    f"{pokemon.nombre} fue guardado correctamente en el PC.",
                )

            elif accion == "retirar":

                if not caja.pokemones.filter(
                    pk=pokemon.pk
                ).exists():
                    messages.error(
                        request,
                        "Este Pokémon no pertenece a esta caja.",
                    )
                    return redirect(
                        "pc_caja",
                        caja_id=caja.pk,
                    )

                if pokemon.entrenador_id not in (
                    None,
                    entrenador.pk,
                ):
                    messages.error(
                        request,
                        "No se puede retirar porque el Pokémon pertenece a otro entrenador.",
                    )
                    return redirect(
                        "pc_caja",
                        caja_id=caja.pk,
                    )

                caja.pokemones.remove(pokemon)

                pokemon.entrenador = entrenador
                pokemon.save(
                    update_fields=["entrenador"]
                )

                messages.success(
                    request,
                    f"{pokemon.nombre} fue retirado del PC y volvió al equipo.",
                )

            else:
                messages.error(
                    request,
                    "La acción solicitada no es válida.",
                )

        return redirect(
            "pc_caja",
            caja_id=caja.pk,
        )

    # Pokémon almacenados en esta caja.
    pokemones = (
        caja.pokemones
        .all()
        .prefetch_related(
            "tipos",
            "habilidades",
            "evoluciones",
        )
        .order_by("numero")
    )

    # Pokémon que el entrenador puede guardar.
    disponibles = (
        Pokemon.objects
        .filter(
            Q(entrenador=entrenador)
            | Q(entrenador__isnull=True)
        )
        .exclude(
            respaldos__isnull=False
        )
        .prefetch_related(
            "tipos",
            "habilidades",
            "evoluciones",
        )
        .order_by("numero")
        .distinct()
    )

    medallas = entrenador.gimnasios.select_related(
        "tipo",
        "region",
    ).all()

    contexto = {
        "caja": caja,
        "entrenador": entrenador,
        "pokemones": pokemones,
        "disponibles": disponibles,
        "medallas": medallas,
        "total_medallas": medallas.count(),
    }

    return render(
        request,
        "pokemon/pc_caja.html",
        contexto,
    )


# =====================================================
# PC POKÉMON - CREAR UNA CAJA
# =====================================================

@require_POST
def pc_crear_caja(request, entrenador_id):
    entrenador = get_object_or_404(
        Entrenador,
        pk=entrenador_id,
    )

    nombre = request.POST.get(
        "nombre",
        "",
    ).strip()

    profesor_id = request.POST.get(
        "profesor",
        "",
    ).strip()

    if not nombre:
        messages.error(
            request,
            "Debes escribir el nombre de la caja.",
        )
        return redirect(
            "pc_entrenador",
            entrenador_id=entrenador.pk,
        )

    if not profesor_id.isdigit():
        messages.error(
            request,
            "Debes seleccionar un profesor.",
        )
        return redirect(
            "pc_entrenador",
            entrenador_id=entrenador.pk,
        )

    profesor = get_object_or_404(
        Profesor,
        pk=int(profesor_id),
    )

    caja = BackupEntrenador.objects.create(
        nombre=nombre,
        entrenador=entrenador,
        profesor=profesor,
    )

    messages.success(
        request,
        f"La caja '{caja.nombre}' fue creada correctamente.",
    )

    return redirect(
        "pc_caja",
        caja_id=caja.pk,
    )
