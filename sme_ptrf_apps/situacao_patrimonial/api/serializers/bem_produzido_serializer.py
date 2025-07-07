from decimal import Decimal
from django.db.models import Sum
from django.db import transaction
from rest_framework import serializers

from django.db.models import Sum
from sme_ptrf_apps.despesas.models.despesa import Despesa
from sme_ptrf_apps.despesas.models.rateio_despesa import RateioDespesa
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido, BemProduzidoDespesa, BemProduzidoItem, BemProduzidoRateio
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.situacao_patrimonial.api.serializers.bem_produzido_despesa_serializer import BemProduzidoDespesaSerializer
from sme_ptrf_apps.situacao_patrimonial.api.serializers.bem_produzido_item_serializer import BemProduzidoItemSerializer, BemProduzidoRascunhoItemSerializer
from sme_ptrf_apps.despesas.models.especificacao_material_servico import EspecificacaoMaterialServico


class BemProduzidoSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(queryset=Associacao.objects.all(), slug_field='uuid')
    despesas = serializers.SerializerMethodField()
    items = BemProduzidoItemSerializer(many=True)
    valor_total_informado = serializers.SerializerMethodField()

    class Meta:
        model = BemProduzido
        fields = ('uuid', 'associacao', 'status', 'despesas', 'items', 'valor_total_informado')
        read_only_fields = ['despesas']

    def get_despesas(self, obj):
        despesas = obj.despesas.all()
        serializer = BemProduzidoDespesaSerializer(
            despesas,
            many=True,
            context={'bem_produzido_uuid': obj.uuid}
        )
        return serializer.data

    def get_valor_total_informado(self, obj):
        total_recursos_proprios = BemProduzidoDespesa.objects.filter(bem_produzido=obj).aggregate(
            total=Sum('valor_recurso_proprio_utilizado')
        )['total'] or Decimal('0.00')

        total_rateios = BemProduzidoRateio.objects.filter(bem_produzido_despesa__bem_produzido=obj).aggregate(
            total=Sum('valor_utilizado')
        )['total'] or Decimal('0.00')

        total = total_rateios + total_recursos_proprios

        return total


class BemProduzidoItemSerializer(serializers.Serializer):
    uuid = serializers.SlugRelatedField(queryset=BemProduzidoItem.objects.all(), slug_field='uuid')
    especificacao_do_bem = serializers.SlugRelatedField(
        queryset=EspecificacaoMaterialServico.objects.all(), slug_field='uuid')
    num_processo_incorporacao = serializers.CharField()
    quantidade = serializers.IntegerField()
    valor_individual = serializers.DecimalField(max_digits=12, decimal_places=2)


class BemProduzidoRateioSerializer(serializers.Serializer):
    uuid = serializers.SlugRelatedField(queryset=RateioDespesa.objects.all(), slug_field='uuid')
    valor_utilizado = serializers.DecimalField(max_digits=12, decimal_places=2)


class RecursoProprioSerializer(serializers.Serializer):
    valor_recurso_proprio_utilizado = serializers.DecimalField(max_digits=10, decimal_places=2)
    despesa = serializers.SlugRelatedField(queryset=Despesa.objects.all(), slug_field='uuid')


class BemProduzidoSaveSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(queryset=Associacao.objects.all(), slug_field='uuid')
    despesas = serializers.ListField(child=serializers.UUIDField(), write_only=True)
    rateios = BemProduzidoRateioSerializer(many=True, write_only=True, required=False)
    itens = BemProduzidoItemSerializer(many=True, write_only=True, required=False)
    recursos_proprios = RecursoProprioSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = BemProduzido
        fields = (
            'uuid',
            'associacao',
            'despesas',
            'rateios',
            'itens',
            'recursos_proprios',
            'status'
        )

    @transaction.atomic
    def create(self, validated_data):
        despesas = validated_data.pop("despesas", [])
        rateios = validated_data.pop("rateios", [])
        itens = validated_data.pop("itens", [])
        recursos_proprios = validated_data.pop("recursos_proprios", [])

        bem_produzido = BemProduzido.objects.create(
            associacao=validated_data['associacao']
        )

        self._handle_despesas(bem_produzido, despesas)
        self._handle_rateios(bem_produzido, rateios)
        self._handle_recursos_proprios(bem_produzido, recursos_proprios)
        self._handle_itens(bem_produzido, itens)
        self._validate_valor_total_itens(bem_produzido, itens)

        bem_produzido.completar()

        return bem_produzido

    @transaction.atomic
    def update(self, instance, validated_data):
        despesas = validated_data.pop("despesas", [])
        rateios = validated_data.pop("rateios", [])
        itens = validated_data.pop("itens", [])
        recursos_proprios = validated_data.pop("recursos_proprios", [])

        self._handle_despesas(instance, despesas)
        self._handle_rateios(instance, rateios, update=True)
        self._handle_recursos_proprios(instance, recursos_proprios)
        self._handle_itens(instance, itens, update=True)
        self._validate_valor_total_itens(instance, itens)

        instance.completar()

        return instance

    def _handle_despesas(self, bem_produzido, despesas):
        for despesa_uuid in despesas:
            try:
                despesa = Despesa.objects.get(uuid=despesa_uuid)
            except Despesa.DoesNotExist:
                raise serializers.ValidationError(f"Despesa com UUID {despesa_uuid} não encontrada.")

            BemProduzidoDespesa.objects.get_or_create(
                bem_produzido=bem_produzido,
                despesa=despesa
            )

    def _handle_rateios(self, bem_produzido, rateios, update=False):
        for rateio_payload in rateios:
            rateio = rateio_payload['uuid']
            try:
                bem_produzido_despesa = bem_produzido.despesas.get(despesa__uuid=rateio.despesa.uuid)
            except BemProduzidoDespesa.despesa.RelatedObjectDoesNotExist:
                raise serializers.ValidationError(
                    f"Bem Produzido Despesa com despesa UUID {rateio.despesa.uuid} não encontrado.")

            if update:
                bem_produzido_rateio, _ = bem_produzido_despesa.rateios.get_or_create(rateio=rateio)

                valor_disponivel = BemProduzidoRateio.valor_disponivel_por_rateio(rateio, bem_produzido_rateio)
                if rateio_payload['valor_utilizado'] > valor_disponivel:
                    raise serializers.ValidationError(
                        {"message": f"O valor utilizado ({rateio_payload['valor_utilizado']}) excede o valor disponível ({valor_disponivel}) para o rateio {rateio.uuid}."})

                bem_produzido_rateio.valor_utilizado = rateio_payload['valor_utilizado']
                bem_produzido_rateio.save()
            else:
                BemProduzidoRateio.objects.create(
                    bem_produzido_despesa=bem_produzido_despesa,
                    rateio=rateio,
                    valor_utilizado=rateio_payload["valor_utilizado"]
                )

    def _handle_itens(self, bem_produzido, itens, update=False):
        for item_payload in itens:
            item_uuid = item_payload.get("uuid")
            if update and item_uuid:
                continue
            BemProduzidoItem.objects.create(bem_produzido=bem_produzido, **item_payload)

    def _handle_recursos_proprios(self, bem_produzido, recursos_proprios):
        for recurso_data in recursos_proprios:
            despesa = recurso_data["despesa"]

            try:
                bem_produzido_despesa = bem_produzido.despesas.get(despesa__uuid=despesa.uuid)
            except BemProduzidoDespesa.despesa.RelatedObjectDoesNotExist:
                raise serializers.ValidationError(
                    f"Bem Produzido Despesa com despesa UUID {despesa.uuid} não encontrada.")

            valor_disponivel = despesa.valor_recursos_proprios

            if recurso_data['valor_recurso_proprio_utilizado'] > valor_disponivel:
                raise serializers.ValidationError(
                    {"message": f"O valor utilizado ({recurso_data['valor_recurso_proprio_utilizado']}) excede o valor disponível ({valor_disponivel}) de recursos próprios da despesa {despesa.uuid}."})

            bem_produzido_despesa.valor_recurso_proprio_utilizado = recurso_data['valor_recurso_proprio_utilizado']
            bem_produzido_despesa.save()

    def _validate_valor_total_itens(self, instance, itens):
        valor_total_itens = sum([
            item['quantidade'] * item['valor_individual'] for item in itens
        ])

        valor_total_esperado = instance.valor_total_utilizado()

        if valor_total_itens != valor_total_esperado:
            raise serializers.ValidationError({
                'mensagem': 'A soma dos valores dos itens não bate com o valor total disponível.',
                'valor_total_itens': float(valor_total_itens),
                'valor_total_esperado': float(valor_total_esperado)
            })


class BemProduzidoSaveRacunhoSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(queryset=Associacao.objects.all(), slug_field='uuid')
    despesas = serializers.ListField(child=serializers.UUIDField(), write_only=True)
    rateios = BemProduzidoRateioSerializer(many=True, write_only=True, required=False)
    itens = BemProduzidoItemSerializer(many=True, write_only=True, required=False)
    recursos_proprios = RecursoProprioSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = BemProduzido
        fields = (
            'uuid',
            'associacao',
            'despesas',
            'rateios',
            'itens',
            'recursos_proprios',
            'status'
        )

    @transaction.atomic
    def create(self, validated_data):
        despesas = validated_data.pop("despesas", [])
        rateios = validated_data.pop("rateios", [])
        itens = validated_data.pop("itens", [])
        recursos_proprios = validated_data.pop("recursos_proprios", [])

        bem_produzido = BemProduzido.objects.create(
            associacao=validated_data['associacao']
        )

        self._handle_despesas(bem_produzido, despesas)
        self._handle_rateios(bem_produzido, rateios)
        self._handle_recursos_proprios(bem_produzido, recursos_proprios)
        self._handle_itens(bem_produzido, itens)

        bem_produzido.rascunhar()

        return bem_produzido

    @transaction.atomic
    def update(self, instance, validated_data):
        despesas = validated_data.pop("despesas", [])
        rateios = validated_data.pop("rateios", [])
        itens = validated_data.pop("itens", [])
        recursos_proprios = validated_data.pop("recursos_proprios", [])

        self._handle_despesas(instance, despesas)
        self._handle_rateios(instance, rateios, update=True)
        self._handle_recursos_proprios(instance, recursos_proprios)
        self._handle_itens(instance, itens, update=True)

        instance.rascunhar()

        return instance

    def _handle_despesas(self, bem_produzido, despesas):
        for despesa_uuid in despesas:
            try:
                despesa = Despesa.objects.get(uuid=despesa_uuid)
            except Despesa.DoesNotExist:
                raise serializers.ValidationError(f"Despesa com UUID {despesa_uuid} não encontrada.")

            BemProduzidoDespesa.objects.get_or_create(
                bem_produzido=bem_produzido,
                despesa=despesa
            )

    def _handle_rateios(self, bem_produzido, rateios, update=False):
        for rateio_payload in rateios:
            rateio = rateio_payload['uuid']
            try:
                bem_produzido_despesa = bem_produzido.despesas.get(despesa__uuid=rateio.despesa.uuid)
            except BemProduzidoDespesa.despesa.RelatedObjectDoesNotExist:
                raise serializers.ValidationError(
                    f"Bem Produzido Despesa com despesa UUID {rateio.despesa.uuid} não encontrado.")

            if update:
                bem_produzido_rateio, _ = bem_produzido_despesa.rateios.get_or_create(rateio=rateio)

                valor_disponivel = BemProduzidoRateio.valor_disponivel_por_rateio(rateio, bem_produzido_rateio)
                if rateio_payload['valor_utilizado'] > valor_disponivel:
                    raise serializers.ValidationError(
                        {"message": f"O valor utilizado ({rateio_payload['valor_utilizado']}) excede o valor disponível ({valor_disponivel}) para o rateio {rateio.uuid}."})

                bem_produzido_rateio.valor_utilizado = rateio_payload['valor_utilizado']
                bem_produzido_rateio.save()
            else:
                BemProduzidoRateio.objects.create(
                    bem_produzido_despesa=bem_produzido_despesa,
                    rateio=rateio,
                    valor_utilizado=rateio_payload["valor_utilizado"]
                )

    def _handle_itens(self, bem_produzido, itens, update=False):
        for item_payload in itens:
            item_uuid = item_payload.get("uuid")
            if update and item_uuid:
                continue
            BemProduzidoItem.objects.create(bem_produzido=bem_produzido, **item_payload)

    def _handle_recursos_proprios(self, bem_produzido, recursos_proprios):
        for recurso_data in recursos_proprios:
            despesa = recurso_data["despesa"]

            try:
                bem_produzido_despesa = bem_produzido.despesas.get(despesa__uuid=despesa.uuid)
            except BemProduzidoDespesa.despesa.RelatedObjectDoesNotExist:
                raise serializers.ValidationError(
                    f"Bem Produzido Despesa com despesa UUID {despesa.uuid} não encontrada.")

            valor_disponivel = despesa.valor_recursos_proprios

            if recurso_data['valor_recurso_proprio_utilizado'] > valor_disponivel:
                raise serializers.ValidationError(
                    {"message": f"O valor utilizado ({recurso_data['valor_recurso_proprio_utilizado']}) excede o valor disponível ({valor_disponivel}) de recursos próprios da despesa {despesa.uuid}."})

            bem_produzido_despesa.valor_recurso_proprio_utilizado = recurso_data['valor_recurso_proprio_utilizado']
            bem_produzido_despesa.save()

    def _validate_valor_total_itens(self, instance, itens):
        valor_total_itens = sum([
            item['quantidade'] * item['valor_individual'] for item in itens
        ])

        valor_total_esperado = instance.valor_total_utilizado()

        if valor_total_itens != valor_total_esperado:
            raise serializers.ValidationError({
                'mensagem': 'A soma dos valores dos itens não bate com o valor total disponível.',
                'valor_total_itens': float(valor_total_itens),
                'valor_total_esperado': float(valor_total_esperado)
            })
