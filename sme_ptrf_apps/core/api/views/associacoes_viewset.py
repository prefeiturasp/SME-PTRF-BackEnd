import datetime
import logging
from io import BytesIO

from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import render_to_string
from django_filters import rest_framework as filters
from openpyxl.writer.excel import save_virtual_workbook
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from weasyprint import HTML

from sme_ptrf_apps.paa.models import PeriodoPaa
from sme_ptrf_apps.paa.api.serializers import PaaSerializer

from sme_ptrf_apps.users.permissoes import (
    PermissaoApiUe,
    PermissaoAPITodosComLeituraOuGravacao,
    PermissaoAPITodosComGravacao,
    PermissaoAPIApenasDreComGravacao,
    PermissaoAPIApenasDreComLeituraOuGravacao
)
from ....despesas.models import Despesa

from ....dre.services import (
    get_verificacao_regularidade_associacao,
    get_lista_associacoes_e_status_regularidade_no_ano,
    atualiza_itens_verificacao,
)
from ...models import Associacao, ContaAssociacao, Periodo, PrestacaoConta, Unidade, Ata, AnalisePrestacaoConta, \
    FechamentoPeriodo
from ...services import (
    atualiza_dados_unidade,
    gerar_planilha,
    implanta_saldos_da_associacao,
    status_prestacao_conta_associacao,
    consulta_unidade,
    get_status_presidente,
    update_status_presidente,
    get_implantacao_de_saldos_da_associacao,
    retorna_repasses_pendentes_periodos_ate_agora
)
from ..serializers.associacao_serializer import (
    AssociacaoCompletoSerializer,
    AssociacaoCreateSerializer,
    AssociacaoUpdateSerializer,
    AssociacaoListSerializer,
    AssociacaoSerializer,
)
from ..serializers.conta_associacao_serializer import (
    ContaAssociacaoCreateSerializer,
    ContaAssociacaoDadosSerializer,
)
from ..serializers.periodo_serializer import PeriodoLookUpSerializer
from ..serializers.processo_associacao_serializer import ProcessoAssociacaoRetrieveSerializer

from ..serializers.ata_serializer import AtaLookUpSerializer

from sme_ptrf_apps.core.services.prestacao_contas_services import pc_requer_geracao_documentos, lancamentos_da_prestacao
from ....receitas.models import Receita
from ...choices import FiltroInformacoesAssociacao
from waffle import flag_is_active

logger = logging.getLogger(__name__)


class AssociacoesViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = Associacao.objects.all()
    serializer_class = AssociacaoSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    filterset_fields = ('unidade__dre__uuid', 'unidade__tipo_unidade')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        atualiza_dados_unidade(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AssociacaoCompletoSerializer
        elif self.action == 'list':
            return AssociacaoListSerializer
        elif self.action == 'create':
            return AssociacaoCreateSerializer
        else:
            return AssociacaoUpdateSerializer

    def destroy(self, request, *args, **kwargs):
        from django.db.models.deletion import ProtectedError

        obj = self.get_object()

        try:
            self.perform_destroy(obj)
        except ProtectedError:
            content = {
                'erro': 'ProtectedError',
                'mensagem': 'Não é possível excluir essa associação porque ela já possui movimentação (despesas, receitas, etc.)'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        qs = Associacao.objects.all().order_by('unidade__tipo_unidade', 'unidade__nome')

        uuid_dre = self.request.query_params.get('unidade__dre__uuid')
        if uuid_dre is not None and uuid_dre != "":
            qs = qs.filter(unidade__dre__uuid=uuid_dre)

        nome = self.request.query_params.get('nome')
        if nome is not None:
            qs = qs.filter(Q(unidade__codigo_eol=nome) | Q(nome__unaccent__icontains=nome) | Q(
                unidade__nome__unaccent__icontains=nome))

        filtro_informacoes = self.request.query_params.get('filtro_informacoes')
        filtro_informacoes_list = filtro_informacoes.split(',') if filtro_informacoes else []

        if filtro_informacoes_list:
            ids_para_excluir_da_listagem = []
            for associacao in qs:
                excluir_associacao_da_listagem = True
                if Associacao.TAG_ENCERRADA['key'] in filtro_informacoes_list and associacao.foi_encerrada():
                    excluir_associacao_da_listagem = False

                if Associacao.TAG_ENCERRAMENTO_DE_CONTA['key'] in filtro_informacoes_list and associacao.tem_solicitacao_conta_pendente():
                    excluir_associacao_da_listagem = False

                if excluir_associacao_da_listagem:
                    ids_para_excluir_da_listagem.append(associacao.id)

            qs = qs.exclude(id__in=ids_para_excluir_da_listagem)

        return qs

    @action(detail=True, url_path='repasses-pendentes-por-periodo', methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def repasses_pendentes_por_periodo(self, request, uuid=None):

        associacao = self.get_object()
        periodo_uuid = request.query_params.get('periodo_uuid')

        if periodo_uuid is None or not periodo_uuid:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o uuid do período.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.filter(uuid=periodo_uuid).get()
        except (ValidationError, Exception):
            erro = {
                'erro': 'parametro_invalido',
                'mensagem': f"Não foi encontrado o objeto periodo para o uuid {periodo_uuid}"
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        resultado = retorna_repasses_pendentes_periodos_ate_agora(associacao, periodo)

        return Response(resultado)

    @action(detail=True, url_path='painel-acoes',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def painel_acoes(self, request, uuid=None):
        from sme_ptrf_apps.core.services.painel_resumo_recursos_service import PainelResumoRecursosService

        periodo_uuid = request.query_params.get('periodo_uuid')

        if periodo_uuid:
            try:
                periodo = Periodo.by_uuid(periodo_uuid)
            except (ValidationError, Exception):
                erro = {'erro': 'UUID do período inválido.'}
                return Response(erro, status=status.HTTP_404_NOT_FOUND)
        else:
            periodo = Periodo.periodo_atual()

        conta_associacao_uuid = request.query_params.get('conta')

        try:
            conta_associacao = ContaAssociacao.by_uuid(conta_associacao_uuid) if conta_associacao_uuid else None
        except (ValidationError, Exception):
            erro = {'erro': 'UUID da conta inválido.'}
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        painel = PainelResumoRecursosService.painel_resumo_recursos(
            self.get_object(),
            periodo,
            conta_associacao
        )

        result = painel.to_json()

        return Response(result)

    @action(detail=True, url_path='status-periodo',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def status_periodo(self, request, uuid=None):
        associacao = self.get_object()

        data = request.query_params.get('data')

        if data is None:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar a data que você quer consultar o status.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        periodo = Periodo.da_data(data)
        prestacao_conta = None
        if periodo:
            periodo_referencia = periodo.referencia
            prestacao_conta_status = status_prestacao_conta_associacao(periodo_uuid=periodo.uuid, associacao_uuid=uuid)
            aceita_alteracoes = not prestacao_conta_status['periodo_bloqueado'] if prestacao_conta_status else True
            prestacao_conta = PrestacaoConta.by_periodo(associacao=associacao, periodo=periodo)
        else:
            periodo_referencia = ''
            aceita_alteracoes = True
            prestacao_conta_status = {}

        gerar_ou_editar_ata_apresentacao = False
        gerar_ou_editar_ata_retificacao = False

        if prestacao_conta_status:
            if prestacao_conta_status['status_prestacao'] == 'NAO_RECEBIDA' or prestacao_conta_status[
                    'status_prestacao'] == 'NAO_APRESENTADA':
                gerar_ou_editar_ata_apresentacao = True

            if prestacao_conta_status['status_prestacao'] == 'DEVOLVIDA_RETORNADA' or prestacao_conta_status[
                    'status_prestacao'] == 'DEVOLVIDA':
                gerar_ou_editar_ata_retificacao = True

        gerar_previas = True
        if prestacao_conta:
            gerar_previas = pc_requer_geracao_documentos(prestacao_conta)

        # TODO código comentado propositalmente em função da história 102412 - Sprint 73 (Conciliação Bancária: Retirar validação e obrigatoriedade de preenchimento dos campos do Saldo bancário da conta ao concluir acerto/período) - que entrou como Hotfix
        # TODO Remover quando implementado solução definitiva
        pendencias_dados = associacao.pendencias_dados_da_associacao()
        pendencias_conciliacao = associacao.pendencias_conciliacao_bancaria_por_periodo_para_geracao_de_documentos(
            periodo)

        # if pendencias_dados or pendencias_conciliacao:
        #     pendencias_cadastrais = {
        #         'dados_associacao': pendencias_dados,
        #         'conciliacao_bancaria': pendencias_conciliacao,
        #     }

        if pendencias_dados:
            pendencias_cadastrais = {
                'dados_associacao': pendencias_dados,
                'conciliacao_bancaria': None,
            }
        else:
            pendencias_cadastrais = None

        from sme_ptrf_apps.core.services.conta_associacao_service import checa_se_tem_conta_encerrada_com_saldo_no_periodo

        tem_conta_encerrada_com_saldo, tipos_das_contas_encerradas = checa_se_tem_conta_encerrada_com_saldo_no_periodo(
            associacao, periodo, data)

        result = {
            'associacao': f'{uuid}',
            'periodo_referencia': periodo_referencia,
            'aceita_alteracoes': aceita_alteracoes,
            'prestacao_contas_status': prestacao_conta_status,
            'prestacao_conta': prestacao_conta.uuid if prestacao_conta else '',
            'gerar_ou_editar_ata_apresentacao': gerar_ou_editar_ata_apresentacao,
            'gerar_ou_editar_ata_retificacao': gerar_ou_editar_ata_retificacao,
            'gerar_previas': gerar_previas,
            'pendencias_cadastrais': pendencias_cadastrais,
            'tem_conta_encerrada_com_saldo': tem_conta_encerrada_com_saldo,
            'tipos_das_contas_encerradas_com_saldo': tipos_das_contas_encerradas
        }

        return Response(result)

    @action(detail=True, url_path='permite-implantacao-saldos', methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def permite_implantacao_saldos(self, request, uuid=None):
        from ...services import associacao_pode_implantar_saldo

        associacao = self.get_object()

        result = associacao_pode_implantar_saldo(associacao=associacao)

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, url_path='implantacao-saldos', methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def implantacao_saldos(self, request, uuid=None):
        result = get_implantacao_de_saldos_da_associacao(associacao=self.get_object())
        return Response(result['conteudo'], result['status_code'])

    @action(detail=True, url_path='implanta-saldos', methods=['post'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def implanta_saldos(self, request, uuid=None):

        associacao = self.get_object()

        saldos = request.data.get('saldos', None)

        if not saldos:
            result_error = {
                'erro': 'campo_requerido',
                'mensagem': 'É necessário enviar os saldos para implantação.'
            }
            return Response(result_error, status=status.HTTP_400_BAD_REQUEST)

        resultado_implantacao = implanta_saldos_da_associacao(associacao=associacao, saldos=saldos)

        if resultado_implantacao['saldo_implantado']:
            result = {
                'associacao': f'{uuid}',
                'periodo': PeriodoLookUpSerializer(associacao.periodo_inicial).data,
                'saldos': saldos,
            }
            status_code = status.HTTP_200_OK
        else:
            result = {
                'erro': resultado_implantacao['codigo_erro'],
                'mensagem': resultado_implantacao['mensagem']
            }
            status_code = status.HTTP_400_BAD_REQUEST

        return Response(result, status=status_code)

    @action(detail=True, url_path='contas', methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def contas(self, request, uuid=None):
        associacao = self.get_object()

        periodo_uuid = request.query_params.get('periodo_uuid')

        if periodo_uuid:
            try:
                periodo = Periodo.objects.get(uuid=periodo_uuid)
            except Periodo.DoesNotExist:
                erro = {
                    'erro': 'parametro_invalido',
                    'mensagem': f"Não foi encontrado o objeto periodo para o uuid {periodo_uuid}"
                }
                return Response(erro, status=status.HTTP_404_NOT_FOUND)

            contas = ContaAssociacao.objects.filter(
                Q(status=ContaAssociacao.STATUS_ATIVA) |
                (Q(status=ContaAssociacao.STATUS_INATIVA) &
                 Q(solicitacao_encerramento__isnull=False) &
                 Q(solicitacao_encerramento__data_de_encerramento_na_agencia__gte=periodo.data_inicio_realizacao_despesas)),
                associacao=associacao
            )

            contas_criadas_nesse_periodo_ou_anteriores = []
            for conta in contas:
                if conta.conta_criada_no_periodo_ou_periodo_anteriores(periodo):
                    contas_criadas_nesse_periodo_ou_anteriores.append(conta)
            contas = contas_criadas_nesse_periodo_ou_anteriores
        else:
            contas = ContaAssociacao.ativas_com_solicitacao_em_aberto.filter(
                associacao=associacao, data_inicio__isnull=False).all()

        contas_data = ContaAssociacaoDadosSerializer(contas, many=True).data

        return Response(contas_data)

    @action(detail=True, url_path='contas/encerradas', methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def contas_encerradas(self, request, uuid=None):
        associacao = self.get_object()
        contas = ContaAssociacao.encerradas.filter(associacao=associacao).all()
        contas_data = ContaAssociacaoDadosSerializer(contas, many=True).data
        return Response(contas_data)

    @action(detail=False, url_path='contas-com-acertos-em-lancamentos', methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def contas_com_acertos_em_lancamentos(self, request):

        associacao_uuid = request.query_params.get('associacao_uuid')
        analise_prestacao_uuid = request.query_params.get('analise_prestacao_uuid')

        if not associacao_uuid or not analise_prestacao_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o UUID da Associacao e o UUID da Análise da PC.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            associacao = Associacao.by_uuid(associacao_uuid)
        except (ValidationError, Exception):
            erro = {'erro': 'UUID da Associação inválido.'}
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            analise_prestacao = AnalisePrestacaoConta.objects.get(uuid=analise_prestacao_uuid)
        except (ValidationError, Exception):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto analise-prestacao-conta para o uuid {analise_prestacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        contas = ContaAssociacao.objects.filter(associacao=associacao).all()

        obj_contas = []
        for conta in contas:
            lancamentos = lancamentos_da_prestacao(
                analise_prestacao_conta=analise_prestacao,
                conta_associacao=conta,
                acao_associacao=None,
                tipo_transacao=None,
                tipo_acerto=None,
                com_ajustes=True,
                inclui_inativas=True,
            )
            if lancamentos:
                obj_contas.append(conta)

        contas_data = ContaAssociacaoDadosSerializer(obj_contas, many=True).data
        return Response(contas_data)

    @action(detail=False, url_path='contas-com-acertos-em-despesas-periodos-anteriores', methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def contas_com_acertos_em_despesas_periodos_anteriores(self, request):

        associacao_uuid = request.query_params.get('associacao_uuid')
        analise_prestacao_uuid = request.query_params.get('analise_prestacao_uuid')

        if not associacao_uuid or not analise_prestacao_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o UUID da Associacao e o UUID da Análise da PC.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            associacao = Associacao.by_uuid(associacao_uuid)
        except (ValidationError, Exception):
            erro = {'erro': 'UUID da Associação inválido.'}
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            analise_prestacao = AnalisePrestacaoConta.objects.get(uuid=analise_prestacao_uuid)
        except (ValidationError, Exception):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto analise-prestacao-conta para o uuid {analise_prestacao_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        contas = ContaAssociacao.objects.filter(associacao=associacao).all()

        obj_contas = []
        for conta in contas:
            lancamentos = lancamentos_da_prestacao(
                analise_prestacao_conta=analise_prestacao,
                conta_associacao=conta,
                acao_associacao=None,
                tipo_transacao="GASTOS",
                tipo_acerto=None,
                com_ajustes=True,
                inclui_inativas=True,
                apenas_despesas_de_periodos_anteriores=True,
            )
            if lancamentos:
                obj_contas.append(conta)

        contas_data = ContaAssociacaoDadosSerializer(obj_contas, many=True).data
        return Response(contas_data)

    @action(detail=True, url_path='contas-update', methods=['post'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def contas_update(self, request, uuid=None):
        logger.info("Atualizando Contas da Associação: %s", uuid)

        lista_contas = self.request.data

        if not lista_contas:
            resultado = {
                'erro': 'Lista Vazia',
                'mensagem': 'A lista de contas está vazia.'
            }

            status_code = status.HTTP_400_BAD_REQUEST
            logger.info('Erro: %r', resultado)

        for dado_conta in lista_contas:
            try:
                conta_associacao = ContaAssociacao.objects.get(uuid=dado_conta['uuid'])
            except ContaAssociacao.DoesNotExist:
                resultado = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto conta-associação para o uuid {dado_conta['uuid']} não foi encontrado na base."
                }
                status_code = status.HTTP_404_NOT_FOUND
                logger.info('Erro: %r', resultado)

            conta_serializer = ContaAssociacaoCreateSerializer(conta_associacao, data=dado_conta, partial=True)
            if conta_serializer.is_valid(raise_exception=False):
                conta_serializer.save()
            else:
                logger.info('Erro: %r', conta_serializer.errors)
                resultado = {
                    'erro': 'Erro de validação',
                    'mensagem': conta_serializer.errors
                }
                status_code = status.HTTP_404_NOT_FOUND

            resultado = {
                'mensagem': 'Contas atualizadas com sucesso'
            }
            status_code = status.HTTP_200_OK

        return Response(resultado, status=status_code)

    @action(detail=False, url_path='tabelas',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def tabelas(self, request):

        filtros_informacoes_associacao_dre = request.query_params.get('filtros_informacoes_associacao_dre')

        result = {
            'tipos_unidade': Unidade.tipos_unidade_to_json(),
            'dres': Unidade.dres_to_json(),
            'filtro_informacoes': Associacao.filtro_informacoes_dre_to_json() if filtros_informacoes_associacao_dre else Associacao.filtro_informacoes_to_json()
        }
        return Response(result)

    @staticmethod
    def _gerar_planilha(associacao_uuid):
        associacao = Associacao.by_uuid(associacao_uuid)
        xlsx = gerar_planilha(associacao)
        return xlsx

    @action(detail=True, methods=['get'], url_path='exportar',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def exportar(self, _, uuid=None):

        xlsx = self._gerar_planilha(uuid)

        result = BytesIO(save_virtual_workbook(xlsx))

        filename = 'associacao.xlsx'
        response = HttpResponse(
            result,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response

    @action(detail=True, methods=['get'], url_path='exportar-pdf',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def exportarpdf(self, _, uuid=None):

        data_atual = datetime.date.today().strftime("%d-%m-%Y")
        usuario_logado = self.request.user
        associacao = Associacao.by_uuid(uuid)
        contas = list(ContaAssociacao.objects.filter(associacao=associacao).all())
        atualiza_dados_unidade(associacao)

        dados_template = {
            'associacao': associacao,
            'contas': contas,
            'dataAtual': data_atual,
            'usuarioLogado': usuario_logado
        }

        if flag_is_active(self.request, "historico-de-membros"):
            dados_template['dados_presidente'] = associacao.dados_presidente_composicao_vigente()

        html_string = render_to_string(
            'pdf/associacoes/exportarpdf/pdf.html',
            dados_template,
            request=self.request  # Inclua o request aqui
        ).encode(encoding="UTF-8")

        html_pdf = HTML(string=html_string, base_url=self.request.build_absolute_uri()).write_pdf()

        response = HttpResponse(
            html_pdf,
            content_type='application/pdf;'
        )
        response['Content-Disposition'] = 'filename="associacao.pdf"'

        return response

    @action(detail=True, url_path='periodos-para-prestacao-de-contas', methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def periodos_para_prestacao_de_contas(self, request, uuid=None):
        associacao = self.get_object()
        ignorar_devolvidas = request.query_params.get('ignorar_devolvidas') == 'true'
        periodos = associacao.periodos_para_prestacoes_de_conta(ignorar_devolvidas)
        return Response(PeriodoLookUpSerializer(periodos, many=True).data)

    @action(detail=True, url_path='periodos-ate-agora-fora-implantacao', methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def periodos_ate_agora_fora_implantacao(self, request, uuid=None):
        associacao = self.get_object()
        periodos = associacao.periodos_ate_agora_fora_implantacao()
        return Response(PeriodoLookUpSerializer(periodos, many=True).data)

    @action(detail=True, url_path='status-prestacoes', methods=['get'],
            permission_classes=[IsAuthenticated, PermissaoAPITodosComLeituraOuGravacao])
    def status_prestacoes(self, request, uuid=None):

        from ...services.associacoes_service import retorna_status_prestacoes

        associacao = self.get_object()
        status_pc = request.query_params.get('status_pc')
        periodo_uuid = request.query_params.get('periodo_uuid')

        if periodo_uuid:
            try:
                Periodo.objects.filter(uuid=periodo_uuid).get()
                periodos = Periodo.objects.filter(uuid=periodo_uuid)
            except (ValidationError, Exception):
                erro = {
                    'erro': 'parametro_invalido',
                    'mensagem': f"Não foi encontrado o objeto periodo para o uuid {periodo_uuid}"
                }
                return Response(erro, status=status.HTTP_404_NOT_FOUND)
        else:
            periodos = associacao.periodos_ate_agora_fora_implantacao()

        lista_de_periodos = retorna_status_prestacoes(periodos=periodos, status_pc=status_pc, uuid=uuid)

        return Response(lista_de_periodos)

    @action(detail=True, url_path='processos', methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def processos_da_associacao(self, request, uuid=None):
        associacao = self.get_object()
        processos = associacao.processos.all()
        return Response(ProcessoAssociacaoRetrieveSerializer(processos, many=True).data)

    @action(detail=False, methods=['get'], url_path='eol',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def consulta_unidade(self, request):
        codigo_eol = self.request.query_params.get('codigo_eol')
        result = consulta_unidade(codigo_eol)
        status_code = status.HTTP_400_BAD_REQUEST if 'erro' in result.keys() else status.HTTP_200_OK
        return Response(result, status=status_code)

    @action(detail=True, url_path='status-presidente', methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def get_status_presidente(self, request, uuid=None):
        associacao = self.get_object()

        result = get_status_presidente(associacao=associacao)

        return Response(result)

    @action(detail=True, url_path='update-status-presidente', methods=['patch'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def update_status_presidente(self, request, uuid=None):
        associacao = self.get_object()

        status_presidente = request.data.get('status_presidente')
        cargo_substituto_presidente_ausente = request.data.get('cargo_substituto_presidente_ausente')

        try:
            result = update_status_presidente(
                associacao=associacao,
                status_presidente=status_presidente,
                cargo_substituto_presidente_ausente=cargo_substituto_presidente_ausente
            )
            return Response(result)
        except ValidationError as e:
            result = {
                'erro': 'Erro de validação.',
                'mensagem': f'{e}'
            }
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, url_path='lista-regularidade-ano',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def lista_regularidade_no_ano(self, _):
        from sme_ptrf_apps.dre.models import AnoAnaliseRegularidade
        # Determina o ano
        ano = self.request.query_params.get('ano')

        if not ano:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'lista-regularidade-ano',
                'mensagem': 'Faltou informar o ano de análise de regularidade. ?ano=2021'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            ano_analise_regularidade = AnoAnaliseRegularidade.objects.get(ano=ano)
        except AnoAnaliseRegularidade.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto AnoAnaliseRegularidade para o ano {ano} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Determina a DRE
        dre_uuid = self.request.query_params.get('dre_uuid')

        if not dre_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'lista-regularidade-ano',
                'mensagem': 'Faltou informar o uuid da dre. ?dre_uuid=uuid_da_dre'
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

        # Pega filtros
        nome = self.request.query_params.get('nome')
        tipo_unidade = self.request.query_params.get('tipo_unidade')
        status_regularidade = self.request.query_params.get('status_regularidade')

        result = get_lista_associacoes_e_status_regularidade_no_ano(dre=dre,
                                                                    ano_analise_regularidade=ano_analise_regularidade,
                                                                    filtro_nome=nome,
                                                                    filtro_tipo_unidade=tipo_unidade,
                                                                    filtro_status=status_regularidade
                                                                    )
        return Response(result)

    @action(detail=True, url_path='verificacao-regularidade', methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def verificacao_regularidade(self, request, uuid=None):
        ano = request.query_params.get('ano')
        verificacao = get_verificacao_regularidade_associacao(associacao_uuid=uuid, ano=ano)
        return Response(verificacao)

    @action(detail=True, url_path='atualiza-itens-verificacao', methods=['post'],
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def atualiza_itens_verificacao(self, request, uuid=None):
        itens = request.data.get('itens')
        motivo = request.data.get('motivo_nao_regularidade')
        ano = request.data.get('ano')

        try:
            result = atualiza_itens_verificacao(
                associacao_uuid=uuid,
                ano=ano,
                itens_verificacao=itens,
                motivo_nao_regularidade=motivo
            )
            status_code = status.HTTP_200_OK

        except ValidationError as e:
            result = {
                'erro': 'Erro ao tentar atualizar regularidade da associação.',
                'mensagem': f'{e}'
            }
            status_code = status.HTTP_400_BAD_REQUEST

        return Response(result, status=status_code)

    @action(detail=True, url_path='previa-ata', methods=['get'],
            permission_classes=[IsAuthenticated, PermissaoAPITodosComLeituraOuGravacao])
    def previa_ata(self, request, uuid=None):
        associacao = self.get_object()

        periodo_uuid = request.query_params.get('periodo_uuid')
        if not periodo_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário informar o uuid do período.'
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

        ata_previa = Ata.objects.filter(associacao=associacao, periodo=periodo, previa=True).first()

        if not ata_previa:
            erro = {
                'mensagem': 'Ainda não existe uma prévia de ata para essa associação e período.'
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        return Response(AtaLookUpSerializer(ata_previa, many=False).data, status=status.HTTP_200_OK)

    @action(detail=True, url_path='validar-data-de-encerramento', methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def valida_data_de_encerramento(self, request, uuid=None):
        from ...services.associacoes_service import ValidaDataDeEncerramento

        associacao = self.get_object()

        data_de_encerramento = request.query_params.get('data_de_encerramento')
        if not data_de_encerramento:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário informar a data de encerramento'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        periodo_inicial_uuid = request.query_params.get('periodo_inicial')
        periodo_inicial = None
        if periodo_inicial_uuid:
            try:
                periodo_inicial = Periodo.objects.get(uuid=periodo_inicial_uuid)
            except Periodo.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto período inicial para o uuid {periodo_inicial_uuid} não foi encontrado na base."
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        data_de_encerramento = datetime.datetime.strptime(data_de_encerramento, '%Y-%m-%d')
        data_de_encerramento = data_de_encerramento.date()

        response = ValidaDataDeEncerramento(associacao=associacao, data_de_encerramento=data_de_encerramento,
                                            periodo_inicial=periodo_inicial).response

        status_response = response.pop("status")

        return Response(response, status=status_response)

    @action(detail=False, url_path='tags-informacoes',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def tags_informacoes_list(self, request):

        result = Associacao.get_tags_informacoes_list()

        return Response(result)

    @action(detail=True, url_path='status-cadastro',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def status_cadastro(self, request, uuid=None):
        associacao = self.get_object()
        response = associacao.pendencias_dados_da_associacao()
        return Response(response)

    @action(detail=True, url_path='contas-do-periodo', methods=['get'],
            permission_classes=[IsAuthenticated, PermissaoAPITodosComLeituraOuGravacao])
    def contas_do_periodo(self, request, uuid=None):
        associacao = self.get_object()
        periodo_uuid = request.query_params.get('periodo_uuid')

        if not periodo_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário informar o uuid do periodo'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            Periodo.objects.filter(uuid=periodo_uuid).get()
            periodo = Periodo.objects.filter(uuid=periodo_uuid).first()
        except (ValidationError, Exception):
            erro = {
                'erro': 'parametro_invalido',
                'mensagem': f"Não foi encontrado o objeto periodo para o uuid {periodo_uuid}"
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        lista_contas = associacao.contas_ativas_do_periodo_selecionado(periodo)
        return Response(lista_contas)

    @action(detail=True, methods=['get'], url_path='paa-vigente',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def paa_vigente(self, request, uuid):
        associacao = self.get_object()

        periodo_paa_vigente = PeriodoPaa.periodo_vigente()
        try:
            paa = associacao.paa_set.get(periodo_paa=periodo_paa_vigente)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serialized = PaaSerializer(paa, many=False)
        return Response(serialized.data, status=status.HTTP_200_OK)
