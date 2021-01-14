from rest_framework import serializers

from ...models import Periodo


class PeriodoLookUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periodo
        fields = ('uuid', 'referencia', 'data_inicio_realizacao_despesas', 'data_fim_realizacao_despesas', 'referencia_por_extenso')


class PeriodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periodo
        exclude = ('criado_em', 'alterado_em', 'id', 'periodo_anterior')


class PeriodoRetrieveSerializer(serializers.ModelSerializer):
    periodo_anterior = PeriodoLookUpSerializer()

    class Meta:
        model = Periodo
        exclude = ('criado_em', 'alterado_em')
