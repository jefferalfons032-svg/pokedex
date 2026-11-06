
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
# WIDGET PERSONALIZADO PARA EL EQUIPO POKÉMON
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
        attrs=None
    ):
        option = super().create_option(
            name,
            value,
            label,
            selected,
            index,
            subindex=subindex,
            attrs=attrs
        )

        valor_pk = getattr(value, "value", value)
        pokemon = self.pokemon_por_id.get(str(valor_pk))

        if pokemon:
            tipos = ", ".join(
                tipo.nombre
                for tipo in pokemon.tipos.all()
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
# ESTILOS GENERALES DE LOS FORMULARIOS
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
                    self.placeholders[nombre]
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

        self.fields["tipos"].queryset = (
            Tipo.objects.order_by("nombre")
        )

        self.fields["habilidades"].queryset = (
            Habilidad.objects.order_by("nombre")
        )

        evoluciones = Pokemon.objects.all()

        if self.instance and self.instance.pk:
            evoluciones = evoluciones.exclude(
                pk=self.instance.pk
            )

        self.fields["evoluciones"].queryset = (
            evoluciones.order_by("numero")
        )

        self.fields["entrenador"].queryset = (
            Entrenador.objects.order_by(
                "apellido",
                "nombre"
            )
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
        widget=PokemonEquipoCheckboxSelectMultiple()
    )

    cantidad_pokemones = forms.IntegerField(
        label="Cantidad actual de Pokémon",
        required=False,
        disabled=True,
        help_text="Este dato se calcula automáticamente."
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
            "cantidad_medallas": "Cantidad de medallas",
            "clasificado": "¿Clasificó a la liga?",
            "liga": "Liga Pokémon",
            "profesor": "Profesor asignado",
            "gimnasios": "Gimnasios relacionados",
            "imagen": "Enlace de imagen",
            "imagen_archivo": "Fotografía del entrenador",
        }

        widgets = {
            "clasificado": forms.CheckboxInput(),
            "gimnasios": forms.SelectMultiple(),
            "imagen": forms.URLInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["profesor"].queryset = (
            Profesor.objects.order_by(
                "nombre",
                "apellido"
            )
        )

        self.fields["gimnasios"].queryset = (
            Gimnasio.objects.select_related(
                "tipo",
                "region"
            ).order_by(
                "region__nombre",
                "ciudad"
            )
        )

        self.fields["gimnasios"].help_text = (
            "Puedes relacionar al entrenador con varios gimnasios."
        )

        # Identifica los Pokémon que ya están guardados en el PC.
        pokemon_en_pc = BackupEntrenador.objects.values_list(
            "pokemones",
            flat=True
        )

        # Permite Pokémon libres y los que ya pertenecen
        # al entrenador que se está editando.
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

            self.fields["cantidad_pokemones"].initial = (
                disponibles.filter(
                    entrenador=self.instance
                ).count()
            )

            self.fields["pokemones_equipo"].initial = (
                disponibles.filter(
                    entrenador=self.instance
                ).values_list(
                    "pk",
                    flat=True
                )
            )

        else:
            self.fields["cantidad_pokemones"].initial = 0

        equipo = self.fields["pokemones_equipo"]
        equipo.queryset = disponibles

        # Relaciona cada ID con su objeto para generar
        # los atributos HTML que utiliza el selector JavaScript.
        equipo.widget.pokemon_por_id = {
            str(pokemon.pk): pokemon
            for pokemon in disponibles
        }

        equipo.help_text = (
            "Abre el selector para buscar por nombre o número, "
            "filtrar por generación y tipo y elegir tus Pokémon."
        )

        self.aplicar_estilos()

    def clean_documento(self):
        documento = self.cleaned_data["documento"].strip()

        consulta = Entrenador.objects.filter(
            documento=documento
        )

        if self.instance and self.instance.pk:
            consulta = consulta.exclude(
                pk=self.instance.pk
            )

        if consulta.exists():
            raise forms.ValidationError(
                "Ya existe un entrenador registrado con este documento."
            )

        return documento

    def clean_pokemones_equipo(self):
        seleccionados = self.cleaned_data.get(
            "pokemones_equipo"
        )

        if not seleccionados:
            return seleccionados

        ids = list(
            seleccionados.values_list(
                "pk",
                flat=True
            )
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
                    self.guardar_pokemones(entrenador)

            self.save_m2m = guardar_relaciones

        return entrenador

    def guardar_pokemones(self, entrenador):
        seleccionados = self.cleaned_data.get(
            "pokemones_equipo"
        )

        ids_seleccionados = (
            list(
                seleccionados.values_list(
                    "pk",
                    flat=True
                )
            )
            if seleccionados
            else []
        )

        # Comprueba que ningún Pokémon seleccionado
        # haya sido guardado en el PC durante el proceso.
        guardados = BackupEntrenador.objects.filter(
            pokemones__in=ids_seleccionados
        ).exists()

        if guardados:
            raise forms.ValidationError(
                "Uno o varios Pokémon ya están almacenados en el PC."
            )

        # Evita asignar Pokémon que pertenezcan a otro entrenador.
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

        # Libera los Pokémon retirados del equipo activo.
        # Los Pokémon guardados en el PC no se modifican.
        Pokemon.objects.filter(
            entrenador=entrenador
        ).exclude(
            pk__in=ids_seleccionados
        ).exclude(
            respaldos__isnull=False
        ).update(
            entrenador=None
        )

        # Asigna los Pokémon seleccionados que continúan disponibles.
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

        self.fields["tipo"].queryset = (
            Tipo.objects.order_by("nombre")
        )

        self.fields["region"].queryset = (
            Region.objects.order_by("nombre")
        )

        self.aplicar_estilos()


# =====================================================
# BACKUP DE ENTRENADORES
# =====================================================

class BackupEntrenadorForm(
    EstiloFormularioMixin,
    forms.ModelForm
):

    cantidad_pokemones = forms.IntegerField(
        label="Pokémon guardados",
        required=False,
        disabled=True,
        help_text=(
            "La cantidad se obtiene de los Pokémon seleccionados."
        )
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

        self.fields["entrenador"].queryset = (
            Entrenador.objects.order_by(
                "apellido",
                "nombre"
            )
        )

        self.fields["profesor"].queryset = (
            Profesor.objects.order_by(
                "nombre",
                "apellido"
            )
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
            seleccionados.values_list(
                "pk",
                flat=True
            )
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
        # Conserva los datos anteriores antes de modificar el respaldo.
        respaldo_anterior = self.instance
        entrenador_anterior = None
        ids_anteriores = []

        if respaldo_anterior and respaldo_anterior.pk:
            entrenador_anterior = respaldo_anterior.entrenador

            ids_anteriores = list(
                respaldo_anterior.pokemones.values_list(
                    "pk",
                    flat=True
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
                    ids_anteriores
                )

        else:
            guardar_relaciones_original = self.save_m2m

            def guardar_relaciones():
                guardar_relaciones_original()

                with transaction.atomic():
                    self.sincronizar_pokemones(
                        respaldo,
                        entrenador_anterior,
                        ids_anteriores
                    )

            self.save_m2m = guardar_relaciones

        return respaldo

    def sincronizar_pokemones(
        self,
        respaldo,
        entrenador_anterior,
        ids_anteriores
    ):
        seleccionados = self.cleaned_data.get("pokemones")

        ids_nuevos = (
            list(
                seleccionados.values_list(
                    "pk",
                    flat=True
                )
            )
            if seleccionados
            else []
        )

        # Identifica los Pokémon que fueron retirados de esta caja.
        ids_retirados = set(ids_anteriores) - set(ids_nuevos)

        # Devuelve al equipo los Pokémon retirados,
        # siempre que sigan libres y exista un entrenador anterior.
        if entrenador_anterior and ids_retirados:
            Pokemon.objects.filter(
                pk__in=ids_retirados,
                entrenador__isnull=True
            ).update(
                entrenador=entrenador_anterior
            )

        # Los Pokémon almacenados dejan de pertenecer
        # al equipo activo del entrenador.
        if ids_nuevos:
            Pokemon.objects.filter(
                pk__in=ids_nuevos,
                entrenador=respaldo.entrenador
            ).update(
                entrenador=None
            )
