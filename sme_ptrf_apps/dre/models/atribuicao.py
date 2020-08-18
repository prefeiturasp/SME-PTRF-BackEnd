from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class Atribuicao(ModeloBase):
    unidade = models.ForeignKey('core.Unidade', on_delete=models.PROTECT, related_name='atribuicoes',
                                blank=True, null=True)
    tecnico = models.ForeignKey('TecnicoDre', on_delete=models.PROTECT, related_name='atribuicoes',
                                blank=True, null=True)
    periodo = models.ForeignKey('core.Periodo', on_delete=models.PROTECT, related_name='atribuicoes',
                                blank=True, null=True)

    class Meta:
        verbose_name = 'Atribuição'
        verbose_name_plural = 'Atribuições'
