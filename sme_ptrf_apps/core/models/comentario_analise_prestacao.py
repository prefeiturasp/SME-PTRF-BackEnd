from django.db import models
from django.db import transaction
from datetime import date

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class ComentarioAnalisePrestacao(ModeloBase):
    history = AuditlogHistoryField()

    prestacao_conta = models.ForeignKey('PrestacaoConta', on_delete=models.CASCADE, related_name='comentarios_de_analise_da_prestacao',
                                        blank=True, null=True)

    periodo = models.ForeignKey('Periodo', on_delete=models.PROTECT, related_name='comentarios_de_analise_do_periodo',
                                 blank=True, null=True)

    associacao = models.ForeignKey('Associacao', on_delete=models.PROTECT, related_name='comentarios_de_analise_da_associacao',
                                   blank=True, null=True)

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

        if not self.notificado:
            self.notificado = True
            self.notificado_em = date.today()
            self.save()

    class Meta:
        verbose_name = "Observação de análise de prestação de contas"
        verbose_name_plural = "09.10) Observações de análise de prestações de contas"


auditlog.register(ComentarioAnalisePrestacao)
