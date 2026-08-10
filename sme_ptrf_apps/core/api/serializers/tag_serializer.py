from rest_framework import serializers

from sme_ptrf_apps.core.models import Tag
from sme_ptrf_apps.core.models.recurso import Recurso


class TagSerializer(serializers.ModelSerializer):
    recurso = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Recurso.objects.all()
    )

    class Meta:
        model = Tag
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Tag.objects.all(),
                fields=['nome', 'recurso'],
                message='Já existe uma tag com este nome para este recurso.'
            )
        ]

    def create(self, validated_data):
        nome = validated_data.get('nome')
        recurso = validated_data.get('recurso')

        # Normaliza o nome: remove espaços em branco extras
        if nome:
            nome = ' '.join(nome.split())
            validated_data['nome'] = nome

        if Tag.objects.filter(nome__iexact=nome, recurso=recurso).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Esta tag já existe para este recurso.'
            })

        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        # Validar se houve alguma mudança
        houve_alteracao = self._verifica_alteracoes(instance, validated_data)

        if not houve_alteracao:
            return instance

        nome = validated_data.get('nome')
        recurso = validated_data.get('recurso')

        # Normaliza o nome: remove espaços em branco extras
        if nome:
            nome = ' '.join(nome.split())
            validated_data['nome'] = nome

        if Tag.objects.filter(nome__iexact=nome, recurso=recurso).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Esta tag já existe para este recurso.'
            })

        return super().update(instance, validated_data)

    def _verifica_alteracoes(self, instance, validated_data):
        """
        Verifica se houve alguma alteração nos dados.
        Retorna True se houve alteração, False caso contrário.
        """
        campos_verificar = ['nome', 'status', 'recurso']

        for campo in campos_verificar:
            if campo not in validated_data:
                continue

            valor_novo = validated_data[campo]

            if campo == 'recurso':
                # Comparar recurso por UUID
                if instance.recurso != valor_novo:
                    return True
            else:
                # Comparar campos simples
                valor_atual = getattr(instance, campo)
                if valor_atual != valor_novo:
                    return True

        return False


class TagLookupSerializer(serializers.ModelSerializer):
    recurso = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Recurso.objects.all()
    )

    class Meta:
        model = Tag
        fields = ('uuid', 'nome', 'status', 'id', 'recurso')
