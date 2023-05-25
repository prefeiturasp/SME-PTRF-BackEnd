from rest_framework import serializers

from ..serializers.acao_serializer import AcaoSerializer
from ..serializers.associacao_serializer import AssociacaoSerializer, AssociacaoListSerializer
from ...models import AcaoAssociacao, Associacao, Acao


class AcaoAssociacaoSerializer(serializers.ModelSerializer):
    acao = AcaoSerializer()
    associacao = AssociacaoSerializer()

    class Meta:
        model = AcaoAssociacao
        fields = ('uuid', 'acao', 'associacao', 'status')


class AcaoAssociacaoLookUpSerializer(serializers.ModelSerializer):
    acao = AcaoSerializer()
    nome = serializers.SerializerMethodField('get_nome_acao')
    e_recursos_proprios = serializers.SerializerMethodField('get_recurso_proprio')

    def get_nome_acao(self, obj):
        return obj.acao.nome

    def get_recurso_proprio(self, obj):
        return obj.acao.e_recursos_proprios

    class Meta:
        model = AcaoAssociacao
        fields = ('uuid', 'id', 'nome', 'e_recursos_proprios', 'acao', )


class AcaoAssociacaoAjustesValoresIniciasSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField('get_nome_acao')

    def get_nome_acao(self, obj):
        return obj.acao.nome

    class Meta:
        model = AcaoAssociacao
        fields = ('uuid', 'nome',)


class AcaoAssociacaoCreateSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )

    acao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Acao.objects.all()
    )

    class Meta:
        model = AcaoAssociacao
        fields = ('uuid', 'associacao', 'acao', 'status')


class AcaoAssociacaoRetrieveSerializer(serializers.ModelSerializer):
    associacao = AssociacaoListSerializer()
    acao = AcaoSerializer()
    data_de_encerramento_associacao = serializers.SerializerMethodField('get_data_de_encerramento_associacao')
    tooltip_associacao_encerrada = serializers.SerializerMethodField('get_tooltip_associacao_encerrada')

    def get_data_de_encerramento_associacao(self, obj):
        return obj.associacao.data_de_encerramento

    def get_tooltip_associacao_encerrada(self, obj):
        return obj.associacao.tooltip_data_encerramento

    class Meta:
        model = AcaoAssociacao
        fields = ('uuid', 'id', 'associacao', 'data_de_encerramento_associacao', 'tooltip_associacao_encerrada', 'acao', 'status', 'criado_em')
