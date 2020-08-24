from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class ProcessoAssociacao(ModeloBase):
    associacao = models.ForeignKey('Associacao', on_delete=models.PROTECT,
                                   related_name='processos',
                                   blank=True, null=True)

    numero_processo = models.CharField('Nº processo prestação de conta', max_length=100, default='', blank=True)

    ano = models.CharField('Ano', max_length=4, blank=True, default="")

    class Meta:
        verbose_name = "Processo de prestação de contas"
        verbose_name_plural = "Processos de prestação de contas"

    def __str__(self):
        return f"<Processo: {self.numero_processo}, Ano: {self.ano}>"
