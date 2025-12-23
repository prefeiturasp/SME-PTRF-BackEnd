from rest_framework import serializers, validators
from sme_ptrf_apps.paa.models import OutroRecursoPeriodoPaa, PeriodoPaa, OutroRecurso
from sme_ptrf_apps.core.api.serializers import UnidadeSerializer


class OutrosRecursosPeriodoPaaSerializer(serializers.ModelSerializer):
    uso_associacao = serializers.CharField(read_only=True)
    outro_recurso_nome = serializers.CharField(read_only=True, source='outro_recurso.nome')
    outro_recurso_cor = serializers.CharField(read_only=True, source='outro_recurso.cor')
    periodo_paa = serializers.SlugRelatedField(
        queryset=PeriodoPaa.objects.all(),
        slug_field='uuid',
        required=True,
        error_messages={
            'required': 'Período não foi informado.',
            'null': 'Período não foi informado.'
        },
    )
    outro_recurso = serializers.SlugRelatedField(
        queryset=OutroRecurso.objects.all(),
        slug_field='uuid',
        required=True,
        error_messages={
            'required': 'Outro Recurso não foi informado.',
            'null': 'Outro Recurso não foi informado.'
        },
    )
    unidades = serializers.SlugRelatedField(
        queryset=UnidadeSerializer.Meta.model.objects.all(),
        slug_field='uuid',
        required=False,
        many=True
    )

    class Meta:
        model = OutroRecursoPeriodoPaa
        fields = ('id', 'uuid', 'outro_recurso', 'periodo_paa', 'ativo', 'unidades',
                  'uso_associacao', 'outro_recurso_nome', 'outro_recurso_cor'
                  )
        read_only_fields = ('uuid', 'id', 'uso_associacao', 'outro_recurso_nome', 'outro_recurso_cor')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=OutroRecursoPeriodoPaa.objects.all(),
                fields=['outro_recurso', 'periodo_paa'],
                message="Já existe um Recurso cadastrado para o período informado."
            ),
        ]
