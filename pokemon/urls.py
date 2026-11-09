
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [

    # =====================================================
    # INICIO Y DETALLE DE POKÉMON
    # =====================================================

    path(
        "",
        views.inicio,
        name="inicio"
    ),

    path(
        "pokemon/<int:numero>/",
        views.detalle,
        name="detalle"
    ),


    # =====================================================
    # ADMINISTRACIÓN DE POKÉMON
    # =====================================================

    path(
        "administracion/pokemones/",
        views.pokemon_lista,
        name="pokemon_lista"
    ),

    path(
        "administracion/pokemones/crear/",
        views.pokemon_crear,
        name="pokemon_crear"
    ),

    path(
        "administracion/pokemones/<int:numero>/editar/",
        views.pokemon_editar,
        name="pokemon_editar"
    ),

    path(
        "administracion/pokemones/<int:numero>/eliminar/",
        views.pokemon_eliminar,
        name="pokemon_eliminar"
    ),


    # =====================================================
    # MÓDULOS ADMINISTRATIVOS
    # =====================================================

    path(
        "administracion/<str:modulo>/",
        views.modulo_lista,
        name="modulo_lista"
    ),

    path(
        "administracion/<str:modulo>/crear/",
        views.modulo_crear,
        name="modulo_crear"
    ),

    path(
        "administracion/<str:modulo>/<int:pk>/editar/",
        views.modulo_editar,
        name="modulo_editar"
    ),

    path(
        "administracion/<str:modulo>/<int:pk>/eliminar/",
        views.modulo_eliminar,
        name="modulo_eliminar"
    ),


    # =====================================================
    # PC POKÉMON
    # =====================================================

    path(
        "pc/entrenador/<int:entrenador_id>/",
        views.pc_entrenador,
        name="pc_entrenador"
    ),

    path(
        "pc/caja/<int:caja_id>/",
        views.pc_caja,
        name="pc_caja"
    ),

    path(
        "pc/entrenador/<int:entrenador_id>/crear-caja/",
        views.pc_crear_caja,
        name="pc_crear_caja"
    ),


    # =====================================================
    # API REST
    # =====================================================

    path(
        "api/",
        include("pokemon.api_urls")
    ),
]


# =====================================================
# SERVIR IMÁGENES DURANTE EL DESARROLLO
# =====================================================

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
