import logging

from rest_framework import serializers
from sme_ptrf_apps.core.models import Associacao, Periodo, PrestacaoConta

logger = logging.getLogger(__name__)

class PrestacoesContasConcluirValidateSerializer(serializers.Serializer): # noqa
    associacao_uuid = serializers.UUIDField(required=True, allow_null=False)
    periodo_uuid = serializers.UUIDField(required=True, allow_null=False)
    justificativa_acertos_pendentes = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    def validate_associacao_uuid(self, value): # noqa
        try:
            Associacao.by_uuid(value)
        except Associacao.DoesNotExist: # noqa
            logger.error(f'Associação com uuid {value} não encontrada.')
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid de Associação {value}.")

        return value


    def validate_periodo_uuid(self, value): # noqa
        try:
            Periodo.by_uuid(value)
        except Periodo.DoesNotExist: # noqa
            logger.error(f'Período com uuid {value} não encontrado.')
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid de Período {value}.")

        return value

    def validate(self, attrs):
        from sme_ptrf_apps.core.services.periodo_services import (
            pc_tem_solicitacoes_de_acerto_pendentes,
        )

        associacao = Associacao.by_uuid(attrs['associacao_uuid'])
        periodo = Periodo.by_uuid(attrs['periodo_uuid'])

        prestacao_conta = PrestacaoConta.objects.filter(
            associacao=associacao,
            periodo=periodo
        ).first()

        if prestacao_conta:
            pc_nao_pode_ser_concluida = prestacao_conta.status not in (
                PrestacaoConta.STATUS_NAO_APRESENTADA,
                PrestacaoConta.STATUS_DEVOLVIDA
            )
            if pc_nao_pode_ser_concluida:
                raise serializers.ValidationError(
                    "A Prestação de Contas só pode ser concluída se estiver com status 'Não Apresentada' ou 'Devolvida'."
                )

            if pc_tem_solicitacoes_de_acerto_pendentes(prestacao_conta):
                raise serializers.ValidationError(
                    "A Prestação de Contas possui solicitações de acerto pendentes e não pode ser concluída."
                )

        attrs['associacao'] = associacao
        attrs['periodo'] = periodo
        attrs['prestacao_conta'] = prestacao_conta
        return attrs
