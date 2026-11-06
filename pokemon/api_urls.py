from rest_framework.routers import DefaultRouter

from .api_views import (
    TipoViewSet,
    HabilidadViewSet,
    ProfesorViewSet,
    RegionViewSet,
    EntrenadorViewSet,
    GimnasioViewSet,
    PokemonViewSet,
    BackupEntrenadorViewSet,
)

router = DefaultRouter()

router.register("pokemones", PokemonViewSet, basename="pokemon")
router.register("tipos", TipoViewSet, basename="tipo")
router.register("habilidades", HabilidadViewSet, basename="habilidad")
router.register("profesores", ProfesorViewSet, basename="profesor")
router.register("regiones", RegionViewSet, basename="region")
router.register("entrenadores", EntrenadorViewSet, basename="entrenador")
router.register("gimnasios", GimnasioViewSet, basename="gimnasio")
router.register("backups", BackupEntrenadorViewSet, basename="backup")

urlpatterns = router.urls