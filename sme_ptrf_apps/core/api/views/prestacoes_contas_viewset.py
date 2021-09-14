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

from sme_ptrf_apps.users.permissoes import (
    PermissaoApiUe,
    PermissaoAPITodosComLeituraOuGravacao,
    PermissaoAPITodosComGravacao,
    PermissaoAPIApenasDreComGravacao,
)

from ....dre.models import Atribuicao, TecnicoDre, MotivoAprovacaoRessalva
from ...models import (
    Associacao,
    Ata,
    Periodo,
    PrestacaoConta,
    Unidade,
    ContaAssociacao,
    AcaoAssociacao,
    AnalisePrestacaoConta,
    AnaliseLancamentoPrestacaoConta
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
)
from ....dre.services import (dashboard_sme)
from ..serializers import (
    AtaLookUpSerializer,
    PrestacaoContaListSerializer,
    PrestacaoContaLookUpSerializer,
    PrestacaoContaRetrieveSerializer,
    AnaliseLancamentoPrestacaoContaRetrieveSerializer
)

from django.core.exceptions import ValidationError

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
    filter_fields = ('associacao__unidade__dre__uuid', 'periodo__uuid', 'associacao__unidade__tipo_unidade')

    def get_queryset(self):
        qs = PrestacaoConta.objects.all().order_by('associacao__unidade__tipo_unidade', 'associacao__unidade__nome')

        status = self.request.query_params.get('status')
        if status is not None:
            if status in ['APROVADA', 'APROVADA_RESSALVA']:
                qs = qs.filter(Q(status='APROVADA') | Q(status='APROVADA_RESSALVA'))
            else:
                qs = qs.filter(status=status)

        nome = self.request.query_params.get('nome')
        if nome is not None:
            qs = qs.filter(Q(associacao__nome__unaccent__icontains=nome) | Q(
                associacao__unidade__nome__unaccent__icontains=nome))

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

    @action(detail=False, methods=['post'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def concluir(self, request):
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

        try:
            prestacao_de_contas = concluir_prestacao_de_contas(associacao=associacao, periodo=periodo,
                                                               usuario=request.user.username)
        except(IntegrityError):
            erro = {
                'erro': 'prestacao_ja_iniciada',
                'mensagem': 'Você não pode iniciar uma prestação de contas que já foi iniciada.'
            }
            return Response(erro, status=status.HTTP_409_CONFLICT)

        return Response(PrestacaoContaLookUpSerializer(prestacao_de_contas, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'],
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def reabrir(self, request, uuid):

        prestacao_de_contas = PrestacaoConta.by_uuid(uuid)

        if prestacao_de_contas:
            associacao = prestacao_de_contas.associacao
            prestacao_de_contas_posteriores = PrestacaoConta.objects.filter(associacao=associacao, id__gt=prestacao_de_contas.id)

            if prestacao_de_contas_posteriores:
                response = {
                    'uuid': f'{uuid}',
                    'erro': 'prestacao_de_contas_posteriores',
                    'operacao': 'reabrir',
                    'mensagem': 'Essa prestação de contas não pode ser reaberta porque há prestação de contas dessa mesma associação de um período posterior. Se necessário, reabra primeiramente a prestação de contas mais recente.'
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

        if prestacao_conta.status != PrestacaoConta.STATUS_RECEBIDA:
            response = {
                'uuid': f'{prestacao_conta.uuid}',
                'erro': 'status_nao_permite_operacao',
                'status': prestacao_conta.status,
                'operacao': 'analisar',
                'mensagem': 'Você não pode analisar uma prestação de contas com status diferente de RECEBIDA.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        prestacao_atualizada = prestacao_conta.analisar()

        return Response(PrestacaoContaRetrieveSerializer(prestacao_atualizada, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='desfazer-analise',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def desfazer_analise(self, request, uuid):
        prestacao_conta = self.get_object()

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

        devolucao_tesouro = request.data.get('devolucao_tesouro', None)
        if devolucao_tesouro is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'salvar-analise',
                'mensagem': 'Faltou informar o campo devolucao_tesouro.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        analises_de_conta_da_prestacao = request.data.get('analises_de_conta_da_prestacao', None)
        if analises_de_conta_da_prestacao is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'salvar-analise',
                'mensagem': 'Faltou informar o campo analises_de_conta_da_prestacao.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        devolucoes_ao_tesouro_da_prestacao = request.data.get('devolucoes_ao_tesouro_da_prestacao', [])

        if prestacao_conta.status != PrestacaoConta.STATUS_EM_ANALISE:
            response = {
                'uuid': f'{uuid}',
                'erro': 'status_nao_permite_operacao',
                'status': prestacao_conta.status,
                'operacao': 'salvar-analise',
                'mensagem': 'Você não pode salvar análise de uma prestação de contas com status diferente de EM_ANALISE.'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        prestacao_salva = prestacao_conta.salvar_analise(devolucao_tesouro=devolucao_tesouro,
                                                         analises_de_conta_da_prestacao=analises_de_conta_da_prestacao,
                                                         devolucoes_ao_tesouro_da_prestacao=devolucoes_ao_tesouro_da_prestacao)

        return Response(PrestacaoContaRetrieveSerializer(prestacao_salva, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='salvar-devolucoes-ao-tesouro',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def salvar_devolucoes_ao_tesouro(self, request, uuid):
        prestacao_conta = self.get_object()

        devolucoes_ao_tesouro_da_prestacao = request.data.get('devolucoes_ao_tesouro_da_prestacao', [])

        if prestacao_conta.status not in [PrestacaoConta.STATUS_EM_ANALISE, PrestacaoConta.STATUS_DEVOLVIDA]:
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

        devolucao_tesouro = request.data.get('devolucao_tesouro', None)
        if devolucao_tesouro is None:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'concluir-analise',
                'mensagem': 'Faltou informar o campo devolucao_tesouro.'
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

        devolucoes_ao_tesouro_da_prestacao = request.data.get('devolucoes_ao_tesouro_da_prestacao', [])

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

        motivos_reprovacao = request.data.get('motivos_reprovacao', '')

        if resultado_analise == PrestacaoConta.STATUS_REPROVADA and not motivos_reprovacao:
            response = {
                'uuid': f'{uuid}',
                'erro': 'falta_de_informacoes',
                'operacao': 'concluir-analise',
                'mensagem': 'Para concluir como Reprovada é necessário informar o campo motivos_reprovacao.'
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

            associacao = prestacao_conta.associacao
            prestacao_de_contas_posteriores = PrestacaoConta.objects.filter(associacao=associacao,
                                                                            id__gt=prestacao_conta.id)

            if prestacao_de_contas_posteriores:
                response = {
                    'uuid': f'{uuid}',
                    'erro': 'prestacao_de_contas_posteriores',
                    'operacao': 'concluir-analise',
                    'mensagem': 'Essa prestação de contas não pode ser devolvida porque há prestação de contas dessa mesma associação de um período posterior. Se necessário, devolva para ajuste a prestação de contas mais recente.'
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        prestacao_salva = prestacao_conta.concluir_analise(
            resultado_analise=resultado_analise,
            devolucao_tesouro=devolucao_tesouro,
            analises_de_conta_da_prestacao=analises_de_conta_da_prestacao,
            motivos_aprovacao_ressalva=motivos_aprovacao_ressalva,
            outros_motivos_aprovacao_ressalva=outros_motivos_aprovacao_ressalva,
            data_limite_ue=data_limite_ue,
            motivos_reprovacao=motivos_reprovacao,
            devolucoes_ao_tesouro_da_prestacao=devolucoes_ao_tesouro_da_prestacao
        )

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
        periodo = request.query_params.get('periodo')

        if not dre_uuid or not periodo:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o uuid da dre (dre_uuid) e o periodo como parâmetros.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        total_associacoes_dre = Associacao.objects.filter(unidade__dre__uuid=dre_uuid).exclude(cnpj__exact='').count()

        par_add_aprovados_ressalva = request.query_params.get('add_aprovadas_ressalva')
        add_aprovados_ressalva = par_add_aprovados_ressalva == 'SIM'
        cards = PrestacaoConta.dashboard(periodo, dre_uuid, add_aprovado_ressalva=add_aprovados_ressalva)
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
        }
        return Response(result)

    @action(detail=False, url_path='nao-recebidas',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def nao_recebidas(self, _):
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

        if status_pc and status_pc not in [PrestacaoConta.STATUS_NAO_APRESENTADA, PrestacaoConta.STATUS_NAO_RECEBIDA]:
            erro = {
                'erro': 'status-invalido',
                'operacao': 'nao-recebidas',
                'mensagem': 'Só é possível filtrar não recebidas pelos status NAO_APRESENTADA e NAO_RECEBIDA.'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        result = lista_prestacoes_de_conta_nao_recebidas(dre=dre,
                                                         periodo=periodo,
                                                         filtro_nome=nome,
                                                         filtro_tipo_unidade=tipo_unidade,
                                                         filtro_status=status_pc
                                                         )
        return Response(result)

    @action(detail=False, url_path='todos-os-status',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def todos_os_status(self, _):
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

        # Pega filtros
        nome = self.request.query_params.get('nome')
        tipo_unidade = self.request.query_params.get('tipo_unidade')
        status_pc = self.request.query_params.get('status')

        if status_pc and status_pc not in ['TODOS']:
            erro = {
                'erro': 'status-invalido',
                'operacao': 'todos-os-status',
                'mensagem': 'Só é possível filtrar Todos pelo status TODOS'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        result = lista_prestacoes_de_conta_todos_os_status(
            dre=dre,
            periodo=periodo,
            filtro_nome=nome,
            filtro_tipo_unidade=tipo_unidade,
        )
        return Response(result)

    @action(detail=False, methods=['get'], url_path="dashboard-sme",
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def dashboard_sme(self, request):
        # Determina o período
        periodo_uuid = self.request.query_params.get('periodo')

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

        dashboard = dashboard_sme(periodo=periodo)

        return Response(dashboard)

    @action(detail=True, methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def lancamentos(self, request, uuid):
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

        # Define a conta de conciliação
        conta_associacao_uuid = self.request.query_params.get('conta_associacao')

        if not conta_associacao_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da conta da associação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            conta_associacao = ContaAssociacao.objects.get(uuid=conta_associacao_uuid)
        except ContaAssociacao.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto conta-associação para o uuid {conta_associacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Define a ação para o filtro de transações
        acao_associacao = None
        acao_associacao_uuid = request.query_params.get('acao_associacao')
        if acao_associacao_uuid:
            try:
                acao_associacao = AcaoAssociacao.objects.get(uuid=acao_associacao_uuid)
            except AcaoAssociacao.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto ação-associação para o uuid {acao_associacao_uuid} não foi encontrado."
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Define o tipo de transação para o filtro das transações
        tipo_transacao = request.query_params.get('tipo')
        if tipo_transacao and tipo_transacao not in ('CREDITOS', 'GASTOS'):
            erro = {
                'erro': 'parametro_inválido',
                'mensagem': 'O parâmetro tipo pode receber como valor "CREDITOS" ou "GASTOS". O parâmetro é opcional.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        lancamentos = lancamentos_da_prestacao(
            analise_prestacao_conta=analise_prestacao,
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            tipo_transacao=tipo_transacao
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
                'operacao': 'get-solicitacoes-acerto',
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

        return Response(AnaliseLancamentoPrestacaoContaRetrieveSerializer(analise_lancamento).data, status=status.HTTP_200_OK)

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
