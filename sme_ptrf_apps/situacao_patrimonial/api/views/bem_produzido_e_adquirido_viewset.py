
import datetime
import logging
import uuid
from itertools import chain
from waffle.mixins import WaffleFlagMixin

from django.db.models import Q
from django.core.exceptions import ValidationError

from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import PermissaoApiUe
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzidoItem
from sme_ptrf_apps.situacao_patrimonial.api.serializers import BemProduzidoEAdquiridoSerializer
from sme_ptrf_apps.despesas.models import RateioDespesa
from sme_ptrf_apps.core.models.periodo import Periodo
from sme_ptrf_apps.core.models.acao import Acao
from sme_ptrf_apps.core.models.acao_associacao import AcaoAssociacao
from sme_ptrf_apps.core.models.associacao import Associacao
from sme_ptrf_apps.core.models.conta_associacao import ContaAssociacao
from sme_ptrf_apps.sme.tasks.exportar_bens_produzidos_adquiridos import exportar_bens_produzidos_adquiridos_async

logger = logging.getLogger(__name__)


class BemAdquiridoProduzidoViewSet(WaffleFlagMixin, ViewSet):
    waffle_flag = "situacao-patrimonial"
    permission_classes = [IsAuthenticated & PermissaoApiUe]

    def list(self, request):
        associacao_uuid = request.query_params.get('associacao_uuid')
        if not associacao_uuid:
            return Response({
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da associação.'
            }, status=status.HTTP_400_BAD_REQUEST)

        especificacao_bem = request.query_params.get('especificacao_bem')
        fornecedor = request.query_params.get('fornecedor')
        acao_uuid = request.query_params.get('acao_associacao_uuid')
        conta_uuid = request.query_params.get('conta_associacao_uuid')
        periodos_uuid = request.query_params.get('periodos_uuid')

        if periodos_uuid:
            try:
                periodos_uuid = [uuid.UUID(u.strip()) for u in periodos_uuid.split(",") if u.strip()]
            except Exception:
                raise ValidationError("Parâmetro período inválido. Deve ser uma lista de UUIDs separadas por vírgula.")

        data_inicio = request.query_params.get('data_inicio')
        data_fim = request.query_params.get('data_fim')

        bens_produzidos = BemProduzidoItem.objects.filter(bem_produzido__associacao__uuid=associacao_uuid)
        bens_produzidos = self.filtrar_bens_produzidos(
            bens_produzidos, especificacao_bem, fornecedor, acao_uuid, conta_uuid, periodos_uuid, data_inicio, data_fim
        )

        bens_adquiridos = RateioDespesa.rateios_completos_de_capital().filter(despesa__associacao__uuid=associacao_uuid)
        bens_adquiridos = self.filtrar_bens_adquiridos(
            bens_adquiridos, especificacao_bem, fornecedor, acao_uuid, conta_uuid, periodos_uuid, data_inicio, data_fim
        )

        combined = list(chain(bens_produzidos, bens_adquiridos))

        paginator = CustomPagination()
        page = paginator.paginate_queryset(combined, request)
        serializer = BemProduzidoEAdquiridoSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def filtrar_bens_produzidos(self, queryset, especificacao_bem, fornecedor, acao_uuid, conta_uuid, periodos_uuid, data_inicio, data_fim):
        if especificacao_bem:
            queryset = queryset.filter(especificacao_do_bem__descricao__unaccent__icontains=especificacao_bem)
        if fornecedor:
            queryset = queryset.filter(
                bem_produzido__despesas__despesa__nome_fornecedor__unaccent__icontains=fornecedor)
        if acao_uuid:
            queryset = queryset.filter(
                bem_produzido__despesas__rateios__rateio__acao_associacao__uuid=acao_uuid).distinct()
        if conta_uuid:
            queryset = queryset.filter(
                bem_produzido__despesas__rateios__rateio__conta_associacao__uuid=conta_uuid).distinct()
        if periodos_uuid:
            periodos = Periodo.objects.filter(uuid__in=periodos_uuid)
            periodo_filters = Q()

            for periodo in periodos:
                if periodo.data_inicio_realizacao_despesas and periodo.data_fim_realizacao_despesas:
                    periodo_filters |= Q(
                        criado_em__gte=periodo.data_inicio_realizacao_despesas,
                        criado_em__lte=periodo.data_fim_realizacao_despesas
                    )
                elif periodo.data_inicio_realizacao_despesas:
                    periodo_filters |= Q(
                        criado_em__gte=periodo.data_inicio_realizacao_despesas,
                    )

            queryset = queryset.filter(periodo_filters)
        if data_inicio:
            queryset = queryset.filter(criado_em__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(criado_em__lte=data_fim)
        return queryset

    def filtrar_bens_adquiridos(self, queryset, especificacao_bem, fornecedor, acao_uuid, conta_uuid, periodos_uuid, data_inicio, data_fim):
        if especificacao_bem:
            queryset = queryset.filter(especificacao_material_servico__descricao__unaccent__icontains=especificacao_bem)
        if fornecedor:
            queryset = queryset.filter(despesa__nome_fornecedor__unaccent__icontains=fornecedor)
        if acao_uuid:
            queryset = queryset.filter(acao_associacao__uuid=acao_uuid)
        if conta_uuid:
            queryset = queryset.filter(conta_associacao__uuid=conta_uuid)
        if periodos_uuid:
            periodos = Periodo.objects.filter(uuid__in=periodos_uuid)
            periodo_filters = Q()
            for periodo in periodos:
                if periodo.data_inicio_realizacao_despesas and periodo.data_fim_realizacao_despesas:
                    periodo_filters |= Q(
                        despesa__data_documento__gte=periodo.data_inicio_realizacao_despesas,
                        despesa__data_documento__lte=periodo.data_fim_realizacao_despesas
                    )
                elif periodo.data_inicio_realizacao_despesas:
                    periodo_filters |= Q(
                        despesa__data_documento__gte=periodo.data_inicio_realizacao_despesas,
                    )

            queryset = queryset.filter(periodo_filters)
        if data_inicio:
            queryset = queryset.filter(despesa__data_documento__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(despesa__data_documento__lte=data_fim)
        return queryset

    @action(
        detail=False,
        methods=['get'],
        url_path='exportar',
        permission_classes=[PermissaoApiUe]
    )
    def exportar(self, request):
        associacao_uuid = request.query_params.get('associacao_uuid')
        if not associacao_uuid:
            return Response({
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da associação.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Obter parâmetros de filtro
        especificacao_bem = request.query_params.get('especificacao_bem')
        fornecedor = request.query_params.get('fornecedor')
        acao_associacao_uuid = request.query_params.get('acao_associacao_uuid')
        conta_uuid = request.query_params.get('conta_associacao_uuid')
        periodos_uuid = request.query_params.get('periodos_uuid')
        data_inicio = request.query_params.get('data_inicio')
        data_fim = request.query_params.get('data_fim')
        user_id = request.user.id
        # Crie a string de filtros separados por ;
        filtros = []
        
        if periodos_uuid:
            filtros.append(f"por período: {periodos_uuid}")
        if especificacao_bem:
            filtros.append(f"por tipo de bem: {especificacao_bem}")
        if fornecedor:
            filtros.append(f"por fornecedor: {fornecedor}")
        if acao_associacao_uuid:
            try:
                logger.info(f"Ação da associação informada: {acao_associacao_uuid}")
                acao_associacao = AcaoAssociacao.objects.get(uuid=acao_associacao_uuid)
                filtros.append(f"por ação: {acao_associacao.acao.nome}")
            except AcaoAssociacao.DoesNotExist:
                return Response({
                    'erro': 'acao_associacao_nao_encontrada',
                    'mensagem': 'A ação da associação informada não foi encontrada.'
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Erro ao buscar ação da associação: {e}")
                return Response({
                    'erro': 'erro_interno',
                    'mensagem': 'Erro interno ao buscar a ação da associação.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if conta_uuid:
            try:
                conta_associacao = ContaAssociacao.objects.get(uuid=conta_uuid)
                filtros.append(f"por conta: {conta_associacao.tipo_conta.nome}")
            except ContaAssociacao.DoesNotExist:
                return Response({
                    'erro': 'conta_associacao_nao_encontrada',
                    'mensagem': 'A conta da associação informada não foi encontrada.'
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Erro ao buscar a conta da associação: {e}")
                return Response({
                    'erro': 'erro_interno',
                    'mensagem': 'Erro interno ao buscar a conta da associação.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        if data_inicio and data_fim:
            # Formate a data para o formato dd/mm/yyyy
            print(f"Data de início: {data_inicio}")
            print(f"Data de fim: {data_fim}")

            data_inicio_formatada = datetime.datetime.strptime(data_inicio, '%Y-%m-%d').strftime('%d/%m/%Y')
            data_fim_formatada = datetime.datetime.strptime(data_fim, '%Y-%m-%d').strftime('%d/%m/%Y')
            
            filtros.append(f"por data do documento: {data_inicio_formatada} até {data_fim_formatada}")
            
        filtros_str = '; '.join(filtros)

        # Processar periodos_uuid se fornecido
        if periodos_uuid:
            try:
                periodos_uuid = [uuid.UUID(u.strip()) for u in periodos_uuid.split(",") if u.strip()]
            except Exception:
                return Response({
                    'erro': 'parametro_invalido',
                    'mensagem': 'Parâmetro período inválido. Deve ser uma lista de UUIDs separadas por vírgula.'
                }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Chamar task assíncrona de exportação
            task = exportar_bens_produzidos_adquiridos_async.delay(
                associacao_uuid=associacao_uuid,
                especificacao_bem=especificacao_bem,
                fornecedor=fornecedor,
                acao_uuid=acao_associacao_uuid,
                conta_uuid=conta_uuid,
                periodos_uuid=periodos_uuid,
                data_inicio=data_inicio,
                data_fim=data_fim,
                user_id=user_id,
                filtros_str=filtros_str
            )

            logger.info(f"Task de exportação iniciada com ID: {task.id}")

            return Response({
                'mensagem': 'Exportação iniciada com sucesso. O arquivo será processado em background.',
                'task_id': task.id,
                'status': 'processing'
            }, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            logger.error(f"Erro ao iniciar exportação: {e}")
            return Response({
                'erro': 'erro_interno',
                'mensagem': 'Erro interno ao iniciar a exportação.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)