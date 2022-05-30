import datetime

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from sme_ptrf_apps.users.permissoes import (
    PermissaoApiDre,
    PermissaoAPIApenasDreComLeituraOuGravacao, PermissaoAPITodosComGravacao
)

from sme_ptrf_apps.dre.models import AtaParecerTecnico
from sme_ptrf_apps.dre.models import ParametrosDre
from sme_ptrf_apps.core.models import Unidade, Periodo
import logging
from sme_ptrf_apps.dre.api.serializers.ata_parecer_tecnico_serializer import (
    AtaParecerTecnicoSerializer,
    AtaParecerTecnicoCreateSerializer,
    AtaParecerTecnicoLookUpSerializer
)
from ...services import (
    informacoes_execucao_financeira_unidades_ata_parecer_tecnico
)
from django.core.exceptions import ValidationError

from ...tasks import gerar_ata_parecer_tecnico_async

from django.http import HttpResponse

# ****************
from decimal import Decimal
from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import get_template
from weasyprint import HTML, CSS

logger = logging.getLogger(__name__)


class AtaParecerTecnicoViewset(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = AtaParecerTecnico.objects.all()
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    serializer_class = AtaParecerTecnicoSerializer

    def get_serializer_class(self):
        if self.action == 'partial_update' or self.action == 'create':
            return AtaParecerTecnicoCreateSerializer
        else:
            return AtaParecerTecnicoSerializer

    dados_da_ata = {
        'cabecalho':
            {
                'titulo': 'Programa de Transferência de Recursos Financeiros -  PTRF',
                'sub_titulo': 'Diretoria Regional de Educação - GUAIANASES',
                'nome_ata': 'Ata de Parecer Técnico Conclusivo',
                'nome_dre': 'GUAIANASES',
                'data_geracao_documento': 'Ata PDF gerada pelo Sig_Escola em 27/05/2022 pelo usuário 6347959 para a DIRETORIA REGIONAL DE EDUCAÇÃO GUAIANASES',
                'numero_portaria': 33333,
                'data_portaria': datetime.date(2022, 5, 13)
            },
        'dados_texto_da_ata':
            {
                'data_reuniao_por_extenso': 'Aos treze dias do mês de maio de dois mil e vinte e dois',
                'hora_reuniao': 'zero hora',
                'numero_ata': 1212,
                'data_reuniao': datetime.date(2022, 5, 13),
                'periodo_data_inicio': '01/01/2022',
                'periodo_data_fim': '31/12/2022'
            }, 'presentes_na_ata': {
            'presentes': [
                {'nome': 'HELOISA INES DE OLIVEIRA', 'rf': '6347959', 'cargo': ''},
                {'nome': 'MARCIA TAMIKO MORIYA', 'rf': '6454836', 'cargo': 'COORDENADOR IV'}
            ]
        },
        'aprovadas': {
            'contas': []
        },
        'aprovadas_ressalva': {
            'contas': [
                {
                    'nome': 'Cheque',
                    'info': [{'unidade': {
                        'uuid': '21869eac-700b-4e2d-8ecb-6c9b64cc5837', 'codigo_eol': '090999', 'tipo_unidade': 'EMEI',
                        'nome': 'ADONIRAN BARBOSA', 'sigla': ''}, 'status_prestacao_contas': 'APROVADA_RESSALVA',
                        'valores': {
                            'saldo_reprogramado_periodo_anterior_custeio': Decimal('200.00'),
                            'saldo_reprogramado_periodo_anterior_capital': Decimal('100.00'),
                            'saldo_reprogramado_periodo_anterior_livre': Decimal('-150.00'),
                            'saldo_reprogramado_periodo_anterior_total': Decimal('150.00'),
                            'repasses_previstos_sme_custeio': 0,
                            'repasses_previstos_sme_capital': 0, 'repasses_previstos_sme_livre': 0,
                            'repasses_previstos_sme_total': 0,
                            'repasses_no_periodo_custeio': Decimal('0.00'),
                            'repasses_no_periodo_capital': Decimal('0.00'),
                            'repasses_no_periodo_livre': Decimal('0.00'), 'repasses_no_periodo_total': Decimal('0.00'),
                            'receitas_rendimento_no_periodo_custeio': 0, 'receitas_rendimento_no_periodo_capital': 0,
                            'receitas_rendimento_no_periodo_livre': 0, 'receitas_rendimento_no_periodo_total': 0,
                            'receitas_devolucao_no_periodo_custeio': Decimal('0.00'),
                            'receitas_devolucao_no_periodo_capital': Decimal('0.00'),
                            'receitas_devolucao_no_periodo_livre': Decimal('222.22'),
                            'receitas_devolucao_no_periodo_total': Decimal('222.22'),
                            'demais_creditos_no_periodo_custeio': Decimal('0.00'),
                            'demais_creditos_no_periodo_capital': Decimal('93.59'),
                            'demais_creditos_no_periodo_livre': Decimal('0.00'),
                            'demais_creditos_no_periodo_total': Decimal('93.59'),
                            'receitas_totais_no_periodo_custeio': Decimal('0.00'),
                            'receitas_totais_no_periodo_capital': Decimal('93.59'),
                            'receitas_totais_no_periodo_livre': Decimal('222.22'),
                            'receitas_totais_no_periodo_total': Decimal('315.81'),
                            'despesas_no_periodo_custeio': Decimal('0.00'),
                            'despesas_no_periodo_capital': Decimal('93.59'),
                            'despesas_no_periodo_total': Decimal('93.59'),
                            'saldo_reprogramado_proximo_periodo_custeio': Decimal('200.00'),
                            'saldo_reprogramado_proximo_periodo_capital': Decimal('100.00'),
                            'saldo_reprogramado_proximo_periodo_livre': Decimal('72.22'),
                            'saldo_reprogramado_proximo_periodo_total': Decimal('372.22'),
                            'devolucoes_ao_tesouro_no_periodo_total': 0
                        },
                        'uuid_pc': 'b5721114-77b8-40c7-bcb8-d7fa39c74582',
                        'motivos_aprovada_ressalva': [
                            'Motivo Aprovação com Ressalva 01',
                            'Motivo Aprovação com Ressalva 02'
                        ],
                        'recomendacoes': 'awedfawfd'}]},
                {
                    'nome': 'Cartão', 'info': [{'unidade': {
                    'uuid': '21869eac-700b-4e2d-8ecb-6c9b64cc5837',
                    'codigo_eol': '090999',
                    'tipo_unidade': 'EMEI',
                    'nome': 'ADONIRAN BARBOSA', 'sigla': ''},
                    'status_prestacao_contas': 'APROVADA_RESSALVA',
                    'valores': {
                        'saldo_reprogramado_periodo_anterior_custeio': Decimal(
                            '300.00'),
                        'saldo_reprogramado_periodo_anterior_capital': Decimal(
                            '0.00'),
                        'saldo_reprogramado_periodo_anterior_livre': Decimal(
                            '170.00'),
                        'saldo_reprogramado_periodo_anterior_total': Decimal(
                            '470.00'),
                        'repasses_previstos_sme_custeio': 0,
                        'repasses_previstos_sme_capital': 0,
                        'repasses_previstos_sme_livre': 0,
                        'repasses_previstos_sme_total': 0,
                        'repasses_no_periodo_custeio': Decimal(
                            '0.00'),
                        'repasses_no_periodo_capital': Decimal(
                            '0.00'),
                        'repasses_no_periodo_livre': Decimal(
                            '0.00'),
                        'repasses_no_periodo_total': Decimal(
                            '0.00'),
                        'receitas_rendimento_no_periodo_custeio': 0,
                        'receitas_rendimento_no_periodo_capital': 0,
                        'receitas_rendimento_no_periodo_livre': 0,
                        'receitas_rendimento_no_periodo_total': 0,
                        'receitas_devolucao_no_periodo_custeio': Decimal(
                            '0.00'),
                        'receitas_devolucao_no_periodo_capital': Decimal(
                            '0.00'),
                        'receitas_devolucao_no_periodo_livre': Decimal(
                            '0.00'),
                        'receitas_devolucao_no_periodo_total': Decimal(
                            '0.00'),
                        'demais_creditos_no_periodo_custeio': Decimal(
                            '156.41'),
                        'demais_creditos_no_periodo_capital': Decimal(
                            '0.00'),
                        'demais_creditos_no_periodo_livre': Decimal(
                            '0.00'),
                        'demais_creditos_no_periodo_total': Decimal(
                            '156.41'),
                        'receitas_totais_no_periodo_custeio': Decimal(
                            '156.41'),
                        'receitas_totais_no_periodo_capital': Decimal(
                            '0.00'),
                        'receitas_totais_no_periodo_livre': Decimal(
                            '0.00'),
                        'receitas_totais_no_periodo_total': Decimal(
                            '156.41'),
                        'despesas_no_periodo_custeio': Decimal(
                            '156.41'),
                        'despesas_no_periodo_capital': Decimal(
                            '0.00'),
                        'despesas_no_periodo_total': Decimal(
                            '156.41'),
                        'saldo_reprogramado_proximo_periodo_custeio': Decimal(
                            '300.00'),
                        'saldo_reprogramado_proximo_periodo_capital': Decimal(
                            '0.00'),
                        'saldo_reprogramado_proximo_periodo_livre': Decimal(
                            '170.00'),
                        'saldo_reprogramado_proximo_periodo_total': Decimal(
                            '470.00'),
                        'devolucoes_ao_tesouro_no_periodo_total': 0},
                    'uuid_pc': 'b5721114-77b8-40c7-bcb8-d7fa39c74582',
                    'motivos_aprovada_ressalva': [
                        'Motivo Aprovação com Ressalva 01',
                        'Motivo Aprovação com Ressalva 02'
                    ],
                    'recomendacoes': 'awedfawfd'
                }
                ]
                }
            ],
            'motivos': [
                {
                    'unidade':
                        {
                            'codigo_eol': '090999',
                            'tipo_unidade': 'EMEI',
                            'nome': 'ADONIRAN BARBOSA'
                        },
                    'motivos': [
                        'Motivo Aprovação com Ressalva 01',
                        'Motivo Aprovação com Ressalva 02'
                    ],
                    'recomendacoes': 'awedfawfd'
                }
            ]
        },
        'reprovadas': {'contas': [], 'motivos': []}}

    @action(detail=False, methods=['get'], url_path='ver-pdf', permission_classes=[AllowAny])
    def ver_pdf(self, request):
        html_template = get_template('pdf/ata_parecer_tecnico/pdf.html')

        rendered_html = html_template.render(
            {'dados': self.dados_da_ata, 'base_static_url': staticfiles_storage.location})

        pdf_file = HTML(
            string=rendered_html,
            base_url=staticfiles_storage.location
        ).write_pdf(
            stylesheets=[CSS(staticfiles_storage.location + '/css/ata-parecer-tecnico-pdf.css')])

        # return HttpResponse(rendered_html)
        return HttpResponse(pdf_file, content_type='application/pdf')

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated, PermissaoAPIApenasDreComLeituraOuGravacao],
            url_path='gerar-ata-parecer-tecnico')
    def gerar_ata_parecer_tecnico(self, request):
        logger.info("Iniciando geração da Ata de Parecer Técnico")

        ata_uuid = request.query_params.get('ata')
        dre_uuid = request.query_params.get('dre')
        periodo_uuid = request.query_params.get('periodo')

        if not ata_uuid or not dre_uuid or not periodo_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da Ata, o uuid da Dre e o uuid do Período'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            ata = AtaParecerTecnico.objects.get(uuid=ata_uuid)
        except (ValidationError, Exception):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ata para o uuid {ata_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
        except (ValidationError, Exception):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.filter(uuid=periodo_uuid).get()
        except (ValidationError, Exception):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto periodo para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        gerar_ata_parecer_tecnico_async.delay(
            ata_uuid=ata_uuid,
            dre_uuid=dre_uuid,
            periodo_uuid=periodo_uuid,
            usuario=request.user.username,
        )
        return Response({'mensagem': 'Arquivo na fila para processamento.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='download-ata-parecer-tecnico',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def download_ata_parecer_tecnico(self, request):
        logger.info("Download da Ata de Parecer Técnico.")

        ata_uuid = request.query_params.get('ata')

        if not ata_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da Ata.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            ata = AtaParecerTecnico.objects.get(uuid=ata_uuid)
        except (ValidationError, Exception):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ata para o uuid {ata_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            filename = 'ata_parecer_tecnico.pdf'
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

    @action(detail=False, url_path='membros-comissao-exame-contas',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def membros_comissao_exame_contas(self, request):
        dre_uuid = self.request.query_params.get('dre')
        ata_uuid = request.query_params.get('ata')

        if not dre_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'mensagem': 'Faltou informar o uuid da dre. ?dre=uuid_da_dre'
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

        if not ata_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da ata e o identificador.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            valida_ata = AtaParecerTecnico.by_uuid(ata_uuid)
        except ValidationError:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ata para o uuid {ata_uuid} não foi encontrado na base."
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        ata = AtaParecerTecnico.objects.filter(uuid=ata_uuid).first()
        comissoes = ParametrosDre.get().comissao_exame_contas
        membros = comissoes.membros.filter(dre=dre).values("uuid", "rf", "nome", "cargo")

        lista = []
        for membro in membros:
            dado = {
                "ata": f"{ata.uuid}",
                "uuid": membro["uuid"],
                "rf": membro["rf"],
                "nome": membro["nome"],
                "cargo": membro["cargo"],
                "editavel": False
            }

            lista.append(dado)

        return Response(lista)

    @action(detail=False, url_path='info-ata',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def info_ata(self, request):
        # Determina a DRE
        dre_uuid = self.request.query_params.get('dre')

        if not dre_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'info-execucao-financeira-unidades',
                'mensagem': 'Faltou informar o uuid da dre. ?dre=uuid_da_dre'
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
        periodo_uuid = self.request.query_params.get('periodo')

        if not periodo_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'info-execucao-financeira-unidades',
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

        info = informacoes_execucao_financeira_unidades_ata_parecer_tecnico(dre=dre, periodo=periodo)

        return Response(info)

    @action(detail=False, methods=['get'], url_path='status-ata',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def status_ata(self, request):
        # Determina a DRE
        dre_uuid = self.request.query_params.get('dre')

        if not dre_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'info-execucao-financeira-unidades',
                'mensagem': 'Faltou informar o uuid da dre. ?dre=uuid_da_dre'
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
        periodo_uuid = self.request.query_params.get('periodo')

        if not periodo_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'info-execucao-financeira-unidades',
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

        ata = AtaParecerTecnico.objects.filter(dre=dre).filter(periodo=periodo).last()

        if not ata:
            erro = {
                'mensagem': 'Ainda não existe uma ata de parecer tecnico para essa DRE.'
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        return Response(AtaParecerTecnicoLookUpSerializer(ata, many=False).data,
                        status=status.HTTP_200_OK)
