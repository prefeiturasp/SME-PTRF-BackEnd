from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase


class DemonstrativoFinanceiro(ModeloBase):

    class Meta:
        verbose_name = 'Demonstrativo Financeiro'
        verbose_name_plural = 'Demonstrativos Financeiros'

    def __str__(self):
        return f"Criado em {self.criado_em}"
