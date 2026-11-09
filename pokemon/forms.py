from django import forms
from django.db import transaction
from django.db.models import Q

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


# =====================================================
# WIDGET DEL EQUIPO POKÉMON
# =====================================================

class PokemonEquipoCheckboxSelectMultiple(forms.CheckboxSelectMultiple):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pokemon_por_id = {}

    @staticmethod
    def obtener_generacion(numero):
        rangos = [
            (1, 151, "1"),
            (152, 251, "2"),
            (252, 386, "3"),
            (387, 493, "4"),
            (494, 649, "5"),
            (650, 721, "6"),
            (722, 809, "7"),
            (810, 905, "8"),
            (906, 1025, "9"),
        ]

        for minimo, maximo, generacion in rangos:
            if minimo <= numero <= maximo:
                return generacion

        return ""

    def create_option(
        self,
        name,
        value,
        label,
        selected,
        index,
        subindex=None,
        attrs=None,
    ):
        option = super().create_option(
            name,
            value,
            label,
            selected,
            index,
            subindex=subindex,
            attrs=attrs,
        )

        valor_pk = getattr(value, "value", value)
        pokemon = self.pokemon_por_id.get(str(valor_pk))

        if pokemon:
            tipos = ", ".join(
                tipo.nombre for tipo in pokemon.tipos.all()
            )

            option["attrs"].update({
                "data-numero": str(pokemon.numero),
                "data-nombre": pokemon.nombre,
                "data-imagen": pokemon.url_imagen or "",
                "data-tipos": tipos,
                "data-generacion": self.obtener_generacion(
                    pokemon.numero
                ),
            })

        return option


# =====================================================
# WIDGET DE MEDALLAS Y GIMNASIOS
# =====================================================

class GimnasioMedallaCheckboxSelectMultiple(
    forms.CheckboxSelectMultiple
):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gimnasios_por_id = {}

    def create_option(
        self,
        name,
        value,
        label,
        selected,
        index,
        subindex=None,
        attrs=None,
    ):
        option = super().create_option(
            name,
            value,
            label,
            selected,
            index,
            subindex=subindex,
            attrs=attrs,
        )

        valor_pk = getattr(value, "value", value)
        gimnasio = self.gimnasios_por_id.get(str(valor_pk))

        if gimnasio:
            tipo = gimnasio.tipo.nombre if gimnasio.tipo else ""
            region = gimnasio.region.nombre if gimnasio.region else ""

            imagen = ""

            if gimnasio.imagen_archivo:
                try:
                    imagen = gimnasio.imagen_archivo.url
                except (ValueError, OSError):
                    pass

            option["attrs"].update({
                "data-medalla": gimnasio.medalla,
                "data-ciudad": gimnasio.ciudad,
                "data-lider": gimnasio.lider,
                "data-tipo": tipo,
                "data-region": region,
                "data-imagen": imagen,
            })

        return option


# =====================================================
# ESTILOS GENERALES
# =====================================================

class EstiloFormularioMixin:

    placeholders = {
        "nombre": "Escribe el nombre",
        "apellido": "Escribe el apellido",
        "documento": "Número de documento",
        "pueblo": "Pueblo o ciudad de procedencia",
        "especialidad": "Especialidad del profesor",
        "descripcion": "Escribe una descripción",
        "numero": "Número de Pokédex",
        "altura": "Altura en decímetros",
        "peso": "Peso en hectogramos",
        "experiencia_base": "Experiencia base",
        "hp": "Puntos de salud",
        "ataque": "Puntos de ataque",
        "defensa": "Puntos de defensa",
        "ataque_especial": "Ataque especial",
        "defensa_especial": "Defensa especial",
        "velocidad": "Velocidad",
        "medalla": "Nombre de la medalla",
        "ciudad": "Ciudad del gimnasio",
        "telefono": "Teléfono de contacto",
        "imagen": "https://ejemplo.com/imagen.jpg",
        "imagen_oficial": "https://ejemplo.com/imagen-oficial.png",
        "color": "#777777",
        "items": "Ejemplo: Poké Balls, Pociones, Revivir...",
        "lider": "Nombre del líder del gimnasio",
    }

    def aplicar_estilos(self):
        for nombre, campo in self.fields.items():
            widget = campo.widget

            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.update({
                    "class": "campo-checkbox",
                })

            elif isinstance(widget, forms.CheckboxSelectMultiple):
                widget.attrs.update({
                    "class": "campo-checkbox-list",
                })

            elif isinstance(widget, forms.SelectMultiple):
                widget.attrs.update({
                    "class": "campo-select multiple",
                })

            elif isinstance(widget, forms.Select):
                widget.attrs.update({
                    "class": "campo-select",
                })

            elif isinstance(widget, forms.Textarea):
                widget.attrs.update({
                    "class": "campo-textarea",
                    "rows": 4,
                })

            elif isinstance(widget, forms.ClearableFileInput):
                widget.attrs.update({
                    "class": "campo-archivo",
                })

            else:
                widget.attrs.update({
                    "class": "campo-input",
                })

            if nombre in self.placeholders:
                widget.attrs.setdefault(
                    "placeholder",
                    self.placeholders[nombre],
                )

            if campo.required:
                widget.attrs["required"] = True

            campo.help_text = campo.help_text or ""


# =====================================================
# TIPOS
# =====================================================

class TipoForm(EstiloFormularioMixin, forms.ModelForm):

    class Meta:
        model = Tipo
        fields = ["nombre", "color"]

        widgets = {
            "color": forms.TextInput(attrs={
                "type": "color",
            }),
        }

        labels = {
            "nombre": "Nombre del tipo",
            "color": "Color identificador",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aplicar_estilos()


# =====================================================
# HABILIDADES
# =====================================================

class HabilidadForm(EstiloFormularioMixin, forms.ModelForm):

    class Meta:
        model = Habilidad
        fields = ["nombre", "descripcion"]

        labels = {
            "nombre": "Nombre de la habilidad",
            "descripcion": "Descripción de la habilidad",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aplicar_estilos()


# =====================================================
# PROFESORES
# =====================================================

class ProfesorForm(EstiloFormularioMixin, forms.ModelForm):

    class Meta:
        model = Profesor
        fields = [
            "nombre",
            "apellido",
            "especialidad",
            "pueblo",
            "imagen_archivo",
        ]

        labels = {
            "nombre": "Nombre",
            "apellido": "Apellido",
            "especialidad": "Especialidad",
            "pueblo": "Pueblo de trabajo",
            "imagen_archivo": "Fotografía del profesor",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aplicar_estilos()


# =====================================================
# REGIONES
# =====================================================

class RegionForm(EstiloFormularioMixin, forms.ModelForm):

    class Meta:
        model = Region
        fields = [
            "nombre",
            "descripcion",
            "imagen",
            "imagen_archivo",
        ]

        labels = {
            "nombre": "Nombre de la región",
            "descripcion": "Descripción",
            "imagen": "Enlace de imagen",
            "imagen_archivo": "Subir imagen",
        }

        widgets = {
            "descripcion": forms.Textarea(attrs={
                "rows": 5,
            }),
            "imagen": forms.URLInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aplicar_estilos()


# =====================================================
# POKÉMON
# =====================================================

class PokemonForm(EstiloFormularioMixin, forms.ModelForm):

    class Meta:
        model = Pokemon

        fields = [
            "numero",
            "nombre",
            "imagen",
            "imagen_oficial",
            "imagen_archivo",
            "altura",
            "peso",
            "experiencia_base",
            "tipos",
            "habilidades",
            "entrenador",
            "evoluciones",
            "hp",
            "ataque",
            "defensa",
            "ataque_especial",
            "defensa_especial",
            "velocidad",
            "es_legendario",
        ]

        labels = {
            "numero": "Número de Pokédex",
            "nombre": "Nombre del Pokémon",
            "imagen": "Enlace de imagen",
            "imagen_oficial": "Enlace de imagen oficial",
            "imagen_archivo": "Subir imagen desde el equipo",
            "altura": "Altura (decímetros)",
            "peso": "Peso (hectogramos)",
            "experiencia_base": "Experiencia base",
            "tipos": "Tipos o elementos",
            "habilidades": "Habilidades",
            "entrenador": "Entrenador asignado",
            "evoluciones": "Evoluciones",
            "hp": "Salud (HP)",
            "ataque": "Ataque",
            "defensa": "Defensa",
            "ataque_especial": "Ataque especial",
            "defensa_especial": "Defensa especial",
            "velocidad": "Velocidad",
            "es_legendario": "¿Es un Pokémon legendario?",
        }

        widgets = {
            "imagen": forms.URLInput(),
            "imagen_oficial": forms.URLInput(),
            "tipos": forms.SelectMultiple(),
            "habilidades": forms.SelectMultiple(),
            "evoluciones": forms.SelectMultiple(),
            "es_legendario": forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["tipos"].queryset = Tipo.objects.order_by("nombre")
        self.fields["habilidades"].queryset = Habilidad.objects.order_by(
            "nombre"
        )

        evoluciones = Pokemon.objects.all()

        if self.instance and self.instance.pk:
            evoluciones = evoluciones.exclude(pk=self.instance.pk)

        self.fields["evoluciones"].queryset = evoluciones.order_by(
            "numero"
        )

        self.fields["entrenador"].queryset = Entrenador.objects.order_by(
            "apellido",
            "nombre",
        )

        self.fields["tipos"].help_text = (
            "Puedes seleccionar uno o varios tipos."
        )
        self.fields["habilidades"].help_text = (
            "Selecciona las habilidades que puede utilizar."
        )
        self.fields["evoluciones"].help_text = (
            "Selecciona los Pokémon a los que puede evolucionar."
        )
        self.fields["imagen"].help_text = (
            "Puedes pegar un enlace directo a una imagen."
        )
        self.fields["imagen_oficial"].help_text = (
            "Enlace de la ilustración oficial del Pokémon."
        )

        self.aplicar_estilos()


# =====================================================
# ENTRENADORES
# =====================================================

class EntrenadorForm(EstiloFormularioMixin, forms.ModelForm):

    pokemones_equipo = forms.ModelMultipleChoiceField(
        queryset=Pokemon.objects.none(),
        required=False,
        label="Equipo Pokémon",
        help_text=(
            "Selecciona los Pokémon que pertenecen al entrenador."
        ),
        widget=PokemonEquipoCheckboxSelectMultiple(),
    )

    cantidad_pokemones = forms.IntegerField(
        label="Cantidad actual de Pokémon",
        required=False,
        disabled=True,
        help_text="Este dato se calcula automáticamente.",
    )

    class Meta:
        model = Entrenador

        fields = [
            "documento",
            "nombre",
            "apellido",
            "pueblo",
            "cantidad_medallas",
            "clasificado",
            "liga",
            "profesor",
            "gimnasios",
            "imagen",
            "imagen_archivo",
            "pokemones_equipo",
            "cantidad_pokemones",
        ]

        labels = {
            "documento": "Documento de identidad",
            "nombre": "Nombre",
            "apellido": "Apellido",
            "pueblo": "Pueblo de procedencia",
            "cantidad_medallas": "Cantidad de medallas obtenidas",
            "clasificado": "¿Clasificó a la liga?",
            "liga": "Liga Pokémon",
            "profesor": "Profesor asignado",
            "gimnasios": "Medallas obtenidas",
            "imagen": "Enlace de imagen",
            "imagen_archivo": "Fotografía del entrenador",
        }

        widgets = {
            "clasificado": forms.CheckboxInput(),
            "gimnasios": GimnasioMedallaCheckboxSelectMultiple(),
            "imagen": forms.URLInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["profesor"].queryset = Profesor.objects.order_by(
            "nombre",
            "apellido",
        )

        gimnasios = Gimnasio.objects.select_related(
            "tipo",
            "region",
        ).order_by(
            "region__nombre",
            "ciudad",
            "medalla",
        )

        campo_medallas = self.fields["gimnasios"]
        campo_medallas.queryset = gimnasios
        campo_medallas.label = "Medallas obtenidas"
        campo_medallas.help_text = (
            "Selecciona las medallas que el entrenador ha conseguido "
            "al vencer a los líderes de gimnasio."
        )

        campo_medallas.widget.gimnasios_por_id = {
            str(gimnasio.pk): gimnasio
            for gimnasio in gimnasios
        }

        self.fields["cantidad_medallas"].disabled = True
        self.fields["cantidad_medallas"].help_text = (
            "Se calcula automáticamente según las medallas seleccionadas."
        )

        # Pokémon que ya están guardados en alguna caja del PC.
        pokemon_en_pc = BackupEntrenador.objects.values_list(
            "pokemones",
            flat=True,
        )

        # Solo permite Pokémon libres o del entrenador actual.
        if self.instance and self.instance.pk:
            disponibles = Pokemon.objects.filter(
                Q(entrenador__isnull=True)
                | Q(entrenador=self.instance)
            )
        else:
            disponibles = Pokemon.objects.filter(
                entrenador__isnull=True
            )

        disponibles = (
            disponibles
            .exclude(pk__in=pokemon_en_pc)
            .distinct()
            .prefetch_related("tipos")
            .order_by("numero")
        )

        if self.instance and self.instance.pk:
            equipo_actual = disponibles.filter(
                entrenador=self.instance
            )

            self.fields["cantidad_pokemones"].initial = (
                equipo_actual.count()
            )

            self.fields["pokemones_equipo"].initial = (
                equipo_actual.values_list("pk", flat=True)
            )

            self.fields["cantidad_medallas"].initial = (
                self.instance.gimnasios.count()
            )

        else:
            self.fields["cantidad_pokemones"].initial = 0
            self.fields["cantidad_medallas"].initial = 0

        equipo = self.fields["pokemones_equipo"]
        equipo.queryset = disponibles

        equipo.widget.pokemon_por_id = {
            str(pokemon.pk): pokemon
            for pokemon in disponibles
        }

        equipo.help_text = (
            "Busca por nombre o número, filtra por generación y tipo "
            "y selecciona los Pokémon del equipo."
        )

        self.aplicar_estilos()

    def clean_documento(self):
        documento = self.cleaned_data.get("documento", "").strip()

        consulta = Entrenador.objects.filter(
            documento=documento
        )

        if self.instance and self.instance.pk:
            consulta = consulta.exclude(pk=self.instance.pk)

        if consulta.exists():
            raise forms.ValidationError(
                "Ya existe un entrenador registrado con este documento."
            )

        return documento

    def clean_pokemones_equipo(self):
        seleccionados = self.cleaned_data.get("pokemones_equipo")

        if not seleccionados:
            return seleccionados

        ids = list(
            seleccionados.values_list("pk", flat=True)
        )

        guardados = BackupEntrenador.objects.filter(
            pokemones__in=ids
        )

        if guardados.exists():
            raise forms.ValidationError(
                "Uno o varios Pokémon seleccionados ya están guardados "
                "en el PC. Actualiza el formulario e inténtalo nuevamente."
            )

        return seleccionados

    def save(self, commit=True):
        entrenador = super().save(commit=False)

        gimnasios = self.cleaned_data.get("gimnasios")
        entrenador.cantidad_medallas = (
            gimnasios.count() if gimnasios else 0
        )

        if commit:
            with transaction.atomic():
                entrenador.save()
                self.save_m2m()
                self.guardar_pokemones(entrenador)

        else:
            guardar_relaciones_original = self.save_m2m

            def guardar_relaciones():
                guardar_relaciones_original()

                with transaction.atomic():
                    self.actualizar_cantidad_medallas(entrenador)
                    self.guardar_pokemones(entrenador)

            self.save_m2m = guardar_relaciones

        return entrenador

    def actualizar_cantidad_medallas(self, entrenador):
        cantidad = entrenador.gimnasios.count()

        Entrenador.objects.filter(
            pk=entrenador.pk
        ).update(
            cantidad_medallas=cantidad
        )

        entrenador.cantidad_medallas = cantidad

    def guardar_pokemones(self, entrenador):
        seleccionados = self.cleaned_data.get("pokemones_equipo")

        ids_seleccionados = (
            list(seleccionados.values_list("pk", flat=True))
            if seleccionados
            else []
        )

        guardados = BackupEntrenador.objects.filter(
            pokemones__in=ids_seleccionados
        ).exists()

        if guardados:
            raise forms.ValidationError(
                "Uno o varios Pokémon ya están almacenados en el PC."
            )

        ocupados = Pokemon.objects.filter(
            pk__in=ids_seleccionados
        ).exclude(
            Q(entrenador__isnull=True)
            | Q(entrenador=entrenador)
        ).exists()

        if ocupados:
            raise forms.ValidationError(
                "Uno o varios Pokémon pertenecen a otro entrenador."
            )

        Pokemon.objects.filter(
            entrenador=entrenador
        ).exclude(
            pk__in=ids_seleccionados
        ).exclude(
            respaldos__isnull=False
        ).update(
            entrenador=None
        )

        Pokemon.objects.filter(
            pk__in=ids_seleccionados
        ).exclude(
            respaldos__isnull=False
        ).update(
            entrenador=entrenador
        )


# =====================================================
# GIMNASIOS
# =====================================================

class GimnasioForm(EstiloFormularioMixin, forms.ModelForm):

    class Meta:
        model = Gimnasio

        fields = [
            "lider",
            "tipo",
            "medalla",
            "ciudad",
            "telefono",
            "region",
            "imagen_archivo",
        ]

        labels = {
            "lider": "Líder de gimnasio",
            "tipo": "Tipo de elemento",
            "medalla": "Medalla entregada",
            "ciudad": "Ciudad",
            "telefono": "Teléfono de contacto",
            "region": "Región",
            "imagen_archivo": "Imagen del gimnasio",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["tipo"].queryset = Tipo.objects.order_by("nombre")
        self.fields["region"].queryset = Region.objects.order_by("nombre")

        self.aplicar_estilos()


# =====================================================
# BACKUP DE ENTRENADORES
# =====================================================

class BackupEntrenadorForm(
    EstiloFormularioMixin,
    forms.ModelForm,
):

    cantidad_pokemones = forms.IntegerField(
        label="Pokémon guardados",
        required=False,
        disabled=True,
        help_text=(
            "La cantidad se obtiene de los Pokémon seleccionados."
        ),
    )

    class Meta:
        model = BackupEntrenador

        fields = [
            "nombre",
            "entrenador",
            "profesor",
            "pokemones",
            "items",
            "cantidad_pokemones",
        ]

        labels = {
            "nombre": "Nombre del respaldo",
            "entrenador": "Entrenador propietario",
            "profesor": "Profesor encargado de cuidar el respaldo",
            "pokemones": "Pokémon almacenados",
            "items": "Ítems almacenados",
        }

        widgets = {
            "pokemones": forms.SelectMultiple(),
            "items": forms.Textarea(attrs={
                "rows": 5,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["entrenador"].queryset = Entrenador.objects.order_by(
            "apellido",
            "nombre",
        )

        self.fields["profesor"].queryset = Profesor.objects.order_by(
            "nombre",
            "apellido",
        )

        self.fields["pokemones"].queryset = (
            Pokemon.objects.select_related(
                "entrenador"
            ).prefetch_related(
                "tipos"
            ).order_by(
                "numero"
            )
        )

        if self.instance and self.instance.pk:
            self.fields["cantidad_pokemones"].initial = (
                self.instance.cantidad_pokemones
            )
        else:
            self.fields["cantidad_pokemones"].initial = 0

        self.fields["items"].help_text = (
            "Registra los objetos guardados en este backup."
        )

        self.fields["pokemones"].help_text = (
            "Puedes seleccionar varios Pokémon para almacenarlos."
        )

        self.aplicar_estilos()

    def clean_pokemones(self):
        seleccionados = self.cleaned_data.get("pokemones")

        if not seleccionados:
            return seleccionados

        ids = list(
            seleccionados.values_list("pk", flat=True)
        )

        otros_backups = BackupEntrenador.objects.filter(
            pokemones__in=ids
        )

        if self.instance and self.instance.pk:
            otros_backups = otros_backups.exclude(
                pk=self.instance.pk
            )

        if otros_backups.exists():
            raise forms.ValidationError(
                "Uno o varios Pokémon ya están almacenados en otra caja."
            )

        entrenador = self.cleaned_data.get("entrenador")

        if entrenador:
            pertenecen_a_otro = seleccionados.exclude(
                Q(entrenador__isnull=True)
                | Q(entrenador=entrenador)
            )

            if pertenecen_a_otro.exists():
                raise forms.ValidationError(
                    "No puedes guardar Pokémon que pertenecen a otro entrenador."
                )

        return seleccionados

    def save(self, commit=True):
        respaldo_anterior = self.instance
        entrenador_anterior = None
        ids_anteriores = []

        if respaldo_anterior and respaldo_anterior.pk:
            entrenador_anterior = respaldo_anterior.entrenador

            ids_anteriores = list(
                respaldo_anterior.pokemones.values_list(
                    "pk",
                    flat=True,
                )
            )

        respaldo = super().save(commit=False)

        if commit:
            with transaction.atomic():
                respaldo.save()
                self.save_m2m()

                self.sincronizar_pokemones(
                    respaldo,
                    entrenador_anterior,
                    ids_anteriores,
                )

        else:
            guardar_relaciones_original = self.save_m2m

            def guardar_relaciones():
                guardar_relaciones_original()

                with transaction.atomic():
                    self.sincronizar_pokemones(
                        respaldo,
                        entrenador_anterior,
                        ids_anteriores,
                    )

            self.save_m2m = guardar_relaciones

        return respaldo

    def sincronizar_pokemones(
        self,
        respaldo,
        entrenador_anterior,
        ids_anteriores,
    ):
        seleccionados = self.cleaned_data.get("pokemones")

        ids_nuevos = (
            list(seleccionados.values_list("pk", flat=True))
            if seleccionados
            else []
        )

        ids_retirados = set(ids_anteriores) - set(ids_nuevos)

        if entrenador_anterior and ids_retirados:
            Pokemon.objects.filter(
                pk__in=ids_retirados,
                entrenador__isnull=True,
            ).update(
                entrenador=entrenador_anterior
            )

        if ids_nuevos:
            Pokemon.objects.filter(
                pk__in=ids_nuevos,
                entrenador=respaldo.entrenador,
            ).update(
                entrenador=None
            )