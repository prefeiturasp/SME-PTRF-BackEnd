from rest_framework import serializers, validators
from sme_ptrf_apps.paa.models import OutroRecurso


class OutroRecursoSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(
        error_messages={
            'null': 'Nome do Recurso não foi informado.',
            'blank': 'Nome do Recurso não foi informado.',
            'required': 'Nome do Recurso é obrigatório.',
        },
        required=True
    )

    class Meta:
        model = OutroRecurso
        fields = ('id', 'uuid', 'nome', 'aceita_capital', 'aceita_custeio', 'aceita_livre_aplicacao', 'cor')
        read_only_fields = ('id', 'uuid',)
        validators = [
            validators.UniqueTogetherValidator(
                queryset=OutroRecurso.objects.all(),
                fields=['nome'],
                message="Já existe um Recurso cadastrado com esse nome."
            )
        ]
