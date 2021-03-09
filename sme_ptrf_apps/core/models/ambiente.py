from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome


class Ambiente(ModeloIdNome):
    prefixo = models.CharField(max_length=50, blank=True, null=True)
    nome = models.CharField(max_length=150)

    class Meta:
        verbose_name = "Ambiente"
        verbose_name_plural = "14.0) Ambientes"
        unique_together = ['prefixo', 'nome', ]
