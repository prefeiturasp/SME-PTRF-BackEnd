from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST

from ...models import ComentarioAnalisePrestacao, PrestacaoConta, Associacao, Periodo


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
        allow_null=True,
        queryset=PrestacaoConta.objects.all()
    )
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        allow_null=True,
        queryset=Associacao.objects.all()
    )
    periodo = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        allow_null=True,
        queryset=Periodo.objects.all()
    )

    def validate(self, data):
        prestacao_conta = self.initial_data['prestacao_conta'] if 'prestacao_conta' in self.initial_data else None
        associacao = self.initial_data['associacao'] if 'associacao' in self.initial_data else None
        periodo = self.initial_data['periodo'] if 'periodo' in self.initial_data else None

        if self.instance:
            if 'prestacao_conta' in self.initial_data or 'associacao' in self.initial_data or 'periodo' in self.initial_data:
                if not (prestacao_conta or (associacao and periodo)):
                    raise CustomError({"detail": "É necessário enviar a prestação de contas ou associação e período."})
        else:
            if not (prestacao_conta or (associacao and periodo)):
                raise CustomError({"detail": "É necessário enviar a prestação de contas ou associação e período."})

        return data

    def validate_notificado(self, value):
        # Validação realizada quando Update é chamado, para Delete será tratado na View, pois validate NÃO é chamado no delete
        # Verifica se o comentário já foi notificado
        if value:
            raise CustomError({"detail": "Comentários já notificados não podem mais ser editados ou removidos."})
        return value

    class Meta:
        model = ComentarioAnalisePrestacao
        order_by = 'ordem'
        fields = ('uuid', 'prestacao_conta', 'associacao', 'periodo', 'ordem', 'comentario', 'notificado', 'notificado_em')
