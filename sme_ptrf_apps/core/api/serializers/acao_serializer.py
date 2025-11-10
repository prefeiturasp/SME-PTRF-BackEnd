from rest_framework import serializers
from django.db import transaction
from ...models import Acao
from ...services.acoes_desabilitadas_paa import desabilitar_acao_ptrf_paa


class AcaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acao
        fields = ('id', 'uuid', 'nome', 'e_recursos_proprios', 'posicao_nas_pesquisas',
                  'aceita_capital', 'aceita_custeio', 'aceita_livre', 'exibir_paa',
                  'tem_receitas_previstas_paa_em_elaboracao', 'tem_prioridades_paa_em_elaboracao')
        read_only_fields = (
            'id', 'uuid', 'tem_receitas_previstas_paa_em_elaboracao', 'tem_prioridades_paa_em_elaboracao')

    def update(self, instance, validated_data):
        with transaction.atomic():
            # Atualiza normalmente os campos
            instance = super().update(instance, validated_data)

            # Executa após o update para que a instância já tenha o campo exibir_paa atualizado
            # verifica se existe o campo exibir_paa
            if 'exibir_paa' in validated_data:
                desabilitando_acao = not (validated_data['exibir_paa'])
                if desabilitando_acao:
                    print('desabilitando_acao', desabilitando_acao)
                    desabilitar_acao_ptrf_paa(instance)

            # Chama o service após salvar
            # (pode ser condicional, dependendo do campo alterado)

            return instance
