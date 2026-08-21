from rest_framework import serializers
from django.db import transaction
from ...models import Acao
from ...services.acoes_desabilitadas_paa import desabilitar_acao_ptrf_paa


class AcaoSerializer(serializers.ModelSerializer):
    from sme_ptrf_apps.core.models.recurso import Recurso

    recurso = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Recurso.objects.all()
    )

    class Meta:
        model = Acao
        fields = ('id', 'uuid', 'nome', 'e_recursos_proprios', 'posicao_nas_pesquisas',
                  'aceita_capital', 'aceita_custeio', 'aceita_livre', 'exibir_paa',
                  'tem_receitas_previstas_paa_em_elaboracao', 'tem_prioridades_paa_em_elaboracao', 'recurso',
                  'ordem_exibicao')
        read_only_fields = (
            'id', 'uuid', 'tem_receitas_previstas_paa_em_elaboracao', 'tem_prioridades_paa_em_elaboracao')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Acao.objects.all(),
                fields=['nome', 'recurso'],
                message='Já existe uma ação com este nome para este recurso.'
            )
        ]

    def create(self, validated_data):
        nome = validated_data.get('nome')
        recurso = validated_data.get('recurso')

        # Normaliza o nome: remove espaços em branco extras
        if nome:
            nome = ' '.join(nome.split())
            validated_data['nome'] = nome

        if Acao.objects.filter(nome__iexact=nome, recurso=recurso).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Já existe uma ação com este nome para este recurso.'
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

        if Acao.objects.filter(nome__iexact=nome, recurso=recurso).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Já existe uma ação com este nome para este recurso.'
            })

        with transaction.atomic():
            # Atualiza normalmente os campos
            instance = super().update(instance, validated_data)

            # Executa após o update para que a instância já tenha o campo exibir_paa atualizado
            # verifica se existe o campo exibir_paa
            if 'exibir_paa' in validated_data:
                desabilitando_acao = not (validated_data['exibir_paa'])
                if desabilitando_acao:
                    desabilitar_acao_ptrf_paa(instance)

            return instance
