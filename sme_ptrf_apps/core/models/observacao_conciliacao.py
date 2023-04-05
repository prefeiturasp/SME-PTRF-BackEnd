from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class ObservacaoConciliacao(ModeloBase):
    history = AuditlogHistoryField()
    periodo = models.ForeignKey('Periodo', on_delete=models.PROTECT, related_name='observacoes_conciliacao_do_periodo')

    associacao = models.ForeignKey('Associacao', on_delete=models.PROTECT,
                                   related_name='observacoes_conciliacao_da_associacao',
                                   blank=True, null=True)

    conta_associacao = models.ForeignKey('ContaAssociacao', on_delete=models.PROTECT,
                                         related_name='observacoes_conciliacao_da_conta', blank=True, null=True)

    texto = models.TextField('Observações da conciliação', max_length=600, blank=True, null=True)

    justificativa_original = models.TextField('Observações da conciliação original', max_length=600, blank=True,
                                              null=True)

    data_extrato = models.DateField('data do extrato', blank=True, null=True)

    saldo_extrato = models.DecimalField('saldo do extrato', max_digits=12, decimal_places=2, default=0)

    comprovante_extrato = models.FileField(blank=True, null=True)

    data_atualizacao_comprovante_extrato = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'informação de conciliação'
        verbose_name_plural = '09.5) Informações de conciliação'

    def __str__(self):
        return f'Conciliação: {self.periodo.referencia}'

    @classmethod
    def criar_atualizar_extrato_bancario(cls, periodo, conta_associacao, data_extrato, saldo_extrato,
                                         comprovante_extrato, data_atualizacao_comprovante_extrato):

        observacao = cls.objects.filter(periodo=periodo, conta_associacao=conta_associacao).first()

        if observacao:
            if data_extrato or saldo_extrato or comprovante_extrato or data_atualizacao_comprovante_extrato:
                observacao.data_extrato = data_extrato
                observacao.saldo_extrato = saldo_extrato

                if data_atualizacao_comprovante_extrato and comprovante_extrato:
                    observacao.comprovante_extrato = comprovante_extrato
                    observacao.data_atualizacao_comprovante_extrato = data_atualizacao_comprovante_extrato

                if not data_atualizacao_comprovante_extrato:
                    observacao.comprovante_extrato = ''

                observacao.save()
        else:
            if data_extrato or saldo_extrato or comprovante_extrato or data_atualizacao_comprovante_extrato:
                cls.objects.create(
                    periodo=periodo,
                    conta_associacao=conta_associacao,
                    associacao=conta_associacao.associacao,
                    data_extrato=data_extrato,
                    saldo_extrato=saldo_extrato,
                    comprovante_extrato=comprovante_extrato,
                    data_atualizacao_comprovante_extrato=data_atualizacao_comprovante_extrato,
                )

    @classmethod
    def criar_atualizar_justificativa(cls, periodo, conta_associacao, texto_observacao):
        observacao = cls.objects.filter(periodo=periodo, conta_associacao=conta_associacao).first()

        if observacao:
            if texto_observacao is not None:
                observacao.texto = texto_observacao
                observacao.save()
        else:
            if texto_observacao is not None:
                cls.objects.create(
                    periodo=periodo,
                    conta_associacao=conta_associacao,
                    associacao=conta_associacao.associacao,
                    texto=texto_observacao,
                    data_extrato=None,
                    comprovante_extrato=None,
                    data_atualizacao_comprovante_extrato=None,
                )


auditlog.register(ObservacaoConciliacao)
