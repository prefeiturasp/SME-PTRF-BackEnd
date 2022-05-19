from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST

from ...models import ComentarioAnalisePrestacao, PrestacaoConta


class CustomError(APIException):
    """Readers error class"""

    def __init__(self, msg):
        APIException.__init__(self, msg)
        self.status_code = HTTP_400_BAD_REQUEST
        self.message = msg


class ComentarioAnalisePrestacaoRetrieveSerializer(serializers.ModelSerializer):
    prestacao_conta = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=PrestacaoConta.objects.all()
    )

    def validate_notificado(self, value):
        # Validação realizada quando Update é chamado, para Delete será tratado na View, pois validate NÃO é chamado no delete
        # Verifica se o comentário já foi notificado
        if value:
            raise CustomError({"detail": "Comentários já notificados não podem mais ser editados ou removidos."})
        return value

    class Meta:
        model = ComentarioAnalisePrestacao
        order_by = 'ordem'
        fields = ('uuid', 'prestacao_conta', 'ordem', 'comentario', 'notificado', 'notificado_em')
