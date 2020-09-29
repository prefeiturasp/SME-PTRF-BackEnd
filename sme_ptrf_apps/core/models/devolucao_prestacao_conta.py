from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase

class DevolucaoPrestacaoConta(ModeloBase):
    prestacao_conta = models.ForeignKey('PrestacaoConta', on_delete=models.CASCADE,
                                        related_name='devolucoes_da_prestacao')

    data = models.DateField('data da devolução')

    data_limite_ue = models.DateField('data limite para a ue')


    def __str__(self):
        return f"{self.data} - {self.data_limite_ue}"

    class Meta:
        verbose_name = "Devolução de prestação de contas"
        verbose_name_plural = "Devoluções de prestações de contas"
