from rest_framework import serializers
from sme_ptrf_apps.core.models import SolicitacaoAcertoLancamento


class AcoesStatusSolicitacaoAcertoLancamentoValidateSerializer(serializers.Serializer): # noqa
    uuids_solicitacoes_acertos_lancamentos = serializers.ListField(required=True)

    def validate_uuids_solicitacoes_acertos_lancamentos(self, value): # noqa
        if len(value) == 0:
            raise serializers.ValidationError(f"É necessário informar ao menos um uuid de solicitação de acerto.")

        for uuid in value:
            try:
                SolicitacaoAcertoLancamento.by_uuid(uuid)
            except SolicitacaoAcertoLancamento.DoesNotExist: # noqa
                raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid {uuid}.")

        return value



