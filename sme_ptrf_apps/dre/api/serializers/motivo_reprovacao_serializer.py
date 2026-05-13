from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from sme_ptrf_apps.core.models.recurso import Recurso
from ...models import MotivoReprovacao

from sme_ptrf_apps.core.api.serializers.recurso_serializer import RecursoSerializer

class MotivoReprovacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoReprovacao
        fields = ('uuid', 'motivo')

class MotivoReprovacaoParametrizacaoSerializer(serializers.ModelSerializer):
    recurso = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Recurso.objects.all()
    )

    class Meta:
        model = MotivoReprovacao
        fields = ('id', 'uuid', 'motivo', 'recurso')
        validators = [
            UniqueTogetherValidator(
                queryset=MotivoReprovacao.objects.all(),
                fields=['motivo', 'recurso'],
                message='Este motivo de reprovação de PC já existe para este recurso.'
            )
        ]

    def create(self, validated_data):
        motivo = validated_data.get('motivo')
        recurso = validated_data.get('recurso')

        if MotivoReprovacao.objects.filter(motivo__iexact=motivo, recurso=recurso).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Este motivo de reprovação já existe para o recurso selecionado.'
                })

        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        motivo = validated_data.get('motivo')
        recurso = validated_data.get('recurso')

        if recurso != self.instance.recurso:
            if self.instance.prestacaoconta_set.exists():
                raise serializers.ValidationError({
                    'non_field_errors': (
                        'Essa operação não pode ser realizada. '
                        'Há PCs com análise concluída com esse motivo de aprovação de PC com ressalvas.'
                    )
                })

        if MotivoReprovacao.objects.filter(motivo__iexact=motivo, recurso=recurso).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Este motivo de reprovação já existe para o recurso selecionado.'
                })

        instance = super().update(instance, validated_data)
        return instance
