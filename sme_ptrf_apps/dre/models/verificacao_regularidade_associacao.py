from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class VerificacaoRegularidadeAssociacao(ModeloBase):
    history = AuditlogHistoryField()
    associacao = models.ForeignKey('core.Associacao', on_delete=models.PROTECT, related_name='verificacoes_regularidade')
    grupo_verificacao = models.ForeignKey('GrupoVerificacaoRegularidade', on_delete=models.PROTECT,
                                          related_name="grupos_de_verificacao")
    lista_verificacao = models.ForeignKey('ListaVerificacaoRegularidade', on_delete=models.PROTECT,
                                          related_name="listas_de_verificacao")
    item_verificacao = models.ForeignKey('ItemVerificacaoRegularidade', on_delete=models.PROTECT,
                                         related_name="itens_de_verificacao")
    regular = models.BooleanField('Regular?', default=True)

    def __str__(self):
        return f'{self.item_verificacao.descricao if self.item_verificacao else ""} - {"Regular" if self.regular else "Irregular"}'

    class Meta:
        verbose_name = 'Verificação de regularidade de associação'
        verbose_name_plural = 'Verificações de regularidade de associações'


auditlog.register(VerificacaoRegularidadeAssociacao)
