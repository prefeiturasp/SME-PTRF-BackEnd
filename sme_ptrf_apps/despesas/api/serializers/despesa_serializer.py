import logging

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ...models import Despesa

from ....core.models import Associacao

from ....core.api.serializers.associacao_serializer import AssociacaoSerializer

from ..serializers.rateio_despesa_serializer import RateioDespesaCreateSerializer

from .rateio_despesa_serializer import RateioDespesaSerializer
from .tipo_documento_serializer import TipoDocumentoSerializer
from .tipo_transacao_serializer import TipoTransacaoSerializer

log = logging.getLogger(__name__)


class DespesaSerializer(serializers.ModelSerializer):
    associacao = AssociacaoSerializer()
    tipo_documento = TipoDocumentoSerializer()
    tipo_transacao = TipoTransacaoSerializer()
    rateios = RateioDespesaSerializer(many=True)

    class Meta:
        model = Despesa
        fields = '__all__'


class DespesaCreateSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )
    rateios = RateioDespesaCreateSerializer(many=True)

    def create(self, validated_data):
        rateios = validated_data.pop('rateios')

        if not rateios:
            msgError = "Pelo menos uma linha de rateio deve ser enviada!"
            log.info(msgError)
            raise ValidationError(msgError)

        despesa = Despesa.objects.create(**validated_data)
        log.info("Criando despesa com uuid: {}".format(despesa.uuid))

        rateios_lista = []
        for rateio in rateios:
            rateio_object = RateioDespesaCreateSerializer().create(rateio)
            rateios_lista.append(rateio_object)
        despesa.rateios.set(rateios_lista)
        log.info("Despesa {}, Rateios: {}".format(despesa.uuid, rateios_lista))

        log.info("Criação de despesa finalizada!")

        return despesa

    class Meta:
        model = Despesa
        exclude = ('id',)
