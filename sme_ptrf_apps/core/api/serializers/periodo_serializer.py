from rest_framework import serializers

from ...models import Periodo


class PeriodoLookUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periodo
        fields = ('uuid', 'referencia', 'data_inicio_realizacao_despesas', 'data_fim_realizacao_despesas', 'referencia_por_extenso')


class PeriodoSerializer(serializers.ModelSerializer):
    periodo_anterior = PeriodoLookUpSerializer()

    class Meta:
        model = Periodo
        fields = (
            'uuid',
            'referencia',
            'data_inicio_realizacao_despesas',
            'data_fim_realizacao_despesas',
            'data_prevista_repasse',
            'data_inicio_prestacao_contas',
            'data_fim_prestacao_contas',
            'editavel',
            'periodo_anterior',
        )


class PeriodoRetrieveSerializer(serializers.ModelSerializer):
    periodo_anterior = PeriodoLookUpSerializer()

    class Meta:
        model = Periodo
        fields = (
            'uuid',
            'id',
            'referencia',
            'data_inicio_realizacao_despesas',
            'data_fim_realizacao_despesas',
            'data_prevista_repasse',
            'data_inicio_prestacao_contas',
            'data_fim_prestacao_contas',
            'editavel',
            'periodo_anterior',
        )


class PeriodoCreateSerializer(serializers.ModelSerializer):
    periodo_anterior = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Periodo.objects.all()
    )

    class Meta:
        model = Periodo
        fields = (
            'uuid',
            'referencia',
            'data_inicio_realizacao_despesas',
            'data_fim_realizacao_despesas',
            'data_prevista_repasse',
            'data_inicio_prestacao_contas',
            'data_fim_prestacao_contas',
            'editavel',
            'periodo_anterior',
        )
