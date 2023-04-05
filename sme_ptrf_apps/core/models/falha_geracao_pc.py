from django.db import models
from sme_ptrf_apps.core.models_abstracts import ModeloBase
from django.contrib.auth import get_user_model
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class FalhaGeracaoPc(ModeloBase):
    history = AuditlogHistoryField()

    ultimo_usuario = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                                       related_name='falhas_geracao_pc_do_usuario', default='',
                                       blank=True, null=True, verbose_name="Usuário")

    associacao = models.ForeignKey('Associacao', on_delete=models.CASCADE,
                                   related_name='falhas_geracao_pc_da_associacao',
                                   blank=True, null=True, verbose_name="Associação")

    periodo = models.ForeignKey('Periodo', on_delete=models.CASCADE, related_name='falhas_geracao_pc_do_periodo',
                                null=True, blank=True, verbose_name="Período")

    data_hora_ultima_ocorrencia = models.DateTimeField("Data e hora da última ocorrência", null=True, blank=True)

    qtd_ocorrencias_sucessivas = models.PositiveSmallIntegerField(
        'Quantidade de ocorrências sucessivas',
        default=0,
        null=True,
        blank=True
    )

    resolvido = models.BooleanField("Resolvido?", default=False)

    class Meta:
        verbose_name = "Falha na Geracao de PC"
        verbose_name_plural = "19.0) Falhas na Geracao de PCs"

    def __str__(self):
        periodo_referencia = self.periodo.referencia if self.periodo and self.periodo.referencia else ''
        texto_retorno = ''
        if periodo_referencia:
            texto_retorno = f"Período {periodo_referencia}"
        return f"{texto_retorno}"


auditlog.register(FalhaGeracaoPc)
