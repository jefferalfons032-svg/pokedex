from django.db import models


# =====================================================
# OPCIONES GENERALES
# =====================================================

class Opciones:
    LIGAS = [
        ("KANTO", "Liga Pokémon de Kanto"),
        ("JOHTO", "Liga Pokémon de Johto"),
        ("HOENN", "Liga Pokémon de Hoenn"),
        ("SINNOH", "Liga Pokémon de Sinnoh"),
        ("UNOVA", "Liga Pokémon de Unova"),
        ("KALOS", "Liga Pokémon de Kalos"),
        ("ALOLA", "Liga Pokémon de Alola"),
        ("GALAR", "Liga Pokémon de Galar"),
    ]


# =====================================================
# TIPOS DE POKÉMON
# =====================================================

class Tipo(models.Model):
    nombre = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Nombre del tipo"
    )

    color = models.CharField(
        max_length=20,
        default="#777777",
        verbose_name="Color identificador"
    )

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Tipo"
        verbose_name_plural = "Tipos"
        ordering = ["nombre"]


# =====================================================
# HABILIDADES
# =====================================================

class Habilidad(models.Model):
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre de la habilidad"
    )

    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Habilidad"
        verbose_name_plural = "Habilidades"
        ordering = ["nombre"]


# =====================================================
# PROFESORES POKÉMON
# =====================================================

class Profesor(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100)
    pueblo = models.CharField(max_length=100)

    imagen_archivo = models.ImageField(
        upload_to="profesores/",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        verbose_name = "Profesor"
        verbose_name_plural = "Profesores"
        ordering = ["nombre", "apellido"]


# =====================================================
# REGIONES
# =====================================================

class Region(models.Model):
    nombre = models.CharField(
        max_length=100,
        unique=True
    )

    descripcion = models.TextField(blank=True)

    imagen = models.URLField(
        blank=True,
        verbose_name="URL de la imagen"
    )

    imagen_archivo = models.ImageField(
        upload_to="regiones/",
        blank=True,
        null=True
    )

    @property
    def url_imagen(self):
        if self.imagen_archivo:
            try:
                return self.imagen_archivo.url
            except (ValueError, OSError):
                pass

        return self.imagen or ""

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Región"
        verbose_name_plural = "Regiones"
        ordering = ["nombre"]


# =====================================================
# ENTRENADORES
# =====================================================

class Entrenador(models.Model):
    documento = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Documento de identidad"
    )

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    pueblo = models.CharField(max_length=100)

    cantidad_medallas = models.PositiveIntegerField(
        default=0,
        verbose_name="Cantidad de medallas"
    )

    clasificado = models.BooleanField(
        default=False,
        verbose_name="¿Está clasificado?"
    )

    liga = models.CharField(
        max_length=20,
        choices=Opciones.LIGAS,
        default="KANTO"
    )

    profesor = models.ForeignKey(
        Profesor,
        on_delete=models.PROTECT,
        related_name="entrenadores"
    )

    gimnasios = models.ManyToManyField(
        "Gimnasio",
        related_name="entrenadores",
        blank=True
    )

    imagen_archivo = models.ImageField(
        upload_to="entrenadores/",
        blank=True,
        null=True
    )

    imagen = models.URLField(
        blank=True,
        help_text="Dirección web alternativa de la imagen del entrenador."
    )

    fecha_registro = models.DateTimeField(auto_now_add=True)

    @property
    def url_imagen(self):
        if self.imagen_archivo:
            try:
                return self.imagen_archivo.url
            except (ValueError, OSError):
                pass

        return self.imagen or ""

    @property
    def cantidad_pokemones(self):
        return self.pokemones.count()

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        verbose_name = "Entrenador"
        verbose_name_plural = "Entrenadores"
        ordering = ["apellido", "nombre"]


# =====================================================
# GIMNASIOS
# =====================================================

class Gimnasio(models.Model):
    lider = models.CharField(
        max_length=150,
        verbose_name="Líder de gimnasio"
    )

    tipo = models.ForeignKey(
        Tipo,
        on_delete=models.PROTECT,
        related_name="gimnasios",
        verbose_name="Tipo de elemento"
    )

    medalla = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)

    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="gimnasios"
    )

    imagen_archivo = models.ImageField(
        upload_to="gimnasios/",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Gimnasio de {self.ciudad} - {self.lider}"

    class Meta:
        verbose_name = "Gimnasio"
        verbose_name_plural = "Gimnasios"
        ordering = ["region", "ciudad"]


# =====================================================
# POKÉMON
# =====================================================

class Pokemon(models.Model):
    numero = models.PositiveIntegerField(
        unique=True,
        verbose_name="Número de Pokédex"
    )

    nombre = models.CharField(
        max_length=100,
        unique=True
    )

    imagen = models.URLField(
        blank=True,
        verbose_name="URL de imagen"
    )

    imagen_oficial = models.URLField(
        blank=True,
        verbose_name="URL de imagen oficial"
    )

    imagen_archivo = models.ImageField(
        upload_to="pokemon/",
        blank=True,
        null=True
    )

    altura = models.PositiveIntegerField(
        default=0,
        help_text="Altura en decímetros."
    )

    peso = models.PositiveIntegerField(
        default=0,
        help_text="Peso en hectogramos."
    )

    experiencia_base = models.PositiveIntegerField(default=0)

    tipos = models.ManyToManyField(
        Tipo,
        related_name="pokemones"
    )

    habilidades = models.ManyToManyField(
        Habilidad,
        related_name="pokemones"
    )

    entrenador = models.ForeignKey(
        Entrenador,
        on_delete=models.SET_NULL,
        related_name="pokemones",
        null=True,
        blank=True
    )

    evoluciones = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="evoluciona_desde"
    )

    hp = models.PositiveIntegerField(default=0)
    ataque = models.PositiveIntegerField(default=0)
    defensa = models.PositiveIntegerField(default=0)
    ataque_especial = models.PositiveIntegerField(default=0)
    defensa_especial = models.PositiveIntegerField(default=0)
    velocidad = models.PositiveIntegerField(default=0)

    es_legendario = models.BooleanField(
        default=False,
        verbose_name="¿Es legendario?"
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    @property
    def url_imagen(self):
        if self.imagen_archivo:
            try:
                return self.imagen_archivo.url
            except (ValueError, OSError):
                pass

        if self.imagen_oficial:
            return self.imagen_oficial

        return self.imagen or ""

    @property
    def total_estadisticas(self):
        return (
            self.hp
            + self.ataque
            + self.defensa
            + self.ataque_especial
            + self.defensa_especial
            + self.velocidad
        )

    def __str__(self):
        return f"#{self.numero} - {self.nombre.capitalize()}"

    class Meta:
        verbose_name = "Pokémon"
        verbose_name_plural = "Pokémon"
        ordering = ["numero"]


# =====================================================
# BACKUP / CAJAS DEL PC
# =====================================================

class BackupEntrenador(models.Model):
    nombre = models.CharField(
        max_length=150,
        verbose_name="Nombre del backup"
    )

    entrenador = models.ForeignKey(
        Entrenador,
        on_delete=models.CASCADE,
        related_name="respaldos"
    )

    profesor = models.ForeignKey(
        Profesor,
        on_delete=models.PROTECT,
        related_name="respaldos"
    )

    pokemones = models.ManyToManyField(
        Pokemon,
        blank=True,
        related_name="respaldos"
    )

    items = models.TextField(
        blank=True,
        help_text="Escribe los objetos almacenados en este respaldo."
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    @property
    def cantidad_pokemones(self):
        return self.pokemones.count()

    def __str__(self):
        return f"{self.nombre} - {self.entrenador}"

    class Meta:
        verbose_name = "Backup de entrenador"
        verbose_name_plural = "Backups de entrenadores"
        ordering = ["-fecha_creacion"]
