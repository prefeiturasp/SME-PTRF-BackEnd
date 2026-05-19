from rest_framework import serializers

from sme_ptrf_apps.core.api.serializers.recurso_serializer import RecursoSerializer

from ...models import TipoConta, Recurso

from rest_framework.validators import UniqueTogetherValidator


class TipoContaSerializer(serializers.ModelSerializer):
    recurso = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Recurso.objects.all()
    )

    recurso_completo = RecursoSerializer(source='recurso', read_only=True, required=False, allow_null=True)

    class Meta:
        model = TipoConta
        fields = (
            'uuid',
            'id',
            'nome',
            'banco_nome',
            'agencia',
            'numero_conta',
            'numero_cartao',
            'apenas_leitura',
            'permite_inativacao',
            'recurso',
            'recurso_completo'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=TipoConta.objects.all(),
                fields=['nome', 'recurso'],
                message='Este tipo de conta já existe para este recurso.'
            )
        ]

    def create(self, validated_data):
        nome = validated_data.get('nome')
        recurso = validated_data.get('recurso')

        # Normaliza o nome: remove espaços em branco extras
        if nome:
            nome = ' '.join(nome.split())
            validated_data['nome'] = nome

        if TipoConta.objects.filter(nome__iexact=nome, recurso=recurso).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Este tipo de conta já existe para este recurso.'
            })

        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        nome = validated_data.get('nome')
        recurso = validated_data.get('recurso')

        # Normaliza o nome: remove espaços em branco extras
        if nome:
            nome = ' '.join(nome.split())
            validated_data['nome'] = nome

        if TipoConta.objects.filter(nome__iexact=nome, recurso=recurso).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Este tipo de conta já existe para este recurso.'
            })

        instance = super().update(instance, validated_data)
        return instance
