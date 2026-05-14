from rest_framework import serializers

from sme_ptrf_apps.core.models.recurso import Recurso

from ...models import MotivoAprovacaoRessalva
from rest_framework.validators import UniqueTogetherValidator


class MotivoAprovacaoRessalvaSerializer(serializers.ModelSerializer):
    recurso = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Recurso.objects.all()
    )

    class Meta:
        model = MotivoAprovacaoRessalva
        fields = ('uuid', 'motivo', 'recurso')


class MotivoAprovacaoRessalvaParametrizacaoSerializer(serializers.ModelSerializer):
    recurso = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Recurso.objects.all()
    )

    class Meta:
        model = MotivoAprovacaoRessalva
        fields = ('id', 'uuid', 'motivo', 'recurso')
        validators = [
            UniqueTogetherValidator(
                queryset=MotivoAprovacaoRessalva.objects.all(),
                fields=['motivo', 'recurso'],
                message='Este motivo de aprovação de PC com ressalva já existe para este recurso.'
            )
        ]

    def create(self, validated_data):
        motivo = validated_data.get('motivo')
        recurso = validated_data.get('recurso')

        if MotivoAprovacaoRessalva.objects.filter(motivo__iexact=motivo, recurso=recurso).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Este motivo de aprovação de PC com ressalva já existe para este recurso.'
            })

        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        motivo = validated_data.get('motivo')
        recurso = validated_data.get('recurso')

        if MotivoAprovacaoRessalva.objects.filter(motivo__iexact=motivo, recurso=recurso).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Este motivo de aprovação de PC com ressalva já existe para este recurso.'
            })

        instance = super().update(instance, validated_data)
        return instance
