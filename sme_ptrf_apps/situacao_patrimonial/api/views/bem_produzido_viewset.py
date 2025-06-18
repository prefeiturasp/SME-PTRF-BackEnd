import logging

from waffle.mixins import WaffleFlagMixin

from decimal import Decimal
from django.db.models import Sum

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.situacao_patrimonial.api.serializers.bem_produzido_serializer import BemProduzidoRascunhoSerializer
from sme_ptrf_apps.users.permissoes import PermissaoApiUe

from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido, BemProduzidoItem, BemProduzidoDespesa, BemProduzidoRateio
from sme_ptrf_apps.situacao_patrimonial.api.serializers import BemProduzidoSerializer, BemProduzidoCreateSerializer, BemProduzidoItemCreateSerializer
from sme_ptrf_apps.despesas.models import Despesa

logger = logging.getLogger(__name__)


class BemProduzidoViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "situacao-patrimonial"
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = BemProduzido.objects.all().order_by('id')
    serializer_class = BemProduzidoSerializer
    pagination_class = CustomPagination
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_queryset(self):
        qs = self.queryset
        associacao = self.request.query_params.get('associacao_uuid', None)

        if associacao is not None:
            qs = qs.filter(associacao__uuid=associacao)

        return qs

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BemProduzidoCreateSerializer
        return BemProduzidoSerializer

    @action(detail=True, methods=['post'], url_path='excluir-lote', permission_classes=[IsAuthenticated & PermissaoApiUe])
    def excluir_em_lote(self, request, *args, **kwargs):
        bem_produzido = self.get_object()
        uuids_para_remover = request.data.get('uuids', [])

        if not isinstance(uuids_para_remover, list) or not all(isinstance(u, str) for u in uuids_para_remover):        
            return Response({'mensagem': 'A lista de UUIDs é obrigatória e deve conter apenas strings.'}, status=status.HTTP_400_BAD_REQUEST)

        despesas_remover = BemProduzidoDespesa.objects.filter(
            uuid__in=uuids_para_remover,
            bem_produzido=bem_produzido
        )

        quantidade = despesas_remover.count()
        despesas_remover.delete()

        return Response({
            'mensagem': f'{quantidade} despesas removidas do bem produzido.'
        }, status=status.HTTP_200_OK)
        
    @action(detail=True, methods=['patch'], url_path='cadastrar-bem', permission_classes=[IsAuthenticated & PermissaoApiUe])
    def cadastrar_bem(self, request, *args, **kwargs):
        bem_produzido = self.get_object()
        itens_data = request.data.get('itens', [])

        itens_uuids = []
        for item in itens_data:
            if 'uuid' in item:
                itens_uuids.append(item['uuid'])

        duplicados = {uuid for uuid in itens_uuids if itens_uuids.count(uuid) > 1}
        if duplicados:
            raise ValidationError(
                f"Os seguintes UUIDs estão duplicados: {', '.join(str(d) for d in duplicados)}"
            )

        if not isinstance(itens_data, list) or not itens_data:
            return Response({'mensagem': 'A lista de itens é obrigatória.'}, status=status.HTTP_400_BAD_REQUEST)

        valor_total_itens = Decimal('0')
        itens_para_criar = []
        itens_para_atualizar = []

        for item_data in itens_data:
            uuid_item = item_data.get('uuid')

            if uuid_item:
                # Atualização de item existente
                try:
                    item_existente = BemProduzidoItem.objects.get(uuid=uuid_item, bem_produzido=bem_produzido)
                except BemProduzidoItem.DoesNotExist:
                    return Response({'mensagem': f'Item com UUID {uuid_item} não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

                serializer = BemProduzidoItemCreateSerializer(item_existente, data=item_data)
            else:
                # Criação de novo item
                serializer = BemProduzidoItemCreateSerializer(data=item_data)

            serializer.is_valid(raise_exception=True)

            quantidade = serializer.validated_data['quantidade']
            valor_individual = serializer.validated_data['valor_individual']
            valor_total_item = quantidade * valor_individual
            valor_total_itens += valor_total_item

            if uuid_item:
                itens_para_atualizar.append((item_existente, serializer))
            else:
                itens_para_criar.append(serializer)

        # Soma dos rateios
        valor_rateios = BemProduzidoRateio.objects.filter(
            bem_produzido_despesa__bem_produzido=bem_produzido
        ).aggregate(
            total=Sum('valor_utilizado')
        )['total'] or Decimal('0')

        # Soma dos recursos próprios
        valor_recurso_proprio = BemProduzidoDespesa.objects.filter(
            bem_produzido=bem_produzido
        ).aggregate(
            total=Sum('valor_recurso_proprio_utilizado')
        )['total'] or Decimal('0')

        valor_total_esperado = valor_rateios + valor_recurso_proprio

        # Validação de correspondência dos valores
        if valor_total_itens != valor_total_esperado:
            return Response({
                'mensagem': 'A soma dos valores dos itens não bate com o valor total disponível.',
                'valor_total_itens': float(valor_total_itens),
                'valor_total_esperado': float(valor_total_esperado)
            }, status=status.HTTP_400_BAD_REQUEST)

        # Cria novos itens
        for serializer in itens_para_criar:
            serializer.save(bem_produzido=bem_produzido)

        # Atualiza itens existentes
        for instance, serializer in itens_para_atualizar:
            serializer.save()

        # Atualiza status para COMPLETO
        bem_produzido.status = BemProduzido.STATUS_COMPLETO
        bem_produzido.save(update_fields=["status"])

        return Response({'mensagem': 'Itens processados com sucesso. Bem Produzido marcado como completo.'}, status=status.HTTP_201_CREATED)

    
    @action(detail=True, methods=['post'], url_path='adicionar-despesas-bem', permission_classes=[IsAuthenticated & PermissaoApiUe])
    def adicionar_em_lote(self, request, *args, **kwargs):
        bem_produzido = self.get_object()
        uuids_para_adicionar = request.data.get('uuids', [])

        if not isinstance(uuids_para_adicionar, list) or not all(isinstance(u, str) for u in uuids_para_adicionar):
            return Response({'mensagem': 'A lista de UUIDs é obrigatória e deve conter apenas strings.'}, status=status.HTTP_400_BAD_REQUEST)

        despesas = Despesa.objects.filter(uuid__in=uuids_para_adicionar)

        if not despesas.exists():
            return Response({'mensagem': 'Nenhuma despesa válida encontrada com os UUIDs fornecidos.'}, status=status.HTTP_404_NOT_FOUND)

        atualizadas = 0
        for despesa in despesas:
            exists = BemProduzidoDespesa.objects.filter(bem_produzido=bem_produzido, despesa=despesa).exists()
            if not exists:
                BemProduzidoDespesa.objects.create(bem_produzido=bem_produzido, despesa=despesa)
                atualizadas += 1

        return Response({
            'mensagem': f'{atualizadas} despesas associadas ao bem produzido com sucesso.'
        }, status=status.HTTP_200_OK)

class BemProduzidoRascunhoViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "situacao-patrimonial"
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = BemProduzido.objects.all().order_by('id')
    serializer_class = BemProduzidoRascunhoSerializer
    pagination_class = CustomPagination
    http_method_names = ['post', 'put', 'patch', 'delete']

    def get_queryset(self):
        qs = self.queryset
        associacao = self.request.query_params.get('associacao_uuid', None)

        if associacao is not None:
            qs = qs.filter(associacao__uuid=associacao)

        return qs
