from rest_framework import serializers

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


class TipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipo
        fields = "__all__"


class HabilidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habilidad
        fields = "__all__"


class ProfesorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profesor
        fields = "__all__"


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = "__all__"


class GimnasioSerializer(serializers.ModelSerializer):
    tipo = serializers.SlugRelatedField(
        slug_field="nombre",
        queryset=Tipo.objects.all()
    )

    class Meta:
        model = Gimnasio
        fields = "__all__"


class EntrenadorSerializer(serializers.ModelSerializer):
    cantidad_pokemones = serializers.IntegerField(read_only=True)

    class Meta:
        model = Entrenador
        fields = "__all__"


class PokemonSerializer(serializers.ModelSerializer):
    tipos = serializers.SlugRelatedField(
        many=True,
        slug_field="nombre",
        queryset=Tipo.objects.all()
    )

    habilidades = serializers.SlugRelatedField(
        many=True,
        slug_field="nombre",
        queryset=Habilidad.objects.all()
    )

    class Meta:
        model = Pokemon
        fields = "__all__"


class BackupEntrenadorSerializer(serializers.ModelSerializer):
    cantidad_pokemones = serializers.IntegerField(read_only=True)

    class Meta:
        model = BackupEntrenador
        fields = "__all__"