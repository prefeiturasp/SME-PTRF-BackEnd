from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class ProcessoAssociacao(ModeloBase):
    history = AuditlogHistoryField()
    associacao = models.ForeignKey('Associacao', on_delete=models.PROTECT,
                                   related_name='processos',
                                   blank=True, null=True)

    numero_processo = models.CharField('Nº processo prestação de conta', max_length=100, default='', blank=True)

    ano = models.CharField('Ano', max_length=4, blank=True, default="")

    class Meta:
        verbose_name = "Processo de prestação de contas"
        verbose_name_plural = "07.1) Processos de prestação de contas"

    def __str__(self):
        return f"<Processo: {self.numero_processo}, Ano: {self.ano}>"

    @classmethod
    def by_associacao_periodo(cls, associacao, periodo):
        ano = periodo.referencia[0:4]
        processos = cls.objects.filter(associacao=associacao, ano=ano)
        return processos.first().numero_processo if processos.exists() else ""


auditlog.register(ProcessoAssociacao)
