from rest_framework import serializers

from ...models import Unidade


class DreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidade
        fields = ('uuid', 'codigo_eol', 'tipo_unidade', 'nome', 'sigla')


class UnidadeLookUpSerializer(serializers.ModelSerializer):
    dre = DreSerializer()

    class Meta:
        model = Unidade
        fields = ('uuid', 'codigo_eol', 'tipo_unidade', 'nome', 'sigla', 'dre')


class UnidadeSerializer(serializers.ModelSerializer):
    dre = DreSerializer()

    class Meta:
        model = Unidade
        fields = (
            'uuid',
            'codigo_eol',
            'tipo_unidade',
            'nome',
            'sigla',
            'dre',
            'email',
            'telefone',
            'tipo_logradouro',
            'logradouro',
            'numero',
            'complemento',
            'bairro',
            'cep',
            'qtd_alunos',
            'diretor_nome',
            'dre_cnpj',
            'dre_diretor_regional_rf',
            'dre_diretor_regional_nome',
            'dre_designacao_portaria',
            'dre_designacao_ano',
            'observacao'
        )


class UnidadeInfoAtaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidade
        fields = ('tipo_unidade', 'nome')


class UnidadeListEmAssociacoesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidade
        fields = ('uuid', 'codigo_eol', 'nome_com_tipo', 'nome_dre')


class UnidadeListSerializer(serializers.ModelSerializer):
    associacao_uuid = serializers.SerializerMethodField('get_associacao_uuid')
    associacao_nome = serializers.SerializerMethodField('get_associacao_nome')
    visao = serializers.SerializerMethodField('get_visao')

    def get_associacao_uuid(self, obj):
        return obj.associacoes.first().uuid if obj.associacoes.exists() else ''

    def get_associacao_nome(self, obj):
        return obj.associacoes.first().nome if obj.associacoes.exists() else ''

    def get_visao(self, obj):
        return 'DRE' if obj.tipo_unidade == 'DRE' else 'UE'

    class Meta:
        model = Unidade
        fields = (
            'uuid',
            'codigo_eol',
            'nome_com_tipo',
            'nome_dre',
            'nome',
            'tipo_unidade',
            'associacao_uuid',
            'associacao_nome',
            'visao'
        )


class UnidadeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidade
        fields = ('codigo_eol', 'nome', 'email', 'telefone', 'numero',
                  'tipo_logradouro', 'logradouro', 'bairro', 'cep', 'tipo_unidade', 'observacao')
