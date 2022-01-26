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
from sme_ptrf_apps.core.models import Unidade, PrestacaoConta, TipoConta, Periodo
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

logger = logging.getLogger(__name__)

# ###########################
from decimal import Decimal
from django.http import HttpResponse

from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import get_template

from django.core.files.uploadedfile import SimpleUploadedFile

from weasyprint import HTML, CSS


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

    # dados_da_ata = {
    #     'cabecalho': {
    #         'titulo': 'Programa de Transferência de Recursos Financeiros -  PTRF',
    #         'sub_titulo': 'Diretoria Regional de Educação - GUAIANASES',
    #         'nome_ata': 'Ata de Parecer Técnico Conclusivo',
    #         'nome_dre': 'GUAIANASES'
    #     },
    #     'dados_texto_da_ata': {
    #         'data_reuniao_por_extenso': 'No primeiro dia do mês de fevereiro de dois mil e vinte e três',
    #         'hora_reuniao': 'uma hora e dois minutos',
    #         'numero_ata': 2,
    #         'data_reuniao': datetime.date(2023, 2, 1),
    #         'periodo_data_inicio': '16/06/2021',
    #         'periodo_data_fim': '31/12/2021'
    #     },
    #     'aprovadas': {
    #         'contas': [
    #             {
    #                 'nome': 'Cheque',
    #                 'info': [
    #                     {
    #                         'unidade':
    #                             {
    #                                 'uuid': '9b63b411-d8f9-4034-866e-4d54c667c41d',
    #                                 'codigo_eol': '200237',
    #                                 'tipo_unidade': 'CEU',
    #                                 'nome': 'AGUA AZUL - PAULO RENATO COSTA SOUZA, PROF.',
    #                                 'sigla': ''
    #                             },
    #                         'status_prestacao_contas': 'APROVADA',
    #                         'valores': {
    #                             'saldo_reprogramado_periodo_anterior_custeio': Decimal('777.77'),
    #                             'saldo_reprogramado_periodo_anterior_capital': Decimal('1000499.98'),
    #                             'saldo_reprogramado_periodo_anterior_livre': Decimal('-2972.18'),
    #                             'saldo_reprogramado_periodo_anterior_total': Decimal('998305.57'),
    #                             'repasses_previstos_sme_custeio': 0,
    #                             'repasses_previstos_sme_capital': 0,
    #                             'repasses_previstos_sme_livre': 0,
    #                             'repasses_previstos_sme_total': 0,
    #                             'repasses_no_periodo_custeio': Decimal('0.00'),
    #                             'repasses_no_periodo_capital': Decimal('0.00'),
    #                             'repasses_no_periodo_livre': Decimal('0.00'),
    #                             'repasses_no_periodo_total': Decimal('0.00'),
    #                             'receitas_rendimento_no_periodo_custeio': Decimal('5555.55'),
    #                             'receitas_rendimento_no_periodo_capital': 0,
    #                             'receitas_rendimento_no_periodo_livre': 0,
    #                             'receitas_rendimento_no_periodo_total': Decimal('5555.55'),
    #                             'receitas_devolucao_no_periodo_custeio': Decimal('0.00'),
    #                             'receitas_devolucao_no_periodo_capital': Decimal('99.00'),
    #                             'receitas_devolucao_no_periodo_livre': Decimal('0.00'),
    #                             'receitas_devolucao_no_periodo_total': Decimal('99.00'),
    #                             'demais_creditos_no_periodo_custeio': Decimal('0.00'),
    #                             'demais_creditos_no_periodo_capital': Decimal('9124.68'),
    #                             'demais_creditos_no_periodo_livre': Decimal('7777.77'),
    #                             'demais_creditos_no_periodo_total': Decimal('16902.45'),
    #                             'receitas_totais_no_periodo_custeio': Decimal('5555.55'),
    #                             'receitas_totais_no_periodo_capital': Decimal('9223.68'),
    #                             'receitas_totais_no_periodo_livre': Decimal('7777.77'),
    #                             'receitas_totais_no_periodo_total': Decimal('22557.00'),
    #                             'despesas_no_periodo_custeio': Decimal('9567.88'),
    #                             'despesas_no_periodo_capital': Decimal('444.44'),
    #                             'despesas_no_periodo_total': Decimal('10012.32'),
    #                             'saldo_reprogramado_proximo_periodo_custeio': Decimal('5777.77'),
    #                             'saldo_reprogramado_proximo_periodo_capital': Decimal('1009723.66'),
    #                             'saldo_reprogramado_proximo_periodo_livre': Decimal('-4651.18'),
    #                             'saldo_reprogramado_proximo_periodo_total': Decimal('1010850.25'),
    #                             'devolucoes_ao_tesouro_no_periodo_total': 0
    #                         },
    #                         'uuid_pc': '3e6b599e-3494-4477-8286-8e2e97d5e566'
    #                     },
    #                     {
    #                         'unidade':
    #                             {
    #                                 'uuid': '9b63b411-d8f9-4034-866e-4d54c667c41d',
    #                                 'codigo_eol': '200237-0',
    #                                 'tipo_unidade': 'CEU',
    #                                 'nome': 'AGUA AZUL - PAULO RENATO COSTA SOUZA, PROF.- 02',
    #                                 'sigla': ''
    #                             },
    #                         'status_prestacao_contas': 'APROVADA',
    #                         'valores': {
    #                             'saldo_reprogramado_periodo_anterior_custeio': Decimal('777.77'),
    #                             'saldo_reprogramado_periodo_anterior_capital': Decimal('1000499.98'),
    #                             'saldo_reprogramado_periodo_anterior_livre': Decimal('-2972.18'),
    #                             'saldo_reprogramado_periodo_anterior_total': Decimal('998305.57'),
    #                             'repasses_previstos_sme_custeio': 0,
    #                             'repasses_previstos_sme_capital': 0,
    #                             'repasses_previstos_sme_livre': 0,
    #                             'repasses_previstos_sme_total': 0,
    #                             'repasses_no_periodo_custeio': Decimal('0.00'),
    #                             'repasses_no_periodo_capital': Decimal('0.00'),
    #                             'repasses_no_periodo_livre': Decimal('0.00'),
    #                             'repasses_no_periodo_total': Decimal('0.00'),
    #                             'receitas_rendimento_no_periodo_custeio': Decimal('5555.55'),
    #                             'receitas_rendimento_no_periodo_capital': 0,
    #                             'receitas_rendimento_no_periodo_livre': 0,
    #                             'receitas_rendimento_no_periodo_total': Decimal('5555.55'),
    #                             'receitas_devolucao_no_periodo_custeio': Decimal('0.00'),
    #                             'receitas_devolucao_no_periodo_capital': Decimal('99.00'),
    #                             'receitas_devolucao_no_periodo_livre': Decimal('0.00'),
    #                             'receitas_devolucao_no_periodo_total': Decimal('99.00'),
    #                             'demais_creditos_no_periodo_custeio': Decimal('0.00'),
    #                             'demais_creditos_no_periodo_capital': Decimal('9124.68'),
    #                             'demais_creditos_no_periodo_livre': Decimal('7777.77'),
    #                             'demais_creditos_no_periodo_total': Decimal('16902.45'),
    #                             'receitas_totais_no_periodo_custeio': Decimal('5555.55'),
    #                             'receitas_totais_no_periodo_capital': Decimal('9223.68'),
    #                             'receitas_totais_no_periodo_livre': Decimal('7777.77'),
    #                             'receitas_totais_no_periodo_total': Decimal('22557.00'),
    #                             'despesas_no_periodo_custeio': Decimal('9567.88'),
    #                             'despesas_no_periodo_capital': Decimal('444.44'),
    #                             'despesas_no_periodo_total': Decimal('10012.32'),
    #                             'saldo_reprogramado_proximo_periodo_custeio': Decimal('5777.77'),
    #                             'saldo_reprogramado_proximo_periodo_capital': Decimal('1009723.66'),
    #                             'saldo_reprogramado_proximo_periodo_livre': Decimal('-4651.18'),
    #                             'saldo_reprogramado_proximo_periodo_total': Decimal('1010850.25'),
    #                             'devolucoes_ao_tesouro_no_periodo_total': 0
    #                         },
    #                         'uuid_pc': '3e6b599e-3494-4477-8286-8e2e97d5e566'
    #                     },
    #                     {
    #                         'unidade':
    #                             {
    #                                 'uuid': '9b63b411-d8f9-4034-866e-4d54c667c41d',
    #                                 'codigo_eol': '200237-1',
    #                                 'tipo_unidade': 'CEU',
    #                                 'nome': 'AGUA AZUL - PAULO RENATO COSTA SOUZA, PROF.- 03',
    #                                 'sigla': ''
    #                             },
    #                         'status_prestacao_contas': 'APROVADA',
    #                         'valores': {
    #                             'saldo_reprogramado_periodo_anterior_custeio': Decimal('777.77'),
    #                             'saldo_reprogramado_periodo_anterior_capital': Decimal('1000499.98'),
    #                             'saldo_reprogramado_periodo_anterior_livre': Decimal('-2972.18'),
    #                             'saldo_reprogramado_periodo_anterior_total': Decimal('998305.57'),
    #                             'repasses_previstos_sme_custeio': 0,
    #                             'repasses_previstos_sme_capital': 0,
    #                             'repasses_previstos_sme_livre': 0,
    #                             'repasses_previstos_sme_total': 0,
    #                             'repasses_no_periodo_custeio': Decimal('0.00'),
    #                             'repasses_no_periodo_capital': Decimal('0.00'),
    #                             'repasses_no_periodo_livre': Decimal('0.00'),
    #                             'repasses_no_periodo_total': Decimal('0.00'),
    #                             'receitas_rendimento_no_periodo_custeio': Decimal('5555.55'),
    #                             'receitas_rendimento_no_periodo_capital': 0,
    #                             'receitas_rendimento_no_periodo_livre': 0,
    #                             'receitas_rendimento_no_periodo_total': Decimal('5555.55'),
    #                             'receitas_devolucao_no_periodo_custeio': Decimal('0.00'),
    #                             'receitas_devolucao_no_periodo_capital': Decimal('99.00'),
    #                             'receitas_devolucao_no_periodo_livre': Decimal('0.00'),
    #                             'receitas_devolucao_no_periodo_total': Decimal('99.00'),
    #                             'demais_creditos_no_periodo_custeio': Decimal('0.00'),
    #                             'demais_creditos_no_periodo_capital': Decimal('9124.68'),
    #                             'demais_creditos_no_periodo_livre': Decimal('7777.77'),
    #                             'demais_creditos_no_periodo_total': Decimal('16902.45'),
    #                             'receitas_totais_no_periodo_custeio': Decimal('5555.55'),
    #                             'receitas_totais_no_periodo_capital': Decimal('9223.68'),
    #                             'receitas_totais_no_periodo_livre': Decimal('7777.77'),
    #                             'receitas_totais_no_periodo_total': Decimal('22557.00'),
    #                             'despesas_no_periodo_custeio': Decimal('9567.88'),
    #                             'despesas_no_periodo_capital': Decimal('444.44'),
    #                             'despesas_no_periodo_total': Decimal('10012.32'),
    #                             'saldo_reprogramado_proximo_periodo_custeio': Decimal('5777.77'),
    #                             'saldo_reprogramado_proximo_periodo_capital': Decimal('1009723.66'),
    #                             'saldo_reprogramado_proximo_periodo_livre': Decimal('-4651.18'),
    #                             'saldo_reprogramado_proximo_periodo_total': Decimal('1010850.25'),
    #                             'devolucoes_ao_tesouro_no_periodo_total': 0
    #                         },
    #                         'uuid_pc': '3e6b599e-3494-4477-8286-8e2e97d5e566'
    #                     },
    #                     {
    #                         'unidade':
    #                             {
    #                                 'uuid': '9b63b411-d8f9-4034-866e-4d54c667c41d',
    #                                 'codigo_eol': '200237-2',
    #                                 'tipo_unidade': 'CEU',
    #                                 'nome': 'AGUA AZUL - PAULO RENATO COSTA SOUZA, PROF.- 04',
    #                                 'sigla': ''
    #                             },
    #                         'status_prestacao_contas': 'APROVADA',
    #                         'valores': {
    #                             'saldo_reprogramado_periodo_anterior_custeio': Decimal('777.77'),
    #                             'saldo_reprogramado_periodo_anterior_capital': Decimal('1000499.98'),
    #                             'saldo_reprogramado_periodo_anterior_livre': Decimal('-2972.18'),
    #                             'saldo_reprogramado_periodo_anterior_total': Decimal('998305.57'),
    #                             'repasses_previstos_sme_custeio': 0,
    #                             'repasses_previstos_sme_capital': 0,
    #                             'repasses_previstos_sme_livre': 0,
    #                             'repasses_previstos_sme_total': 0,
    #                             'repasses_no_periodo_custeio': Decimal('0.00'),
    #                             'repasses_no_periodo_capital': Decimal('0.00'),
    #                             'repasses_no_periodo_livre': Decimal('0.00'),
    #                             'repasses_no_periodo_total': Decimal('0.00'),
    #                             'receitas_rendimento_no_periodo_custeio': Decimal('5555.55'),
    #                             'receitas_rendimento_no_periodo_capital': 0,
    #                             'receitas_rendimento_no_periodo_livre': 0,
    #                             'receitas_rendimento_no_periodo_total': Decimal('5555.55'),
    #                             'receitas_devolucao_no_periodo_custeio': Decimal('0.00'),
    #                             'receitas_devolucao_no_periodo_capital': Decimal('99.00'),
    #                             'receitas_devolucao_no_periodo_livre': Decimal('0.00'),
    #                             'receitas_devolucao_no_periodo_total': Decimal('99.00'),
    #                             'demais_creditos_no_periodo_custeio': Decimal('0.00'),
    #                             'demais_creditos_no_periodo_capital': Decimal('9124.68'),
    #                             'demais_creditos_no_periodo_livre': Decimal('7777.77'),
    #                             'demais_creditos_no_periodo_total': Decimal('16902.45'),
    #                             'receitas_totais_no_periodo_custeio': Decimal('5555.55'),
    #                             'receitas_totais_no_periodo_capital': Decimal('9223.68'),
    #                             'receitas_totais_no_periodo_livre': Decimal('7777.77'),
    #                             'receitas_totais_no_periodo_total': Decimal('22557.00'),
    #                             'despesas_no_periodo_custeio': Decimal('9567.88'),
    #                             'despesas_no_periodo_capital': Decimal('444.44'),
    #                             'despesas_no_periodo_total': Decimal('10012.32'),
    #                             'saldo_reprogramado_proximo_periodo_custeio': Decimal('5777.77'),
    #                             'saldo_reprogramado_proximo_periodo_capital': Decimal('1009723.66'),
    #                             'saldo_reprogramado_proximo_periodo_livre': Decimal('-4651.18'),
    #                             'saldo_reprogramado_proximo_periodo_total': Decimal('1010850.25'),
    #                             'devolucoes_ao_tesouro_no_periodo_total': 0
    #                         },
    #                         'uuid_pc': '3e6b599e-3494-4477-8286-8e2e97d5e566'
    #                     }
    #                 ]
    #             },
    #             {
    #                 'nome': 'Cartão',
    #                 'info': [
    #                     {
    #                         'unidade': {
    #                             'uuid': '9b63b411-d8f9-4034-866e-4d54c667c41d',
    #                             'codigo_eol': '200237',
    #                             'tipo_unidade': 'CEU',
    #                             'nome': 'AGUA AZUL - PAULO RENATO COSTA SOUZA, PROF.',
    #                             'sigla': ''
    #                         },
    #                         'status_prestacao_contas': 'APROVADA',
    #                         'valores': {
    #                             'saldo_reprogramado_periodo_anterior_custeio': Decimal('1000199.99'),
    #                             'saldo_reprogramado_periodo_anterior_capital': Decimal('0.00'),
    #                             'saldo_reprogramado_periodo_anterior_livre': Decimal('-455.25'),
    #                             'saldo_reprogramado_periodo_anterior_total': Decimal('999744.74'),
    #                             'repasses_previstos_sme_custeio': 0,
    #                             'repasses_previstos_sme_capital': 0,
    #                             'repasses_previstos_sme_livre': 0,
    #                             'repasses_previstos_sme_total': 0,
    #                             'repasses_no_periodo_custeio': Decimal('0.00'),
    #                             'repasses_no_periodo_capital': Decimal('0.00'),
    #                             'repasses_no_periodo_livre': Decimal('0.00'),
    #                             'repasses_no_periodo_total': Decimal('0.00'),
    #                             'receitas_rendimento_no_periodo_custeio': 0,
    #                             'receitas_rendimento_no_periodo_capital': 0,
    #                             'receitas_rendimento_no_periodo_livre': 0,
    #                             'receitas_rendimento_no_periodo_total': 0,
    #                             'receitas_devolucao_no_periodo_custeio': Decimal('0.00'),
    #                             'receitas_devolucao_no_periodo_capital': Decimal('0.00'),
    #                             'receitas_devolucao_no_periodo_livre': Decimal('0.00'),
    #                             'receitas_devolucao_no_periodo_total': Decimal('0.00'),
    #                             'demais_creditos_no_periodo_custeio': Decimal('0.00'),
    #                             'demais_creditos_no_periodo_capital': Decimal('0.00'),
    #                             'demais_creditos_no_periodo_livre': Decimal('0.00'),
    #                             'demais_creditos_no_periodo_total': Decimal('0.00'),
    #                             'receitas_totais_no_periodo_custeio': Decimal('0.00'),
    #                             'receitas_totais_no_periodo_capital': Decimal('0.00'),
    #                             'receitas_totais_no_periodo_livre': Decimal('0.00'),
    #                             'receitas_totais_no_periodo_total': Decimal('0.00'),
    #                             'despesas_no_periodo_custeio': Decimal('0.00'),
    #                             'despesas_no_periodo_capital': Decimal('222.22'),
    #                             'despesas_no_periodo_total': Decimal('222.22'),
    #                             'saldo_reprogramado_proximo_periodo_custeio': Decimal('1000199.99'),
    #                             'saldo_reprogramado_proximo_periodo_capital': Decimal('0.00'),
    #                             'saldo_reprogramado_proximo_periodo_livre': Decimal('-677.47'),
    #                             'saldo_reprogramado_proximo_periodo_total': Decimal('999522.52'),
    #                             'devolucoes_ao_tesouro_no_periodo_total': 0
    #                         },
    #                         'uuid_pc': '3e6b599e-3494-4477-8286-8e2e97d5e566'
    #                     }
    #                 ]
    #             }
    #         ]
    #     },
    #     'aprovadas_ressalva': {
    #         'contas': [
    #             {
    #                 'nome': 'Cheque',
    #                 'info': [
    #                     {
    #                         'unidade': {
    #                             'uuid': '9b63b411-d8f9-4034-866e-4d54c667c41d',
    #                             'codigo_eol': '200237',
    #                             'tipo_unidade': 'CEU',
    #                             'nome': 'AGUA AZUL - PAULO RENATO COSTA SOUZA, PROF.',
    #                             'sigla': ''
    #                         },
    #                         'status_prestacao_contas': 'APROVADA_RESSALVA',
    #                         'valores': {
    #                             'saldo_reprogramado_periodo_anterior_custeio': Decimal('777.77'),
    #                             'saldo_reprogramado_periodo_anterior_capital': Decimal('1000499.98'),
    #                             'saldo_reprogramado_periodo_anterior_livre': Decimal('-2972.18'),
    #                             'saldo_reprogramado_periodo_anterior_total': Decimal('998305.57'),
    #                             'repasses_previstos_sme_custeio': 0,
    #                             'repasses_previstos_sme_capital': 0,
    #                             'repasses_previstos_sme_livre': 0,
    #                             'repasses_previstos_sme_total': 0,
    #                             'repasses_no_periodo_custeio': Decimal('0.00'),
    #                             'repasses_no_periodo_capital': Decimal('0.00'),
    #                             'repasses_no_periodo_livre': Decimal('0.00'),
    #                             'repasses_no_periodo_total': Decimal('0.00'),
    #                             'receitas_rendimento_no_periodo_custeio': Decimal('5555.55'),
    #                             'receitas_rendimento_no_periodo_capital': 0,
    #                             'receitas_rendimento_no_periodo_livre': 0,
    #                             'receitas_rendimento_no_periodo_total': Decimal('5555.55'),
    #                             'receitas_devolucao_no_periodo_custeio': Decimal('0.00'),
    #                             'receitas_devolucao_no_periodo_capital': Decimal('99.00'),
    #                             'receitas_devolucao_no_periodo_livre': Decimal('0.00'),
    #                             'receitas_devolucao_no_periodo_total': Decimal('99.00'),
    #                             'demais_creditos_no_periodo_custeio': Decimal('0.00'),
    #                             'demais_creditos_no_periodo_capital': Decimal('9124.68'),
    #                             'demais_creditos_no_periodo_livre': Decimal('7777.77'),
    #                             'demais_creditos_no_periodo_total': Decimal('16902.45'),
    #                             'receitas_totais_no_periodo_custeio': Decimal('5555.55'),
    #                             'receitas_totais_no_periodo_capital': Decimal('9223.68'),
    #                             'receitas_totais_no_periodo_livre': Decimal('7777.77'),
    #                             'receitas_totais_no_periodo_total': Decimal('22557.00'),
    #                             'despesas_no_periodo_custeio': Decimal('9567.88'),
    #                             'despesas_no_periodo_capital': Decimal('444.44'),
    #                             'despesas_no_periodo_total': Decimal('10012.32'),
    #                             'saldo_reprogramado_proximo_periodo_custeio': Decimal('5777.77'),
    #                             'saldo_reprogramado_proximo_periodo_capital': Decimal('1009723.66'),
    #                             'saldo_reprogramado_proximo_periodo_livre': Decimal('-4651.18'),
    #                             'saldo_reprogramado_proximo_periodo_total': Decimal('1010850.25'),
    #                             'devolucoes_ao_tesouro_no_periodo_total': 0},
    #                         'uuid_pc': '3e6b599e-3494-4477-8286-8e2e97d5e566'
    #                     }
    #                 ]
    #             },
    #             {
    #                 'nome': 'Cartão',
    #                 'info': [
    #                     {
    #                         'unidade': {
    #                             'uuid': '9b63b411-d8f9-4034-866e-4d54c667c41d', 'codigo_eol': '200237',
    #                             'tipo_unidade': 'CEU',
    #                             'nome': 'AGUA AZUL - PAULO RENATO COSTA SOUZA, PROF.', 'sigla': ''
    #                         },
    #                         'status_prestacao_contas': 'APROVADA_RESSALVA',
    #                         'valores': {
    #                             'saldo_reprogramado_periodo_anterior_custeio': Decimal('1000199.99'),
    #                             'saldo_reprogramado_periodo_anterior_capital': Decimal('0.00'),
    #                             'saldo_reprogramado_periodo_anterior_livre': Decimal('-455.25'),
    #                             'saldo_reprogramado_periodo_anterior_total': Decimal('999744.74'),
    #                             'repasses_previstos_sme_custeio': 0,
    #                             'repasses_previstos_sme_capital': 0,
    #                             'repasses_previstos_sme_livre': 0,
    #                             'repasses_previstos_sme_total': 0,
    #                             'repasses_no_periodo_custeio': Decimal('0.00'),
    #                             'repasses_no_periodo_capital': Decimal('0.00'),
    #                             'repasses_no_periodo_livre': Decimal('0.00'),
    #                             'repasses_no_periodo_total': Decimal('0.00'),
    #                             'receitas_rendimento_no_periodo_custeio': 0,
    #                             'receitas_rendimento_no_periodo_capital': 0,
    #                             'receitas_rendimento_no_periodo_livre': 0,
    #                             'receitas_rendimento_no_periodo_total': 0,
    #                             'receitas_devolucao_no_periodo_custeio': Decimal('0.00'),
    #                             'receitas_devolucao_no_periodo_capital': Decimal('0.00'),
    #                             'receitas_devolucao_no_periodo_livre': Decimal('0.00'),
    #                             'receitas_devolucao_no_periodo_total': Decimal('0.00'),
    #                             'demais_creditos_no_periodo_custeio': Decimal('0.00'),
    #                             'demais_creditos_no_periodo_capital': Decimal('0.00'),
    #                             'demais_creditos_no_periodo_livre': Decimal('0.00'),
    #                             'demais_creditos_no_periodo_total': Decimal('0.00'),
    #                             'receitas_totais_no_periodo_custeio': Decimal('0.00'),
    #                             'receitas_totais_no_periodo_capital': Decimal('0.00'),
    #                             'receitas_totais_no_periodo_livre': Decimal('0.00'),
    #                             'receitas_totais_no_periodo_total': Decimal('0.00'),
    #                             'despesas_no_periodo_custeio': Decimal('0.00'),
    #                             'despesas_no_periodo_capital': Decimal('222.22'),
    #                             'despesas_no_periodo_total': Decimal('222.22'),
    #                             'saldo_reprogramado_proximo_periodo_custeio': Decimal('1000199.99'),
    #                             'saldo_reprogramado_proximo_periodo_capital': Decimal('0.00'),
    #                             'saldo_reprogramado_proximo_periodo_livre': Decimal('-677.47'),
    #                             'saldo_reprogramado_proximo_periodo_total': Decimal('999522.52'),
    #                             'devolucoes_ao_tesouro_no_periodo_total': 0},
    #                         'uuid_pc': '3e6b599e-3494-4477-8286-8e2e97d5e566'
    #                     }
    #                 ]
    #             }
    #         ],
    #         'motivos': [
    #             {
    #                 'unidade': {
    #                     'codigo_eol': '200237',
    #                     'tipo_unidade': 'CEU',
    #                     'nome': 'AGUA AZUL - PAULO RENATO COSTA SOUZA, PROF.'
    #                 },
    #                 'motivos': [
    #                     'Motivo Aprovação com Ressalva 01',
    #                     'Motivo Aprovação com Ressalva 02',
    #                     'Outro motivo 01\nOutro motivo 02'
    #                 ]
    #             }
    #         ]
    #     },
    #     'reprovadas': {
    #         'info': [],
    #         'motivos': []
    #     }
    # }

    dados_da_ata = {
        'cabecalho':
            {
                'titulo': 'Programa de Transferência de Recursos Financeiros -  PTRF',
                'sub_titulo': 'Diretoria Regional de Educação - BUTANTA - DRE',
                'nome_ata': 'Ata de Parecer Técnico Conclusivo', 'nome_dre': 'BUTANTA - DRE',
                'data_geracao_documento': 'Ata PDF gerada pelo Sig_Escola em 26/01/2022 pelo usuário 7483902 para a DIRETORIA REGIONAL DE EDUCAÇÃO BUTANTA - DRE'
            },
        'dados_texto_da_ata':
            {
                'data_reuniao_por_extenso': 'Aos vinte e quatro dias do mês de janeiro de dois mil e vinte e dois',
                'hora_reuniao': 'zero hora',
                'numero_ata': 1,
                'data_reuniao': datetime.date(2022, 1, 24),
                'periodo_data_inicio': '01/07/2020',
                'periodo_data_fim': '31/12/2020'
            },
        'aprovadas': {
            'contas': [
                {
                    'nome': 'Cheque',
                    'info': [
                        {
                            'unidade':
                                {
                                    'uuid': '9b63b411-d8f9-4034-866e-4d54c667c41d',
                                    'codigo_eol': '200237',
                                    'tipo_unidade': 'CEU',
                                    'nome': 'AGUA AZUL - PAULO RENATO COSTA SOUZA, PROF.',
                                    'sigla': ''
                                },
                            'status_prestacao_contas': 'APROVADA',
                            'valores': {
                                'saldo_reprogramado_periodo_anterior_custeio': Decimal('777.77'),
                                'saldo_reprogramado_periodo_anterior_capital': Decimal('1000499.98'),
                                'saldo_reprogramado_periodo_anterior_livre': Decimal('-2972.18'),
                                'saldo_reprogramado_periodo_anterior_total': Decimal('998305.57'),
                                'repasses_previstos_sme_custeio': 0,
                                'repasses_previstos_sme_capital': 0,
                                'repasses_previstos_sme_livre': 0,
                                'repasses_previstos_sme_total': 0,
                                'repasses_no_periodo_custeio': Decimal('0.00'),
                                'repasses_no_periodo_capital': Decimal('0.00'),
                                'repasses_no_periodo_livre': Decimal('0.00'),
                                'repasses_no_periodo_total': Decimal('0.00'),
                                'receitas_rendimento_no_periodo_custeio': Decimal('5555.55'),
                                'receitas_rendimento_no_periodo_capital': 0,
                                'receitas_rendimento_no_periodo_livre': 0,
                                'receitas_rendimento_no_periodo_total': Decimal('5555.55'),
                                'receitas_devolucao_no_periodo_custeio': Decimal('0.00'),
                                'receitas_devolucao_no_periodo_capital': Decimal('99.00'),
                                'receitas_devolucao_no_periodo_livre': Decimal('0.00'),
                                'receitas_devolucao_no_periodo_total': Decimal('99.00'),
                                'demais_creditos_no_periodo_custeio': Decimal('0.00'),
                                'demais_creditos_no_periodo_capital': Decimal('9124.68'),
                                'demais_creditos_no_periodo_livre': Decimal('7777.77'),
                                'demais_creditos_no_periodo_total': Decimal('16902.45'),
                                'receitas_totais_no_periodo_custeio': Decimal('5555.55'),
                                'receitas_totais_no_periodo_capital': Decimal('9223.68'),
                                'receitas_totais_no_periodo_livre': Decimal('7777.77'),
                                'receitas_totais_no_periodo_total': Decimal('22557.00'),
                                'despesas_no_periodo_custeio': Decimal('9567.88'),
                                'despesas_no_periodo_capital': Decimal('444.44'),
                                'despesas_no_periodo_total': Decimal('10012.32'),
                                'saldo_reprogramado_proximo_periodo_custeio': Decimal('5777.77'),
                                'saldo_reprogramado_proximo_periodo_capital': Decimal('1009723.66'),
                                'saldo_reprogramado_proximo_periodo_livre': Decimal('-4651.18'),
                                'saldo_reprogramado_proximo_periodo_total': Decimal('1010850.25'),
                                'devolucoes_ao_tesouro_no_periodo_total': 0
                            },
                            'uuid_pc': '3e6b599e-3494-4477-8286-8e2e97d5e566'
                        },
                        {
                            'unidade':
                                {
                                    'uuid': '9b63b411-d8f9-4034-866e-4d54c667c41d',
                                    'codigo_eol': '200237-0',
                                    'tipo_unidade': 'CEU',
                                    'nome': 'AGUA AZUL - PAULO RENATO COSTA SOUZA, PROF.- 02',
                                    'sigla': ''
                                },
                            'status_prestacao_contas': 'APROVADA',
                            'valores': {
                                'saldo_reprogramado_periodo_anterior_custeio': Decimal('777.77'),
                                'saldo_reprogramado_periodo_anterior_capital': Decimal('1000499.98'),
                                'saldo_reprogramado_periodo_anterior_livre': Decimal('-2972.18'),
                                'saldo_reprogramado_periodo_anterior_total': Decimal('998305.57'),
                                'repasses_previstos_sme_custeio': 0,
                                'repasses_previstos_sme_capital': 0,
                                'repasses_previstos_sme_livre': 0,
                                'repasses_previstos_sme_total': 0,
                                'repasses_no_periodo_custeio': Decimal('0.00'),
                                'repasses_no_periodo_capital': Decimal('0.00'),
                                'repasses_no_periodo_livre': Decimal('0.00'),
                                'repasses_no_periodo_total': Decimal('0.00'),
                                'receitas_rendimento_no_periodo_custeio': Decimal('5555.55'),
                                'receitas_rendimento_no_periodo_capital': 0,
                                'receitas_rendimento_no_periodo_livre': 0,
                                'receitas_rendimento_no_periodo_total': Decimal('5555.55'),
                                'receitas_devolucao_no_periodo_custeio': Decimal('0.00'),
                                'receitas_devolucao_no_periodo_capital': Decimal('99.00'),
                                'receitas_devolucao_no_periodo_livre': Decimal('0.00'),
                                'receitas_devolucao_no_periodo_total': Decimal('99.00'),
                                'demais_creditos_no_periodo_custeio': Decimal('0.00'),
                                'demais_creditos_no_periodo_capital': Decimal('9124.68'),
                                'demais_creditos_no_periodo_livre': Decimal('7777.77'),
                                'demais_creditos_no_periodo_total': Decimal('16902.45'),
                                'receitas_totais_no_periodo_custeio': Decimal('5555.55'),
                                'receitas_totais_no_periodo_capital': Decimal('9223.68'),
                                'receitas_totais_no_periodo_livre': Decimal('7777.77'),
                                'receitas_totais_no_periodo_total': Decimal('22557.00'),
                                'despesas_no_periodo_custeio': Decimal('9567.88'),
                                'despesas_no_periodo_capital': Decimal('444.44'),
                                'despesas_no_periodo_total': Decimal('10012.32'),
                                'saldo_reprogramado_proximo_periodo_custeio': Decimal('5777.77'),
                                'saldo_reprogramado_proximo_periodo_capital': Decimal('1009723.66'),
                                'saldo_reprogramado_proximo_periodo_livre': Decimal('-4651.18'),
                                'saldo_reprogramado_proximo_periodo_total': Decimal('1010850.25'),
                                'devolucoes_ao_tesouro_no_periodo_total': 0
                            },
                            'uuid_pc': '3e6b599e-3494-4477-8286-8e2e97d5e566'
                        },
                        {
                            'unidade':
                                {
                                    'uuid': '9b63b411-d8f9-4034-866e-4d54c667c41d',
                                    'codigo_eol': '200237-1',
                                    'tipo_unidade': 'CEU',
                                    'nome': 'AGUA AZUL - PAULO RENATO COSTA SOUZA, PROF.- 03',
                                    'sigla': ''
                                },
                            'status_prestacao_contas': 'APROVADA',
                            'valores': {
                                'saldo_reprogramado_periodo_anterior_custeio': Decimal('777.77'),
                                'saldo_reprogramado_periodo_anterior_capital': Decimal('1000499.98'),
                                'saldo_reprogramado_periodo_anterior_livre': Decimal('-2972.18'),
                                'saldo_reprogramado_periodo_anterior_total': Decimal('998305.57'),
                                'repasses_previstos_sme_custeio': 0,
                                'repasses_previstos_sme_capital': 0,
                                'repasses_previstos_sme_livre': 0,
                                'repasses_previstos_sme_total': 0,
                                'repasses_no_periodo_custeio': Decimal('0.00'),
                                'repasses_no_periodo_capital': Decimal('0.00'),
                                'repasses_no_periodo_livre': Decimal('0.00'),
                                'repasses_no_periodo_total': Decimal('0.00'),
                                'receitas_rendimento_no_periodo_custeio': Decimal('5555.55'),
                                'receitas_rendimento_no_periodo_capital': 0,
                                'receitas_rendimento_no_periodo_livre': 0,
                                'receitas_rendimento_no_periodo_total': Decimal('5555.55'),
                                'receitas_devolucao_no_periodo_custeio': Decimal('0.00'),
                                'receitas_devolucao_no_periodo_capital': Decimal('99.00'),
                                'receitas_devolucao_no_periodo_livre': Decimal('0.00'),
                                'receitas_devolucao_no_periodo_total': Decimal('99.00'),
                                'demais_creditos_no_periodo_custeio': Decimal('0.00'),
                                'demais_creditos_no_periodo_capital': Decimal('9124.68'),
                                'demais_creditos_no_periodo_livre': Decimal('7777.77'),
                                'demais_creditos_no_periodo_total': Decimal('16902.45'),
                                'receitas_totais_no_periodo_custeio': Decimal('5555.55'),
                                'receitas_totais_no_periodo_capital': Decimal('9223.68'),
                                'receitas_totais_no_periodo_livre': Decimal('7777.77'),
                                'receitas_totais_no_periodo_total': Decimal('22557.00'),
                                'despesas_no_periodo_custeio': Decimal('9567.88'),
                                'despesas_no_periodo_capital': Decimal('444.44'),
                                'despesas_no_periodo_total': Decimal('10012.32'),
                                'saldo_reprogramado_proximo_periodo_custeio': Decimal('5777.77'),
                                'saldo_reprogramado_proximo_periodo_capital': Decimal('1009723.66'),
                                'saldo_reprogramado_proximo_periodo_livre': Decimal('-4651.18'),
                                'saldo_reprogramado_proximo_periodo_total': Decimal('1010850.25'),
                                'devolucoes_ao_tesouro_no_periodo_total': 0
                            },
                            'uuid_pc': '3e6b599e-3494-4477-8286-8e2e97d5e566'
                        },
                        {
                            'unidade':
                                {
                                    'uuid': '9b63b411-d8f9-4034-866e-4d54c667c41d',
                                    'codigo_eol': '200237-2',
                                    'tipo_unidade': 'CEU',
                                    'nome': 'AGUA AZUL - PAULO RENATO COSTA SOUZA, PROF.- 04',
                                    'sigla': ''
                                },
                            'status_prestacao_contas': 'APROVADA',
                            'valores': {
                                'saldo_reprogramado_periodo_anterior_custeio': Decimal('777.77'),
                                'saldo_reprogramado_periodo_anterior_capital': Decimal('1000499.98'),
                                'saldo_reprogramado_periodo_anterior_livre': Decimal('-2972.18'),
                                'saldo_reprogramado_periodo_anterior_total': Decimal('998305.57'),
                                'repasses_previstos_sme_custeio': 0,
                                'repasses_previstos_sme_capital': 0,
                                'repasses_previstos_sme_livre': 0,
                                'repasses_previstos_sme_total': 0,
                                'repasses_no_periodo_custeio': Decimal('0.00'),
                                'repasses_no_periodo_capital': Decimal('0.00'),
                                'repasses_no_periodo_livre': Decimal('0.00'),
                                'repasses_no_periodo_total': Decimal('0.00'),
                                'receitas_rendimento_no_periodo_custeio': Decimal('5555.55'),
                                'receitas_rendimento_no_periodo_capital': 0,
                                'receitas_rendimento_no_periodo_livre': 0,
                                'receitas_rendimento_no_periodo_total': Decimal('5555.55'),
                                'receitas_devolucao_no_periodo_custeio': Decimal('0.00'),
                                'receitas_devolucao_no_periodo_capital': Decimal('99.00'),
                                'receitas_devolucao_no_periodo_livre': Decimal('0.00'),
                                'receitas_devolucao_no_periodo_total': Decimal('99.00'),
                                'demais_creditos_no_periodo_custeio': Decimal('0.00'),
                                'demais_creditos_no_periodo_capital': Decimal('9124.68'),
                                'demais_creditos_no_periodo_livre': Decimal('7777.77'),
                                'demais_creditos_no_periodo_total': Decimal('16902.45'),
                                'receitas_totais_no_periodo_custeio': Decimal('5555.55'),
                                'receitas_totais_no_periodo_capital': Decimal('9223.68'),
                                'receitas_totais_no_periodo_livre': Decimal('7777.77'),
                                'receitas_totais_no_periodo_total': Decimal('22557.00'),
                                'despesas_no_periodo_custeio': Decimal('9567.88'),
                                'despesas_no_periodo_capital': Decimal('444.44'),
                                'despesas_no_periodo_total': Decimal('10012.32'),
                                'saldo_reprogramado_proximo_periodo_custeio': Decimal('5777.77'),
                                'saldo_reprogramado_proximo_periodo_capital': Decimal('1009723.66'),
                                'saldo_reprogramado_proximo_periodo_livre': Decimal('-4651.18'),
                                'saldo_reprogramado_proximo_periodo_total': Decimal('1010850.25'),
                                'devolucoes_ao_tesouro_no_periodo_total': 0
                            },
                            'uuid_pc': '3e6b599e-3494-4477-8286-8e2e97d5e566'
                        }
                    ]
                },
                {
                    'nome': 'Cartão',
                    'info': [
                        {
                            'unidade': {
                                'uuid': '9b63b411-d8f9-4034-866e-4d54c667c41d',
                                'codigo_eol': '200237',
                                'tipo_unidade': 'CEU',
                                'nome': 'AGUA AZUL - PAULO RENATO COSTA SOUZA, PROF.',
                                'sigla': ''
                            },
                            'status_prestacao_contas': 'APROVADA',
                            'valores': {
                                'saldo_reprogramado_periodo_anterior_custeio': Decimal('1000199.99'),
                                'saldo_reprogramado_periodo_anterior_capital': Decimal('0.00'),
                                'saldo_reprogramado_periodo_anterior_livre': Decimal('-455.25'),
                                'saldo_reprogramado_periodo_anterior_total': Decimal('999744.74'),
                                'repasses_previstos_sme_custeio': 0,
                                'repasses_previstos_sme_capital': 0,
                                'repasses_previstos_sme_livre': 0,
                                'repasses_previstos_sme_total': 0,
                                'repasses_no_periodo_custeio': Decimal('0.00'),
                                'repasses_no_periodo_capital': Decimal('0.00'),
                                'repasses_no_periodo_livre': Decimal('0.00'),
                                'repasses_no_periodo_total': Decimal('0.00'),
                                'receitas_rendimento_no_periodo_custeio': 0,
                                'receitas_rendimento_no_periodo_capital': 0,
                                'receitas_rendimento_no_periodo_livre': 0,
                                'receitas_rendimento_no_periodo_total': 0,
                                'receitas_devolucao_no_periodo_custeio': Decimal('0.00'),
                                'receitas_devolucao_no_periodo_capital': Decimal('0.00'),
                                'receitas_devolucao_no_periodo_livre': Decimal('0.00'),
                                'receitas_devolucao_no_periodo_total': Decimal('0.00'),
                                'demais_creditos_no_periodo_custeio': Decimal('0.00'),
                                'demais_creditos_no_periodo_capital': Decimal('0.00'),
                                'demais_creditos_no_periodo_livre': Decimal('0.00'),
                                'demais_creditos_no_periodo_total': Decimal('0.00'),
                                'receitas_totais_no_periodo_custeio': Decimal('0.00'),
                                'receitas_totais_no_periodo_capital': Decimal('0.00'),
                                'receitas_totais_no_periodo_livre': Decimal('0.00'),
                                'receitas_totais_no_periodo_total': Decimal('0.00'),
                                'despesas_no_periodo_custeio': Decimal('0.00'),
                                'despesas_no_periodo_capital': Decimal('222.22'),
                                'despesas_no_periodo_total': Decimal('222.22'),
                                'saldo_reprogramado_proximo_periodo_custeio': Decimal('1000199.99'),
                                'saldo_reprogramado_proximo_periodo_capital': Decimal('0.00'),
                                'saldo_reprogramado_proximo_periodo_livre': Decimal('-677.47'),
                                'saldo_reprogramado_proximo_periodo_total': Decimal('999522.52'),
                                'devolucoes_ao_tesouro_no_periodo_total': 0
                            },
                            'uuid_pc': '3e6b599e-3494-4477-8286-8e2e97d5e566'
                        }
                    ]
                }
            ]
        },
        'aprovadas_ressalva':
            {
                'contas': [
                    {
                        'nome': 'Cheque',
                        'info': [
                            {
                                'unidade':
                                    {
                                        'uuid': '00188676-7465-4270-87d8-1ebc3ed1fbda',
                                        'codigo_eol': '200256',
                                        'tipo_unidade': 'CEU',
                                        'nome': 'UIRAPURU', 'sigla': ''
                                    },
                                'status_prestacao_contas': 'APROVADA_RESSALVA',
                                'valores': {
                                    'saldo_reprogramado_periodo_anterior_custeio': Decimal('0.00'),
                                    'saldo_reprogramado_periodo_anterior_capital': Decimal('10000.00'),
                                    'saldo_reprogramado_periodo_anterior_livre': Decimal('-777.77'),
                                    'saldo_reprogramado_periodo_anterior_total': Decimal('9222.23'),
                                    'repasses_previstos_sme_custeio': 0,
                                    'repasses_previstos_sme_capital': 0, 'repasses_previstos_sme_livre': 0,
                                    'repasses_previstos_sme_total': 0,
                                    'repasses_no_periodo_custeio': Decimal('0.00'),
                                    'repasses_no_periodo_capital': Decimal('0.00'),
                                    'repasses_no_periodo_livre': Decimal('0.00'),
                                    'repasses_no_periodo_total': Decimal('0.00'),
                                    'receitas_rendimento_no_periodo_custeio': 0,
                                    'receitas_rendimento_no_periodo_capital': 0,
                                    'receitas_rendimento_no_periodo_livre': 0,
                                    'receitas_rendimento_no_periodo_total': 0,
                                    'receitas_devolucao_no_periodo_custeio': Decimal('200.00'),
                                    'receitas_devolucao_no_periodo_capital': Decimal('0.00'),
                                    'receitas_devolucao_no_periodo_livre': Decimal('500.00'),
                                    'receitas_devolucao_no_periodo_total': Decimal('700.00'),
                                    'demais_creditos_no_periodo_custeio': Decimal('0.00'),
                                    'demais_creditos_no_periodo_capital': Decimal('0.00'),
                                    'demais_creditos_no_periodo_livre': Decimal('0.00'),
                                    'demais_creditos_no_periodo_total': Decimal('0.00'),
                                    'receitas_totais_no_periodo_custeio': Decimal('200.00'),
                                    'receitas_totais_no_periodo_capital': Decimal('0.00'),
                                    'receitas_totais_no_periodo_livre': Decimal('500.00'),
                                    'receitas_totais_no_periodo_total': Decimal('700.00'),
                                    'despesas_no_periodo_custeio': Decimal('301.11'),
                                    'despesas_no_periodo_capital': Decimal('0.00'),
                                    'despesas_no_periodo_total': Decimal('301.11'),
                                    'saldo_reprogramado_proximo_periodo_custeio': Decimal('10.00'),
                                    'saldo_reprogramado_proximo_periodo_capital': Decimal('10000.00'),
                                    'saldo_reprogramado_proximo_periodo_livre': Decimal('-388.88'),
                                    'saldo_reprogramado_proximo_periodo_total': Decimal('9621.12'),
                                    'devolucoes_ao_tesouro_no_periodo_total': 0
                                },
                                'uuid_pc': 'e4b8074a-a4ad-4438-ae19-370b4b010ced',
                                'motivos_aprovada_ressalva': [
                                    'Motivo Aprovação com Ressalva 01',
                                    'Motivo Aprovação com Ressalva 02',
                                    'Outro Motivo Aprovação com Ressalva UIRAPURU 01\nOutro Motivo Aprovação com Ressalva UIRAPURU 02'
                                ]
                            }
                        ]
                    },
                    {
                        'nome': 'Cartão',
                        'info': [
                            {
                                'unidade': {
                                    'uuid': '00188676-7465-4270-87d8-1ebc3ed1fbda',
                                    'codigo_eol': '200256',
                                    'tipo_unidade': 'CEU', 'nome': 'UIRAPURU',
                                    'sigla': ''},
                                'status_prestacao_contas': 'APROVADA_RESSALVA',
                                'valores': {
                                    'saldo_reprogramado_periodo_anterior_custeio': Decimal('0.00'),
                                    'saldo_reprogramado_periodo_anterior_capital': Decimal('0.00'),
                                    'saldo_reprogramado_periodo_anterior_livre': Decimal('0.00'),
                                    'saldo_reprogramado_periodo_anterior_total': Decimal('0.00'),
                                    'repasses_previstos_sme_custeio': 0,
                                    'repasses_previstos_sme_capital': 0,
                                    'repasses_previstos_sme_livre': 0,
                                    'repasses_previstos_sme_total': 0,
                                    'repasses_no_periodo_custeio': Decimal('0.00'),
                                    'repasses_no_periodo_capital': Decimal('0.00'),
                                    'repasses_no_periodo_livre': Decimal('0.00'),
                                    'repasses_no_periodo_total': Decimal('0.00'),
                                    'receitas_rendimento_no_periodo_custeio': Decimal('1000.00'),
                                    'receitas_rendimento_no_periodo_capital': Decimal('150.00'),
                                    'receitas_rendimento_no_periodo_livre': 0,
                                    'receitas_rendimento_no_periodo_total': Decimal('1150.00'),
                                    'receitas_devolucao_no_periodo_custeio': Decimal('0.00'),
                                    'receitas_devolucao_no_periodo_capital': Decimal('0.00'),
                                    'receitas_devolucao_no_periodo_livre': Decimal('300.00'),
                                    'receitas_devolucao_no_periodo_total': Decimal('300.00'),
                                    'demais_creditos_no_periodo_custeio': Decimal('0.00'),
                                    'demais_creditos_no_periodo_capital': Decimal('0.00'),
                                    'demais_creditos_no_periodo_livre': Decimal('0.00'),
                                    'demais_creditos_no_periodo_total': Decimal('0.00'),
                                    'receitas_totais_no_periodo_custeio': Decimal('1000.00'),
                                    'receitas_totais_no_periodo_capital': Decimal('150.00'),
                                    'receitas_totais_no_periodo_livre': Decimal('300.00'),
                                    'receitas_totais_no_periodo_total': Decimal('1450.00'),
                                    'despesas_no_periodo_custeio': Decimal('0.00'),
                                    'despesas_no_periodo_capital': Decimal('222.22'),
                                    'despesas_no_periodo_total': Decimal('222.22'),
                                    'saldo_reprogramado_proximo_periodo_custeio': Decimal('1000.00'),
                                    'saldo_reprogramado_proximo_periodo_capital': Decimal('150.00'),
                                    'saldo_reprogramado_proximo_periodo_livre': Decimal('77.78'),
                                    'saldo_reprogramado_proximo_periodo_total': Decimal('1227.78'),
                                    'devolucoes_ao_tesouro_no_periodo_total': 0
                                },
                                'uuid_pc': 'e4b8074a-a4ad-4438-ae19-370b4b010ced',
                                'motivos_aprovada_ressalva': [
                                    'Motivo Aprovação com Ressalva 01',
                                    'Motivo Aprovação com Ressalva 02',
                                    'Outro Motivo Aprovação com Ressalva UIRAPURU 01\nOutro Motivo Aprovação com Ressalva UIRAPURU 02'
                                ]
                            }
                        ]
                    }
                ],
                'motivos': [
                    {
                        'unidade':
                            {
                                'codigo_eol': '200256',
                                'tipo_unidade': 'CEU',
                                'nome': 'UIRAPURU'
                            },
                        'motivos': [
                            'Motivo Aprovação com Ressalva 01',
                            'Motivo Aprovação com Ressalva 02',
                            'Outro Motivo Aprovação com Ressalva UIRAPURU 01\nOutro Motivo Aprovação com Ressalva UIRAPURU 02'
                        ]
                    }
                ]
            },
        'reprovadas': {
            'info': [
                {
                    'unidade': {
                        'uuid': '5b7d1ffb-11d5-412d-be72-70c29f375557',
                        'codigo_eol': '000191',
                        'tipo_unidade': 'EMEF', 'nome': 'ALIPIO CORREA NETO, PROF.', 'sigla': ''
                    },
                    'status_prestacao_contas': 'REPROVADA',
                    'valores': {
                        'saldo_reprogramado_periodo_anterior_custeio': Decimal('0.00'),
                        'saldo_reprogramado_periodo_anterior_capital': Decimal('0.00'),
                        'saldo_reprogramado_periodo_anterior_livre': Decimal('0.00'),
                        'saldo_reprogramado_periodo_anterior_total': Decimal('0.00'),
                        'repasses_previstos_sme_custeio': 0, 'repasses_previstos_sme_capital': 0,
                        'repasses_previstos_sme_livre': 0, 'repasses_previstos_sme_total': 0,
                        'repasses_no_periodo_custeio': Decimal('0.00'),
                        'repasses_no_periodo_capital': Decimal('0.00'),
                        'repasses_no_periodo_livre': Decimal('0.00'),
                        'repasses_no_periodo_total': Decimal('0.00'),
                        'receitas_rendimento_no_periodo_custeio': 0,
                        'receitas_rendimento_no_periodo_capital': 0,
                        'receitas_rendimento_no_periodo_livre': 0,
                        'receitas_rendimento_no_periodo_total': 0,
                        'receitas_devolucao_no_periodo_custeio': Decimal('0.00'),
                        'receitas_devolucao_no_periodo_capital': Decimal('200.00'),
                        'receitas_devolucao_no_periodo_livre': Decimal('0.00'),
                        'receitas_devolucao_no_periodo_total': Decimal('200.00'),
                        'demais_creditos_no_periodo_custeio': Decimal('0.00'),
                        'demais_creditos_no_periodo_capital': Decimal('0.00'),
                        'demais_creditos_no_periodo_livre': Decimal('0.00'),
                        'demais_creditos_no_periodo_total': Decimal('0.00'),
                        'receitas_totais_no_periodo_custeio': Decimal('0.00'),
                        'receitas_totais_no_periodo_capital': Decimal('200.00'),
                        'receitas_totais_no_periodo_livre': Decimal('0.00'),
                        'receitas_totais_no_periodo_total': Decimal('200.00'),
                        'despesas_no_periodo_custeio': Decimal('0.00'),
                        'despesas_no_periodo_capital': Decimal('180.00'),
                        'despesas_no_periodo_total': Decimal('180.00'),
                        'saldo_reprogramado_proximo_periodo_custeio': Decimal('0.00'),
                        'saldo_reprogramado_proximo_periodo_capital': Decimal('20.00'),
                        'saldo_reprogramado_proximo_periodo_livre': Decimal('0.00'),
                        'saldo_reprogramado_proximo_periodo_total': Decimal('20.00'),
                        'devolucoes_ao_tesouro_no_periodo_total': 0
                    },
                    'uuid_pc': 'afb8e45d-20c9-4947-a76a-136c4c850ce3',
                    'motivos_reprovacao':
                        [
                            'Motivo reprovação 01',
                            'Motivo reprovação 02',
                            'Motivo Reprovação Alipio 01\nMotivo Reprovação Alipio 02'
                        ]
                }
            ],
            'motivos': [{'unidade': {'codigo_eol': '000191', 'tipo_unidade': 'EMEF',
                                     'nome': 'ALIPIO CORREA NETO, PROF.'},
                         'motivos': ['Motivo reprovação 01', 'Motivo reprovação 02',
                                     'Motivo Reprovação Alipio 01\nMotivo Reprovação Alipio 02']}]}}

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
        logger.info("Iniciando geração da Ata de Parecer Técnico em PDF")

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
