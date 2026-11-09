from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import (
    Tipo,
    Habilidad,
    Profesor,
    Region,
    Entrenador,
    Gimnasio,
    Pokemon,
    BackupEntrenador,
)

from .serializers import (
    TipoSerializer,
    HabilidadSerializer,
    ProfesorSerializer,
    RegionSerializer,
    EntrenadorSerializer,
    GimnasioSerializer,
    PokemonSerializer,
    BackupEntrenadorSerializer,
)


class BaseAPIViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]


class TipoViewSet(BaseAPIViewSet):
    queryset = Tipo.objects.all()
    serializer_class = TipoSerializer
    search_fields = ["nombre"]
    ordering_fields = ["nombre"]


class HabilidadViewSet(BaseAPIViewSet):
    queryset = Habilidad.objects.all()
    serializer_class = HabilidadSerializer
    search_fields = ["nombre", "descripcion"]
    ordering_fields = ["nombre"]


class ProfesorViewSet(BaseAPIViewSet):
    queryset = Profesor.objects.all()
    serializer_class = ProfesorSerializer
    search_fields = ["nombre", "apellido", "especialidad", "pueblo"]
    ordering_fields = ["nombre", "apellido"]


class RegionViewSet(BaseAPIViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    search_fields = ["nombre", "descripcion"]
    ordering_fields = ["nombre"]


class GimnasioViewSet(BaseAPIViewSet):
    queryset = Gimnasio.objects.select_related(
        "tipo", "region"
    )
    serializer_class = GimnasioSerializer
    search_fields = ["lider", "medalla", "ciudad", "region__nombre", "tipo__nombre"]
    ordering_fields = ["ciudad", "lider"]


class EntrenadorViewSet(BaseAPIViewSet):
    queryset = Entrenador.objects.select_related(
        "profesor"
    ).prefetch_related("gimnasios", "pokemones")
    serializer_class = EntrenadorSerializer
    search_fields = [
        "documento",
        "nombre",
        "apellido",
        "pueblo",
        "liga",
        "profesor__nombre",
    ]
    ordering_fields = ["nombre", "apellido", "cantidad_medallas"]


class PokemonViewSet(BaseAPIViewSet):
    queryset = Pokemon.objects.select_related(
        "entrenador"
    ).prefetch_related(
        "tipos",
        "habilidades",
        "evoluciones",
    )
    serializer_class = PokemonSerializer
    search_fields = ["nombre", "tipos__nombre", "habilidades__nombre"]
    ordering_fields = ["numero", "nombre", "hp", "ataque", "defensa"]

    def get_queryset(self):
        queryset = super().get_queryset()

        numero = self.request.query_params.get("numero")
        tipo = self.request.query_params.get("tipo")

        if numero and numero.isdigit():
            queryset = queryset.filter(numero=int(numero))

        if tipo:
            queryset = queryset.filter(tipos__nombre__iexact=tipo)

        return queryset.distinct()

class BackupEntrenadorViewSet(BaseAPIViewSet):
    queryset = BackupEntrenador.objects.select_related(
        "entrenador", "profesor"
    ).prefetch_related("pokemones")
    serializer_class = BackupEntrenadorSerializer
    search_fields = [
        "nombre",
        "entrenador__nombre",
        "entrenador__apellido",
        "profesor__nombre",
    ]
    ordering_fields = ["fecha_creacion", "nombre"]