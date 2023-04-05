from rest_framework import serializers
from sme_ptrf_apps.core.models import SolicitacaoAcertoDocumento, AnaliseDocumentoPrestacaoConta
from sme_ptrf_apps.receitas.models import Receita
from sme_ptrf_apps.despesas.models import Despesa

class AcoesStatusSolicitacaoAcertoDocumentoValidateSerializer(serializers.Serializer): # noqa
    uuids_solicitacoes_acertos_documentos = serializers.ListField(required=True)
    justificativa = serializers.CharField(required=False, allow_blank=False)

    def validate_uuids_solicitacoes_acertos_documentos(self, value): # noqa
        if len(value) == 0:
            raise serializers.ValidationError(f"É necessário informar ao menos um uuid de solicitação de acerto.")

        for uuid in value:
            try:
                SolicitacaoAcertoDocumento.by_uuid(uuid)
            except SolicitacaoAcertoDocumento.DoesNotExist: # noqa
                raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid {uuid}.")

        return value


class GravarEsclarecimentoAcertoDocumentoValidateSerializer(serializers.Serializer): # noqa
    uuid_solicitacao_acerto = serializers.CharField(required=True, allow_blank=False)
    esclarecimento = serializers.CharField(required=True, allow_blank=False)

    def validate_uuid_solicitacao_acerto(self, value): # noqa
        try:
            SolicitacaoAcertoDocumento.by_uuid(value)
        except SolicitacaoAcertoDocumento.DoesNotExist:  # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid {value}.")


class GravarCreditoIncluidoDocumentoValidateSerializer(serializers.Serializer): # noqa
    uuid_solicitacao_acerto = serializers.CharField(required=True, allow_blank=False)
    uuid_credito_incluido = serializers.CharField(required=True, allow_blank=False)

    def validate_uuid_solicitacao_acerto(self, value): # noqa
        try:
            SolicitacaoAcertoDocumento.by_uuid(value)
        except SolicitacaoAcertoDocumento.DoesNotExist:  # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid {value}.")

    def validate_uuid_credito_incluido(self, value): # noqa
        try:
            Receita.by_uuid(value)
        except Receita.DoesNotExist:  # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid {value}.")


class GravarGastoIncluidoDocumentoValidateSerializer(serializers.Serializer): # noqa
    uuid_solicitacao_acerto = serializers.CharField(required=True, allow_blank=False)
    uuid_gasto_incluido = serializers.CharField(required=True, allow_blank=False)

    def validate_uuid_solicitacao_acerto(self, value): # noqa
        try:
            SolicitacaoAcertoDocumento.by_uuid(value)
        except SolicitacaoAcertoDocumento.DoesNotExist:  # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid {value}.")

    def validate_uuid_gasto_incluido(self, value): # noqa
        try:
            Despesa.by_uuid(value)
        except Despesa.DoesNotExist:  # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid {value}.")


class EditarInformacaoConciliacaoValidateSerializer(serializers.Serializer): # noqa
    uuid_analise_documento = serializers.CharField(required=True, allow_blank=False)
    justificativa_conciliacao = serializers.CharField(required=True, allow_blank=True)

    def validate_uuid_analise_documento(self, value): # noqa
        try:
            AnaliseDocumentoPrestacaoConta.by_uuid(value)
        except AnaliseDocumentoPrestacaoConta.DoesNotExist:
            raise serializers.ValidationError(f"Não foi encontrado um objeto AnaliseDocumentoPrestacaoConta para o uuid {value}.")

        return value

class DesfazerEditacaoInformacaoConciliacaoValidateSerializer(serializers.Serializer): # noqa
    uuid_solicitacao_acerto = serializers.CharField(required=True, allow_blank=False)

    def validate_uuid_analise_documento(self, value): # noqa
        try:
            SolicitacaoAcertoDocumento.by_uuid(value)
        except SolicitacaoAcertoDocumento.DoesNotExist:  # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto SolicitacaoAcertoDocumento para o uuid {value}.")

        return value
