from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.http import Http404
import logging
import django_filters
from waffle.mixins import WaffleFlagMixin
from decimal import Decimal

from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum, TipoAplicacaoOpcoesEnum
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.paa.models import PrioridadePaa
from sme_ptrf_apps.paa.models.prioridade_paa import SimNaoChoices
from sme_ptrf_apps.paa.api.serializers import (
    PrioridadePaaCreateUpdateSerializer,
    PrioridadePaaListSerializer
)
from sme_ptrf_apps.users.permissoes import PermissaoApiUe, PermissaoAPITodosComGravacao
from sme_ptrf_apps.paa.querysets import queryset_prioridades_paa
from sme_ptrf_apps.core.api.serializers import AcaoAssociacaoRetrieveSerializer

logger = logging.getLogger(__name__)
class PrioridadePaaViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "paa"
    permission_classes = [PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = PrioridadePaa.objects.all()
    serializer_class = PrioridadePaaCreateUpdateSerializer
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_fields = (
        'acao_associacao__uuid',
        'paa__uuid',
        'recurso',
        'prioridade',  # 0 (False) ou 1 (True)
        'programa_pdde__uuid',
        'acao_pdde__uuid',
        'tipo_aplicacao',
        'tipo_despesa_custeio__uuid',
        'especificacao_material__uuid',
    )

    def get_queryset(self):
        qs = super().get_queryset()
        qs = queryset_prioridades_paa(qs)

        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return PrioridadePaaListSerializer
        else:
            return PrioridadePaaCreateUpdateSerializer

    @action(detail=False, methods=['get'], url_path='tabelas',
            permission_classes=[PermissaoApiUe])
    def tabelas(self, request, *args, **kwrgs):
        tabelas = dict(
            prioridades=SimNaoChoices.to_dict(),
            recursos=RecursoOpcoesEnum.to_dict(),
            tipos_aplicacao=TipoAplicacaoOpcoesEnum.to_dict(),
        )

        return Response(tabelas, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='excluir-lote',
            permission_classes=[PermissaoApiUe & PermissaoAPITodosComGravacao])
    def excluir_em_lote(self, request, *args, **kwargs):
        """
        Exclui em lote as prioridades de PAA.

        Essa action pode ser usada para excluir em lote as prioridades de PAA.

        - lista_uuids: lista de uuids das prioridades a serem excluídas.

        Retorna um dicionário com as informações dos erros e a mensagem
        de sucesso ou erro.
        """
        lista_uuids = request.data.get('lista_uuids', [])

        if not len(lista_uuids):
            content = {
                'erro': 'Falta de informações',
                'mensagem': 'É necessário enviar a lista de uuids a serem excluídos (lista_uuids).'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            erros = PrioridadePaa.excluir_em_lote(lista_uuids)
            if len(erros):
                mensagem = 'Alguma das prioridades selecionadas já foi removida.'
            else:
                mensagem = 'Prioridades removidas com sucesso.'
            return Response({
                'erros': erros,
                'mensagem': mensagem
            }, status=status.HTTP_200_OK)

        except Exception as err:
            error = {
                'erro': "Falha ao excluir Prioridades em lote",
                'mensagem': str(err)
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        """
        Cria uma nova PrioridadePaa.
        
        Valida os dados através do serializer e cria o objeto.
        Retorna os dados da prioridade criada ou erros de validação.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Verifica se o valor da prioridade não excede os recursos disponíveis
        validation_error = self._validar_valor_prioridade(serializer.validated_data)
        if validation_error:
            return validation_error
        
        prioridade = serializer.save()
                
        return Response(
            PrioridadePaaCreateUpdateSerializer(prioridade).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """
        Atualiza uma PrioridadePaa existente.
        
        Valida os dados através do serializer e aplica a validação de valor.
        Retorna os dados da prioridade atualizada ou erros de validação.
        """
        try:
            # Verifica se a prioridade existe
            instance = self.get_object()
            
            # Valida os dados de entrada
            serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
            serializer.is_valid(raise_exception=True)
            
            # Verifica se o valor da prioridade não excede os recursos disponíveis
            validation_error = self._validar_valor_prioridade(serializer.validated_data)
            if validation_error:
                return validation_error
            
            # Salva as alterações
            prioridade = serializer.save()
            
            return Response(
                PrioridadePaaCreateUpdateSerializer(prioridade).data,
                status=status.HTTP_200_OK
            )
            
        except (Http404, NotFound):
            return Response(
                {"mensagem": "Prioridade não encontrada ou já foi removida da base de dados."},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], url_path='duplicar')
    def duplicar(self, request, uuid=None):
        """
        Duplicar uma PrioridadePaa existente, criando um novo registro com os mesmos dados.
        O campo `valor_total` não informado
        """
        try:
            original = self.get_object()
        except (Http404, NotFound):
            return Response(
                {"mensagem": "Prioridade não encontrada ou já foi removida da base de dados."},
                status=status.HTTP_404_NOT_FOUND
            )

        original_data = {
            'paa': str(original.paa.uuid) if original.paa else None,
            'prioridade': int(original.prioridade),
            'recurso': original.recurso,
            'acao_associacao': str(original.acao_associacao.uuid) if original.acao_associacao else None,
            'programa_pdde': str(original.programa_pdde.uuid) if original.programa_pdde else None,
            'acao_pdde': str(original.acao_pdde.uuid) if original.acao_pdde else None,
            'tipo_aplicacao': original.tipo_aplicacao,
            'tipo_despesa_custeio': str(original.tipo_despesa_custeio.uuid) if original.tipo_despesa_custeio else None,
            'especificacao_material': (
                str(original.especificacao_material.uuid) if original.especificacao_material else None),
            'valor_total': None,
            'copia_de': str(original.uuid),
        }
        original_data = {k: v for k, v in original_data.items() if v is not None}

        serializer = PrioridadePaaCreateUpdateSerializer(data=original_data)

        serializer.is_valid(raise_exception=True)
        nova_prioridade = serializer.save()

        return Response(PrioridadePaaCreateUpdateSerializer(nova_prioridade).data, status=status.HTTP_201_CREATED)

    def _validar_valor_prioridade(self, validated_data):
        """
        Valida se o valor da prioridade não excede os valores disponíveis de receita.
        Retorna um Response de erro se a validação falhar, ou None se passar.
        """
        valor_total = validated_data.get('valor_total')
        acao_associacao = validated_data.get('acao_associacao')
        tipo_aplicacao = validated_data.get('tipo_aplicacao')
        
        if valor_total and acao_associacao and tipo_aplicacao:
            try:
                # Obter dados da ação associação para cálculo dos valores disponíveis
                acao_associacao_data = AcaoAssociacaoRetrieveSerializer(acao_associacao).data
                
                if acao_associacao_data:
                    # Calcula os valores disponíveis para todos os tipos de aplicação
                    valor_custeio = self._calcular_valor_disponivel(acao_associacao_data, TipoAplicacaoOpcoesEnum.CUSTEIO.name)
                    valor_capital = self._calcular_valor_disponivel(acao_associacao_data, TipoAplicacaoOpcoesEnum.CAPITAL.name)
                    valor_livre = self._calcular_valor_livre(acao_associacao_data)
                    
                    valor_prioridade = Decimal(str(valor_total))
                    
                    # Calcula o valor disponível baseado no tipo de aplicação
                    if tipo_aplicacao == TipoAplicacaoOpcoesEnum.CUSTEIO.name:
                        valor_disponivel = valor_custeio
                    elif tipo_aplicacao == TipoAplicacaoOpcoesEnum.CAPITAL.name:
                        valor_disponivel = valor_capital
                    else:
                        valor_disponivel = Decimal('0')
                    
                    # Calcula o valor total disponível (custeio + capital + livre aplicação)
                    valor_total_disponivel = valor_custeio + valor_capital + valor_livre
                    
                    # Verifica se o valor da prioridade excede o valor total disponível
                    if valor_prioridade > valor_total_disponivel:
                        return Response(
                            {"mensagem": "O valor indicado para a prioridade excede o valor disponível de receita prevista."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Verifica se o valor da prioridade excede o valor disponível no tipo específico
                    if valor_prioridade > valor_disponivel:
                        # Se não há saldo suficiente no tipo específico, verifica se há saldo suficiente em livre aplicação
                        if tipo_aplicacao in [TipoAplicacaoOpcoesEnum.CUSTEIO.name, TipoAplicacaoOpcoesEnum.CAPITAL.name]:
                            # Calcula quanto precisa ser usado da livre aplicação
                            valor_necessario_livre = valor_prioridade - valor_disponivel
                            
                            if valor_livre >= valor_necessario_livre:
                                # Há saldo suficiente em livre aplicação, permite o cadastro
                                pass
                            else:
                                # Não há saldo suficiente em livre aplicação, rejeita
                                return Response(
                                    {"mensagem": "O valor indicado para a prioridade excede o valor disponível de receita prevista."},
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                        else:
                            # Para outros tipos, rejeita se não há saldo suficiente
                            return Response(
                                {"mensagem": "O valor indicado para a prioridade excede o valor disponível de receita prevista."},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        
            except Exception as e:
                logger.error(f"Erro ao validar valor da prioridade: {str(e)}")
                # Em caso de erro na validação, permite a operação mas registra o erro
                pass
        
        return None

    def _calcular_valor_livre(self, acao_associacao_data):
        """
        Calcula o valor de livre aplicação disponível para uma ação associação.
        Usa a mesma lógica do serviço de resumo de prioridades.
        """
        def get_receita_prevista_da_acao_associacao(acao_associacao_data):
            """Busca as receitas previstas da ação associação"""
            receitas_previstas_paa = acao_associacao_data.get('receitas_previstas_paa', [])
            return receitas_previstas_paa[0] if len(receitas_previstas_paa) else {}

        def calcular_saldos_congelado_atual_previsao(congelado, atual, previsao):
            """Soma saldo congelado (ou atual) com previsão"""
            previsao_valor = Decimal(previsao)
            saldo_congelado = Decimal(congelado)
            saldo_atual = Decimal(atual)
            return (saldo_congelado or saldo_atual) + previsao_valor

        def get_valor_livre(acao_associacao_data):
            """Calcula o valor de livre aplicação baseado nos saldos e previsões"""
            receitas_previstas_paa = get_receita_prevista_da_acao_associacao(acao_associacao_data)
            saldos = acao_associacao_data.get('saldos', {})

            previsao_valor = Decimal(receitas_previstas_paa.get('previsao_valor_livre', None) or 0)
            saldo_congelado = Decimal(receitas_previstas_paa.get('saldo_congelado_livre', None) or 0)
            saldo_atual = Decimal(saldos.get('saldo_atual_livre', None) or 0)

            return calcular_saldos_congelado_atual_previsao(saldo_congelado, saldo_atual, previsao_valor)

        return get_valor_livre(acao_associacao_data)

    def _calcular_valor_disponivel(self, acao_associacao_data, tipo_aplicacao):
        """
        Calcula o valor disponível para uma ação associação baseado no tipo de aplicação.
        Usa a mesma lógica do serviço de resumo de prioridades.
        """
        def get_receita_prevista_da_acao_associacao(acao_associacao_data):
            """Busca as receitas previstas da ação associação"""
            receitas_previstas_paa = acao_associacao_data.get('receitas_previstas_paa', [])
            return receitas_previstas_paa[0] if len(receitas_previstas_paa) else {}

        def calcular_saldos_congelado_atual_previsao(congelado, atual, previsao):
            """Soma saldo congelado (ou atual) com previsão"""
            previsao_valor = Decimal(previsao)
            saldo_congelado = Decimal(congelado)
            saldo_atual = Decimal(atual)
            return (saldo_congelado or saldo_atual) + previsao_valor

        def get_valor_custeio(acao_associacao_data):
            """Calcula o valor de custeio disponível"""
            receitas_previstas_paa = get_receita_prevista_da_acao_associacao(acao_associacao_data)
            saldos = acao_associacao_data.get('saldos', {})

            previsao_valor = Decimal(receitas_previstas_paa.get('previsao_valor_custeio', None) or 0)
            saldo_congelado = Decimal(receitas_previstas_paa.get('saldo_congelado_custeio', None) or 0)
            saldo_atual = Decimal(saldos.get('saldo_atual_custeio', None) or 0)

            return calcular_saldos_congelado_atual_previsao(saldo_congelado, saldo_atual, previsao_valor)

        def get_valor_capital(acao_associacao_data):
            """Calcula o valor de capital disponível"""
            receitas_previstas_paa = get_receita_prevista_da_acao_associacao(acao_associacao_data)
            saldos = acao_associacao_data.get('saldos', {})

            previsao_valor = Decimal(receitas_previstas_paa.get('previsao_valor_capital', None) or 0)
            saldo_congelado = Decimal(receitas_previstas_paa.get('saldo_congelado_capital', None) or 0)
            saldo_atual = Decimal(saldos.get('saldo_atual_capital', None) or 0)

            return calcular_saldos_congelado_atual_previsao(saldo_congelado, saldo_atual, previsao_valor)

        def get_valor_livre(acao_associacao_data):
            """Calcula o valor de livre aplicação disponível"""
            receitas_previstas_paa = get_receita_prevista_da_acao_associacao(acao_associacao_data)
            saldos = acao_associacao_data.get('saldos', {})

            previsao_valor = Decimal(receitas_previstas_paa.get('previsao_valor_livre', None) or 0)
            saldo_congelado = Decimal(receitas_previstas_paa.get('saldo_congelado_livre', None) or 0)
            saldo_atual = Decimal(saldos.get('saldo_atual_livre', None) or 0)

            return calcular_saldos_congelado_atual_previsao(saldo_congelado, saldo_atual, previsao_valor)

        # Retorna o valor disponível baseado no tipo de aplicação
        if tipo_aplicacao == TipoAplicacaoOpcoesEnum.CUSTEIO.name:
            return get_valor_custeio(acao_associacao_data)
        elif tipo_aplicacao == TipoAplicacaoOpcoesEnum.CAPITAL.name:
            return get_valor_capital(acao_associacao_data)
        else:
            return Decimal('0')
