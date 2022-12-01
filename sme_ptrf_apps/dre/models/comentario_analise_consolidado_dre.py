from django.db import models
from django.db import transaction
from datetime import date

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_ptrf_apps.core.models_abstracts import ModeloBase


class ComentarioAnaliseConsolidadoDRE(ModeloBase):
    history = AuditlogHistoryField()

    consolidado_dre = models.ForeignKey('ConsolidadoDRE', on_delete=models.CASCADE, related_name='comentarios_de_analise_do_consolidado_dre')

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
        verbose_name = "Comentário de análise do consolidado DRE"
        verbose_name_plural = "Comentários de análises dos consolidados DRE"


auditlog.register(ComentarioAnaliseConsolidadoDRE)
