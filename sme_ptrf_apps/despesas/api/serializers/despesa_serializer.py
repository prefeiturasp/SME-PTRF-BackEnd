import logging

from rest_framework import serializers

from .rateio_despesa_serializer import RateioDespesaSerializer, RateioDespesaTabelaGastosEscolaSerializer
from .tipo_documento_serializer import TipoDocumentoSerializer, TipoDocumentoListSerializer
from .tipo_transacao_serializer import TipoTransacaoSerializer
from ..serializers.rateio_despesa_serializer import RateioDespesaCreateSerializer
from ...models import Despesa, RateioDespesa
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

        despesa = Despesa.objects.create(**validated_data)
        despesa.verifica_cnpj_zerado()
        despesa.verifica_data_documento_vazio()
        log.info("Criando despesa com uuid: {}".format(despesa.uuid))

        rateios_lista = []
        for rateio in rateios:
            rateio["eh_despesa_sem_comprovacao_fiscal"] = despesa.eh_despesa_sem_comprovacao_fiscal(
                validated_data['cpf_cnpj_fornecedor']
            )
            rateio_object = RateioDespesaCreateSerializer().create(rateio)
            rateios_lista.append(rateio_object)
        despesa.rateios.set(rateios_lista)
        despesa.atualiza_status()
        log.info("Despesa {}, Rateios: {}".format(despesa.uuid, rateios_lista))

        log.info("Criação de despesa finalizada!")

        return despesa

    def update(self, instance, validated_data):
        rateios = validated_data.pop('rateios')

        # Atualiza campos da despesa
        Despesa.objects.filter(uuid=instance.uuid).update(**validated_data)

        # Atualiza os rateios
        log.info(f"Atualizando rateios da despesa {instance.uuid}")
        keep_rateios = []  # rateios que serão mantidos. qualquer um que não estiver na lista será apagado.
        for rateio in rateios:
            if "uuid" in rateio.keys():
                log.info(f"Encontrada chave uuid no rateio {rateio['uuid']} R${rateio['valor_rateio']}. Será atualizado.")
                if RateioDespesa.objects.filter(uuid=rateio["uuid"]).exists():
                    log.info(f"Rateio encontrado {rateio['uuid']} R${rateio['valor_rateio']}")
                    RateioDespesa.objects.filter(uuid=rateio["uuid"]).update(**rateio)
                    rateio_updated = RateioDespesa.objects.get(uuid=rateio["uuid"])
                    keep_rateios.append(rateio_updated.uuid)
                else:
                    log.info(f"Rateio NÃO encontrado {rateio['uuid']} R${rateio['valor_rateio']}")
                    continue
            else:
                log.info(f"Não encontrada chave uuid de rateio R${rateio['valor_rateio']}. Será criado.")
                rateio_updated = RateioDespesa.objects.create(**rateio, despesa=instance)
                keep_rateios.append(rateio_updated.uuid)

        # Apaga rateios da despesa que não estão na lista de rateios a serem mantidos
        for rateio in instance.rateios.all():
            if rateio.uuid not in keep_rateios:
                log.info(f"Rateio apagado {rateio.uuid} R${rateio.valor_rateio}")
                rateio.delete()

        # Retorna a despesa atualizada
        despesa_updated = Despesa.objects.get(uuid=instance.uuid)

        return despesa_updated

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
    tipo_transacao = TipoTransacaoSerializer()

    class Meta:
        model = Despesa
        fields = ('uuid', 'associacao', 'numero_documento', 'tipo_documento', 'data_documento', 'cpf_cnpj_fornecedor',
                  'nome_fornecedor', 'valor_total', 'valor_ptrf', 'data_transacao', 'tipo_transacao', 'documento_transacao')


class DespesaListComRateiosSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )

    tipo_documento = TipoDocumentoListSerializer()
    tipo_transacao = TipoTransacaoSerializer()
    rateios = RateioDespesaTabelaGastosEscolaSerializer(many=True)

    receitas_saida_do_recurso = serializers.SerializerMethodField('get_recurso_externo')

    def get_recurso_externo(self, despesa):
        return despesa.receitas_saida_do_recurso.first().uuid if despesa.receitas_saida_do_recurso.exists() else None

    class Meta:
        model = Despesa
        fields = ('uuid', 'associacao', 'numero_documento', 'status', 'tipo_documento', 'data_documento', 'cpf_cnpj_fornecedor',
                  'nome_fornecedor', 'valor_total', 'valor_ptrf', 'data_transacao', 'tipo_transacao', 'documento_transacao', 'rateios', 'receitas_saida_do_recurso',)


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


class DespesaDocumentoMestreSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )

    tipo_documento = TipoDocumentoListSerializer()
    tipo_transacao = TipoTransacaoSerializer()

    receitas_saida_do_recurso = serializers.SerializerMethodField('get_recurso_externo')

    def get_recurso_externo(self, despesa):
        return despesa.receitas_saida_do_recurso.first().uuid if despesa.receitas_saida_do_recurso.exists() else None

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
            'receitas_saida_do_recurso',
        )
