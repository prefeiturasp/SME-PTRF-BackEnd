import logging

from rest_framework import serializers

from .rateio_despesa_serializer import RateioDespesaSerializer, RateioDespesaTabelaGastosEscolaSerializer
from .tipo_documento_serializer import TipoDocumentoSerializer, TipoDocumentoListSerializer
from .tipo_transacao_serializer import TipoTransacaoSerializer
from .motivo_pagamento_antecipado_serializer import MotivoPagamentoAntecipadoSerializer
from ..serializers.rateio_despesa_serializer import RateioDespesaCreateSerializer
from ...models import Despesa, RateioDespesa, TipoDocumento, TipoTransacao
from ....core.api.serializers.associacao_serializer import AssociacaoSerializer
from ....core.models import Associacao

log = logging.getLogger(__name__)


class DespesaImpostoSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )

    tipo_documento = serializers.SlugRelatedField(
        slug_field='id',
        required=False,
        queryset=TipoDocumento.objects.all()
    )

    tipo_transacao = serializers.SlugRelatedField(
        slug_field='id',
        required=False,
        queryset=TipoTransacao.objects.all()
    )

    rateios = RateioDespesaCreateSerializer(many=True, required=False)

    class Meta:
        model = Despesa
        fields = '__all__'


class DespesaSerializer(serializers.ModelSerializer):
    associacao = AssociacaoSerializer()
    tipo_documento = TipoDocumentoSerializer()
    tipo_transacao = TipoTransacaoSerializer()
    rateios = RateioDespesaSerializer(many=True)
    despesa_imposto = DespesaImpostoSerializer(many=False, required=False)
    despesa_geradora_do_imposto = serializers.SerializerMethodField(method_name="get_despesa_de_imposto",
                                                                    required=False)
    motivos_pagamento_antecipado = MotivoPagamentoAntecipadoSerializer(many=True)

    def get_despesa_de_imposto(self, despesa):
        despesa_geradora_do_imposto = despesa.despesa_geradora_do_imposto.first()
        return DespesaImpostoSerializer(despesa_geradora_do_imposto, many=False).data

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
    despesa_imposto = DespesaImpostoSerializer(many=False, required=False, allow_null=True)

    def create(self, validated_data):
        rateios = validated_data.pop('rateios')
        despesa_imposto = validated_data.pop('despesa_imposto') if validated_data.get('despesa_imposto') else None
        rateios_imposto = despesa_imposto.pop('rateios') if despesa_imposto else None

        motivos_pagamento_antecipado = validated_data.pop('motivos_pagamento_antecipado')
        outros_motivos_pagamento_antecipado = validated_data['outros_motivos_pagamento_antecipado']

        data_transacao = validated_data['data_transacao']
        data_documento = validated_data['data_documento']

        if data_transacao and data_documento:
            if data_transacao < data_documento and not motivos_pagamento_antecipado and not outros_motivos_pagamento_antecipado:
                raise serializers.ValidationError({
                                                      "detail": "Quando a Data da transação for menor que a Data do Documento é necessário enviar os motivos do pagamento antecipado"})
            elif data_transacao >= data_documento:
                motivos_pagamento_antecipado = []
                outros_motivos_pagamento_antecipado = ""

        despesa = Despesa.objects.create(**validated_data)
        # despesa.verifica_cnpj_zerado()
        despesa.verifica_data_documento_vazio()
        log.info("Criando despesa com uuid: {}".format(despesa.uuid))

        rateios_lista = []
        for rateio in rateios:
            rateio["eh_despesa_sem_comprovacao_fiscal"] = despesa.eh_despesa_sem_comprovacao_fiscal
            rateio_object = RateioDespesaCreateSerializer().create(rateio)
            rateios_lista.append(rateio_object)

        motivos_list = []
        for motivo in motivos_pagamento_antecipado:
            motivos_list.append(motivo.id)

        despesa.rateios.set(rateios_lista)
        despesa.motivos_pagamento_antecipado.set(motivos_list)
        despesa.outros_motivos_pagamento_antecipado = outros_motivos_pagamento_antecipado
        despesa.atualiza_status()
        log.info("Despesa {}, Rateios: {}".format(despesa.uuid, rateios_lista))

        log.info("Criação de despesa finalizada!")

        # Despesa de Imposto
        if despesa.retem_imposto and despesa_imposto:
            despesa_do_imposto = Despesa.objects.create(**despesa_imposto)
            log.info("Criando despesa de imposto com uuid: {}".format(despesa_do_imposto.uuid))

            rateios_do_imposto_lista = []
            for rateio in rateios_imposto:
                rateio_object = RateioDespesaCreateSerializer().create(rateio)
                rateios_do_imposto_lista.append(rateio_object)

            despesa_do_imposto.rateios.set(rateios_do_imposto_lista)

            despesa_do_imposto.atualiza_status()

            despesa.despesa_imposto = despesa_do_imposto
            despesa.save()

            log.info("Despesa do imposto {}, Rateios do imposto: {}".format(despesa_do_imposto.uuid,
                                                                            rateios_do_imposto_lista))

            log.info("Criação de despesa de imposto finalizada!")

        return despesa

    def update(self, instance, validated_data):
        rateios = validated_data.pop('rateios')

        despesa_imposto = validated_data.pop('despesa_imposto') if validated_data.get('despesa_imposto') else None
        rateios_imposto = despesa_imposto.pop('rateios') if despesa_imposto else None

        motivos_pagamento_antecipado = validated_data.pop('motivos_pagamento_antecipado')
        outros_motivos_pagamento_antecipado = validated_data['outros_motivos_pagamento_antecipado']

        data_transacao = validated_data['data_transacao']
        data_documento = validated_data['data_documento']

        if data_transacao and data_documento:
            if data_transacao < data_documento and not motivos_pagamento_antecipado and not outros_motivos_pagamento_antecipado:
                raise serializers.ValidationError({"detail": "Quando a Data da transação for menor que a Data do Documento é necessário enviar os motivos do pagamento antecipado"})
            elif data_transacao >= data_documento:
                motivos_pagamento_antecipado = []
                outros_motivos_pagamento_antecipado = ""

        # Atualiza campos da despesa
        Despesa.objects.filter(uuid=instance.uuid).update(**validated_data)

        # Atualiza os rateios
        log.info(f"Atualizando rateios da despesa {instance.uuid}")
        keep_rateios = []  # rateios que serão mantidos. Qualquer um que não estiver na lista será apagado.
        for rateio in rateios:
            if "uuid" in rateio.keys():
                log.info(
                    f"Encontrada chave uuid no rateio {rateio['uuid']} R${rateio['valor_rateio']}. Será atualizado.")
                if RateioDespesa.objects.filter(uuid=rateio["uuid"]).exists():
                    log.info(f"Rateio encontrado {rateio['uuid']} R${rateio['valor_rateio']}")
                    RateioDespesa.objects.filter(uuid=rateio["uuid"]).update(**rateio)
                    rateio_updated = RateioDespesa.objects.get(uuid=rateio["uuid"])

                    # Necessário para forçar a verificação se o rateio está completo
                    rateio_updated.save()

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

        motivos_list = []
        for motivo in motivos_pagamento_antecipado:
            motivos_list.append(motivo.id)

        # Despesa de Imposto
        if validated_data.get('retem_imposto') and despesa_imposto:

            if instance and instance.despesa_imposto and instance.despesa_imposto.uuid:
                Despesa.objects.filter(uuid=instance.despesa_imposto.uuid).update(**despesa_imposto)
                despesa_do_imposto = Despesa.objects.get(uuid=instance.despesa_imposto.uuid)
            else:
                despesa_do_imposto = Despesa.objects.create(**despesa_imposto)

            rateios_do_imposto_lista = []
            uuid_rateios_do_imposto_lista = []
            for rateio in rateios_imposto:
                if "uuid" in rateio.keys():
                    if RateioDespesa.objects.filter(uuid=rateio["uuid"]).exists():
                        RateioDespesa.objects.filter(uuid=rateio["uuid"]).update(**rateio)
                        rateio_updated = RateioDespesa.objects.get(uuid=rateio["uuid"])
                        rateios_do_imposto_lista.append(rateio_updated)
                        uuid_rateios_do_imposto_lista.append(rateio_updated.uuid)
                    else:
                        log.info(f"Rateio NÃO encontrado {rateio['uuid']} R${rateio['valor_rateio']}")
                        continue
                else:
                    log.info(f"Não encontrada chave uuid de rateio R${rateio['valor_rateio']}. Será criado.")
                    rateio_object = RateioDespesaCreateSerializer().create(rateio)
                    rateios_do_imposto_lista.append(rateio_object)
                    uuid_rateios_do_imposto_lista.append(rateio_object.uuid)

            # Apaga rateios da despesa de imposto que não estão na lista de rateios a serem mantidos
            if instance.despesa_imposto and instance.despesa_imposto.rateios:
                for rateio in instance.despesa_imposto.rateios.all():
                    if rateio.uuid not in uuid_rateios_do_imposto_lista:
                        log.info(f"Rateio apagado {rateio.uuid} R${rateio.valor_rateio}")
                        rateio.delete()

            despesa_do_imposto.rateios.set(rateios_do_imposto_lista)
            despesa_do_imposto.save()

            despesa_do_imposto.atualiza_status()

            instance.despesa_imposto = despesa_do_imposto
            instance.save()

        elif not validated_data.get('retem_imposto'):

            if instance and instance.despesa_imposto and instance.despesa_imposto.uuid:
                despesa_do_imposto = Despesa.objects.get(uuid=instance.despesa_imposto.uuid)
                despesa_do_imposto.delete()

        # Retorna a despesa atualizada
        despesa_updated = Despesa.objects.get(uuid=instance.uuid)

        despesa_updated.motivos_pagamento_antecipado.set(motivos_list)
        despesa_updated.outros_motivos_pagamento_antecipado = outros_motivos_pagamento_antecipado
        despesa_updated.save()

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
                  'nome_fornecedor', 'valor_total', 'valor_ptrf', 'data_transacao', 'tipo_transacao',
                  'documento_transacao')


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
        fields = (
        'uuid', 'associacao', 'numero_documento', 'status', 'tipo_documento', 'data_documento', 'cpf_cnpj_fornecedor',
        'nome_fornecedor', 'valor_total', 'valor_ptrf', 'data_transacao', 'tipo_transacao', 'documento_transacao',
        'rateios', 'receitas_saida_do_recurso',)


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
