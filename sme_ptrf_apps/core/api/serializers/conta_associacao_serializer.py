from rest_framework import serializers

from ..serializers.associacao_serializer import AssociacaoSerializer
from ..serializers.tipo_conta_serializer import TipoContaSerializer
from ..serializers.solicitacao_encerramento_conta_associacao_serializer import SolicitacaoEncerramentoContaAssociacaoSerializer
from ...models import ContaAssociacao, Associacao


class ContaAssociacaoSerializer(serializers.ModelSerializer):
    tipo_conta = TipoContaSerializer()
    associacao = AssociacaoSerializer()

    class Meta:
        model = ContaAssociacao
        fields = ('uuid', 'tipo_conta', 'associacao', 'status')


class ContaAssociacaoLookUpSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField('get_nome_conta')
    solicitacao_encerramento = SolicitacaoEncerramentoContaAssociacaoSerializer()

    def get_nome_conta(self, obj):
        return obj.tipo_conta.nome

    class Meta:
        model = ContaAssociacao
        fields = ('uuid', 'nome', 'status', 'solicitacao_encerramento')


class ContaAssociacaoInfoAtaSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField('get_nome_conta')

    def get_nome_conta(self, obj):
        return obj.tipo_conta.nome

    class Meta:
        model = ContaAssociacao
        fields = ('uuid', 'nome', 'banco_nome', 'agencia', 'numero_conta', 'status', )


class ContaAssociacaoDadosSerializer(serializers.ModelSerializer):
    tipo_conta = TipoContaSerializer()
    solicitacao_encerramento = SolicitacaoEncerramentoContaAssociacaoSerializer()
    saldo_atual_conta = serializers.SerializerMethodField()
    habilitar_solicitar_encerramento = serializers.SerializerMethodField()
    nome = serializers.SerializerMethodField('get_nome_conta')

    def get_nome_conta(self, obj):
        return obj.tipo_conta.nome

    class Meta:
        model = ContaAssociacao
        fields = (
            'uuid',
            'tipo_conta',
            'banco_nome',
            'agencia',
            'numero_conta',
            'solicitacao_encerramento',
            'saldo_atual_conta',
            'habilitar_solicitar_encerramento',
            'nome',
            'status'
        )

    def get_habilitar_solicitar_encerramento(self, obj):
        saldo_atual = self.get_saldo_atual_conta(obj)

        try:
            solicitacao_encerramento = obj.solicitacao_encerramento
        except ContaAssociacao.solicitacao_encerramento.RelatedObjectDoesNotExist:
            solicitacao_encerramento = None

        if saldo_atual == 0 and (not solicitacao_encerramento or (solicitacao_encerramento and solicitacao_encerramento.rejeitada)):
            return True

        return False

    def get_saldo_atual_conta(self, obj):
        return obj.get_saldo_atual_conta()

class ContaAssociacaoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContaAssociacao
        exclude = ('id',)
