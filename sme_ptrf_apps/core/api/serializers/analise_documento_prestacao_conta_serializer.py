from rest_framework import serializers

from ...models import AnalisePrestacaoConta, AnaliseDocumentoPrestacaoConta

from .solicitacao_acerto_documento_serializer import SolicitacaoAcertoDocumentoRetrieveSerializer
from .tipo_documento_prestacao_conta_serializer import TipoDocumentoPrestacaoContaSerializer
from .conta_associacao_serializer import ContaAssociacaoLookUpSerializer

from sme_ptrf_apps.despesas.models import Despesa
from sme_ptrf_apps.receitas.models import Receita


class AnaliseDocumentoPrestacaoContaRetrieveSerializer(serializers.ModelSerializer):

    analise_prestacao_conta = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AnalisePrestacaoConta.objects.all()
    )
    documento = serializers.SerializerMethodField('get_nome_documento')
    tipo_documento_prestacao_conta = TipoDocumentoPrestacaoContaSerializer(many=False)
    conta_associacao = ContaAssociacaoLookUpSerializer(many=False)


    # solicitacoes_de_ajuste_da_analise = SolicitacaoAcertoDocumentoRetrieveSerializer(many=True)
    solicitacoes_de_ajuste_da_analise = serializers.SerializerMethodField('get_solicitacoes_ajuste')

    def get_solicitacoes_ajuste(self, obj):
        return obj.solicitacoes_de_acertos_agrupado_por_categoria()

    solicitacoes_de_ajuste_da_analise_total = serializers.SerializerMethodField('get_solicitacoes_ajuste_total')

    def get_solicitacoes_ajuste_total(self, obj):
        return obj.solicitacoes_de_acertos_total()


    despesa_incluida = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Despesa.objects.all(),
        allow_null=True,
        allow_empty=True,
    )
    receita_incluida = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Receita.objects.all(),
        allow_null=True,
        allow_empty=True,
    )

    def get_nome_documento(self, obj):
        _documento = obj.tipo_documento_prestacao_conta
        _conta_associacao = obj.conta_associacao
        return f'{_documento.nome} {_conta_associacao.tipo_conta.nome}' if _conta_associacao else _documento.nome

    class Meta:
        model = AnaliseDocumentoPrestacaoConta
        fields = (
            'analise_prestacao_conta',
            'documento',
            'tipo_documento_prestacao_conta',
            'conta_associacao',
            'resultado',
            'id',
            'uuid',
            'solicitacoes_de_ajuste_da_analise',
            'status_realizacao',
            'justificativa',
            'esclarecimentos',
            'despesa_incluida',
            'receita_incluida',
            'requer_esclarecimentos',
            'requer_inclusao_credito',
            'requer_inclusao_gasto',
            'requer_ajuste_externo',
            'solicitacoes_de_ajuste_da_analise_total'
        )


class AnaliseDocumentoPrestacaoContaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnaliseDocumentoPrestacaoConta
        fields = (
            'justificativa',
        )
