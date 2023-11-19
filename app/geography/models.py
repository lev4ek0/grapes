from django.db import models


class Region(models.Model):
    name = models.CharField(max_length=127, verbose_name="Название", unique=True)

    coords = models.JSONField(
        blank=True, null=True, verbose_name="Координаты", help_text="В формате GeoJSON"
    )

    lat = models.FloatField(verbose_name="Широта")
    lon = models.FloatField(verbose_name="Долгота")
    code = models.CharField(max_length=7, verbose_name="Код ISO 3166-2")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Регион"
        verbose_name_plural = "Регионы"
        ordering = ("name",)
