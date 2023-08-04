from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST

from ...models import Mandato

class CustomError(APIException):
    """Readers error class"""

    def __init__(self, msg):
        APIException.__init__(self, msg)
        self.status_code = HTTP_400_BAD_REQUEST
        self.message = msg


class MandatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mandato
        fields = ('id', 'uuid', 'referencia_mandato', 'data_inicial', 'data_final')

    def validate(self, data):
        data_inicial = data.get('data_inicial')
        data_final = data.get('data_final')

        # Verificar se a data final é menor que a data inicial
        if data_final < data_inicial:
            raise CustomError({"detail": "A data final não pode ser menor que a data inicial"})

        # Verificar se a data inicial está dentro de outro mandato existente
        if data_inicial and data_final:
            mandatos = Mandato.objects.filter(data_inicial__lte=data_inicial, data_final__gte=data_inicial)

            if self.instance:
                mandatos = mandatos.exclude(uuid=self.instance.uuid)  # Excluir o próprio objeto atual ao verificar colisões

            if mandatos.exists():
                raise CustomError({"detail": "A data inicial informada é de vigência de outro mandato cadastrado."})

        return data
