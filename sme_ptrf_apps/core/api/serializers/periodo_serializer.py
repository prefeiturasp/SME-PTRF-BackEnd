from rest_framework import serializers

from ...models import Periodo
from .recurso_serializer import RecursoSerializer


class PeriodoLookUpSerializer(serializers.ModelSerializer):
    recurso = RecursoSerializer(read_only=True)

    class Meta:
        model = Periodo
        fields = ('id', 'uuid', 'referencia', 'data_inicio_realizacao_despesas',
                  'data_fim_realizacao_despesas', 'referencia_por_extenso', 'recurso')


class PeriodoSerializer(serializers.ModelSerializer):
    periodo_anterior = PeriodoLookUpSerializer()
    recurso = RecursoSerializer(read_only=True)

    class Meta:
        model = Periodo
        fields = (
            'id',
            'uuid',
            'referencia',
            'data_inicio_realizacao_despesas',
            'data_fim_realizacao_despesas',
            'data_prevista_repasse',
            'data_inicio_prestacao_contas',
            'data_fim_prestacao_contas',
            'editavel',
            'periodo_anterior',
            'recurso'
        )


class PeriodoRetrieveSerializer(serializers.ModelSerializer):
    periodo_anterior = PeriodoLookUpSerializer()
    recurso = RecursoSerializer(read_only=True)

    class Meta:
        model = Periodo
        fields = (
            'id',
            'uuid',
            'referencia',
            'data_inicio_realizacao_despesas',
            'data_fim_realizacao_despesas',
            'data_prevista_repasse',
            'data_inicio_prestacao_contas',
            'data_fim_prestacao_contas',
            'editavel',
            'periodo_anterior',
            'recurso',
        )


class PeriodoCreateSerializer(serializers.ModelSerializer):
    from sme_ptrf_apps.core.models.recurso import Recurso

    periodo_anterior = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Periodo.objects.all(),
        allow_null=True,
        allow_empty=True,
    )

    recurso = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Recurso.objects.all()
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
            'recurso'
        )
