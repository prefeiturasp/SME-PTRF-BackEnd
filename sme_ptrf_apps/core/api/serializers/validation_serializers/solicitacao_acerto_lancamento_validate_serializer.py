from rest_framework import serializers
from sme_ptrf_apps.core.models import SolicitacaoAcertoLancamento


class AcoesStatusSolicitacaoAcertoLancamentoValidateSerializer(serializers.Serializer): # noqa
    uuids_solicitacoes_acertos_lancamentos = serializers.ListField(required=True)
    justificativa = serializers.CharField(required=False, allow_blank=False)

    def validate_uuids_solicitacoes_acertos_lancamentos(self, value): # noqa
        if len(value) == 0:
            raise serializers.ValidationError(f"É necessário informar ao menos um uuid de solicitação de acerto.")

        for uuid in value:
            try:
                SolicitacaoAcertoLancamento.by_uuid(uuid)
            except SolicitacaoAcertoLancamento.DoesNotExist: # noqa
                raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid {uuid}.")

        return value


class GravarEsclarecimentoAcertoLancamentoValidateSerializer(serializers.Serializer): # noqa
    uuid_solicitacao_acerto = serializers.CharField(required=True, allow_blank=False)
    esclarecimento = serializers.CharField(required=True, allow_blank=False)

    def validate_uuid_solicitacao_acerto(self, value): # noqa
        try:
            SolicitacaoAcertoLancamento.by_uuid(value)
        except SolicitacaoAcertoLancamento.DoesNotExist:  # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid {value}.")

