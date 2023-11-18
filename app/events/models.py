from django.db import models

from geography.models import Region


class Event(models.Model):
    date = models.CharField(max_length=10, verbose_name="Дата")
    temp = models.CharField(max_length=10, verbose_name="Температура")
    humidity = models.CharField(max_length=10, verbose_name="Влажность")
    notes = models.CharField(max_length=127, verbose_name="Заметки")
    region = models.ForeignKey(
        to=Region,
        on_delete=models.PROTECT,
        verbose_name="Регион",
        related_name="events",
    )

    class Meta:
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"
        ordering = ("-date",)
