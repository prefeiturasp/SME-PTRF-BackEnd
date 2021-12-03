import logging
from decimal import Decimal

from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import status
from sme_ptrf_apps.core.models.prestacao_conta import PrestacaoConta
from sme_ptrf_apps.core.models.periodo import Periodo
from django.core.exceptions import ValidationError
from sme_ptrf_apps.core.tasks import gerar_arquivo_ata_async

from sme_ptrf_apps.users.permissoes import PermissaoApiUe, PermissaoAPITodosComLeituraOuGravacao

from ....utils.choices_to_json import choices_to_json
from ...models import Ata
from ..serializers import AtaSerializer, AtaCreateSerializer

from django.http import HttpResponse

# *********************
from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import get_template
from weasyprint import HTML, CSS

logger = logging.getLogger(__name__)


class AtasViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = Ata.objects.all()
    serializer_class = AtaSerializer

    dados_da_ata = {
        'cabecalho': {
            'titulo': 'Programa de Transferência de Recursos Financeiros - PTRF',
            'subtitulo': 'Prestação de Contas',
            'tipo_ata': 'Retificação',
            'periodo_referencia': '2020.1',
            'periodo_data_inicio': '01/01/2020',
            'periodo_data_fim': '30/06/2020'
        },
        'retificacoes': 'lsdflmnsçldfnkgsçldfgknçslnkgfçsnkfgçsldkngfsdgndf\r\n\r\n2- gskdfgjsçljkgf',
        'devolucoes_ao_tesouro': [
            {
                'tipo': 'Invasão de dotação',
                'data': '29/11/2021',
                'numero_documento': None,
                'cpf_cnpj_fornecedor': '51.510.540/0001-56',
                'valor': Decimal('7777.77'),
                'motivo': ''
            },
            {
                'tipo': 'Desacordo com o art. 3o da lei 13.991/2005 (gasto indevido)',
                'data': '02/12/2021',
                'numero_documento': '999',
                'cpf_cnpj_fornecedor': '007.461.987-01',
                'valor': Decimal('250.00'),
                'motivo': ''
            },

        ],
        'info_financeira_ata': {'uuid': '8f4ba6c9-1fc8-476c-877c-cef64119bc1c',
                                'contas': [
                                    {
                                        'conta_associacao': {
                                            'uuid': 'de7b74e8-22e0-4fff-a22a-6e3759495dd6',
                                            'nome': 'Cheque',
                                            'banco_nome': 'Banco do Brasil',
                                            'agencia': '7370',
                                            'numero_conta': '12345-6'},
                                        'acoes': [
                                            {
                                                'acao_associacao_uuid': '8414ff14-d2d5-4540-b9c6-f4726843cefd',
                                                'acao_associacao_nome': 'Rolê Cultural',
                                                'saldo_reprogramado': 0,
                                                'saldo_reprogramado_capital': 0,
                                                'saldo_reprogramado_custeio': 0,
                                                'saldo_reprogramado_livre': 0,
                                                'receitas_no_periodo': Decimal(
                                                    '555.55'),
                                                'receitas_devolucao_no_periodo': Decimal(
                                                    '0.00'),
                                                'receitas_devolucao_no_periodo_custeio': Decimal(
                                                    '0.00'),
                                                'receitas_devolucao_no_periodo_capital': Decimal(
                                                    '0.00'),
                                                'receitas_devolucao_no_periodo_livre': Decimal(
                                                    '0.00'),
                                                'repasses_no_periodo': Decimal(
                                                    '0.00'),
                                                'repasses_no_periodo_capital': Decimal(
                                                    '0.00'),
                                                'repasses_no_periodo_custeio': Decimal(
                                                    '0.00'),
                                                'repasses_no_periodo_livre': Decimal(
                                                    '0.00'),
                                                'outras_receitas_no_periodo': Decimal(
                                                    '555.55'),
                                                'outras_receitas_no_periodo_capital': Decimal(
                                                    '555.55'),
                                                'outras_receitas_no_periodo_custeio': Decimal(
                                                    '0.00'),
                                                'outras_receitas_no_periodo_livre': Decimal(
                                                    '0.00'),
                                                'despesas_no_periodo': Decimal(
                                                    '0.00'),
                                                'despesas_no_periodo_capital': Decimal(
                                                    '0.00'),
                                                'despesas_no_periodo_custeio': Decimal(
                                                    '0.00'),
                                                'despesas_nao_conciliadas': Decimal(
                                                    '0.00'),
                                                'despesas_nao_conciliadas_capital': Decimal(
                                                    '0.00'),
                                                'despesas_nao_conciliadas_custeio': Decimal(
                                                    '0.00'),
                                                'despesas_nao_conciliadas_anteriores_capital': 0,
                                                'despesas_nao_conciliadas_anteriores_custeio': 0,
                                                'despesas_nao_conciliadas_anteriores': 0,
                                                'despesas_conciliadas': Decimal(
                                                    '0.00'),
                                                'despesas_conciliadas_capital': Decimal(
                                                    '0.00'),
                                                'despesas_conciliadas_custeio': Decimal(
                                                    '0.00'),
                                                'receitas_nao_conciliadas': Decimal(
                                                    '0.00'),
                                                'receitas_nao_conciliadas_capital': Decimal(
                                                    '0.00'),
                                                'receitas_nao_conciliadas_custeio': Decimal(
                                                    '0.00'),
                                                'receitas_nao_conciliadas_livre': Decimal(
                                                    '0.00'),
                                                'saldo_atual_custeio': Decimal(
                                                    '0.00'),
                                                'saldo_atual_capital': Decimal(
                                                    '555.55'),
                                                'saldo_atual_livre': Decimal(
                                                    '0.00'),
                                                'saldo_atual_total': Decimal(
                                                    '555.55'),
                                                'especificacoes_despesas_capital': [],
                                                'especificacoes_despesas_custeio': [],
                                                'repasses_nao_realizados_capital': 0,
                                                'repasses_nao_realizados_custeio': 0,
                                                'repasses_nao_realizados_livre': 0,
                                                'saldo_bancario_custeio': Decimal(
                                                    '0.00'),
                                                'saldo_bancario_capital': Decimal(
                                                    '555.55'),
                                                'saldo_bancario_livre': Decimal(
                                                    '0.00'),
                                                'saldo_bancario_total': Decimal(
                                                    '555.55')}],
                                        'totais': {
                                            'saldo_reprogramado': 0,
                                            'saldo_reprogramado_capital': 0,
                                            'saldo_reprogramado_custeio': 0,
                                            'saldo_reprogramado_livre': 0,
                                            'receitas_no_periodo': Decimal(
                                                '555.55'),
                                            'receitas_devolucao_no_periodo': Decimal(
                                                '0.00'),
                                            'receitas_devolucao_no_periodo_custeio': Decimal(
                                                '0.00'),
                                            'receitas_devolucao_no_periodo_capital': Decimal(
                                                '0.00'),
                                            'receitas_devolucao_no_periodo_livre': Decimal(
                                                '0.00'),
                                            'repasses_no_periodo': Decimal(
                                                '0.00'),
                                            'repasses_no_periodo_capital': Decimal(
                                                '0.00'),
                                            'repasses_no_periodo_custeio': Decimal(
                                                '0.00'),
                                            'repasses_no_periodo_livre': Decimal(
                                                '0.00'),
                                            'outras_receitas_no_periodo': Decimal(
                                                '555.55'),
                                            'outras_receitas_no_periodo_capital': Decimal(
                                                '555.55'),
                                            'outras_receitas_no_periodo_custeio': Decimal(
                                                '0.00'),
                                            'outras_receitas_no_periodo_livre': Decimal(
                                                '0.00'),
                                            'despesas_no_periodo': Decimal(
                                                '0.00'),
                                            'despesas_no_periodo_capital': Decimal(
                                                '0.00'),
                                            'despesas_no_periodo_custeio': Decimal(
                                                '0.00'),
                                            'despesas_nao_conciliadas': Decimal(
                                                '0.00'),
                                            'despesas_nao_conciliadas_capital': Decimal(
                                                '0.00'),
                                            'despesas_nao_conciliadas_custeio': Decimal(
                                                '0.00'),
                                            'despesas_nao_conciliadas_anteriores': 0,
                                            'despesas_nao_conciliadas_anteriores_capital': 0,
                                            'despesas_nao_conciliadas_anteriores_custeio': 0,
                                            'despesas_conciliadas': Decimal(
                                                '0.00'),
                                            'despesas_conciliadas_capital': Decimal(
                                                '0.00'),
                                            'despesas_conciliadas_custeio': Decimal(
                                                '0.00'),
                                            'receitas_nao_conciliadas': Decimal(
                                                '0.00'),
                                            'receitas_nao_conciliadas_capital': Decimal(
                                                '0.00'),
                                            'receitas_nao_conciliadas_custeio': Decimal(
                                                '0.00'),
                                            'receitas_nao_conciliadas_livre': Decimal(
                                                '0.00'),
                                            'saldo_atual_custeio': Decimal(
                                                '0.00'),
                                            'saldo_atual_capital': Decimal(
                                                '555.55'),
                                            'saldo_atual_livre': Decimal(
                                                '0.00'),
                                            'saldo_atual_total': Decimal(
                                                '555.55'),
                                            'repasses_nao_realizados_capital': 0,
                                            'repasses_nao_realizados_custeio': 0,
                                            'repasses_nao_realizados_livre': 0,
                                            'saldo_bancario_custeio': Decimal(
                                                '0.00'),
                                            'saldo_bancario_capital': Decimal(
                                                '555.55'),
                                            'saldo_bancario_livre': Decimal(
                                                '0.00'),
                                            'saldo_bancario_total': Decimal(
                                                '555.55')
                                        }
                                    },
                                    {
                                        'conta_associacao': {
                                            'uuid': '785ae4ab-1d9d-49ea-9707-6cfe70f419ce',
                                            'nome': 'Cartão',
                                            'banco_nome': 'Banco do Brasil - Cartão',
                                            'agencia': '1330',
                                            'numero_conta': '65432-1'},
                                        'acoes': [],
                                        'totais': {
                                            'saldo_reprogramado': 0,
                                            'saldo_reprogramado_capital': 0,
                                            'saldo_reprogramado_custeio': 0,
                                            'saldo_reprogramado_livre': 0,
                                            'receitas_no_periodo': 0,
                                            'receitas_devolucao_no_periodo': 0,
                                            'receitas_devolucao_no_periodo_custeio': 0,
                                            'receitas_devolucao_no_periodo_capital': 0,
                                            'receitas_devolucao_no_periodo_livre': 0,
                                            'repasses_no_periodo': 0,
                                            'repasses_no_periodo_capital': 0,
                                            'repasses_no_periodo_custeio': 0,
                                            'repasses_no_periodo_livre': 0,
                                            'outras_receitas_no_periodo': 0,
                                            'outras_receitas_no_periodo_capital': 0,
                                            'outras_receitas_no_periodo_custeio': 0,
                                            'outras_receitas_no_periodo_livre': 0,
                                            'despesas_no_periodo': 0,
                                            'despesas_no_periodo_capital': 0,
                                            'despesas_no_periodo_custeio': 0,
                                            'despesas_nao_conciliadas': 0,
                                            'despesas_nao_conciliadas_capital': 0,
                                            'despesas_nao_conciliadas_custeio': 0,
                                            'despesas_nao_conciliadas_anteriores': 0,
                                            'despesas_nao_conciliadas_anteriores_capital': 0,
                                            'despesas_nao_conciliadas_anteriores_custeio': 0,
                                            'despesas_conciliadas': 0,
                                            'despesas_conciliadas_capital': 0,
                                            'despesas_conciliadas_custeio': 0,
                                            'receitas_nao_conciliadas': 0,
                                            'receitas_nao_conciliadas_capital': 0,
                                            'receitas_nao_conciliadas_custeio': 0,
                                            'receitas_nao_conciliadas_livre': 0,
                                            'saldo_atual_custeio': 0,
                                            'saldo_atual_capital': 0,
                                            'saldo_atual_livre': 0,
                                            'saldo_atual_total': 0,
                                            'repasses_nao_realizados_capital': 0,
                                            'repasses_nao_realizados_custeio': 0,
                                            'repasses_nao_realizados_livre': 0,
                                            'saldo_bancario_custeio': 0,
                                            'saldo_bancario_capital': 0,
                                            'saldo_bancario_livre': 0,
                                            'saldo_bancario_total': 0}}]},
        'dados_da_ata': 'Ata: Ata 2020.1 - Retificação - 2021 - 11 - 2900',
        'dados_texto_da_ata': {
            'prestacao_conta': 'PrestacaoConta: 2020.1 - 2020 - 01 - 01 a 2020 - 06 - 30 - DEVOLVIDA',
            'periodo': 'Periodo: 2020.1 - 2020 - 01 - 01 a 2020 - 06 - 30',
            'associacao_nome': 'AGUA AZUL',
            'unidade_cod_eol': '200237',
            'unidade_tipo': 'CEU',
            'unidade_nome': 'AGUA AZUL - PAULO RENATO COSTA SOUZA, PROF.',
            'local_reuniao': 'São Paulo',
            'periodo_referencia': '1° repasse de 2020',
            'presidente_reuniao': 'REBECA DOS SANTOS ARAUJO',
            'cargo_presidente_reuniao': '___',
            'secretario_reuniao': 'LUCIA HELENA LEAL SORIA DOS REIS',
            'cargo_secretaria_reuniao': '___',
            'data_reuniao_por_extenso': 'Aos vinte e nove dias do mês de novembro de dois mil e vinte e um',
            'comentarios': '',
            'parecer_conselho': 'APROVADA',
            'usuario': '6347959'
        },
        'presentes_na_ata': {
            'presentes_ata_membros': {
                'uuid': '3bdc5730-41f9-4c83-b531-81b2fd23bdad',
                'ata_id': 180,
                'identificacao': '238.973.520-79',
                'nome': 'Ollyver Ottoboni',
                'cargo': 'Presidente da diretoria executiva',
                'membro': True,
                'conselho_fiscal': False
            },
            'presentes_ata_nao_membros': [],
            'presentes_ata_conselho_fiscal': []
        }
    }

    @action(detail=False, methods=['get'], url_path='ver-pdf', permission_classes=[AllowAny])
    def ver_pdf(self, request):
        html_template = get_template('pdf/ata/pdf.html')

        rendered_html = html_template.render(
            {'dados': self.dados_da_ata, 'base_static_url': staticfiles_storage.location})

        pdf_file = HTML(
            string=rendered_html,
            base_url=staticfiles_storage.location
        ).write_pdf(
            stylesheets=[CSS(staticfiles_storage.location + '/css/ata-pdf.css')])

        # return HttpResponse(rendered_html)
        return HttpResponse(pdf_file, content_type='application/pdf')

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return AtaCreateSerializer
        else:
            return AtaSerializer

    @action(detail=False, methods=['get'], url_path='gerar-arquivo-ata',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def gerar_arquivo_ata(self, request):

        prestacao_de_contas_uuid = request.query_params.get('prestacao-de-conta-uuid')
        ata_uuid = request.query_params.get('ata-uuid')

        if not prestacao_de_contas_uuid or not ata_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da prestação de contas e o uuid da ata.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            prestacao_de_contas = PrestacaoConta.by_uuid(prestacao_de_contas_uuid)
        except ValidationError:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto prestação de contas para o uuid {prestacao_de_contas_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            ata = Ata.by_uuid(ata_uuid)
        except ValidationError:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ata para o uuid {ata_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        gerar_arquivo_ata_async.delay(
            prestacao_de_contas_uuid=prestacao_de_contas_uuid,
            ata_uuid=ata_uuid,
            usuario=request.user.username,
        )

        return Response({'mensagem': 'Arquivo na fila para processamento.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='download-arquivo-ata',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def download_arquivo_ata(self, request):
        ata_uuid = request.query_params.get('ata-uuid')

        if not ata_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da ata.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            ata = Ata.by_uuid(ata_uuid)
        except ValidationError:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ata para o uuid {ata_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            filename = 'ata.pdf'
            response = HttpResponse(
                open(ata.arquivo_pdf.path, 'rb'),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = 'attachment; filename=%s' % filename

        except Exception as err:
            erro = {
                'erro': 'arquivo_nao_gerado',
                'mensagem': str(err)
            }
            logger.info("Erro: %s", str(err))
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        return response

    @action(detail=False, url_path='tabelas',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def tabelas(self, request):

        result = {
            'tipos_ata': choices_to_json(Ata.ATA_CHOICES),
            'tipos_reuniao': choices_to_json(Ata.REUNIAO_CHOICES),
            'convocacoes': choices_to_json(Ata.CONVOCACAO_CHOICES),
            'pareceres': choices_to_json(Ata.PARECER_CHOICES),
        }

        return Response(result)
