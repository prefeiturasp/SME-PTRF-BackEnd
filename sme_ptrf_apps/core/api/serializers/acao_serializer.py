from rest_framework import serializers

from ...models import Acao


class AcaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acao
        fields = ('id', 'uuid', 'nome', 'e_recursos_proprios', 'posicao_nas_pesquisas',
                  'aceita_capital', 'aceita_custeio', 'aceita_livre')
