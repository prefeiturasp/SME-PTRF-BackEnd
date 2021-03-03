import logging

from rest_framework import serializers

from sme_ptrf_apps.utils.update_instance_from_dict import update_instance_from_dict
from .rateio_despesa_serializer import RateioDespesaSerializer
from .tipo_documento_serializer import TipoDocumentoSerializer, TipoDocumentoListSerializer
from .tipo_transacao_serializer import TipoTransacaoSerializer
from ..serializers.rateio_despesa_serializer import RateioDespesaCreateSerializer
from ...models import Despesa
from ....core.api.serializers.associacao_serializer import AssociacaoSerializer
from ....core.models import Associacao

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
    rateios = RateioDespesaCreateSerializer(many=True, required=False)

    def create(self, validated_data):
        rateios = validated_data.pop('rateios')

        # if not rateios:
        #     msgError = "Pelo menos uma linha de rateio deve ser enviada!"
        #     log.info(msgError)
        #     raise ValidationError(msgError)

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

    def update(self, instance, validated_data):
        rateios_json = validated_data.pop('rateios')
        instance.rateios.all().delete()

        rateios_lista = []
        for rateio_json in rateios_json:
            rateios_object = RateioDespesaCreateSerializer(
            ).create(rateio_json)
            rateios_lista.append(rateios_object)

        update_instance_from_dict(instance, validated_data)
        instance.rateios.set(rateios_lista)
        instance.save()

        return instance

    class Meta:
        model = Despesa
        exclude = ('id',)


class DespesaListSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )

    tipo_documento = TipoDocumentoListSerializer()

    class Meta:
        model = Despesa
        fields = ('uuid', 'associacao', 'numero_documento', 'tipo_documento', 'data_documento', 'cpf_cnpj_fornecedor',
                  'nome_fornecedor', 'valor_total', 'valor_ptrf')


class DespesaConciliacaoSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )

    tipo_documento = TipoDocumentoListSerializer()
    tipo_transacao = TipoTransacaoSerializer()

    class Meta:
        model = Despesa
        fields = (
            'associacao',
            'numero_documento',
            'tipo_documento',
            'tipo_transacao',
            'documento_transacao',
            'data_documento',
            'data_transacao',
            'cpf_cnpj_fornecedor',
            'nome_fornecedor',
            'valor_ptrf',
            'valor_total',
            'status',
            'conferido',
            'uuid',
        )
