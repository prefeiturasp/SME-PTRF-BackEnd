from rest_framework import serializers

from sme_ptrf_apps.core.models.recurso import Recurso
from ...models import MotivoReprovacao

from sme_ptrf_apps.core.api.serializers.recurso_serializer import RecursoSerializer

class MotivoReprovacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoReprovacao
        fields = ('uuid', 'motivo')

class MotivoReprovacaoParametrizacaoSerializer(serializers.ModelSerializer):
    recurso = RecursoSerializer(read_only=True)
    recurso_uuid = serializers.UUIDField(write_only=True)

    class Meta:
        model = MotivoReprovacao
        fields = ('id', 'uuid', 'motivo', 'recurso', 'recurso_uuid')

    def create(self, validated_data):
        motivo = validated_data.get('motivo')
        recurso_uuid = validated_data.pop('recurso_uuid')

        recurso = Recurso.objects.filter(uuid=recurso_uuid).first() or None
        if not recurso:
            raise serializers.ValidationError({
                'non_field_errors': 'Por favor, informe os campos corretamente.'
            })

        if MotivoReprovacao.objects.filter(motivo__iexact=motivo.lower(), recurso=recurso).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Este motivo de reprovação já existe para o recurso selecionado.'
                })

        validated_data['recurso'] = recurso
        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        motivo = validated_data.get('motivo')
        recurso_uuid = validated_data.pop('recurso_uuid')

        if self.instance.prestacaoconta_set.exists():
            raise serializers.ValidationError({
                'non_field_errors': (
                    'Essa operação não pode ser realizada. '
                    'Há PCs com análise concluída com esse motivo de aprovação de PC com ressalvas.'
                )
            })

        recurso = Recurso.objects.filter(uuid=recurso_uuid).first() or None
        if not recurso:
            raise serializers.ValidationError({
                'non_field_errors': 'Por favor, informe os campos corretamente.'
            })

        if MotivoReprovacao.objects.filter(motivo__iexact=motivo.lower(), recurso=recurso).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Este motivo de reprovação já existe para o recurso selecionado.'
                })

        validated_data['recurso'] = recurso
        instance = super().update(instance, validated_data)
        return instance
