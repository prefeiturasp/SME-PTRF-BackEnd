from django.core.exceptions import ValidationError

from rest_framework import serializers

from ..serializers.associacao_serializer import AssociacaoSerializer
from ..serializers.tipo_conta_serializer import TipoContaSerializer
from ..serializers.solicitacao_encerramento_conta_associacao_serializer import SolicitacaoEncerramentoContaAssociacaoSerializer
from ...models import ContaAssociacao, Associacao, TipoConta


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
        fields = ('uuid', 'nome', 'status', 'solicitacao_encerramento', 'data_inicio', )


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
    periodo_encerramento_conta = serializers.SerializerMethodField('get_periodo_encerramento_conta')
    mostrar_alerta_valores_reprogramados_ao_solicitar = serializers.SerializerMethodField(
        'get_mostrar_alerta_valores_reprogramados_ao_solicitar')

    def get_nome_conta(self, obj):
        return obj.tipo_conta.nome

    def get_periodo_encerramento_conta(self, obj):
        from sme_ptrf_apps.core.models import Periodo

        if obj.data_encerramento:
            periodo = Periodo.da_data(obj.data_encerramento)
            if periodo:
                return periodo.referencia
        return None

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
            'status',
            'periodo_encerramento_conta',
            'mostrar_alerta_valores_reprogramados_ao_solicitar'
        )

    def get_mostrar_alerta_valores_reprogramados_ao_solicitar(self, obj):
        if obj.associacao.periodo_inicial and obj.associacao.periodo_inicial.proximo_periodo:
            pc_do_primeiro_periodo_de_uso_do_sistema = obj.associacao.prestacoes_de_conta_da_associacao.filter(
                periodo=obj.associacao.periodo_inicial.proximo_periodo)

            if pc_do_primeiro_periodo_de_uso_do_sistema.exists():
                return False

        if obj.associacao.valores_reprogramados_associacao.exists():
            return False

        return True

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


class ContaAssociacaoCriacaoSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Associacao.objects.all()
    )

    tipo_conta = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=TipoConta.objects.all()
    )
    tipo_conta_dados = TipoContaSerializer(many=False, read_only=True)
    associacao_dados = AssociacaoSerializer(many=False, read_only=True)

    class Meta:
        model = ContaAssociacao
        fields = ('id', 'uuid', 'banco_nome', 'agencia', 'numero_conta', 'numero_cartao',
                  'data_inicio', 'associacao', 'tipo_conta', 'status', 'tipo_conta_dados', 'associacao_dados')
        read_only_fields = ('tipo_conta_dados', 'associacao_dados',)

    def create(self, validated_data):
        associacao = validated_data.get('associacao')
        tipo_conta = validated_data.get('tipo_conta')
        banco_nome = validated_data.get('banco_nome')
        agencia = validated_data.get('agencia')
        numero_conta = validated_data.get('numero_conta')
        numero_cartao = validated_data.get('numero_cartao')

        if ContaAssociacao.objects.filter(
                associacao=associacao,
                tipo_conta=tipo_conta,
                banco_nome=banco_nome,
                agencia=agencia,
                numero_conta=numero_conta,
                numero_cartao=numero_cartao).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Esta conta de associacao já existe.'
                })

        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        associacao = validated_data.get('associacao')
        tipo_conta = validated_data.get('tipo_conta')
        banco_nome = validated_data.get('banco_nome')
        agencia = validated_data.get('agencia')
        numero_conta = validated_data.get('numero_conta')
        numero_cartao = validated_data.get('numero_cartao')

        if ContaAssociacao.objects.filter(
            associacao=associacao,
            tipo_conta=tipo_conta,
            banco_nome=banco_nome,
            agencia=agencia,
            numero_conta=numero_conta,
            numero_cartao=numero_cartao
        ).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Esta conta de associacao já existe.'
                })

        instance = super().update(instance, validated_data)
        return instance
