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
        )


class UnidadeInfoAtaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidade
        fields = ('tipo_unidade', 'nome')


class UnidadeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidade
        fields = ('uuid', 'codigo_eol', 'nome_com_tipo', 'nome_dre', 'nome')


class UnidadeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidade
        fields = ('codigo_eol', 'nome', 'email', 'telefone', 'numero',
                  'tipo_logradouro', 'logradouro', 'bairro', 'cep', 'tipo_unidade',)
