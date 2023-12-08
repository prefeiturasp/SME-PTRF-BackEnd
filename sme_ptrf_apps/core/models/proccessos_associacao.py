from django.db import models
from datetime import date
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

    @classmethod
    def ultimo_processo_do_ano_por_associacao(cls, associacao, ano):
        processos = cls.objects.filter(associacao=associacao, ano=ano).order_by('criado_em')
        return processos.last()

    @property
    def prestacoes_vinculadas(self):
        from sme_ptrf_apps.core.models import PrestacaoConta
        inicio = date(int(self.ano), 1, 1)
        fim = date(int(self.ano), 12, 31)
        pcs = PrestacaoConta.objects.filter(associacao=self.associacao,
                                            periodo__data_inicio_realizacao_despesas__range=[inicio, fim])
        return pcs

    @property
    def e_o_ultimo_processo_do_ano_com_pcs_vinculada(self):
        ultimo_processo = ProcessoAssociacao.ultimo_processo_do_ano_por_associacao(
            associacao=self.associacao, ano=self.ano)
        return (self == ultimo_processo) and self.prestacoes_vinculadas.exists()

auditlog.register(ProcessoAssociacao)
