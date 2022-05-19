from django.db import models
from django.db import transaction
from datetime import date

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class ComentarioAnalisePrestacao(ModeloBase):
    prestacao_conta = models.ForeignKey('PrestacaoConta', on_delete=models.CASCADE,
                                        related_name='comentarios_de_analise_da_prestacao')

    ordem = models.PositiveSmallIntegerField('ordem')

    comentario = models.TextField('Comentário', max_length=600, blank=True, null=True)

    notificado = models.BooleanField("Foi notificado?", default=False)

    notificado_em = models.DateField('Notificado em', blank=True, null=True)

    def __str__(self):
        return f"{self.ordem} - {self.comentario}"

    @classmethod
    @transaction.atomic
    def reordenar_comentarios(cls, novas_ordens_comentarios):
        for nova_ordem in novas_ordens_comentarios:
            comentario = cls.by_uuid(nova_ordem['uuid'])
            comentario.ordem = nova_ordem['ordem']
            comentario.save()

    def set_comentario_notificado(self):
        self.notificado = True
        self.notificado_em = date.today()
        self.save()

    class Meta:
        verbose_name = "Observação de análise de prestação de contas"
        verbose_name_plural = "09.9) Observações de análise de prestações de contas"
