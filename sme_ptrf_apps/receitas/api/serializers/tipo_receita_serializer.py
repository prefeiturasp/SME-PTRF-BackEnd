from rest_framework import serializers

from sme_ptrf_apps.core.api.serializers import TipoContaSerializer
from .detalhe_tipo_receita_serializer import DetalheTipoReceitaSerializer
from ...models import TipoReceita


class TipoReceitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoReceita
        fields = ('id', 'nome', 'e_repasse', 'aceita_capital', 'aceita_custeio', 'aceita_livre', 'e_devolucao', 'e_recursos_proprios')


class TipoReceitaEDetalhesSerializer(serializers.ModelSerializer):
    detalhes_tipo_receita = DetalheTipoReceitaSerializer(many=True)
    tipos_conta = TipoContaSerializer(many=True)

    class Meta:
        model = TipoReceita
        fields = ('id',
                  'nome',
                  'aceita_capital',
                  'aceita_custeio',
                  'aceita_livre',
                  'detalhes_tipo_receita',
                  'e_repasse',
                  'e_devolucao',
                  'e_recursos_proprios',
                  'e_estorno',
                  'mensagem_usuario',
                  'possui_detalhamento',
                  'tipos_conta',
                )


class TipoReceitaLookUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoReceita
        fields = ('id', 'nome')

