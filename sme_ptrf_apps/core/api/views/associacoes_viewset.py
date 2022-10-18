import logging
from datetime import date
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

from sme_ptrf_apps.users.permissoes import (
    PermissaoApiUe,
    PermissaoAPITodosComLeituraOuGravacao,
    PermissaoAPITodosComGravacao,
    PermissaoAPIApenasDreComGravacao,
    PermissaoAPIApenasDreComLeituraOuGravacao
)

from ....dre.services import (
    get_verificacao_regularidade_associacao,
    get_lista_associacoes_e_status_regularidade_no_ano,
    atualiza_itens_verificacao,
)
from ...models import Associacao, ContaAssociacao, Periodo, PrestacaoConta, Unidade, Ata
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

from sme_ptrf_apps.core.services.prestacao_contas_services import pc_requer_geracao_documentos

logger = logging.getLogger(__name__)


class AssociacoesViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = Associacao.objects.all()
    serializer_class = AssociacaoSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    filter_fields = ('unidade__dre__uuid', 'unidade__tipo_unidade')

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

        nome = self.request.query_params.get('nome')
        if nome is not None:
            qs = qs.filter(Q(unidade__codigo_eol=nome) | Q(nome__unaccent__icontains=nome) | Q(
                unidade__nome__unaccent__icontains=nome))

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
            except(ValidationError, Exception):
                erro = {'erro': 'UUID do período inválido.'}
                return Response(erro, status=status.HTTP_404_NOT_FOUND)
        else:
            periodo = Periodo.periodo_atual()

        conta_associacao_uuid = request.query_params.get('conta')

        try:
            conta_associacao = ContaAssociacao.by_uuid(conta_associacao_uuid) if conta_associacao_uuid else None
        except(ValidationError, Exception):
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
            gerar_ou_editar_ata_apresentacao = prestacao_conta_status['status_prestacao'] == 'NAO_RECEBIDA'
            gerar_ou_editar_ata_retificacao = prestacao_conta_status['status_prestacao'] == 'DEVOLVIDA_RETORNADA'

        gerar_previas = True
        if prestacao_conta:
            gerar_previas = pc_requer_geracao_documentos(prestacao_conta)

        result = {
            'associacao': f'{uuid}',
            'periodo_referencia': periodo_referencia,
            'aceita_alteracoes': aceita_alteracoes,
            'prestacao_contas_status': prestacao_conta_status,
            'prestacao_conta': prestacao_conta.uuid if prestacao_conta else '',
            'gerar_ou_editar_ata_apresentacao': gerar_ou_editar_ata_apresentacao,
            'gerar_ou_editar_ata_retificacao': gerar_ou_editar_ata_retificacao,
            'gerar_previas': gerar_previas,
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
        contas = ContaAssociacao.objects.filter(associacao=associacao).all()
        contas_data = ContaAssociacaoDadosSerializer(contas, many=True).data
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
    def tabelas(self, _):
        result = {
            'tipos_unidade': Unidade.tipos_unidade_to_json(),
            'dres': Unidade.dres_to_json()
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

        data_atual = date.today().strftime("%d-%m-%Y")
        usuario_logado = self.request.user
        associacao = Associacao.by_uuid(uuid)
        contas = list(ContaAssociacao.objects.filter(associacao=associacao).all())
        atualiza_dados_unidade(associacao)

        html_string = render_to_string('pdf/associacoes/exportarpdf/pdf.html', {'associacao': associacao, 'contas': contas, 'dataAtual': data_atual, 'usuarioLogado': usuario_logado}).encode(encoding="UTF-8")

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
        periodos = associacao.periodos_para_prestacoes_de_conta()
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
                periodos=Periodo.objects.filter(uuid=periodo_uuid)
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
