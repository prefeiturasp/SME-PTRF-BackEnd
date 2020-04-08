from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class Periodo(ModeloBase):
    data_inicio_realizacao_despesas = models.DateField('Inicio realização de despesas')
    data_fim_realizacao_despesas = models.DateField('Fim realização de despesas')
    data_prevista_repasse = models.DateField('Data prevista do repasse', blank=True, null=True)
    data_inicio_prestacao_contas = models.DateField('Início prestação de contas', blank=True, null=True)
    data_fim_prestacao_contas = models.DateField('Fim prestação de contas', blank=True, null=True)

    def __str__(self):
        return f"{self.data_inicio_realizacao_despesas} a {self.data_fim_realizacao_despesas}"

    class Meta:
        verbose_name = "Período"
        verbose_name_plural = "Períodos"
