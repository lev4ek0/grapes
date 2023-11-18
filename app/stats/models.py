from django.db import models


class Illness(models.Model):
    name = models.CharField(max_length=32, verbose_name="Наименование болезни")
