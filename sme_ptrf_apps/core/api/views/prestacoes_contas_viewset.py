import logging

from django.db.models import Q
from django.db.utils import IntegrityError
from django_filters import rest_framework as filters
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import extend_schema
from waffle import flag_is_active

from sme_ptrf_apps.users.permissoes import (
    PermissaoApiUe,
    PermissaoAPITodosComLeituraOuGravacao,
    PermissaoAPITodosComGravacao,
    PermissaoAPIApenasDreComGravacao,
    PermissaoAPIApenasDreComLeituraOuGravacao,
)
from ....despesas.models import TipoDocumento, TipoTransacao

from ....dre.models import Atribuicao, TecnicoDre, MotivoAprovacaoRessalva, MotivoReprovacao
from ...models import (
    Associacao,
    Ata,
    Periodo,
    PrestacaoConta,
    Unidade,
    ContaAssociacao,
    AcaoAssociacao,
    AnalisePrestacaoConta,
    AnaliseLancamentoPrestacaoConta,
    AnaliseDocumentoPrestacaoConta,
    TaskCelery
)
from ...services import (
    concluir_prestacao_de_contas,
    informacoes_financeiras_para_atas,
    reabrir_prestacao_de_contas,
    lista_prestacoes_de_conta_nao_recebidas,
    lista_prestacoes_de_conta_todos_os_status,
    lancamentos_da_prestacao,
    marca_lancamentos_como_corretos,
    marca_lancamentos_como_nao_conferidos,
    solicita_acertos_de_lancamentos,
    documentos_da_prestacao,
    marca_documentos_como_corretos,
    marca_documentos_como_nao_conferidos,
    solicita_acertos_de_documentos,
    previa_prestacao_conta,
    previa_informacoes_financeiras_para_atas,
)
from ....dre.services import (dashboard_sme)
from ..serializers import (
    AtaLookUpSerializer,
    PrestacaoContaListSerializer,
    PrestacaoContaLookUpSerializer,
    PrestacaoContaRetrieveSerializer,
    AnaliseLancamentoPrestacaoContaSolicitacoesNaoAgrupadasRetrieveSerializer,
    AnaliseDocumentoPrestacaoContaRetrieveSerializer,
    AnalisePrestacaoContaRetrieveSerializer
)
from sme_ptrf_apps.core.api.serializers.validation_serializers.prestacoes_contas_concluir_validate_serializer import PrestacoesContasConcluirValidateSerializer

from sme_ptrf_apps.core.tasks import gerar_previa_relatorio_acertos_async, concluir_prestacao_de_contas_async, gerar_relatorio_apos_acertos_async
from ...services.analise_prestacao_conta_service import _criar_documento_final_relatorio_acertos

from django.core.exceptions import ValidationError

from ....logging.loggers import ContextualLogger

logger = logging.getLogger(__name__)


class PrestacoesContasViewSet(mixins.RetrieveModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.ListModelMixin,
                              GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = PrestacaoConta.objects.all().order_by('associacao__unidade__tipo_unidade', 'associacao__unidade__nome')
    serializer_class = PrestacaoContaLookUpSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    filterset_fields = ('associacao__unidade__dre__uuid', 'periodo__uuid', 'associacao__unidade__tipo_unidade')

    def get_queryset(self):
        qs = PrestacaoConta.objects.all().order_by('associacao__unidade__tipo_unidade', 'associacao__unidade__nome')

        status_pc = self.request.query_params.get('status')
        status_pc_list = status_pc.split(',') if status_pc else []
        if status_pc_list:
            qs = qs.filter(status__in=status_pc_list)

        nome = self.request.query_params.get('nome')
        if nome is not None:
            qs = qs.filter(
                Q(associacao__unidade__codigo_eol=nome) |
                Q(associacao__nome__unaccent__icontains=nome) |
                Q(associacao__unidade__nome__unaccent__icontains=nome)
            )

        dre_uuid = self.request.query_params.get('associacao__unidade__dre__uuid')
        periodo_uuid = self.request.query_params.get('periodo__uuid')
        tecnico_uuid = self.request.query_params.get('tecnico')
        if tecnico_uuid and dre_uuid and periodo_uuid:

            try:
                dre = Unidade.dres.get(uuid=dre_uuid)
            except Unidade.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

            try:
                periodo = Periodo.objects.get(uuid=periodo_uuid)
            except Periodo.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

            try:
                tecnico = TecnicoDre.objects.get(uuid=tecnico_uuid)
            except TecnicoDre.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto tecnico_dre para o uuid {tecnico_uuid} não foi encontrado na base."
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

            atribuicoes = Atribuicao.objects.filter(
                tecnico=tecnico,
                periodo=periodo,
                unidade__dre=dre
            ).values_list('unidade__codigo_eol', flat=True)

            qs = qs.filter(associacao__unidade__codigo_eol__in=atribuicoes)

        data_inicio = self.request.query_params.get('data_inicio')
        data_fim = self.request.query_params.get('data_fim')
        if data_inicio is not None and data_fim is not None:
            qs = qs.filter(data_recebimento__range=[data_inicio, data_fim])

        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return PrestacaoContaListSerializer
        elif self.action == 'retrieve':
            return PrestacaoContaRetrieveSerializer
        else:
            return PrestacaoContaLookUpSerializer

    @action(detail=False, url_path='por-associacao-e-periodo',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def por_associacao_e_periodo(self, request):
        associacao_uuid = request.query_params.get('associacao_uuid')
        periodo_uuid = request.query_params.get('periodo_uuid')
        return Response(PrestacaoContaLookUpSerializer(
            self.queryset.filter(associacao__uuid=associacao_uuid).filter(
                periodo__uuid=periodo_uuid).first(), many=False).data)

    # TODO: Renomear essa action para "concluir" quando a feature flag 'novo-processo-pc' for removida
    @extend_schema(
        request=PrestacoesContasConcluirValidateSerializer,
        responses={200: "Operação realizada com sucesso"},
    )
    @action(
        detail=False,
        url_path="concluir-v2",
        methods=["post"],
        permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao],
    )
    def concluir_v2(self, request):
        from sme_ptrf_apps.core.api.serializers.validation_serializers.prestacoes_contas_concluir_validate_serializer import (
            PrestacoesContasConcluirValidateSerializer,
        )  # noqa
        from sme_ptrf_apps.core.services.prestacao_conta_service import PrestacaoContaService

        if not flag_is_active(request, "novo-processo-pc"):
            return Response(
                {
                    "erro": "A feature flag 'novo-processo-pc' está desabilitada. Deve ser usada a action 'concluir'."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PrestacoesContasConcluirValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        logger_pc = ContextualLogger.get_logger(__name__)

        pc_service = PrestacaoContaService(
            periodo_uuid=serializer.validated_data["periodo_uuid"],
            associacao_uuid=serializer.validated_data["associacao_uuid"],
            username=request.user.username,
            logger=logger_pc,
        )

        try:
            pc = pc_service.iniciar_tasks_de_conclusao_de_pc(
                usuario=request.user,
                justificativa_acertos_pendentes=serializer.validated_data.get("justificativa_acertos_pendentes", "")
            )
        except IntegrityError:
            erro = {
                'erro': 'prestacao_ja_iniciada',
                'mensagem': 'Você não pode iniciar uma prestação de contas que já foi iniciada.'
            }
            logger_pc.error('Prestação de contas já iniciada', stack_info=True, exc_info=True)
            return Response(erro, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            erro = {
                'erro': 'prestacao_em_processamento',
                'mensagem': f'{e}'
            }
            logger_pc.error('Erro ao iniciar prestação de contas', stack_info=True, exc_info=True)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        return Response(PrestacaoContaLookUpSerializer(pc, many=False).data, status=status.HTTP_200_OK)

    # TODO: Remover essa action quando a feature flag 'novo-processo-pc' for removida
    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao],
    )
    def concluir(self, request):
        if flag_is_active(request, "novo-processo-pc"):
            return Response(
                {
                    "erro": "A feature flag 'novo-processo-pc' está habilitada. Deve ser usada a action 'concluir-v2'."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        associacao_uuid = request.query_params.get('associacao_uuid')
        if not associacao_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da associação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            associacao = Associacao.objects.get(uuid=associacao_uuid)
        except Associacao.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto associação para o uuid {associacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        periodo_uuid = request.query_params.get('periodo_uuid')
        if not periodo_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do período de conciliação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except Periodo.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        justificativa_acertos_pendentes = request.data.get('justificativa_acertos_pendentes', '')

        usuario = request.user

        try:
            dados = concluir_prestacao_de_contas(
                associacao=associacao,
                periodo=periodo,
                usuario=usuario,
                monitoraPc=True,
            )
            prestacao_de_contas = dados["prestacao"]

            erro_pc = dados["erro"]
            if erro_pc:
                raise Exception(erro_pc)
            else:
                task_celery = TaskCelery.objects.create(
                    nome_task="concluir_prestacao_de_contas_async",
                    usuario=usuario,
                    associacao=associacao,
                    periodo=periodo,
                    prestacao_conta=prestacao_de_contas
                )

                id_task = concluir_prestacao_de_contas_async.apply_async(
                    (
                        periodo.uuid,
                        associacao.uuid,
                        request.user.username,
                        True,
                        dados["e_retorno_devolucao"],
                        dados["requer_geracao_documentos"],
                        dados["requer_geracao_fechamentos"],
                        dados["requer_acertos_em_extrato"],
                        justificativa_acertos_pendentes,
                    ), countdown=1
                )

                if dados["e_retorno_devolucao"]:
                    task_celery_geracao_relatorio_apos_acerto = TaskCelery.objects.create(
                        nome_task="gerar_relatorio_apos_acertos_async",
                        associacao=associacao,
                        periodo=periodo,
                        usuario=usuario
                    )

                    id_task_geracao_relatorio_apos_acerto = gerar_relatorio_apos_acertos_async.apply_async(
                        (
                            task_celery_geracao_relatorio_apos_acerto.uuid,
                            associacao.uuid,
                            periodo.uuid,
                            request.user.name
                        ), countdown=1
                    )

                    task_celery_geracao_relatorio_apos_acerto.id_task_assincrona = id_task_geracao_relatorio_apos_acerto
                    task_celery_geracao_relatorio_apos_acerto.save()

                task_celery.id_task_assincrona = id_task
                task_celery.save()
        except (IntegrityError):
            erro = {
                'erro': 'prestacao_ja_iniciada',
                'mensagem': 'Você não pode iniciar uma prestação de contas que já foi iniciada.'
            }
            return Response(erro, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            erro = {
                'erro': 'prestacao_em_processamento',
                'mensagem': f'{e}'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        return Response(PrestacaoContaLookUpSerializer(prestacao_de_contas, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'],
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def reabrir(self, request, uuid):

        prestacao_de_contas = PrestacaoConta.by_uuid(uuid)

        if prestacao_de_contas:
            associacao = prestacao_de_contas.associacao
            prestacao_de_contas_posteriores = PrestacaoConta.objects.filter(
                associacao=associacao, id__gt=prestacao_de_contas.id)

            if prestacao_de_contas_posteriores:
                response = {
                    'uuid': f'{uuid}',
                    'erro': 'prestacao_de_contas_posteriores',
                    'operacao': 'reabrir',
                    'mensagem': 'Essa prestação de contas não pode ser devolvida, ou reaberta porque há prestação de contas dessa associação de um período posterior. Se necessário, reabra ou devolva primeiro a prestação de contas mais recente.'
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        reaberta = reabrir_prestacao_de_contas(prestacao_contas_uuid=uuid)
        if reaberta:
            response = {
                'uuid': f'{uuid}',
                'mensagem': 'Prestação de contas reaberta com sucesso. Todos os seus registros foram apagados.'
            }
            return Response(response, status=status.HTTP_204_NO_CONTENT)
        else:
            response = {
                'uuid': f'{uuid}',
                'mensagem': 'Houve algum erro ao tentar reabrir a prestação de contas.'
            }
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'],
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def receber(self, request, uuid):
        from sme_ptrf_apps.core.services.processos_services import (
            trata_processo_sei_ao_receber_pc,
            trata_processo_sei_ao_receber_pc_v2,
        )

        prestacao_conta = self.get_object()

        data_recebimento = request.data.get('data_recebimento', None)
        if not data_recebimento:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'receber',
                'mensagem': 'Faltou informar a data de recebimento da Prestação de Contas.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if prestacao_conta.status != PrestacaoConta.STATUS_NAO_RECEBIDA:
            response = {
                'uuid': f'{uuid}',
                'erro': 'status_nao_permite_operacao',
                'status': prestacao_conta.status,
                'operacao': 'receber',
                'mensagem': 'Você não pode receber uma prestação de contas com status diferente de NAO_RECEBIDA.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        processo_sei = request.data.get('processo_sei', None)
        if not processo_sei:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes_processo_sei',
                'operacao': 'receber',
                'mensagem': 'Faltou informar o processo SEI de recebimento da Prestação de Contas.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        acao_processo_sei = request.data.get('acao_processo_sei', None)

        if not prestacao_conta.ata_apresentacao_gerada():
            response = {
                'uuid': f'{uuid}',
                'erro': 'pendencias',
                'operacao': 'receber',
                'mensagem': 'É necessário gerar ata de apresentação para realizar o recebimento.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if flag_is_active(request, "periodos-processo-sei"):
            trata_processo_sei_ao_receber_pc_v2(prestacao_conta=prestacao_conta,
                                             processo_sei=processo_sei, acao_processo_sei=acao_processo_sei)
        else:
            trata_processo_sei_ao_receber_pc(prestacao_conta=prestacao_conta,
                                             processo_sei=processo_sei, acao_processo_sei=acao_processo_sei)

        prestacao_recebida = prestacao_conta.receber(data_recebimento=data_recebimento)

        return Response(PrestacaoContaRetrieveSerializer(prestacao_recebida, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='desfazer-recebimento',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def desfazer_recebimento(self, request, uuid):
        prestacao_conta = self.get_object()

        if prestacao_conta.status != PrestacaoConta.STATUS_RECEBIDA:
            response = {
                'uuid': f'{prestacao_conta.uuid}',
                'erro': 'status_nao_permite_operacao',
                'status': prestacao_conta.status,
                'operacao': 'desfazer-recebimento',
                'mensagem': 'Impossível desfazer recebimento de uma PC com status diferente de RECEBIDA.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        prestacao_atualizada = prestacao_conta.desfazer_recebimento()

        return Response(PrestacaoContaRetrieveSerializer(prestacao_atualizada, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='analisar',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def analisar(self, request, uuid):
        prestacao_conta = self.get_object()

        if prestacao_conta.status not in (PrestacaoConta.STATUS_RECEBIDA, PrestacaoConta.STATUS_DEVOLVIDA_RECEBIDA):
            response = {
                'uuid': f'{prestacao_conta.uuid}',
                'erro': 'status_nao_permite_operacao',
                'status': prestacao_conta.status,
                'operacao': 'analisar',
                'mensagem': 'Você não pode analisar uma prestação de contas com status diferente de RECEBIDA ou DEVOLVIDA_RECEBIDA.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        prestacao_atualizada = prestacao_conta.analisar()

        return Response(PrestacaoContaRetrieveSerializer(prestacao_atualizada, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='desfazer-analise',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def desfazer_analise(self, request, uuid):
        prestacao_conta = self.get_object()

        if prestacao_conta.em_retificacao:
            return Response({'erro': 'Impossível desfazer análise de uma PC em retificação.'}, status=status.HTTP_403_FORBIDDEN)

        if prestacao_conta.status != PrestacaoConta.STATUS_EM_ANALISE:
            response = {
                'uuid': f'{prestacao_conta.uuid}',
                'erro': 'status_nao_permite_operacao',
                'status': prestacao_conta.status,
                'operacao': 'desfazer-analise',
                'mensagem': 'Impossível desfazer análise de uma PC com status diferente de EM_ANALISE.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        prestacao_atualizada = prestacao_conta.desfazer_analise()

        return Response(PrestacaoContaRetrieveSerializer(prestacao_atualizada, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='salvar-analise',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def salvar_analise(self, request, uuid):
        prestacao_conta = self.get_object()

        if prestacao_conta.status != PrestacaoConta.STATUS_EM_ANALISE:
            response = {
                'uuid': f'{uuid}',
                'erro': 'status_nao_permite_operacao',
                'status': prestacao_conta.status,
                'operacao': 'salvar-analise',
                'mensagem': 'Você não pode salvar análise de uma prestação de contas com status diferente de EM_ANALISE.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        prestacao_salva = prestacao_conta.salvar_analise()

        return Response(PrestacaoContaRetrieveSerializer(prestacao_salva, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='salvar-devolucoes-ao-tesouro',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def salvar_devolucoes_ao_tesouro(self, request, uuid):
        prestacao_conta = self.get_object()

        devolucoes_ao_tesouro_da_prestacao = request.data.get('devolucoes_ao_tesouro_da_prestacao', [])

        if prestacao_conta.status not in [PrestacaoConta.STATUS_EM_ANALISE, PrestacaoConta.STATUS_DEVOLVIDA, PrestacaoConta.STATUS_DEVOLVIDA_RETORNADA]:
            response = {
                'uuid': f'{uuid}',
                'erro': 'status_nao_permite_operacao',
                'status': prestacao_conta.status,
                'operacao': 'salvar-devolucoes-ao-tesouro',
                'mensagem': 'Você não pode salvar devoluções ao tesouro de uma prestação de contas com status diferente de EM_ANALISE ou DEVOLVIDA.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        prestacao_salva = prestacao_conta.salvar_devolucoes_ao_tesouro(
            devolucoes_ao_tesouro_da_prestacao=devolucoes_ao_tesouro_da_prestacao)

        return Response(PrestacaoContaRetrieveSerializer(prestacao_salva, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='apagar-devolucoes-ao-tesouro',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def apagar_devolucoes_ao_tesouro(self, request, uuid):
        prestacao_conta = self.get_object()

        devolucoes_ao_tesouro_a_apagar = request.data.get('devolucoes_ao_tesouro_a_apagar', [])

        if prestacao_conta.status not in [PrestacaoConta.STATUS_EM_ANALISE, PrestacaoConta.STATUS_DEVOLVIDA, PrestacaoConta.STATUS_DEVOLVIDA_RETORNADA]:
            response = {
                'uuid': f'{uuid}',
                'erro': 'status_nao_permite_operacao',
                'status': prestacao_conta.status,
                'operacao': 'apagar-devolucoes-ao-tesouro',
                'mensagem': 'Você não pode apagar devoluções ao tesouro de uma prestação de contas com status diferente de EM_ANALISE ou DEVOLVIDA.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        prestacao_salva = prestacao_conta.apagar_devolucoes_ao_tesouro(
            devolucoes_ao_tesouro_a_apagar=devolucoes_ao_tesouro_a_apagar)

        return Response(PrestacaoContaRetrieveSerializer(prestacao_salva, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='concluir-analise',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def concluir_analise(self, request, uuid):
        prestacao_conta = self.get_object()

        resultado_analise = request.data.get('resultado_analise', None)
        if resultado_analise is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'concluir-analise',
                'mensagem': 'Faltou informar o campo resultado_analise.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if resultado_analise not in [PrestacaoConta.STATUS_APROVADA, PrestacaoConta.STATUS_APROVADA_RESSALVA,
                                     PrestacaoConta.STATUS_DEVOLVIDA, PrestacaoConta.STATUS_REPROVADA]:
            response = {
                'uuid': f'{uuid}',
                'erro': 'resultado_analise_invalido',
                'status': resultado_analise,
                'operacao': 'concluir-analise',
                'mensagem': 'Resultado inválido. Resultados possíveis: APROVADA, APROVADA_RESSALVA, REPROVADA, DEVOLVIDA.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        analises_de_conta_da_prestacao = request.data.get('analises_de_conta_da_prestacao', None)
        if analises_de_conta_da_prestacao is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'concluir-analise',
                'mensagem': 'Faltou informar o campo analises_de_conta_da_prestacao.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if prestacao_conta.status != PrestacaoConta.STATUS_EM_ANALISE:
            response = {
                'uuid': f'{uuid}',
                'erro': 'status_nao_permite_operacao',
                'status': prestacao_conta.status,
                'operacao': 'concluir-analise',
                'mensagem': 'Você não pode concluir análise de uma prestação de contas com status diferente de EM_ANALISE.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        outros_motivos_aprovacao_ressalva = request.data.get('outros_motivos_aprovacao_ressalva', '')
        motivos_aprovacao_ressalva_uuid = request.data.get('motivos_aprovacao_ressalva', [])

        if resultado_analise == PrestacaoConta.STATUS_APROVADA_RESSALVA and not motivos_aprovacao_ressalva_uuid and not outros_motivos_aprovacao_ressalva:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'concluir-analise',
                'mensagem': 'Para concluir como APROVADO_RESSALVA é necessário informar motivos_aprovacao_ressalva ou outros_motivos_aprovacao_ressalva.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        motivos_aprovacao_ressalva = []
        for motivo_uuid in motivos_aprovacao_ressalva_uuid:
            try:
                motivo_aprovacao_ressalva = MotivoAprovacaoRessalva.objects.get(uuid=motivo_uuid)
                motivos_aprovacao_ressalva.append(motivo_aprovacao_ressalva)
            except MotivoAprovacaoRessalva.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto motivo de aprovação com ressalva para o uuid {motivo_uuid} não foi encontrado na base."
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        motivos_reprovacao_uuid = request.data.get('motivos_reprovacao', [])
        outros_motivos_reprovacao = request.data.get('outros_motivos_reprovacao', '')

        if resultado_analise == PrestacaoConta.STATUS_REPROVADA and not motivos_reprovacao_uuid and not outros_motivos_reprovacao:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'concluir-analise',
                'mensagem': 'Para concluir como Reprovada é necessário informar o campo motivos_reprovacao ou outros_motivos_reprovacao.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        motivos_reprovacao = []

        for motivo_uuid in motivos_reprovacao_uuid:
            try:
                motivo_reprovacao = MotivoReprovacao.objects.get(uuid=motivo_uuid)
                motivos_reprovacao.append(motivo_reprovacao)
            except MotivoReprovacao.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto motivo de reprovação para o uuid {motivo_uuid} não foi encontrado na base."
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        recomendacoes = request.data.get('recomendacoes', '')

        if resultado_analise == PrestacaoConta.STATUS_APROVADA_RESSALVA and not recomendacoes:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'concluir-analise',
                'mensagem': 'Para concluir como APROVADO_RESSALVA é necessário informar as recomendações.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        data_limite_ue = request.data.get('data_limite_ue', None)

        if resultado_analise == PrestacaoConta.STATUS_DEVOLVIDA and not data_limite_ue:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'concluir-analise',
                'mensagem': 'Para concluir como DEVOLVIDA é necessário informar o campo data_limite_ue.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if resultado_analise == PrestacaoConta.STATUS_DEVOLVIDA:
            if not prestacao_conta.pode_devolver():
                response = {
                    'uuid': f'{uuid}',
                    'erro': 'prestacao_de_contas_posteriores',
                    'operacao': 'concluir-analise',
                    'mensagem': 'Essa prestação de contas não pode ser devolvida, ou reaberta porque há prestação de contas dessa associação de um período posterior. Se necessário, reabra ou devolva primeiro a prestação de contas mais recente.'
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        analise_prestacao = prestacao_conta.analise_atual

        prestacao_salva = prestacao_conta.concluir_analise(
            resultado_analise=resultado_analise,
            analises_de_conta_da_prestacao=analises_de_conta_da_prestacao,
            motivos_aprovacao_ressalva=motivos_aprovacao_ressalva,
            outros_motivos_aprovacao_ressalva=outros_motivos_aprovacao_ressalva,
            data_limite_ue=data_limite_ue,
            motivos_reprovacao=motivos_reprovacao,
            outros_motivos_reprovacao=outros_motivos_reprovacao,
            recomendacoes=recomendacoes
        )

        if prestacao_conta.status == PrestacaoConta.STATUS_DEVOLVIDA:
            _criar_documento_final_relatorio_acertos(analise_prestacao.uuid, request.user.username)

        return Response(PrestacaoContaRetrieveSerializer(prestacao_salva, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='desfazer-conclusao-analise',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def desfazer_conclusao_analise(self, request, uuid):
        prestacao_conta = self.get_object()

        if prestacao_conta.status not in [PrestacaoConta.STATUS_APROVADA, PrestacaoConta.STATUS_APROVADA_RESSALVA,
                                          PrestacaoConta.STATUS_REPROVADA]:
            response = {
                'uuid': f'{prestacao_conta.uuid}',
                'erro': 'status_nao_permite_operacao',
                'status': prestacao_conta.status,
                'operacao': 'desfazer-conclusao-analise',
                'mensagem': 'Impossível desfazer conclusão de análise de uma PC com status diferente de APROVADA, APROVADA_RESSALVA ou REPROVADA.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        prestacao_atualizada = prestacao_conta.desfazer_conclusao_analise()

        return Response(PrestacaoContaRetrieveSerializer(prestacao_atualizada, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def ata(self, request, uuid):
        prestacao_conta = PrestacaoConta.by_uuid(uuid)

        ata = prestacao_conta.ultima_ata()

        if not ata:
            erro = {
                'mensagem': 'Ainda não existe uma ata para essa prestação de contas.'
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        return Response(AtaLookUpSerializer(ata, many=False).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='iniciar-ata',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def iniciar_ata(self, request, uuid):
        prestacao_conta = PrestacaoConta.by_uuid(uuid)

        ata = prestacao_conta.ultima_ata()

        if ata:
            erro = {
                'erro': 'ata-ja-iniciada',
                'mensagem': 'Já existe uma ata iniciada para essa prestação de contas.'
            }
            return Response(erro, status=status.HTTP_409_CONFLICT)

        ata = Ata.iniciar(prestacao_conta=prestacao_conta)

        return Response(AtaLookUpSerializer(ata, many=False).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='info-para-ata')
    def info_para_ata(self, request, uuid):
        prestacao_conta = self.get_object()
        result = informacoes_financeiras_para_atas(prestacao_contas=prestacao_conta)
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='ata-retificacao',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def ata_retificacao(self, request, uuid):
        prestacao_conta = PrestacaoConta.by_uuid(uuid)

        ata = prestacao_conta.ultima_ata_retificacao()

        if not ata:
            erro = {
                'mensagem': 'Ainda não existe uma ata de retificação para essa prestação de contas.'
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        return Response(AtaLookUpSerializer(ata, many=False).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='iniciar-ata-retificacao',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def iniciar_ata_retificacao(self, request, uuid):
        prestacao_conta = PrestacaoConta.by_uuid(uuid)

        ata = prestacao_conta.ultima_ata_retificacao()

        if ata:
            erro = {
                'erro': 'ata-ja-iniciada',
                'mensagem': 'Já existe uma ata de retificação iniciada para essa prestação de contas.'
            }
            return Response(erro, status=status.HTTP_409_CONFLICT)

        ata = Ata.iniciar(prestacao_conta=prestacao_conta, retificacao=True)

        return Response(AtaLookUpSerializer(ata, many=False).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='fique-de-olho',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def fique_de_olho(self, request, uuid=None):
        from sme_ptrf_apps.core.models import ParametroFiqueDeOlhoPc
        fique_de_olho = ParametroFiqueDeOlhoPc.get().fique_de_olho

        return Response({'detail': fique_de_olho}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='update-fique-de-olho',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def update_fique_de_olho(self, request, uuid=None):

        texto_fique_de_olho = request.data.get('fique_de_olho', None)

        if texto_fique_de_olho is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'update-fique-de-olho',
                'mensagem': 'Faltou informar o campo Fique de Olho.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        from sme_ptrf_apps.core.models import ParametroFiqueDeOlhoPc

        # Pegando o objeto ParametroFiqueDeOlhoPc
        obj_fique_de_olho = ParametroFiqueDeOlhoPc.get()

        # Atribuindo ao objeto-> propriedade (fique_de_olho), o request.data.get('fique_de_olho', None)
        obj_fique_de_olho.fique_de_olho = texto_fique_de_olho

        # E por fim Salvando
        obj_fique_de_olho.save()

        return Response({'detail': 'Salvo com sucesso'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path="dashboard",
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def dashboard(self, request):
        dre_uuid = request.query_params.get('dre_uuid')
        periodo_uuid = request.query_params.get('periodo')

        if not dre_uuid or not periodo_uuid:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o uuid da dre (dre_uuid) e o periodo como parâmetros.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        periodo = Periodo.by_uuid(periodo_uuid)
        dre = Unidade.by_uuid(dre_uuid)

        total_associacoes_dre = Associacao.get_associacoes_ativas_no_periodo(periodo=periodo, dre=dre).count()

        par_add_aprovados_ressalva = request.query_params.get('add_aprovadas_ressalva')
        add_aprovados_ressalva = par_add_aprovados_ressalva == 'SIM'

        par_add_reprovadas_nao_apresentacao = request.query_params.get('add_reprovadas_nao_apresentacao')
        add_reprovadas_nao_apresentacao = par_add_reprovadas_nao_apresentacao == 'SIM'

        cards = PrestacaoConta.dashboard(
            periodo_uuid,
            dre_uuid,
            add_aprovado_ressalva=add_aprovados_ressalva,
            add_info_devolvidas_retornadas=True,
            add_reprovadas_nao_apresentacao=add_reprovadas_nao_apresentacao,
        )
        dashboard = {
            "total_associacoes_dre": total_associacoes_dre,
            "cards": cards
        }

        return Response(dashboard)

    @action(detail=False, url_path='tabelas',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def tabelas(self, _):
        result = {
            'status': PrestacaoConta.status_to_json(),
            'status_de_conclusao_de_pc': PrestacaoConta.status_conclusao_pc_to_json()
        }
        return Response(result)

    @action(detail=False, url_path='nao-recebidas',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def nao_recebidas(self, request):
        # Determina a DRE
        dre_uuid = self.request.query_params.get('associacao__unidade__dre__uuid')

        if not dre_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'nao-recebidas',
                'mensagem': 'Faltou informar o uuid da dre. ?associacao__unidade__dre__uuid=uuid_da_dre'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
        except Unidade.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina o período
        periodo_uuid = self.request.query_params.get('periodo__uuid')

        if not periodo_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'nao-recebidas',
                'mensagem': 'Faltou informar o uuid do período. ?periodo__uuid=uuid_do_periodo'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except Periodo.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Pega filtros
        nome = self.request.query_params.get('nome')
        tipo_unidade = self.request.query_params.get('tipo_unidade')
        status_pc = self.request.query_params.get('status')

        status_pc_list = status_pc.split(',') if status_pc else []
        for status_str in status_pc_list:
            if status_str not in [PrestacaoConta.STATUS_NAO_APRESENTADA, PrestacaoConta.STATUS_NAO_RECEBIDA]:
                erro = {
                    'erro': 'status-invalido',
                    'operacao': 'nao-recebidas',
                    'mensagem': 'Esse endpoint só aceita o filtro por status para os status NAO_APRESENTADA e NAO_RECEBIDA.'
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        result = lista_prestacoes_de_conta_nao_recebidas(dre=dre,
                                                         periodo=periodo,
                                                         filtro_nome=nome,
                                                         filtro_tipo_unidade=tipo_unidade,
                                                         filtro_status=status_pc_list,
                                                         periodos_processo_sei=flag_is_active(request,'periodos-processo-sei')
                                                        )
        return Response(result)

    @action(detail=False, url_path='todos-os-status',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def todos_os_status(self, request):
        # Determina a DRE
        dre_uuid = self.request.query_params.get('associacao__unidade__dre__uuid')

        if not dre_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'todos-os-status',
                'mensagem': 'Faltou informar o uuid da dre. ?associacao__unidade__dre__uuid=uuid_da_dre'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
        except (Unidade.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina o período
        periodo_uuid = self.request.query_params.get('periodo__uuid')

        if not periodo_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'todos-os-status',
                'mensagem': 'Faltou informar o uuid do período. ?periodo__uuid=uuid_do_periodo'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except (Periodo.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        devolucao_tesouro = self.request.query_params.get('devolucao_tesouro')

        # Pega filtros por nome e tipo de unidade
        nome = self.request.query_params.get('nome')
        tipo_unidade = self.request.query_params.get('tipo_unidade')

        # Pega e valida filtro por status
        status_pc = self.request.query_params.get('status')
        status_pc_list = status_pc.split(',') if status_pc else []
        for status_str in status_pc_list:
            if status_str not in PrestacaoConta.STATUS_NOMES.keys():
                erro = {
                    'erro': 'status-invalido',
                    'operacao': 'todos-os-status',
                    'mensagem': 'Passe um status de prestação de contas válido.'
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        result = lista_prestacoes_de_conta_todos_os_status(
            dre=dre,
            periodo=periodo,
            filtro_nome=nome,
            filtro_tipo_unidade=tipo_unidade,
            filtro_por_status=status_pc_list,
            filtro_por_devolucao_tesouro=devolucao_tesouro,
            periodos_processo_sei=flag_is_active(request, 'periodos-processo-sei')
        )
        return Response(result)

    @action(detail=False, methods=['get'], url_path="dashboard-sme",
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def dashboard_sme(self, request):
        # Determina o período
        periodo_uuid = self.request.query_params.get('periodo')
        unificar_pcs_apresentadas_nao_recebidas = self.request.query_params.get(
            'unificar_pcs_apresentadas_nao_recebidas')

        if not periodo_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'dashboard-sme',
                'mensagem': 'Faltou informar o uuid do período. ?periodo=uuid_do_periodo'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except Periodo.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        dashboard = dashboard_sme(
            periodo=periodo, unificar_pcs_apresentadas_nao_recebidas=unificar_pcs_apresentadas_nao_recebidas)

        return Response(dashboard)

    @action(detail=True, methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def lancamentos(self, request, uuid):
        from sme_ptrf_apps.core.api.serializers.validation_serializers.prestacoes_contas_lancamentos_validate_serializer import PrestacoesContasLancamentosValidateSerializer
        prestacao_conta = PrestacaoConta.by_uuid(uuid)

        filtro_informacoes = self.request.query_params.get('filtrar_por_informacoes')
        filtro_informacoes_list = filtro_informacoes.split(',') if filtro_informacoes else []

        filtro_conferencia = self.request.query_params.get('filtrar_por_conferencia')
        filtro_conferencia_list = filtro_conferencia.split(',') if filtro_conferencia else []

        query = PrestacoesContasLancamentosValidateSerializer(data=self.request.query_params, context={
                                                              'prestacao_conta': prestacao_conta})
        query.is_valid(raise_exception=True)

        lancamentos = lancamentos_da_prestacao(
            analise_prestacao_conta=AnalisePrestacaoConta.by_uuid(self.request.query_params.get('analise_prestacao')),
            conta_associacao=ContaAssociacao.by_uuid(self.request.query_params.get('conta_associacao')),
            acao_associacao=AcaoAssociacao.by_uuid(request.query_params.get(
                'acao_associacao')) if request.query_params.get('acao_associacao') else None,
            tipo_transacao=request.query_params.get('tipo'),
            ordenar_por_imposto=request.query_params.get('ordenar_por_imposto'),
            numero_de_documento=request.query_params.get('filtrar_por_numero_de_documento'),
            tipo_de_documento=TipoDocumento.by_id(request.query_params.get(
                'filtrar_por_tipo_de_documento')) if request.query_params.get('filtrar_por_tipo_de_documento') else None,
            tipo_de_pagamento=TipoTransacao.by_id(request.query_params.get(
                'filtrar_por_tipo_de_pagamento')) if request.query_params.get('filtrar_por_tipo_de_pagamento') else None,
            filtrar_por_data_inicio=request.query_params.get('filtrar_por_data_inicio'),
            filtrar_por_data_fim=request.query_params.get('filtrar_por_data_fim'),
            filtrar_por_nome_fornecedor=request.query_params.get('filtrar_por_nome_fornecedor'),
            filtro_informacoes_list=filtro_informacoes_list,
            filtro_conferencia_list=filtro_conferencia_list,
        )

        return Response(lancamentos, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path="lancamentos-corretos",
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def lancamentos_corretos(self, request, uuid):
        prestacao_conta = PrestacaoConta.by_uuid(uuid)

        analise_prestacao_uuid = request.data.get('analise_prestacao', None)
        if analise_prestacao_uuid is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'lancamentos-corretos',
                'mensagem': 'Faltou informar no payload o UUID da analise_prestacao.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            analise_prestacao = AnalisePrestacaoConta.objects.get(uuid=analise_prestacao_uuid)
        except AnalisePrestacaoConta.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto analise-prestacao-conta para o uuid {analise_prestacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if analise_prestacao.prestacao_conta != prestacao_conta:
            erro = {
                'erro': 'Análise de prestação inválida.',
                'mensagem': f"A análise de prestação {analise_prestacao_uuid} não pertence à Prestação de Contas {uuid}."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        lancamentos_corretos = request.data.get('lancamentos_corretos', None)
        if lancamentos_corretos is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'lancamentos-corretos',
                'mensagem': 'Faltou informar a lista com os lançamentos corretos.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        marca_lancamentos_como_corretos(analise_prestacao, lancamentos_corretos)

        return Response({"message": "Lançamentos marcados como corretos."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path="lancamentos-nao-conferidos",
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def lancamentos_nao_conferidos(self, request, uuid):
        prestacao_conta = PrestacaoConta.by_uuid(uuid)

        analise_prestacao_uuid = request.data.get('analise_prestacao', None)
        if analise_prestacao_uuid is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'lancamentos-nao-conferidos',
                'mensagem': 'Faltou informar no payload o UUID da analise_prestacao.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            analise_prestacao = AnalisePrestacaoConta.objects.get(uuid=analise_prestacao_uuid)
        except AnalisePrestacaoConta.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto analise-prestacao-conta para o uuid {analise_prestacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if analise_prestacao.prestacao_conta != prestacao_conta:
            erro = {
                'erro': 'Análise de prestação inválida.',
                'mensagem': f"A análise de prestação {analise_prestacao_uuid} não pertence à Prestação de Contas {uuid}."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        lancamentos_nao_conferidos = request.data.get('lancamentos_nao_conferidos', None)
        if lancamentos_nao_conferidos is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'lancamentos-nao-conferidos',
                'mensagem': 'Faltou informar a lista com os lançamentos não conferidos.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        marca_lancamentos_como_nao_conferidos(analise_prestacao, lancamentos_nao_conferidos)

        return Response({"message": "Lançamentos marcados como não conferidos."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path="solicitacoes-de-acerto",
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def solicitacoes_acerto(self, request, uuid):
        prestacao_conta = PrestacaoConta.by_uuid(uuid)

        analise_prestacao_uuid = request.data.get('analise_prestacao', None)
        if analise_prestacao_uuid is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'solicitacoes-de-acerto',
                'mensagem': 'Faltou informar no payload o UUID da analise_prestacao.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            analise_prestacao = AnalisePrestacaoConta.objects.get(uuid=analise_prestacao_uuid)
        except AnalisePrestacaoConta.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto analise-prestacao-conta para o uuid {analise_prestacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if analise_prestacao.prestacao_conta != prestacao_conta:
            erro = {
                'erro': 'Análise de prestação inválida.',
                'mensagem': f"A análise de prestação {analise_prestacao_uuid} não pertence à Prestação de Contas {uuid}."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        lancamentos = request.data.get('lancamentos', None)
        if lancamentos is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'solicitacoes-de-acertos',
                'mensagem': 'Faltou informar a lista com os lançamentos. lancamentos:'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        solicitacoes_acerto = request.data.get('solicitacoes_acerto', None)
        if solicitacoes_acerto is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'solicitacoes-de-acertos',
                'mensagem': 'Faltou informar a lista com as solicitações de acerto. solicitacoes_acerto:'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        solicita_acertos_de_lancamentos(
            analise_prestacao=analise_prestacao,
            lancamentos=lancamentos,
            solicitacoes_acerto=solicitacoes_acerto
        )

        return Response({"message": "Solicitações de acerto gravadas para os lançamentos."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path="analises-de-lancamento",
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def analises_de_lancamento(self, request, uuid):
        prestacao_conta = PrestacaoConta.by_uuid(uuid)

        # Define a análise de lançamaneto
        analise_lancamento_uuid = self.request.query_params.get('analise_lancamento')

        if analise_lancamento_uuid is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'analises-de-lancamento',
                'mensagem': 'Faltou informar o parâmetro analise_lancamento com o UUID da analise de lançamaneto.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            analise_lancamento = AnaliseLancamentoPrestacaoConta.objects.get(uuid=analise_lancamento_uuid)
        except AnaliseLancamentoPrestacaoConta.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto analise-lancamento-prestacao-conta para o uuid {analise_lancamento_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if analise_lancamento.analise_prestacao_conta.prestacao_conta != prestacao_conta:
            erro = {
                'erro': 'Análise de prestação inválida.',
                'mensagem': f"A análise de lançamento {analise_lancamento_uuid} não pertence à Prestação de Contas {uuid}."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        return Response(AnaliseLancamentoPrestacaoContaSolicitacoesNaoAgrupadasRetrieveSerializer(analise_lancamento).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def documentos(self, request, uuid):
        prestacao_conta = PrestacaoConta.by_uuid(uuid)

        # Define a análise da prestação de contas
        analise_prestacao_uuid = self.request.query_params.get('analise_prestacao')

        if not analise_prestacao_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da analise de prestacao de contas.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            analise_prestacao = AnalisePrestacaoConta.objects.get(uuid=analise_prestacao_uuid)
        except AnalisePrestacaoConta.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto analise-prestacao-conta para o uuid {analise_prestacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if analise_prestacao.prestacao_conta != prestacao_conta:
            erro = {
                'erro': 'Análise de prestação inválida.',
                'mensagem': f"A análise de prestação {analise_prestacao_uuid} não pertence à Prestação de Contas {uuid}."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        documentos = documentos_da_prestacao(analise_prestacao_conta=analise_prestacao)

        return Response(documentos, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path="documentos-corretos",
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def documentos_corretos(self, request, uuid):
        prestacao_conta = PrestacaoConta.by_uuid(uuid)

        analise_prestacao_uuid = request.data.get('analise_prestacao', None)
        if analise_prestacao_uuid is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'lancamentos-corretos',
                'mensagem': 'Faltou informar no payload o UUID da analise_prestacao.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            analise_prestacao = AnalisePrestacaoConta.objects.get(uuid=analise_prestacao_uuid)
        except AnalisePrestacaoConta.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto analise-prestacao-conta para o uuid {analise_prestacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if analise_prestacao.prestacao_conta != prestacao_conta:
            erro = {
                'erro': 'Análise de prestação inválida.',
                'mensagem': f"A análise de prestação {analise_prestacao_uuid} não pertence à Prestação de Contas {uuid}."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        documentos_corretos = request.data.get('documentos_corretos', None)
        if documentos_corretos is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'documentos-corretos',
                'mensagem': 'Faltou informar a lista com os documentos corretos.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        marca_documentos_como_corretos(analise_prestacao, documentos_corretos)

        return Response({"message": "Documentos marcados como corretos."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path="documentos-nao-conferidos",
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def documentos_nao_conferidos(self, request, uuid):
        prestacao_conta = PrestacaoConta.by_uuid(uuid)

        analise_prestacao_uuid = request.data.get('analise_prestacao', None)
        if analise_prestacao_uuid is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'documentos-nao-conferidos',
                'mensagem': 'Faltou informar no payload o UUID da analise_prestacao.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            analise_prestacao = AnalisePrestacaoConta.objects.get(uuid=analise_prestacao_uuid)
        except AnalisePrestacaoConta.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto analise-prestacao-conta para o uuid {analise_prestacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if analise_prestacao.prestacao_conta != prestacao_conta:
            erro = {
                'erro': 'Análise de prestação inválida.',
                'mensagem': f"A análise de prestação {analise_prestacao_uuid} não pertence à Prestação de Contas {uuid}."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        documentos_nao_conferidos = request.data.get('documentos_nao_conferidos', None)
        if documentos_nao_conferidos is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'documentos-nao-conferidos',
                'mensagem': 'Faltou informar a lista com os documentos não conferidos.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        marca_documentos_como_nao_conferidos(analise_prestacao, documentos_nao_conferidos)

        return Response({"message": "Documentos marcados como não conferidos."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path="solicitacoes-de-acerto-documento",
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def solicitacoes_acerto_documento(self, request, uuid):
        prestacao_conta = PrestacaoConta.by_uuid(uuid)

        analise_prestacao_uuid = request.data.get('analise_prestacao', None)
        if analise_prestacao_uuid is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'solicitacoes-de-acerto-documento',
                'mensagem': 'Faltou informar no payload o UUID da analise_prestacao.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            analise_prestacao = AnalisePrestacaoConta.objects.get(uuid=analise_prestacao_uuid)
        except AnalisePrestacaoConta.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto analise-prestacao-conta para o uuid {analise_prestacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if analise_prestacao.prestacao_conta != prestacao_conta:
            erro = {
                'erro': 'Análise de prestação inválida.',
                'mensagem': f"A análise de prestação {analise_prestacao_uuid} não pertence à Prestação de Contas {uuid}."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        documentos = request.data.get('documentos', None)
        if documentos is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'solicitacoes-de-acerto-documento',
                'mensagem': 'Faltou informar a lista com os documentos. documentos:'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        solicitacoes_acerto = request.data.get('solicitacoes_acerto', None)
        if solicitacoes_acerto is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'solicitacoes-de-acerto-documento',
                'mensagem': 'Faltou informar a lista com as solicitações de acerto. solicitacoes_acerto:'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        solicita_acertos_de_documentos(
            analise_prestacao=analise_prestacao,
            documentos=documentos,
            solicitacoes_acerto=solicitacoes_acerto
        )

        return Response({"message": "Solicitações de acerto gravadas para os documentos."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path="analises-de-documento",
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def analises_de_documento(self, request, uuid):
        prestacao_conta = PrestacaoConta.by_uuid(uuid)

        # Define a análise de documento
        analise_documento_uuid = self.request.query_params.get('analise_documento')

        if analise_documento_uuid is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'analises-de-documento',
                'mensagem': 'Faltou informar o parâmetro analise_documento com o UUID da analise de documento.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            analise_documento = AnaliseDocumentoPrestacaoConta.objects.get(uuid=analise_documento_uuid)
        except AnaliseLancamentoPrestacaoConta.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto analise-documento-prestacao-conta para o uuid {analise_documento_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if analise_documento.analise_prestacao_conta.prestacao_conta != prestacao_conta:
            erro = {
                'erro': 'Análise de prestação inválida.',
                'mensagem': f"A análise de documento {analise_documento_uuid} não pertence à Prestação de Contas {uuid}."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        return Response(AnaliseDocumentoPrestacaoContaRetrieveSerializer(analise_documento).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path="devolucoes",
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def devolucoes(self, request, uuid):
        prestacao_conta = PrestacaoConta.by_uuid(uuid)
        devolucoes = prestacao_conta.analises_da_prestacao.filter(status='DEVOLVIDA').order_by('id')
        return Response(AnalisePrestacaoContaRetrieveSerializer(devolucoes, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path="ultima-analise-pc", permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def ultima_analise_da_pc(self, request, uuid):
        prestacao_conta = PrestacaoConta.by_uuid(uuid)
        ultima_analise_pc = prestacao_conta.analises_da_prestacao.order_by('id').last()
        return Response(AnalisePrestacaoContaRetrieveSerializer(ultima_analise_pc, many=False).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path="receber-apos-acertos",
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def receber_apos_acertos(self, request, uuid):
        prestacao_conta = self.get_object()

        data_recebimento = request.data.get('data_recebimento_apos_acertos', None)
        if not data_recebimento:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'receber-apos-acertos',
                'mensagem': 'Faltou informar a data de recebimento da Prestação de Contas. data_recebimento_apos_acertos'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if prestacao_conta.status != PrestacaoConta.STATUS_DEVOLVIDA_RETORNADA:
            response = {
                'uuid': f'{uuid}',
                'erro': 'status_nao_permite_operacao',
                'status': prestacao_conta.status,
                'operacao': 'receber-apos-acertos',
                'mensagem': 'Você não pode receber após acertos uma prestação de contas com status diferente de DEVOLVIDA_RETORNADA.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        prestacao_recebida = prestacao_conta.receber_apos_acertos(data_recebimento_apos_acertos=data_recebimento)

        return Response(PrestacaoContaRetrieveSerializer(prestacao_recebida, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='desfazer-recebimento-apos-acertos',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def desfazer_recebimento_apos_acertos(self, request, uuid):
        prestacao_conta = self.get_object()

        if prestacao_conta.status != PrestacaoConta.STATUS_DEVOLVIDA_RECEBIDA:
            response = {
                'uuid': f'{prestacao_conta.uuid}',
                'erro': 'status_nao_permite_operacao',
                'status': prestacao_conta.status,
                'operacao': 'desfazer-recebimento-apos-acertos',
                'mensagem': 'Impossível desfazer recebimento após acertos de uma PC com status diferente de DEVOLVIDA_RECEBIDA.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        prestacao_atualizada = prestacao_conta.desfazer_recebimento_apos_acertos()

        return Response(PrestacaoContaRetrieveSerializer(prestacao_atualizada, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path="previa",
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def previa_pc(self, request):
        # Determinar Associação
        associacao_uuid = request.query_params.get('associacao')
        if not associacao_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'operacao': 'previa',
                'mensagem': 'É necessário informar o uuid da associação. ?associacao=uuida_da_associacao'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            associacao = Associacao.objects.get(uuid=associacao_uuid)
        except Associacao.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto associação para o uuid {associacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina o período
        periodo_uuid = self.request.query_params.get('periodo')

        if not periodo_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'operacao': 'previa',
                'mensagem': 'Faltou informar o uuid do período. ?periodo=uuid_do_periodo'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except Periodo.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        previa_pc = previa_prestacao_conta(associacao=associacao, periodo=periodo)

        return Response(previa_pc)

    @action(detail=False, methods=['get'], url_path="previa-info-para-ata",
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def get_previa_info_para_ata(self, request):
        # Determinar Associação
        associacao_uuid = request.query_params.get('associacao')
        if not associacao_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'operacao': 'previa',
                'mensagem': 'É necessário informar o uuid da associação. ?associacao=uuida_da_associacao'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            associacao = Associacao.objects.get(uuid=associacao_uuid)
        except Associacao.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto associação para o uuid {associacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina o período
        periodo_uuid = self.request.query_params.get('periodo')

        if not periodo_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'operacao': 'previa',
                'mensagem': 'Faltou informar o uuid do período. ?periodo=uuid_do_periodo'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except Periodo.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        previa_info = previa_informacoes_financeiras_para_atas(associacao=associacao, periodo=periodo)
        return Response(previa_info)

    @action(detail=False, methods=['post'], url_path='iniciar-previa-ata',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def iniciar_previa_ata(self, request):
        # Determinar Associação
        associacao_uuid = request.query_params.get('associacao')
        if not associacao_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'operacao': 'previa',
                'mensagem': 'É necessário informar o uuid da associação. ?associacao=uuida_da_associacao'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            associacao = Associacao.objects.get(uuid=associacao_uuid)
        except Associacao.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto associação para o uuid {associacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina o período
        periodo_uuid = self.request.query_params.get('periodo')

        if not periodo_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'operacao': 'previa',
                'mensagem': 'Faltou informar o uuid do período. ?periodo=uuid_do_periodo'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except Periodo.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        ata = Ata.objects.filter(associacao=associacao, periodo=periodo)

        if ata:
            erro = {
                'erro': 'ata-ja-iniciada',
                'mensagem': 'Já existe uma ata iniciada para esse período e associação.'
            }
            return Response(erro, status=status.HTTP_409_CONFLICT)

        ata = Ata.iniciar_previa(associacao=associacao, periodo=periodo)

        return Response(AtaLookUpSerializer(ata, many=False).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='contas-com-movimento',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def contas_com_movimento(self, request, uuid):
        from ..serializers.conta_associacao_serializer import ContaAssociacaoDadosSerializer

        prestacao_conta: PrestacaoConta = self.get_object()
        contas = prestacao_conta.get_contas_com_movimento()

        return Response(ContaAssociacaoDadosSerializer(contas, many=True).data)

    @action(detail=True, methods=['get'], url_path='contas-com-movimento-despesas-periodos-anteriores',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def contas_com_movimento_despesas_periodos_anteriores(self, request, uuid):
        from ..serializers.conta_associacao_serializer import ContaAssociacaoDadosSerializer

        prestacao_conta: PrestacaoConta = self.get_object()
        contas = prestacao_conta.get_contas_com_movimento_em_periodos_anteriores()

        return Response(ContaAssociacaoDadosSerializer(contas, many=True).data)

    @action(detail=True, methods=['post'], url_path='notificar/pendencia_geracao_ata_apresentacao',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def notificar_pendencia_geracao_ata_apresentacao(self, request, uuid):
        from sme_ptrf_apps.core.services.notificacao_services.notificacao_pendencia_geracao_ata import notificar_pendencia_geracao_ata_apresentacao
        prestacao_contas = self.get_object()

        if not prestacao_contas.ata_apresentacao_gerada():
            notificar_pendencia_geracao_ata_apresentacao(prestacao_contas)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path="despesas-periodos-anteriores",
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def despesas_periodos_anteriores(self, request, uuid):
        from sme_ptrf_apps.core.api.serializers.validation_serializers.prestacoes_contas_lancamentos_validate_serializer import PrestacoesContasLancamentosValidateSerializer
        prestacao_conta = PrestacaoConta.by_uuid(uuid)

        filtro_informacoes = self.request.query_params.get('filtrar_por_informacoes')
        filtro_informacoes_list = filtro_informacoes.split(',') if filtro_informacoes else []

        filtro_conferencia = self.request.query_params.get('filtrar_por_conferencia')
        filtro_conferencia_list = filtro_conferencia.split(',') if filtro_conferencia else []

        query = PrestacoesContasLancamentosValidateSerializer(data=self.request.query_params, context={
                                                              'prestacao_conta': prestacao_conta})
        query.is_valid(raise_exception=True)

        lancamentos = lancamentos_da_prestacao(
            analise_prestacao_conta=AnalisePrestacaoConta.by_uuid(self.request.query_params.get('analise_prestacao')),
            conta_associacao=ContaAssociacao.by_uuid(self.request.query_params.get('conta_associacao')),
            acao_associacao=AcaoAssociacao.by_uuid(request.query_params.get(
                'acao_associacao')) if request.query_params.get('acao_associacao') else None,
            tipo_transacao="GASTOS",
            apenas_despesas_de_periodos_anteriores=True,
            ordenar_por_imposto=request.query_params.get('ordenar_por_imposto'),
            numero_de_documento=request.query_params.get('filtrar_por_numero_de_documento'),
            tipo_de_documento=TipoDocumento.by_id(request.query_params.get(
                'filtrar_por_tipo_de_documento')) if request.query_params.get('filtrar_por_tipo_de_documento') else None,
            tipo_de_pagamento=TipoTransacao.by_id(request.query_params.get(
                'filtrar_por_tipo_de_pagamento')) if request.query_params.get('filtrar_por_tipo_de_pagamento') else None,
            filtrar_por_data_inicio=request.query_params.get('filtrar_por_data_inicio'),
            filtrar_por_data_fim=request.query_params.get('filtrar_por_data_fim'),
            filtrar_por_nome_fornecedor=request.query_params.get('filtrar_por_nome_fornecedor'),
            filtro_informacoes_list=filtro_informacoes_list,
            filtro_conferencia_list=filtro_conferencia_list,
        )

        return Response(lancamentos, status=status.HTTP_200_OK)
