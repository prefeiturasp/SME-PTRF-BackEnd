from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class Composicao(ModeloBase):
    history = AuditlogHistoryField()
    associacao = models.ForeignKey('core.Associacao', verbose_name="Associação", on_delete=models.CASCADE, related_name='composicoes_da_associacao')
    mandato = models.ForeignKey('Mandato', on_delete=models.CASCADE, verbose_name="Mandato", related_name='composicoes_do_mandato')
    data_inicial = models.DateField(verbose_name='Data de início da composição', blank=True, null=True)
    data_final = models.DateField(verbose_name='Data de término da composição', blank=True, null=True)

    class Meta:
        verbose_name = 'Composição'
        verbose_name_plural = 'Composições'

    def __str__(self):
        data_inicial = self.data_inicial.strftime("%d/%m/%Y") if self.data_inicial else ""
        data_final = self.data_final.strftime("%d/%m/%Y") if self.data_final else ""
        associacao_nome = self.associacao.nome if self.associacao and self.associacao.nome else ""
        return f"{associacao_nome} Período {data_inicial} até {data_final}"

    def eh_primeira_composicao(self):
        composicoes_da_associacao = Composicao.objects.filter(
            associacao=self.associacao,
            mandato=self.mandato
        ).all().order_by('-id')

        primeira_composicao = composicoes_da_associacao.last()

        return self == primeira_composicao

    def eh_ultima_composicao(self):
        composicoes_da_associacao = Composicao.objects.filter(
            associacao=self.associacao,
            mandato=self.mandato
        ).all().order_by('-id')

        ultima_composicao = composicoes_da_associacao.first()

        return self == ultima_composicao


auditlog.register(Composicao)
