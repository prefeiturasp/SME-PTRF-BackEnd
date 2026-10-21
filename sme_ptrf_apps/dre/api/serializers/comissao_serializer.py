from rest_framework import serializers

from sme_ptrf_apps.core.models.recurso import Recurso
from sme_ptrf_apps.dre.models import comissao
from ...models import Comissao


class ComissaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comissao
        fields = ('uuid', 'id', 'nome')


class SimpleRecursoSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    nome = serializers.CharField(max_length=255)
    nome_exibicao = serializers.CharField(max_length=160)


class ComissaoParametrizacaoSerializer(serializers.ModelSerializer):
    recursos = SimpleRecursoSerializer(many=True, read_only=True)
    class Meta:
        model = Comissao
        fields = ('uuid', 'id', 'nome', 'responsavel_analise_pc', 'recursos')


    def create(self, validated_data):
        recursos_data = self.initial_data.get('recursos', [])
        recursos = []

        for recurso_uuid in recursos_data:
            if recurso_uuid:
                try:
                    recurso = Recurso.objects.get(uuid=recurso_uuid)
                    recursos.append(recurso)
                except ValueError:
                    continue
                except Recurso.DoesNotExist:
                    continue

        if len(recursos) <= 0:
            raise serializers.ValidationError({
                "non_field_errors": "Pelo menos um recurso válido deve ser associado à comissão."
            })

        nome = validated_data.get('nome')
        nome = ' '.join(nome.split()) if nome else ''
        validated_data['nome'] = nome

        is_valid, error_message = Comissao.is_valid_data(
            nome=nome,
            recursos=recursos,
            responsavel_analise_pc=validated_data.get('responsavel_analise_pc', False)
        )

        if not is_valid:
            raise serializers.ValidationError({
                "non_field_errors": error_message
            })

        instance = super().create(validated_data)
        instance.recursos.set(recursos)

        return instance


    def update(self, instance, validated_data):
        recursos_data = self.initial_data.get('recursos', [])
        recursos = []

        for recurso_uuid in recursos_data:
            if recurso_uuid:
                try:
                    recurso = Recurso.objects.get(uuid=recurso_uuid)
                    recursos.append(recurso)
                except ValueError:
                    continue
                except Recurso.DoesNotExist:
                    continue

        if len(recursos) <= 0:
            raise serializers.ValidationError({
                "non_field_errors": "Pelo menos um recurso válido deve ser associado à comissão."
            })

        nome = validated_data.get('nome')
        nome = ' '.join(nome.split()) if nome else ''
        validated_data['nome'] = nome

        is_valid, error_message = Comissao.is_valid_data(
            nome=nome,
            recursos=recursos,
            responsavel_analise_pc=validated_data.get('responsavel_analise_pc', False),
            instance_id=instance.id
        )

        if not is_valid:
            raise serializers.ValidationError({
                "non_field_errors": error_message
            })

        instance = super().update(instance, validated_data)
        instance.recursos.set(recursos)

        return instance
