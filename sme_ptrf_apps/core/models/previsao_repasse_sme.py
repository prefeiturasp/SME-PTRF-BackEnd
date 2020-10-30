from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase

class PrevisaoRepasseSme(ModeloBase):
    periodo = models.ForeignKey('Periodo', on_delete=models.PROTECT, related_name='previsoes_repasse_sme')

    associacao = models.ForeignKey('Associacao', on_delete=models.PROTECT,
                                   related_name='previsoes_de_repasse_sme_para_a_associacao',
                                   blank=True, null=True)

    valor = models.DecimalField('Valor', max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.periodo.referencia} - {self.associacao} - {self.valor}"


    class Meta:
        verbose_name = "Previsão repasse SME"
        verbose_name_plural = "12.0) Previsões de repasse"
        unique_together = ['associacao', 'periodo']
