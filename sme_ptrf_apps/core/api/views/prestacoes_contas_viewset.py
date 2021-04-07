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
from ...models import Associacao, Ata, Periodo, PrestacaoConta, Unidade
from ...services import (
    concluir_prestacao_de_contas,
    informacoes_financeiras_para_atas,
    reabrir_prestacao_de_contas,
    lista_prestacoes_de_conta_nao_recebidas,
)
from ....dre.services import (dashboard_sme)
from ..serializers import (
    AtaLookUpSerializer,
    PrestacaoContaListSerializer,
    PrestacaoContaLookUpSerializer,
    PrestacaoContaRetrieveSerializer,
)

logger = logging.getLogger(__name__)


class PrestacoesContasViewSet(mixins.RetrieveModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.ListModelMixin,
                              GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = PrestacaoConta.objects.all()
    serializer_class = PrestacaoContaLookUpSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    filter_fields = ('associacao__unidade__dre__uuid', 'periodo__uuid', 'associacao__unidade__tipo_unidade')

    def get_queryset(self):
        qs = PrestacaoConta.objects.all()

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
            prestacao_de_contas = concluir_prestacao_de_contas(associacao=associacao, periodo=periodo)
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
