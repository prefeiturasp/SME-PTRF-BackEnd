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
    acao = models.ForeignKey('Acao', on_delete=models.PROTECT, blank=True,
                             null=True, related_name='associacoes_da_acao')
    status = models.CharField(
        'status',
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_ATIVA
    )

    def saldo_atual(self):
        from ..services.acoes_associacoes_service import obter_saldos_periodo_atual

        saldos = obter_saldos_periodo_atual(self)
        return saldos

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
    def filter_by_recurso(cls, queryset, recurso):
        return queryset.filter(acao__recurso=recurso)

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
    def is_valid_data(cls, instance_uuid):
        try:
            obj = cls.objects.get(uuid=instance_uuid)
        except cls.DoesNotExist:
            return False, 'Objeto não encontrado.'
        except Exception:
            return False, 'Ocorreu um erro ao validar os dados.'

        # Lista de relacionamentos a serem verificados que impedem a exclusão
        campos_vinculados = [
            'valores_reprogramados_da_acao',
            'receita_prevista_paa_da_associacao',
            'prioridade_paa_da_associacao',
            'rateios_da_associacao',
            'repasses_da_associacao',
            'receitas_da_associacao',
            'fechamentos_da_acao',
        ]

        # Verificar se algum campo possui dados vinculados
        for campo in campos_vinculados:
            if hasattr(obj, campo) and getattr(obj, campo).exists():
                return False, 'Essa operação não pode ser realizada. Há dados vinculados a essa ação da referida Associação.'

        return True, ''

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

    def receitas_previstas_paa(self):
        return self.receitaprevistapaa_set.all()

    @staticmethod
    def filter_by_recurso(queryset, recurso):
        return queryset.filter(acao__recurso=recurso)

    class Meta:
        verbose_name = "Ação de Associação"
        verbose_name_plural = "07.3) Ações de Associações"


auditlog.register(AcaoAssociacao)
