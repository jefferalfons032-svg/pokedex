
from django.contrib import admin
from .models import (
    Tipo,
    Habilidad,
    Pokemon,
    Profesor,
    Region,
    Entrenador,
    Gimnasio,
    BackupEntrenador,
)


# ==========================================
# TIPOS
# ==========================================

@admin.register(Tipo)
class TipoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "color")
    search_fields = ("nombre",)
    ordering = ("nombre",)


# ==========================================
# HABILIDADES
# ==========================================

@admin.register(Habilidad)
class HabilidadAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)


# ==========================================
# POKEMON
# ==========================================

@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    list_display = (
        "numero",
        "nombre",
        "mostrar_tipos",
        "hp",
        "ataque",
        "defensa",
        "es_legendario",
        "entrenador",
    )

    list_filter = (
        "tipos",
        "es_legendario",
    )

    search_fields = ("nombre",)
    filter_horizontal = ("tipos", "habilidades", "evoluciones")
    list_per_page = 20

    @admin.display(description="Tipos")
    def mostrar_tipos(self, obj):
        return ", ".join(tipo.nombre for tipo in obj.tipos.all())


# ==========================================
# PROFESORES
# ==========================================

@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "apellido",
        "especialidad",
        "pueblo",
    )

    search_fields = ("nombre", "apellido", "especialidad")


# ==========================================
# REGIONES
# ==========================================

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)


# ==========================================
# ENTRENADORES
# ==========================================

@admin.register(Entrenador)
class EntrenadorAdmin(admin.ModelAdmin):
    list_display = (
        "documento",
        "nombre",
        "apellido",
        "cantidad_pokemones",
        "cantidad_medallas",
        "clasificado",
        "liga",
        "profesor",
    )

    list_filter = (
        "clasificado",
        "liga",
        "profesor",
    )

    search_fields = (
        "documento",
        "nombre",
        "apellido",
        "pueblo",
    )

    filter_horizontal = ("gimnasios",)
    list_per_page = 20


# ==========================================
# GIMNASIOS
# ==========================================

@admin.register(Gimnasio)
class GimnasioAdmin(admin.ModelAdmin):
    list_display = (
        "lider",
        "tipo",
        "medalla",
        "ciudad",
        "telefono",
        "region",
    )

    list_filter = ("tipo", "region")
    search_fields = ("lider", "ciudad", "medalla")


# ==========================================
# BACKUPS
# ==========================================

@admin.register(BackupEntrenador)
class BackupEntrenadorAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "entrenador",
        "profesor",
        "cantidad_pokemones",
        "fecha_creacion",
    )

    search_fields = (
        "nombre",
        "entrenador__nombre",
        "entrenador__apellido",
    )

    list_filter = ("profesor",)
    filter_horizontal = ("pokemones",)
    readonly_fields = ("fecha_creacion",)
    list_per_page = 20


# ==========================================
# PERSONALIZACIÓN DEL ADMINISTRADOR
# ==========================================

admin.site.site_header = "POKÉDEX | CENTRO DE CONTROL"
admin.site.site_title = "Pokédex Administración"
admin.site.index_title = "Gestión del universo Pokémon"
