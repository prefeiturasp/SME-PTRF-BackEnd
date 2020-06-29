from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloIdNome


class DetalheTipoReceita(ModeloIdNome):
    tipo_receita = models.ForeignKey('TipoReceita', on_delete=models.PROTECT, blank=True, null=True)

    class Meta:
        verbose_name = 'Detalhe de tipo de receita'
        verbose_name_plural = 'Detalhes de tipos de receita'

    def __str__(self):
        return self.nome
