import datetime

from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class Periodo(ModeloBase):
    referencia = models.CharField('Referência', max_length=7, blank=True, default="")
    data_inicio_realizacao_despesas = models.DateField('Inicio realização de despesas')
    data_fim_realizacao_despesas = models.DateField('Fim realização de despesas', blank=True, null=True)
    data_prevista_repasse = models.DateField('Data prevista do repasse', blank=True, null=True)
    data_inicio_prestacao_contas = models.DateField('Início prestação de contas', blank=True, null=True)
    data_fim_prestacao_contas = models.DateField('Fim prestação de contas', blank=True, null=True)
    periodo_anterior = models.ForeignKey('Periodo', on_delete=models.PROTECT, related_name='periodo_seguinte',
                                         blank=True, null=True)

    def __str__(self):
        return f"{self.referencia} - {self.data_inicio_realizacao_despesas} a {self.data_fim_realizacao_despesas}"

    @property
    def proximo_periodo(self):
        return self.periodo_seguinte.first() if self.periodo_seguinte.exists() else None

    @property
    def encerrado(self):
        return  self.data_fim_realizacao_despesas and self.data_fim_realizacao_despesas < datetime.date.today()

    @classmethod
    def periodo_atual(cls):
        return cls.objects.latest('data_inicio_realizacao_despesas') if cls.objects.exists() else None

    @classmethod
    def da_data(cls, data):
        periodos_da_data = cls.objects.filter(data_inicio_realizacao_despesas__lte=data).filter(
            data_fim_realizacao_despesas__gte=data)
        return periodos_da_data.first() if periodos_da_data else None

    class Meta:
        verbose_name = "Período"
        verbose_name_plural = "Períodos"
