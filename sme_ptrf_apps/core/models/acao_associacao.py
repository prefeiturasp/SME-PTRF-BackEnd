import uuid

from django.db import models
from django.db.models.deletion import ProtectedError

from sme_ptrf_apps.core.models_abstracts import ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class AcaoAssociacao(ModeloBase):
    history = AuditlogHistoryField()
    # Status Choice
    STATUS_ATIVA = 'ATIVA'
    STATUS_INATIVA = 'INATIVA'

    STATUS_NOMES = {
        STATUS_ATIVA: 'Ativa',
        STATUS_INATIVA: 'Inativa',
    }

    STATUS_CHOICES = (
        (STATUS_ATIVA, STATUS_NOMES[STATUS_ATIVA]),
        (STATUS_INATIVA, STATUS_NOMES[STATUS_INATIVA]),
    )

    associacao = models.ForeignKey('Associacao', on_delete=models.CASCADE, related_name='acoes', blank=True, null=True)
    acao = models.ForeignKey('Acao', on_delete=models.PROTECT, blank=True, null=True, related_name='associacoes_da_acao')
    status = models.CharField(
        'status',
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_ATIVA
    )

    def __str__(self):
        associacao = self.associacao.nome if self.associacao else 'ACM indefinida'
        acao = self.acao.nome if self.acao else 'Ação indefinida'
        status = AcaoAssociacao.STATUS_NOMES[self.status]
        return f"{associacao} - Ação {acao} - {status}"

    @classmethod
    def get_valores(cls, user=None, associacao_uuid=None):
        query = cls.objects.filter(status=cls.STATUS_ATIVA)
        if user:
            query = query.filter(associacao__uuid=associacao_uuid)
        return query.all()

    @classmethod
    def excluir_em_lote(cls, lista_uuids):
        erros = []
        for uuid_str in lista_uuids:
            try:
                obj = cls.objects.get(uuid=uuid.UUID(uuid_str))
                obj.delete()
            except cls.DoesNotExist:
                erros.append(
                    {
                        'erro': 'Objeto não encontrado.',
                        'mensagem': f'O objeto acao_associacao para o uuid {uuid_str} não foi encontrado na base.'
                    }
                )
            except ProtectedError:
                erros.append(
                    {
                        'erro': 'ProtectedError',
                        'mensagem': (f'O vínculo de ação e associação de uuid {uuid_str} não pode ser excluido '
                                     'porque está sendo usado na aplicação.')
                    }
                )
        return erros

    @classmethod
    def incluir_em_lote(cls, acao, associacoes):
        erros = []
        for associacao in associacoes:
            cls.objects.create(
                acao=acao,
                associacao=associacao,
                status="ATIVA"
            )
        return erros

    class Meta:
        verbose_name = "Ação de Associação"
        verbose_name_plural = "07.2) Ações de Associações"


auditlog.register(AcaoAssociacao)
