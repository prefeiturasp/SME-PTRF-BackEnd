from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class ComentarioAnalisePrestacao(ModeloBase):
    prestacao_conta = models.ForeignKey('PrestacaoConta', on_delete=models.CASCADE,
                                        related_name='comentarios_de_analise_da_prestacao')

    ordem = models.PositiveSmallIntegerField('ordem')

    comentario = models.TextField('Comentário', max_length=600, blank=True, null=True)

    def __str__(self):
        return f"{self.ordem} - {self.comentario}"

    class Meta:
        verbose_name = "Observação de análise de prestação de contas"
        verbose_name_plural = "09.9) Observações de análise de prestações de contas"
