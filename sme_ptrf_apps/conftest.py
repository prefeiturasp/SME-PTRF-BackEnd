from datetime import date, timedelta

import pytest
from django.test import RequestFactory
from model_bakery import baker
from rest_framework.test import APIClient

from sme_ptrf_apps.users.models import User
from sme_ptrf_apps.users.tests.factories import UserFactory
from .core.choices import MembroEnum, RepresentacaoCargo, StatusTag
from .core.models import (
    AcaoAssociacao,
    ContaAssociacao,
    SolicitacaoEncerramentoContaAssociacao,
    STATUS_FECHADO, STATUS_ABERTO, STATUS_IMPLANTACAO,
    TipoAcertoDocumento
)
from .core.models.prestacao_conta import PrestacaoConta
from .despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL, APLICACAO_CUSTEIO
from sme_ptrf_apps.dre.models import ConsolidadoDRE
import datetime

from pytest_factoryboy import register
from sme_ptrf_apps.core.fixtures.factories.unidade_factory import DreFactory, UnidadeFactory
from sme_ptrf_apps.core.fixtures.factories.associacao_factory import AssociacaoFactory
from sme_ptrf_apps.core.fixtures.factories.conta_associacao_factory import ContaAssociacaoFactory
from sme_ptrf_apps.core.fixtures.factories.periodo_factory import PeriodoFactory
from sme_ptrf_apps.core.fixtures.factories.tipo_conta_factory import TipoContaFactory
from sme_ptrf_apps.core.fixtures.factories.observacao_conciliacao_factory import ObservacaoConciliacaoFactory
from sme_ptrf_apps.core.fixtures.factories.prestacao_conta_factory import PrestacaoContaFactory
from sme_ptrf_apps.users.fixtures.factories.usuario_factory import UsuarioFactory
from sme_ptrf_apps.users.fixtures.factories.unidade_em_suporte_factory import UnidadeEmSuporteFactory
from sme_ptrf_apps.users.fixtures.factories.grupo_acesso_factory import GrupoAcessoFactory
from sme_ptrf_apps.users.fixtures.factories.visao_factory import VisaoFactory
from sme_ptrf_apps.core.fixtures.factories.acao_factory import AcaoFactory
from sme_ptrf_apps.core.fixtures.factories.arquivo_factory import ArquivoFactory
from sme_ptrf_apps.core.fixtures.factories.solicitacao_encerramento_conta_associacao_factory import SolicitacaoEncerramentoContaAssociacaoFactory
from sme_ptrf_apps.core.fixtures.factories.acao_associacao_factory import AcaoAssociacaoFactory
from sme_ptrf_apps.core.fixtures.factories.fechamento_periodo_factory import FechamentoPeriodoFactory
from sme_ptrf_apps.despesas.fixtures.factories.despesa_factory import DespesaFactory
from sme_ptrf_apps.despesas.fixtures.factories.rateio_despesa_factory import RateioDespesaFactory
from sme_ptrf_apps.core.fixtures.factories.membro_associacao_factory import MembroAssociacaoFactory
from sme_ptrf_apps.users.fixtures.factories.acesso_concedido_sme_factory import AcessoConcedidoSmeFactory
from sme_ptrf_apps.mandatos.fixtures.factories.mandato_factory import MandatoFactory
from sme_ptrf_apps.mandatos.fixtures.factories.composicao_factory import ComposicaoFactory
from sme_ptrf_apps.core.fixtures.factories.prestacao_conta_reprovada_nao_apresentacao_factory import PrestacaoContaReprovadaNaoApresentacaoFactory

from sme_ptrf_apps.fixtures import *

register(DreFactory)
register(UnidadeFactory)
register(AssociacaoFactory)
register(ContaAssociacaoFactory)
register(PeriodoFactory)
register(TipoContaFactory)
register(ObservacaoConciliacaoFactory)
register(PrestacaoContaFactory)
register(UsuarioFactory)
register(UnidadeEmSuporteFactory)
register(GrupoAcessoFactory)
register(VisaoFactory)
register(SolicitacaoEncerramentoContaAssociacaoFactory)
register(ArquivoFactory)
register(AcaoFactory)
register(AcaoAssociacaoFactory)
register(FechamentoPeriodoFactory)
register(DespesaFactory)
register(RateioDespesaFactory)
register(MembroAssociacaoFactory)
register(AcessoConcedidoSmeFactory)
register(MandatoFactory)
register(ComposicaoFactory)
register(PrestacaoContaReprovadaNaoApresentacaoFactory)

@pytest.fixture
def fake_user(client, django_user_model, unidade):
    password = 'teste'
    username = 'fake'
    user = django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)
    user.unidades.add(unidade)
    user.save()
    return user


@pytest.fixture
def authenticated_client(client, django_user_model, unidade):
    password = 'teste'
    username = 'fake'
    user = django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)
    user.unidades.add(unidade)
    user.save()
    return client


@pytest.fixture
def usuario(unidade):
    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client(client, usuario):
    api_client = APIClient()
    api_client.force_authenticate(user=usuario)
    return api_client


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()


@pytest.fixture
def tipo_conta():
    return baker.make(
        'TipoConta',
        nome='Cheque',
        banco_nome='Banco do Inter',
        agencia='67945',
        numero_conta='935556-x',
        numero_cartao='987644164221'
    )


@pytest.fixture
def tipo_conta_cheque(tipo_conta):
    return tipo_conta


@pytest.fixture
def tipo_conta_cartao():
    return baker.make('TipoConta', nome='Cartão')


@pytest.fixture
def tipo_conta_teste():
    return baker.make('TipoConta', nome='Teste')


@pytest.fixture
def acao():
    return baker.make('Acao', nome='PTRF')


@pytest.fixture
def acao_aceita_custeio():
    return baker.make('Acao', nome='PTRF-aceita-custeio', aceita_custeio=True)


@pytest.fixture
def acao_recurso_externo_valor_reprogramado():
    return baker.make('Acao', nome='PTRF', e_recursos_proprios=True)


@pytest.fixture
def acao_ptrf(acao):
    return acao


@pytest.fixture
def acao_de_destaque():
    return baker.make('Acao', nome='ZZZZZ', posicao_nas_pesquisas='AAAAAAAAAA')


@pytest.fixture
def acao_role_cultural():
    return baker.make('Acao', nome='Rolê Cultural')


@pytest.fixture
def dre():
    return baker.make('Unidade', codigo_eol='99999', tipo_unidade='DRE', nome='DRE teste', sigla='TT')


@pytest.fixture
def dre_ipiranga():
    return baker.make('Unidade', codigo_eol='108600', tipo_unidade='DRE', nome='DRE IPIRANGA', sigla='IP')


@pytest.fixture
def valores_reprogramados_nao_finalizado(associacao_status_nao_finalizado, conta_associacao, acao_associacao):
    return baker.make(
        'ValoresReprogramados',
        associacao=associacao_status_nao_finalizado,
        periodo=associacao_status_nao_finalizado.periodo_inicial,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso="CUSTEIO",
        valor_ue=0.10,
        valor_dre=0.20
    )


@pytest.fixture
def valores_reprogramados_correcao_ue(associacao_status_correcao_ue, conta_associacao, acao_associacao):
    return baker.make(
        'ValoresReprogramados',
        associacao=associacao_status_correcao_ue,
        periodo=associacao_status_correcao_ue.periodo_inicial,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso="CUSTEIO",
        valor_ue=0.10,
        valor_dre=0.20
    )


@pytest.fixture
def valores_reprogramados_correcao_ue_com_valores_iguais(associacao_status_correcao_ue, conta_associacao, acao_associacao):
    return baker.make(
        'ValoresReprogramados',
        associacao=associacao_status_correcao_ue,
        periodo=associacao_status_correcao_ue.periodo_inicial,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso="CUSTEIO",
        valor_ue=0.10,
        valor_dre=0.10
    )


@pytest.fixture
def valores_reprogramados_conferencia_dre(associacao_status_conferencia_dre, conta_associacao, acao_associacao):
    return baker.make(
        'ValoresReprogramados',
        associacao=associacao_status_conferencia_dre,
        periodo=associacao_status_conferencia_dre.periodo_inicial,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso="CUSTEIO",
        valor_ue=0.10,
        valor_dre=0.20
    )


@pytest.fixture
def valores_reprogramados_conferencia_dre_com_valores_iguais(associacao_status_conferencia_dre, conta_associacao, acao_associacao):
    return baker.make(
        'ValoresReprogramados',
        associacao=associacao_status_conferencia_dre,
        periodo=associacao_status_conferencia_dre.periodo_inicial,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso="CUSTEIO",
        valor_ue=0.10,
        valor_dre=0.10
    )


@pytest.fixture
def valores_reprogramados_valores_corretos(associacao, conta_associacao, acao_associacao_aceita_custeio):
    return baker.make(
        'ValoresReprogramados',
        associacao=associacao,
        periodo=associacao.periodo_inicial,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_aceita_custeio,
        aplicacao_recurso="CUSTEIO",
        valor_ue=0.10,
        valor_dre=0.20
    )


@pytest.fixture
def valores_reprogramados_valores_corretos_com_valores_iguais(associacao, conta_associacao, acao_associacao):
    return baker.make(
        'ValoresReprogramados',
        associacao=associacao,
        periodo=associacao.periodo_inicial,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso="CUSTEIO",
        valor_ue=0.10,
        valor_dre=0.10
    )


@pytest.fixture
def valores_reprogramados_valores_corretos_com_valores_iguais_2(associacao, conta_associacao, acao_associacao):
    return baker.make(
        'ValoresReprogramados',
        associacao=associacao,
        periodo=associacao.periodo_inicial,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso="CUSTEIO",
        valor_ue=0.10,
        valor_dre=0.10
    )


@pytest.fixture
def unidade(dre):
    return baker.make(
        'Unidade',
        nome='Escola Teste',
        tipo_unidade='CEU',
        codigo_eol='123456',
        dre=dre,
        sigla='ET',
        cep='5868120',
        tipo_logradouro='Travessa',
        logradouro='dos Testes',
        bairro='COHAB INSTITUTO ADVENTISTA',
        numero='200',
        complemento='fundos',
        telefone='58212627',
        email='emefjopfilho@sme.prefeitura.sp.gov.br',
        diretor_nome='Pedro Amaro',
        dre_cnpj='63.058.286/0001-86',
        dre_diretor_regional_rf='1234567',
        dre_diretor_regional_nome='Anthony Edward Stark',
        dre_designacao_portaria='Portaria nº 0.000',
        dre_designacao_ano='2017',
    )


@pytest.fixture
def outra_unidade(dre):
    return baker.make(
        'Unidade',
        nome='Outra Escola Teste',
        tipo_unidade='CEU',
        codigo_eol='777777',
        dre=dre,
    )


@pytest.fixture
def terceira_unidade(dre):
    return baker.make(
        'Unidade',
        nome='Terceira Escola Teste',
        tipo_unidade='CEU',
        codigo_eol='888889',
        dre=dre,
    )


@pytest.fixture
def quarta_unidade(dre):
    return baker.make(
        'Unidade',
        nome='Quarta Escola Teste',
        tipo_unidade='CEU',
        codigo_eol='999999',
        dre=dre,
    )


@pytest.fixture
def associacao_com_data_de_encerramento(unidade, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='34.845.266/0001-57',
        unidade=unidade,
        periodo_inicial=periodo_anterior,
        ccm='0.000.00-0',
        email="ollyverottoboni2@gmail.com",
        processo_regularidade='123456',
        data_de_encerramento=date(2023, 4, 25),
    )


@pytest.fixture
def associacao(unidade, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='52.302.275/0001-83',
        unidade=unidade,
        periodo_inicial=periodo_anterior,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456'
    )


@pytest.fixture
def associacao_iniciada_2020_1(periodo_2020_1, unidade):
    return baker.make(
        'Associacao',
        nome='Escola Iniciada em 2020.1',
        cnpj='99.073.449/0001-47',
        unidade=unidade,
        periodo_inicial=periodo_2020_1,
    )


@pytest.fixture
def associacao_iniciada_2020_2(periodo_2020_2, outra_unidade):
    return baker.make(
        'Associacao',
        nome='Escola Iniciada em 2020.2',
        cnpj='23.500.058/0001-08',
        unidade=outra_unidade,
        periodo_inicial=periodo_2020_2,
    )


@pytest.fixture
def associacao_encerrada_2020_1(periodo_2019_2, periodo_2020_1, unidade):
    return baker.make(
        'Associacao',
        nome='Escola Encerrada em 2020.1',
        cnpj='99.073.449/0001-47',
        unidade=unidade,
        periodo_inicial=periodo_2019_2,
        data_de_encerramento=periodo_2020_1.data_fim_realizacao_despesas,
    )


@pytest.fixture
def associacao_encerrada_2020_2(periodo_2019_2, periodo_2020_2, quarta_unidade):
    return baker.make(
        'Associacao',
        nome='Escola Encerrada em 2020.2',
        cnpj='23.500.058/0001-08',
        unidade=quarta_unidade,
        periodo_inicial=periodo_2019_2,
        data_de_encerramento=periodo_2020_2.data_fim_realizacao_despesas,
    )


@pytest.fixture
def associacao_encerrada_2021_2(periodo_2019_2, outra_unidade):
    return baker.make(
        'Associacao',
        nome='Escola Encerrada em 2021.2',
        cnpj='23.500.058/0001-08',
        unidade=outra_unidade,
        periodo_inicial=periodo_2019_2,
        data_de_encerramento=date(2021, 12, 10),
    )


@pytest.fixture
def associacao_status_nao_finalizado(unidade, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='36.749.017/0001-93',
        unidade=unidade,
        periodo_inicial=periodo_anterior,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456',
        status_valores_reprogramados="NAO_FINALIZADO"
    )


@pytest.fixture
def associacao_status_correcao_ue(unidade, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='20.686.126/0001-79',
        unidade=unidade,
        periodo_inicial=periodo_anterior,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456',
        status_valores_reprogramados="EM_CORRECAO_UE"
    )


@pytest.fixture
def associacao_status_conferencia_dre(unidade, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='04.013.611/0001-25',
        unidade=unidade,
        periodo_inicial=periodo_anterior,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456',
        status_valores_reprogramados="EM_CONFERENCIA_DRE"
    )


@pytest.fixture
def associacao_com_presidente_ausente(unidade, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='52.302.275/0001-83',
        unidade=unidade,
        periodo_inicial=periodo_anterior,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456',
        status_presidente='AUSENTE',
        cargo_substituto_presidente_ausente=MembroEnum.VICE_PRESIDENTE_DIRETORIA_EXECUTIVA.name
    )


@pytest.fixture
def associacao_cadastro_incompleto(unidade, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='',
        cnpj='52.302.275/0001-84',
        unidade=unidade,
        periodo_inicial=periodo_anterior,
        ccm='0.000.00-0',
        email="associacaosemnome@gmail.com",
        processo_regularidade='000000',
        status_presidente='AUSENTE',
        cargo_substituto_presidente_ausente=MembroEnum.VICE_PRESIDENTE_DIRETORIA_EXECUTIVA.name
    )


@pytest.fixture
def outra_associacao(unidade, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Outra',
        cnpj='52.302.275/0001-99',
        unidade=unidade,
        periodo_inicial=periodo_anterior,
    )


@pytest.fixture
def associacao_sem_periodo_inicial(unidade):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='44.219.758/0001-90',
        unidade=unidade,
        periodo_inicial=None,
    )


@pytest.fixture
def outra_associacao_sem_periodo_inicial(terceira_unidade):
    return baker.make(
        'Associacao',
        nome='Associacao Não Iniciada',
        cnpj='78.275.825/0001-06',
        unidade=terceira_unidade,
        periodo_inicial=None,
    )


@pytest.fixture
def conta_associacao(associacao, tipo_conta):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta,
        banco_nome='Banco do Brasil',
        agencia='12345',
        numero_conta='123456-x',
        numero_cartao='534653264523',
        data_inicio=date(2019, 1, 1)
    )


@pytest.fixture
def conta_associacao_tipo_cheque(associacao, tipo_conta_cheque):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta_cheque,
        banco_nome='Banco do Brasil',
        agencia='12345',
        numero_conta='123456-x',
        numero_cartao='534653264523'
    )


@pytest.fixture
def conta_associacao_tipo_teste(associacao, tipo_conta_teste, periodo_2020_1):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta_teste,
        banco_nome='Banco do Brasil',
        agencia='12345',
        numero_conta='123456-x',
        numero_cartao='534653264523',
        data_inicio=periodo_2020_1.data_inicio_realizacao_despesas
    )


@pytest.fixture
def conta_associacao_incompleta(associacao_cadastro_incompleto, tipo_conta_cartao):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao_cadastro_incompleto,
        tipo_conta=tipo_conta_cartao,
    )


@pytest.fixture
def conta_associacao_incompleta_002(associacao, tipo_conta_cartao):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta_cartao,
    )


@pytest.fixture
def conta_associacao_cheque(associacao, tipo_conta_cheque):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta_cheque,
        data_inicio=date(2019, 1, 1)
    )


@pytest.fixture
def conta_associacao_cartao(associacao, tipo_conta_cartao):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta_cartao,
        data_inicio=date(2019, 1, 1)
    )


@pytest.fixture
def conta_associacao_inativa(associacao, tipo_conta):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta,
        status=ContaAssociacao.STATUS_INATIVA,
        data_inicio=date(2019, 1, 1)
    )


@pytest.fixture
def conta_associacao_inativa_x(associacao, tipo_conta):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta,
        banco_nome='Bando X',
        status=ContaAssociacao.STATUS_INATIVA,
        data_inicio=date(2019, 1, 1)
    )


@pytest.fixture
def solicitacao_encerramento_conta_associacao(conta_associacao_inativa):
    return baker.make(
        'SolicitacaoEncerramentoContaAssociacao',
        conta_associacao=conta_associacao_inativa,
        data_de_encerramento_na_agencia='2019-09-02',
        status=SolicitacaoEncerramentoContaAssociacao.STATUS_APROVADA
    )


@pytest.fixture
def solicitacao_encerramento_conta_associacao_no_periodo_2020_1(conta_associacao_inativa_x, periodo_2020_1):
    return baker.make(
        'SolicitacaoEncerramentoContaAssociacao',
        conta_associacao=conta_associacao_inativa_x,
        data_de_encerramento_na_agencia=periodo_2020_1.data_inicio_realizacao_despesas,
        status=SolicitacaoEncerramentoContaAssociacao.STATUS_APROVADA
    )


@pytest.fixture
def acao_associacao(associacao, acao):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao,
        acao=acao
    )


@pytest.fixture
def acao_associacao_aceita_custeio(associacao, acao_aceita_custeio):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao,
        acao=acao_aceita_custeio
    )


@pytest.fixture
def acao_associacao_aceita_recurso_externo(associacao, acao_recurso_externo_valor_reprogramado):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao,
        acao=acao_recurso_externo_valor_reprogramado
    )


@pytest.fixture
def acao_associacao_de_destaque(associacao, acao_de_destaque):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao,
        acao=acao_de_destaque
    )


@pytest.fixture
def acao_associacao_inativa(associacao, acao):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao,
        acao=acao,
        status=AcaoAssociacao.STATUS_INATIVA
    )


@pytest.fixture
def acao_associacao_ptrf(associacao, acao_ptrf):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao,
        acao=acao_ptrf
    )


@pytest.fixture
def acao_associacao_role_cultural(associacao, acao_role_cultural):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao,
        acao=acao_role_cultural
    )


@pytest.fixture
def periodo_anterior():
    return baker.make(
        'Periodo',
        referencia='2019.1',
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 8, 31),
    )


@pytest.fixture
def periodo(periodo_anterior):
    return baker.make(
        'Periodo',
        referencia='2019.2',
        data_inicio_realizacao_despesas=date(2019, 9, 1),
        data_fim_realizacao_despesas=date(2019, 11, 30),
        data_prevista_repasse=date(2019, 10, 1),
        data_inicio_prestacao_contas=date(2019, 12, 1),
        data_fim_prestacao_contas=date(2019, 12, 5),
        periodo_anterior=periodo_anterior,
    )


@pytest.fixture
def periodo_aberto(periodo_anterior):
    return baker.make(
        'Periodo',
        referencia='2019.2',
        data_inicio_realizacao_despesas=date(2019, 9, 1),
        data_fim_realizacao_despesas=None,
        data_prevista_repasse=date(2019, 10, 1),
        data_inicio_prestacao_contas=date(2019, 12, 1),
        data_fim_prestacao_contas=date(2019, 12, 5),
        periodo_anterior=periodo_anterior
    )


@pytest.fixture
def periodo_2020_1(periodo):
    return baker.make(
        'Periodo',
        referencia='2020.1',
        data_inicio_realizacao_despesas=date(2020, 1, 1),
        data_fim_realizacao_despesas=date(2020, 6, 30),
        data_prevista_repasse=date(2020, 1, 1),
        data_inicio_prestacao_contas=date(2020, 7, 1),
        data_fim_prestacao_contas=date(2020, 7, 10),
        periodo_anterior=periodo
    )


@pytest.fixture
def periodo_2020_2(periodo_2020_1):
    return baker.make(
        'Periodo',
        referencia='2020.2',
        data_inicio_realizacao_despesas=date(2020, 7, 1),
        data_fim_realizacao_despesas=date(2020, 12, 31),
        periodo_anterior=periodo_2020_1,
    )


@pytest.fixture
def periodo_2021_1(periodo_2020_2):
    return baker.make(
        'Periodo',
        referencia='2021.1',
        data_inicio_realizacao_despesas=date(2021, 1, 1),
        data_fim_realizacao_despesas=date(2021, 6, 30),
        periodo_anterior=periodo_2020_2,
    )


@pytest.fixture
def periodo_2021_2(periodo_2021_1):
    return baker.make(
        'Periodo',
        referencia='2021.2',
        data_inicio_realizacao_despesas=date(2021, 7, 1),
        data_fim_realizacao_despesas=None,
        periodo_anterior=periodo_2021_1,
    )


@pytest.fixture
def periodo_2019_2(periodo):
    return baker.make(
        'Periodo',
        referencia='2019.2',
        data_inicio_realizacao_despesas=date(2019, 6, 1),
        data_fim_realizacao_despesas=date(2019, 12, 30),
        data_prevista_repasse=date(2019, 6, 1),
        data_inicio_prestacao_contas=date(2020, 1, 1),
        data_fim_prestacao_contas=date(2020, 1, 10),
        periodo_anterior=periodo
    )


@pytest.fixture
def periodo_fim_em_2020_06_30():
    return baker.make(
        'Periodo',
        referencia='2020.1',
        data_inicio_realizacao_despesas=date(2020, 1, 1),
        data_fim_realizacao_despesas=date(2020, 6, 30),
        data_prevista_repasse=date(2020, 1, 1),
        data_inicio_prestacao_contas=date(2020, 7, 1),
        data_fim_prestacao_contas=date(2020, 7, 10),
        periodo_anterior=None
    )


@pytest.fixture
def periodo_fim_em_aberto():
    return baker.make(
        'Periodo',
        referencia='2020.1',
        data_inicio_realizacao_despesas=date(2020, 1, 1),
        data_fim_realizacao_despesas=None,
        data_prevista_repasse=date(2020, 1, 1),
        data_inicio_prestacao_contas=date(2020, 7, 1),
        data_fim_prestacao_contas=date(2020, 7, 10),
        periodo_anterior=None
    )


@pytest.fixture
def periodo_futuro():
    return baker.make(
        'Periodo',
        referencia='2020.3',
        data_inicio_realizacao_despesas=date(2020, 6, 15),
        data_fim_realizacao_despesas=None,
        data_prevista_repasse=date(2020, 9, 30),
        data_inicio_prestacao_contas=date(2020, 12, 1),
        data_fim_prestacao_contas=date(2020, 12, 5),
        periodo_anterior=None
    )


@pytest.fixture
def prestacao_conta_anterior(periodo_anterior, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_anterior,
        associacao=associacao,
    )


@pytest.fixture
def motivo_aprovacao_ressalva_x():
    return baker.make(
        'dre.MotivoAprovacaoRessalva',
        motivo='X'
    )


@pytest.fixture
def motivo_reprovacao_x():
    return baker.make(
        'dre.MotivoReprovacao',
        motivo='X'
    )


@pytest.fixture
def motivo_reprovacao_y():
    return baker.make(
        'dre.MotivoReprovacao',
        motivo='Y'
    )


@pytest.fixture
def prestacao_conta(periodo, associacao, motivo_aprovacao_ressalva_x, motivo_reprovacao_x):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        data_recebimento_apos_acertos=date(2020, 10, 1),
        data_ultima_analise=date(2020, 10, 1),
        motivos_reprovacao=[motivo_reprovacao_x, ],
        outros_motivos_reprovacao="Outros motivos reprovacao",
        motivos_aprovacao_ressalva=[motivo_aprovacao_ressalva_x, ],
        outros_motivos_aprovacao_ressalva="Outros motivos",
        recomendacoes="recomendacao",
        publicada=None,
        consolidado_dre=None,
        justificativa_pendencia_realizacao="Teste de justificativa.",
    )


@pytest.fixture
def prestacao_conta_iniciada(periodo_2020_1, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
    )


@pytest.fixture
def prestacao_conta_2020_1_devolvida(periodo_2020_1, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
        status=PrestacaoConta.STATUS_DEVOLVIDA
    )


@pytest.fixture
def prestacao_conta_devolvida(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        status=PrestacaoConta.STATUS_DEVOLVIDA
    )


@pytest.fixture
def prestacao_conta_devolvida_posterior(periodo_futuro, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_futuro,
        associacao=associacao,
        status=PrestacaoConta.STATUS_DEVOLVIDA
    )


@pytest.fixture
def consolidado_dre_publicado_diario_oficial(periodo, dre):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre,
        periodo=periodo,
        status=ConsolidadoDRE.STATUS_NAO_GERADOS,
        data_publicacao=date(2020, 7, 1),
        pagina_publicacao='1'
    )


@pytest.fixture
def prestacao_conta_2020_1_aprovada_associacao_encerrada_publicada_diario_oficial(
    periodo_2020_1,
    associacao_encerrada_2020_1,
    consolidado_dre_publicado_diario_oficial
):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao_encerrada_2020_1,
        status=PrestacaoConta.STATUS_APROVADA,
        consolidado_dre=consolidado_dre_publicado_diario_oficial
    )


@pytest.fixture
def prestacao_conta_2020_1_aprovada_associacao_encerrada(periodo_2020_1, associacao_encerrada_2020_1):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao_encerrada_2020_1,
        status=PrestacaoConta.STATUS_APROVADA,
    )


@pytest.fixture
def fechamento_periodo_anterior(periodo_anterior, associacao, conta_associacao, acao_associacao, ):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_anterior,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_capital=500,
        total_repasses_capital=450,
        total_despesas_capital=400,
        total_receitas_custeio=1000,
        total_repasses_custeio=900,
        total_despesas_custeio=800,
        total_receitas_livre=2000,
        total_repasses_livre=2000,
        status=STATUS_FECHADO
    )


@pytest.fixture
def fechamento_periodo_anterior_capital_1000_livre_2000(periodo_anterior, associacao, conta_associacao,
                                                        acao_associacao, ):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_anterior,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_capital=1000,
        total_repasses_capital=1000,
        total_receitas_livre=2000,
        total_repasses_livre=2000,
        status=STATUS_IMPLANTACAO
    )


@pytest.fixture
def prestacao_conta_2020_1_conciliada(periodo_2020_1, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
        status=PrestacaoConta.STATUS_NAO_RECEBIDA
    )


@pytest.fixture
def prestacao_conta_2019_2_conciliada(periodo_2019_2, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2019_2,
        associacao=associacao,
        status=PrestacaoConta.STATUS_NAO_RECEBIDA
    )


@pytest.fixture
def prestacao_conta_2020_1_conciliada_outra_conta(periodo_2020_1, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
        status=STATUS_ABERTO,
    )


@pytest.fixture
def prestacao_conta_2021_1_aprovada_associacao_encerrada(periodo_2021_1, associacao_encerrada_2021_2):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2021_1,
        associacao=associacao_encerrada_2021_2,
        status=PrestacaoConta.STATUS_APROVADA
    )


@pytest.fixture
def prestacao_conta_2021_2_aprovada_associacao_encerrada(periodo_2021_2, associacao_encerrada_2021_2):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2021_2,
        associacao=associacao_encerrada_2021_2,
        status=PrestacaoConta.STATUS_APROVADA
    )


@pytest.fixture
def fechamento_2020_1(periodo_2020_1, associacao, conta_associacao, acao_associacao, prestacao_conta_2020_1_conciliada):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_capital=1000,
        total_repasses_capital=900,
        total_despesas_capital=800,
        total_receitas_custeio=2000,
        total_repasses_custeio=1800,
        total_despesas_custeio=1600,
        total_despesas_nao_conciliadas_capital=8.0,
        total_despesas_nao_conciliadas_custeio=16.0,
        total_receitas_nao_conciliadas_capital=10.0,
        total_receitas_nao_conciliadas_custeio=20.0,
        status=STATUS_FECHADO,
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        especificacoes_despesas_capital=['ar condicionado', ],
        especificacoes_despesas_custeio=['cadeira', 'mesa'],
    )


@pytest.fixture
def fechamento_2020_1_com_livre(periodo_2020_1, associacao, conta_associacao, acao_associacao,
                                prestacao_conta_2020_1_conciliada):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_capital=1000,
        total_repasses_capital=900,
        total_despesas_capital=800,
        total_receitas_custeio=2000,
        total_repasses_custeio=1800,
        total_despesas_custeio=1600,
        total_receitas_livre=3000,
        total_repasses_livre=2700,
        total_despesas_nao_conciliadas_capital=8.0,
        total_despesas_nao_conciliadas_custeio=16.0,
        total_receitas_nao_conciliadas_capital=10.0,
        total_receitas_nao_conciliadas_custeio=20.0,
        total_receitas_nao_conciliadas_livre=30.0,
        status=STATUS_FECHADO,
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        especificacoes_despesas_capital=['ar condicionado', ],
        especificacoes_despesas_custeio=['cadeira', 'mesa'],
    )


@pytest.fixture
def fechamento_2020_1_outra_conta(periodo_2020_1, associacao, conta_associacao_cartao, acao_associacao,
                                  prestacao_conta_2020_1_conciliada_outra_conta):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_capital=1000,
        total_repasses_capital=900,
        total_despesas_capital=800,
        total_receitas_custeio=2000,
        total_repasses_custeio=1800,
        total_despesas_custeio=1600,
        total_despesas_nao_conciliadas_capital=8.0,
        total_despesas_nao_conciliadas_custeio=16.0,
        total_receitas_nao_conciliadas_capital=10.0,
        total_receitas_nao_conciliadas_custeio=20.0,
        status=STATUS_FECHADO,
        prestacao_conta=prestacao_conta_2020_1_conciliada_outra_conta,
        especificacoes_despesas_capital=['ar condicionado', ],
        especificacoes_despesas_custeio=['cadeira', 'mesa'],
    )


@pytest.fixture
def fechamento_periodo_anterior_role(periodo_anterior, associacao, conta_associacao, acao_associacao_role_cultural, ):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_anterior,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        fechamento_anterior=None,
        total_receitas_capital=500,
        total_repasses_capital=450,
        total_despesas_capital=400,
        total_receitas_custeio=1000,
        total_repasses_custeio=900,
        total_despesas_custeio=800,
        status=STATUS_FECHADO
    )


@pytest.fixture
def fechamento_periodo_anterior_role_implantado(periodo_anterior, associacao, conta_associacao,
                                                acao_associacao_role_cultural, ):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_anterior,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        fechamento_anterior=None,
        total_receitas_capital=1000,
        total_repasses_capital=0,
        total_despesas_capital=0,
        total_receitas_custeio=2000,
        total_repasses_custeio=0,
        total_despesas_custeio=0,
        status=STATUS_IMPLANTACAO
    )


@pytest.fixture
def fechamento_periodo_anterior_role_implantado_com_livre_aplicacao(periodo_anterior, associacao, conta_associacao,
                                                                    acao_associacao_role_cultural, ):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_anterior,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        fechamento_anterior=None,
        total_receitas_capital=1000,
        total_repasses_capital=0,
        total_despesas_capital=0,
        total_receitas_custeio=2000,
        total_repasses_custeio=0,
        total_despesas_custeio=0,
        total_receitas_livre=3000,
        status=STATUS_IMPLANTACAO
    )


@pytest.fixture
def fechamento_2020_1_role(periodo_2020_1, associacao, conta_associacao, acao_associacao_role_cultural,
                           prestacao_conta_2020_1_conciliada, fechamento_periodo_anterior_role):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        fechamento_anterior=fechamento_periodo_anterior_role,
        total_receitas_capital=2000,
        total_repasses_capital=1000,
        total_despesas_capital=200,
        total_receitas_custeio=1000,
        total_repasses_custeio=800,
        total_despesas_custeio=100,
        total_despesas_nao_conciliadas_capital=20.0,
        total_despesas_nao_conciliadas_custeio=10.0,
        total_receitas_nao_conciliadas_capital=20.0,
        total_receitas_nao_conciliadas_custeio=10.0,
        status=STATUS_FECHADO,
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        especificacoes_despesas_capital=['ar condicionado', ],
        especificacoes_despesas_custeio=['ventilador', 'contador']
    )


@pytest.fixture
def fechamento_2020_1_role_cartao(periodo_2020_1, associacao, conta_associacao_cartao, acao_associacao_role_cultural,
                                  prestacao_conta_2020_1_conciliada, fechamento_periodo_anterior_role):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        fechamento_anterior=fechamento_periodo_anterior_role,
        total_receitas_capital=2000,
        total_repasses_capital=1000,
        total_despesas_capital=200,
        total_receitas_custeio=1000,
        total_repasses_custeio=800,
        total_despesas_custeio=100,
        total_despesas_nao_conciliadas_capital=20.0,
        total_despesas_nao_conciliadas_custeio=10.0,
        total_receitas_nao_conciliadas_capital=20.0,
        total_receitas_nao_conciliadas_custeio=10.0,
        status=STATUS_FECHADO,
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        especificacoes_despesas_capital=['ar condicionado', ],
        especificacoes_despesas_custeio=['ventilador', 'contador']
    )


@pytest.fixture
def fechamento_periodo_com_saldo(periodo, associacao, conta_associacao, acao_associacao, ):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_capital=20000,
        total_repasses_capital=20000,
        total_despesas_capital=0,
        total_receitas_custeio=20000,
        total_repasses_custeio=20000,
        total_despesas_custeio=0,
        status=STATUS_FECHADO
    )


@pytest.fixture
def fechamento_periodo_com_saldo_livre_aplicacao(periodo, associacao, conta_associacao, acao_associacao, ):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_livre=20000,
        total_repasses_livre=20000,
        status=STATUS_FECHADO
    )


@pytest.fixture
def fechamento_periodo_com_saldo_outra_acao(periodo, associacao, conta_associacao, acao_associacao_role_cultural, ):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        fechamento_anterior=None,
        total_receitas_capital=90000,
        total_repasses_capital=90000,
        total_despesas_capital=0,
        total_receitas_custeio=90000,
        total_repasses_custeio=90000,
        total_despesas_custeio=0,
        status=STATUS_FECHADO
    )


@pytest.fixture
def fechamento_periodo(periodo, associacao, conta_associacao, acao_associacao, fechamento_periodo_anterior):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=fechamento_periodo_anterior,
        total_receitas_capital=1000,
        total_repasses_capital=900,
        total_despesas_capital=800,
        total_receitas_custeio=2000,
        total_repasses_custeio=1800,
        total_despesas_custeio=1600,
        total_receitas_livre=3000,
        total_repasses_livre=3000,
        total_receitas_nao_conciliadas_capital=10,
        total_receitas_nao_conciliadas_custeio=20,
        total_receitas_nao_conciliadas_livre=30,
        total_despesas_nao_conciliadas_capital=8,
        total_despesas_nao_conciliadas_custeio=16,
        status=STATUS_FECHADO,
        especificacoes_despesas_capital=['teste1', 'teste2'],
        especificacoes_despesas_custeio=['teste1', 'teste2'],
    )


@pytest.fixture
def tipo_receita():
    return baker.make('TipoReceita', nome='Estorno')


@pytest.fixture
def tipo_receita_repasse():
    return baker.make('TipoReceita', nome='Repasse', e_repasse=True)


@pytest.fixture
def detalhe_tipo_receita_repasse(tipo_receita_repasse):
    return baker.make('DetalheTipoReceita', nome='Repasse YYYÇ', tipo_receita=tipo_receita_repasse)


@pytest.fixture
def detalhe_tipo_receita(tipo_receita):
    return baker.make('DetalheTipoReceita', nome='Estorno A', tipo_receita=tipo_receita)


@pytest.fixture
def receita_teste_valida_data_de_encerramento(associacao, conta_associacao, acao_associacao, tipo_receita, periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=date(2023, 4, 20),
        valor=100.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
    )


@pytest.fixture
def receita_teste_valida_data_de_encerramento_associacao_02(associacao_02, conta_associacao, acao_associacao, tipo_receita, periodo):
    return baker.make(
        'Receita',
        associacao=associacao_02,
        data=date(2023, 4, 20),
        valor=100.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
    )


@pytest.fixture
def receita_100_no_periodo(associacao, conta_associacao, acao_associacao, tipo_receita, periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_inicio_realizacao_despesas + timedelta(days=3),
        valor=100.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
    )


@pytest.fixture
def receita_1000_no_periodo_livre_aplicacao(associacao, conta_associacao, acao_associacao, tipo_receita, periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_inicio_realizacao_despesas + timedelta(days=3),
        valor=1000.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
        categoria_receita='LIVRE'
    )


@pytest.fixture
def receita_100_no_periodo_capital(associacao, conta_associacao, acao_associacao, tipo_receita, periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_inicio_realizacao_despesas + timedelta(days=3),
        valor=100.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
        categoria_receita='CAPITAL'
    )


@pytest.fixture
def receita_100_nao_conferida_anterior_ao_periodo(associacao, conta_associacao, acao_associacao, tipo_receita, periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_inicio_realizacao_despesas - timedelta(days=3),
        valor=100.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
        conferido=False,
    )


@pytest.fixture
def receita_100_no_periodo_acao_de_destaque(associacao, conta_associacao, acao_associacao_de_destaque, tipo_receita,
                                            periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_inicio_realizacao_despesas + timedelta(days=3),
        valor=100.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_de_destaque,
        tipo_receita=tipo_receita,
    )


@pytest.fixture
def receita_300_repasse_no_periodo(associacao, conta_associacao, acao_associacao, tipo_receita_repasse, periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_inicio_realizacao_despesas + timedelta(days=3),
        valor=300.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita_repasse,
    )


@pytest.fixture
def receita_200_no_inicio_do_periodo(associacao, conta_associacao, acao_associacao, tipo_receita, periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_inicio_realizacao_despesas,
        valor=200.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
    )


@pytest.fixture
def receita_300_no_fim_do_periodo(associacao, conta_associacao, acao_associacao, tipo_receita, periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_fim_realizacao_despesas,
        valor=300.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
    )


@pytest.fixture
def receita_50_fora_do_periodo(associacao, conta_associacao, acao_associacao, tipo_receita, periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_inicio_realizacao_despesas - timedelta(days=1),
        valor=50.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
    )


@pytest.fixture
def receita_30_no_periodo_outra_acao(associacao, conta_associacao, acao_associacao_role_cultural, tipo_receita,
                                     periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_inicio_realizacao_despesas + timedelta(days=3),
        valor=30.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita,
    )


@pytest.fixture
def receita_no_periodo_2020_1(associacao, conta_associacao, acao_associacao, tipo_receita, periodo_2020_1):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo_2020_1.data_inicio_realizacao_despesas,
        valor=100.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
    )


@pytest.fixture
def tipo_documento():
    return baker.make('TipoDocumento', nome='NFe')


@pytest.fixture
def tipo_transacao():
    return baker.make('TipoTransacao', nome='Boleto')


@pytest.fixture
def tipo_aplicacao_recurso_custeio():
    return APLICACAO_CUSTEIO


@pytest.fixture
def tipo_aplicacao_recurso_capital():
    return APLICACAO_CAPITAL


@pytest.fixture
def tipo_custeio():
    return baker.make('TipoCusteio', nome='Material')


@pytest.fixture
def tipo_custeio_material():
    return baker.make('TipoCusteio', nome='Material 02')


@pytest.fixture
def tipo_custeio_servico():
    return baker.make('TipoCusteio', nome='Servico')


@pytest.fixture
def tipo_custeio_tributos_e_tarifas():
    return baker.make('TipoCusteio', nome='tributos e tarifas')


@pytest.fixture
def especificacao_material_eletrico(tipo_aplicacao_recurso_custeio, tipo_custeio_material):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Material elétrico',
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_material,
    )


@pytest.fixture
def especificacao_ar_condicionado(tipo_aplicacao_recurso_capital):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Ar condicionado',
        aplicacao_recurso=tipo_aplicacao_recurso_capital,
        tipo_custeio=None,
    )


# despesa_no_periodo
@pytest.fixture
def despesa_no_periodo(associacao, tipo_documento, tipo_transacao, periodo):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=periodo.data_inicio_realizacao_despesas + timedelta(days=3),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=periodo.data_inicio_realizacao_despesas + timedelta(days=3),
        valor_total=310.00,
        valor_recursos_proprios=0,
    )


@pytest.fixture
def receita_no_periodo(associacao, conta_associacao, acao_associacao, tipo_receita_repasse, periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_inicio_realizacao_despesas,
        valor=10000,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita_repasse,
    )


@pytest.fixture
def rateio_despesa_demonstrativo(associacao, despesa_no_periodo, conta_associacao, acao, tipo_aplicacao_recurso_capital,
                                 tipo_custeio,
                                 especificacao_material_eletrico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_no_periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_capital,
        tipo_custeio=tipo_custeio,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=100.00,
        quantidade_itens_capital=2,
        valor_item_capital=50.00,
        numero_processo_incorporacao_capital='Teste123456'
    )


@pytest.fixture
def rateio_despesa_demonstrativo2(associacao, despesa_no_periodo, conta_associacao, acao,
                                  tipo_aplicacao_recurso_custeio, tipo_custeio_material,
                                  especificacao_material_eletrico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_no_periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_material,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=200.00,
        quantidade_itens_capital=2,
        valor_item_capital=100.00,
        numero_processo_incorporacao_capital='Teste654321'
    )


# rateio_100_custeio
@pytest.fixture
def rateio_no_periodo_100_custeio(associacao, despesa_no_periodo, conta_associacao, acao,
                                  tipo_aplicacao_recurso_custeio,
                                  tipo_custeio_material,
                                  especificacao_material_eletrico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_no_periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_material,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=100.00

    )


# rateio_200_capital
@pytest.fixture
def rateio_no_periodo_200_capital(associacao, despesa_no_periodo, conta_associacao, acao,
                                  tipo_aplicacao_recurso_capital,
                                  tipo_custeio,
                                  especificacao_ar_condicionado, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_no_periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_capital,
        tipo_custeio=None,
        especificacao_material_servico=especificacao_ar_condicionado,
        valor_rateio=200.00,
        quantidade_itens_capital=1,
        valor_item_capital=200.00,
        numero_processo_incorporacao_capital='Teste123456'

    )


# rateio_200_capital
@pytest.fixture
def rateio_no_periodo_1500_capital(associacao, despesa_no_periodo, conta_associacao, acao,
                                   tipo_aplicacao_recurso_capital,
                                   tipo_custeio,
                                   especificacao_ar_condicionado, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_no_periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_capital,
        tipo_custeio=None,
        especificacao_material_servico=especificacao_ar_condicionado,
        valor_rateio=1500.00,
        quantidade_itens_capital=1,
        valor_item_capital=1500.00,
        numero_processo_incorporacao_capital='Teste123456'

    )


# rateio_10_custeio_outra_acao
@pytest.fixture
def rateio_no_periodo_10_custeio_outra_acao(associacao, despesa_no_periodo, conta_associacao, acao,
                                            tipo_aplicacao_recurso_custeio,
                                            tipo_custeio_servico,
                                            especificacao_material_eletrico, acao_associacao_role_cultural):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_no_periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=100.00

    )


@pytest.fixture
def rateio_no_periodo_1500_capital_outra_conta(associacao, despesa_no_periodo, conta_associacao_cartao, acao,
                                               tipo_aplicacao_recurso_capital,
                                               tipo_custeio,
                                               especificacao_ar_condicionado, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_no_periodo,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_capital,
        tipo_custeio=None,
        especificacao_material_servico=especificacao_ar_condicionado,
        valor_rateio=1500.00,
        quantidade_itens_capital=1,
        valor_item_capital=1500.00,
        numero_processo_incorporacao_capital='Teste123456'

    )


# despesa_fora_do_periodo
@pytest.fixture
def despesa_fora_periodo(associacao, tipo_documento, tipo_transacao, periodo):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=periodo.data_inicio_realizacao_despesas - timedelta(days=1),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=periodo.data_inicio_realizacao_despesas - timedelta(days=1),
        valor_total=50.00,
        valor_recursos_proprios=0,
    )


# rateio_50_custeio
@pytest.fixture
def rateio_fora_periodo_50_custeio(associacao, despesa_fora_periodo, conta_associacao, acao,
                                   tipo_aplicacao_recurso_custeio,
                                   tipo_custeio_tributos_e_tarifas,
                                   especificacao_material_eletrico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_fora_periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_tributos_e_tarifas,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=50.00

    )


@pytest.fixture
def parametros():
    return baker.make(
        'Parametros',
        permite_saldo_conta_negativo=True,
        fique_de_olho='',
        fique_de_olho_relatorio_dre='',
        tempo_aguardar_conclusao_pc=1,
        quantidade_tentativas_concluir_pc=3,
        periodo_de_tempo_tentativas_concluir_pc=120,
        texto_pagina_suporte_dre='Teste DRE',
        texto_pagina_suporte_sme='Teste SME',
        texto_pagina_valores_reprogramados_ue='Teste UE',
        texto_pagina_valores_reprogramados_dre='Teste DRE'
    )


@pytest.fixture
def parametro_fique_de_olho_pc():
    return baker.make(
        'ParametroFiqueDeOlhoPc',
        fique_de_olho='',
    )


@pytest.fixture
def parametro_fique_de_olho_pc_texto_abc():
    return baker.make(
        'ParametroFiqueDeOlhoPc',
        fique_de_olho='abc',
    )


@pytest.fixture
def parametros_aceita_saldo_negativo_em_conta():
    return baker.make(
        'Parametros',
        permite_saldo_conta_negativo=True
    )


@pytest.fixture
def parametros_nao_aceita_saldo_negativo_em_conta():
    return baker.make(
        'Parametros',
        permite_saldo_conta_negativo=False
    )


@pytest.fixture
def parametros_tempo_nao_conferido_10_dias():
    return baker.make(
        'Parametros',
        tempo_notificar_nao_demonstrados=10
    )


@pytest.fixture
def parametros_tempo_nao_conferido_60_dias():
    return baker.make(
        'Parametros',
        tempo_notificar_nao_demonstrados=60
    )


@pytest.fixture
def ata_2020_1_cheque_aprovada(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'Ata',
        arquivo_pdf=None,
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        periodo=prestacao_conta_2020_1_conciliada.periodo,
        associacao=prestacao_conta_2020_1_conciliada.associacao,
        tipo_ata='APRESENTACAO',
        tipo_reuniao='ORDINARIA',
        convocacao='PRIMEIRA',
        status_geracao_pdf='NAO_GERADO',
        data_reuniao=date(2020, 7, 1),
        local_reuniao='Escola Teste',
        presidente_reuniao='José',
        cargo_presidente_reuniao='Presidente',
        secretario_reuniao='Ana',
        cargo_secretaria_reuniao='Secretária',
        comentarios='Teste',
        parecer_conselho='APROVADA',
    )


@pytest.fixture
def presente_ata_membro(ata_2020_1_cheque_aprovada):
    return baker.make(
        'Participante',
        ata=ata_2020_1_cheque_aprovada,
        identificacao="123",
        nome="membro",
        cargo="teste cargo",
        membro=True,
        conselho_fiscal=False
    )


@pytest.fixture
def membro_associacao_presidente_conselho_01(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='Arthur Nobrega Junior',
        associacao=associacao,
        cargo_associacao='PRESIDENTE_CONSELHO_FISCAL',
        cargo_educacao='Coordenador',
        representacao=RepresentacaoCargo.SERVIDOR.value,
        codigo_identificacao='967499',
        email='ollyverottoboni@gmail.com'
    )


@pytest.fixture
def presente_ata_membro_e_conselho_fiscal(ata_2020_1_cheque_aprovada):
    return baker.make(
        'Participante',
        ata=ata_2020_1_cheque_aprovada,
        identificacao="123",
        nome="membro",
        cargo="teste cargo",
        membro=True,
        conselho_fiscal=True
    )


@pytest.fixture
def presente_ata_nao_membro(ata_2020_1_cheque_aprovada):
    return baker.make(
        'Participante',
        ata=ata_2020_1_cheque_aprovada,
        identificacao="123",
        nome="membro",
        cargo="teste cargo",
        membro=False,
        conselho_fiscal=False
    )


@pytest.fixture
def ata_2020_1_retificacao(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'Ata',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        periodo=prestacao_conta_2020_1_conciliada.periodo,
        associacao=prestacao_conta_2020_1_conciliada.associacao,
        tipo_ata='RETIFICACAO',
        tipo_reuniao='ORDINARIA',
        convocacao='PRIMEIRA',
        data_reuniao=date(2020, 7, 1),
        local_reuniao='Escola Teste',
        presidente_reuniao='José',
        cargo_presidente_reuniao='Presidente',
        secretario_reuniao='Ana',
        cargo_secretaria_reuniao='Secretária',
        comentarios='Teste',
        parecer_conselho='APROVADA',
        retificacoes='Teste'
    )


@pytest.fixture
def ata_prestacao_conta_iniciada(prestacao_conta_iniciada):
    return baker.make(
        'Ata',
        prestacao_conta=prestacao_conta_iniciada,
        periodo=prestacao_conta_iniciada.periodo,
        associacao=prestacao_conta_iniciada.associacao,
        tipo_ata='APRESENTACAO',
        tipo_reuniao='ORDINARIA',
        convocacao='PRIMEIRA',
        data_reuniao=date(2020, 7, 1),
        local_reuniao='Escola Teste',
        presidente_reuniao='José',
        cargo_presidente_reuniao='Presidente',
        secretario_reuniao='Ana',
        cargo_secretaria_reuniao='Secretaria',
        comentarios='Teste',
        parecer_conselho='APROVADA',
        hora_reuniao=datetime.time(0, 0)
    )


@pytest.fixture
def ata_retificacao_prestacao_conta_iniciada(prestacao_conta_iniciada):
    return baker.make(
        'Ata',
        prestacao_conta=prestacao_conta_iniciada,
        periodo=prestacao_conta_iniciada.periodo,
        associacao=prestacao_conta_iniciada.associacao,
        tipo_ata='RETIFICACAO',
        tipo_reuniao='ORDINARIA',
        convocacao='PRIMEIRA',
        data_reuniao=date(2020, 7, 1),
        local_reuniao='Escola Teste',
        presidente_reuniao='José',
        cargo_presidente_reuniao='Presidente',
        secretario_reuniao='Ana',
        cargo_secretaria_reuniao='Secretaria',
        comentarios='Teste',
        parecer_conselho='APROVADA'
    )


@pytest.fixture
def membro_associacao(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='Arthur Nobrega',
        associacao=associacao,
        cargo_associacao=MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.value,
        cargo_educacao='Coordenador',
        representacao=RepresentacaoCargo.SERVIDOR.value,
        codigo_identificacao='567432',
        email='ollyverottoboni@gmail.com',
        cpf='148.712.970-04',
        telefone='11992137854',
        cep='04302000',
        bairro='Vila da Saúde',
        endereco='Rua Apotribu, 57 - apto 12'
    )


@pytest.fixture
def membro_associacao_presidente_conselho(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='Arthur Nobrega Junior',
        associacao=associacao,
        cargo_associacao=MembroEnum.PRESIDENTE_CONSELHO_FISCAL.value,
        cargo_educacao='Coordenador',
        representacao=RepresentacaoCargo.SERVIDOR.value,
        codigo_identificacao='967499',
        email='ollyverottoboni@gmail.com'
    )


@pytest.fixture
def membro_associacao_presidente_associacao(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='Arthur Nobrega Silva',
        associacao=associacao,
        cargo_associacao=MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.value,
        cargo_educacao='Coordenador',
        representacao=RepresentacaoCargo.SERVIDOR.value,
        codigo_identificacao='567411',
        email='ollyverottoboni@gmail.com'
    )


@pytest.fixture
def payload_membro_servidor(associacao):
    payload = {
        'nome': "Adriano Imperador",
        'associacao': str(associacao.uuid),
        'cargo_associacao': MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.name,
        'cargo_educacao': 'Coordenador',
        'representacao': RepresentacaoCargo.SERVIDOR.name,
        'codigo_identificacao': '567432',
        'telefone': '11992137854',
        'cep': '04302000',
        'bairro': 'Vila da Saúde',
        'endereco': 'Rua Apotribu, 57 - apto 12',
    }
    return payload


@pytest.fixture
def payload_membro_estudante(associacao):
    payload = {
        'nome': "Arthur Oliveira",
        'associacao': str(associacao.uuid),
        'cargo_associacao': MembroEnum.VOGAL_1.name,
        'cargo_educacao': '',
        'representacao': RepresentacaoCargo.ESTUDANTE.name,
        'codigo_identificacao': '567431'
    }
    return payload


@pytest.fixture
def payload_membro_pai_responsavel(associacao):
    payload = {
        'nome': "Lana Oliveira",
        'associacao': str(associacao.uuid),
        'cargo_associacao': MembroEnum.VOGAL_3.name,
        'cargo_educacao': '',
        'representacao': RepresentacaoCargo.PAI_RESPONSAVEL.name,
        'codigo_identificacao': ''
    }
    return payload


@pytest.fixture
def observacao(acao_associacao, prestacao_conta):
    return baker.make(
        'Observacao',
        prestacao_conta=prestacao_conta,
        acao_associacao=acao_associacao,
        texto="Uma bela observação."
    )


@pytest.fixture
def tag():
    return baker.make(
        'Tag',
        nome="COVID-19",
        status=StatusTag.INATIVO.name
    )


@pytest.fixture
def tag_ativa():
    return baker.make(
        'Tag',
        nome="COVID-19",
        status=StatusTag.ATIVO.name
    )


@pytest.fixture
def processo_associacao_123456_2019(associacao):
    return baker.make(
        'ProcessoAssociacao',
        associacao=associacao,
        numero_processo='123456',
        ano='2019'
    )


@pytest.fixture
def observacao_conciliacao(periodo, conta_associacao):
    return baker.make(
        'ObservacaoConciliacao',
        periodo=periodo,
        associacao=conta_associacao.associacao,
        conta_associacao=conta_associacao,
        texto="Uma bela observação.",
        data_extrato=date(2020, 7, 1),
        saldo_extrato=1000
    )


@pytest.fixture
def observacao_conciliacao_campos_nao_preenchidos(periodo_2020_1, conta_associacao):
    return baker.make(
        'ObservacaoConciliacao',
        periodo=periodo_2020_1,
        associacao=conta_associacao.associacao,
        conta_associacao=conta_associacao,
        texto="Observação com campos não preenchidos.",
    )


@pytest.fixture
def observacao_conciliacao_com_saldo_zero(periodo_2020_1, conta_associacao):
    return baker.make(
        'ObservacaoConciliacao',
        periodo=periodo_2020_1,
        associacao=conta_associacao.associacao,
        conta_associacao=conta_associacao,
        data_extrato=date(2020, 7, 1),
        saldo_extrato=0,
        texto="Observação com saldo zero."
    )


@pytest.fixture
def observacao_conciliacao_campos_nao_preenchidos_002(periodo_2020_1, conta_associacao_tipo_cheque):
    return baker.make(
        'ObservacaoConciliacao',
        periodo=periodo_2020_1,
        associacao=conta_associacao_tipo_cheque.associacao,
        conta_associacao=conta_associacao_tipo_cheque,
        texto="Observação com campos não preenchidos 002.",
    )


@pytest.fixture
def observacao_conciliacao_campos_preenchidos(periodo_2020_1, conta_associacao):
    return baker.make(
        'ObservacaoConciliacao',
        periodo=periodo_2020_1,
        associacao=conta_associacao.associacao,
        conta_associacao=conta_associacao,
        texto="Observação com campos não preenchidos.",
        data_extrato=date(2020, 7, 1),
        saldo_extrato=1000,
        comprovante_extrato=None
    )


@pytest.fixture
def devolucao_prestacao_conta_2020_1(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'DevolucaoPrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        data=date(2020, 7, 1),
        data_limite_ue=date(2020, 8, 1),
        data_retorno_ue=None
    )


@pytest.fixture
def devolucao_prestacao_conta_2019_2(prestacao_conta_devolvida):
    return baker.make(
        'DevolucaoPrestacaoConta',
        prestacao_conta=prestacao_conta_devolvida,
        data=date(2020, 7, 1),
        data_limite_ue=date(2020, 8, 1),
        data_retorno_ue=None
    )


@pytest.fixture
def analise_conta_prestacao_conta_2020_1_solicitar_envio_do_comprovante_do_saldo_da_conta(prestacao_conta_2020_1_conciliada, conta_associacao_cheque):
    return baker.make(
        'AnaliseContaPrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        conta_associacao=conta_associacao_cheque,
        data_extrato=date(2020, 7, 1),
        saldo_extrato=100.00,
        solicitar_envio_do_comprovante_do_saldo_da_conta=True,
        observacao_solicitar_envio_do_comprovante_do_saldo_da_conta='Observação de solicitação de envio de comprovante de saldo conta cheque',
    )


@pytest.fixture
def analise_conta_prestacao_conta_2020_1(prestacao_conta_2020_1_conciliada, conta_associacao_cheque):
    return baker.make(
        'AnaliseContaPrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        conta_associacao=conta_associacao_cheque,
        data_extrato=date(2020, 7, 1),
        saldo_extrato=100.00,
    )


@pytest.fixture
def analise_conta_prestacao_conta_2019_2(prestacao_conta_devolvida, conta_associacao_cheque, analise_prestacao_conta_2019_2):
    return baker.make(
        'AnaliseContaPrestacaoConta',
        prestacao_conta=prestacao_conta_devolvida,
        conta_associacao=conta_associacao_cheque,
        data_extrato=date(2020, 7, 1),
        saldo_extrato=100.00,
        analise_prestacao_conta=analise_prestacao_conta_2019_2
    )


@pytest.fixture
def previsao_repasse_sme(periodo, associacao, conta_associacao):
    return baker.make(
        'PrevisaoRepasseSme',
        periodo=periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        valor_custeio=10000.50,
        valor_capital=10000.50,
        valor_livre=10000.50,
    )


@pytest.fixture
def analise_prestacao_conta_2020_1(prestacao_conta_2020_1_conciliada, devolucao_prestacao_conta_2020_1):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        devolucao_prestacao_conta=devolucao_prestacao_conta_2020_1
    )


@pytest.fixture
def analise_prestacao_conta_2020_1_2(prestacao_conta_2020_1_conciliada, devolucao_prestacao_conta_2020_1):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        devolucao_prestacao_conta=devolucao_prestacao_conta_2020_1
    )


@pytest.fixture
def analise_prestacao_conta_2019_2(prestacao_conta_devolvida, devolucao_prestacao_conta_2019_2):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=prestacao_conta_devolvida,
        devolucao_prestacao_conta=devolucao_prestacao_conta_2019_2
    )


@pytest.fixture
def analise_lancamento_receita_prestacao_conta_2020_1(analise_prestacao_conta_2020_1, receita_no_periodo_2020_1):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_lancamento='CREDITO',
        receita=receita_no_periodo_2020_1,
        resultado='CORRETO'
    )


@pytest.fixture
def analise_lancamento_receita_prestacao_conta_2020_1_com_justificativa(analise_prestacao_conta_2020_1, receita_no_periodo_2020_1):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_lancamento='CREDITO',
        receita=receita_no_periodo_2020_1,
        resultado='CORRETO',
    )


@pytest.fixture
def despesa_no_periodo_2020_1(prestacao_conta_2020_1_conciliada, tipo_documento, tipo_transacao, periodo_2020_1):
    return baker.make(
        'Despesa',
        associacao=prestacao_conta_2020_1_conciliada.associacao,
        numero_documento='123456',
        data_documento=periodo_2020_1.data_inicio_realizacao_despesas + timedelta(days=3),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=periodo_2020_1.data_inicio_realizacao_despesas + timedelta(days=3),
        valor_total=310.00,
        valor_recursos_proprios=0,
    )


@pytest.fixture
def analise_lancamento_despesa_prestacao_conta_2020_1(analise_prestacao_conta_2020_1, despesa_no_periodo_2020_1):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_lancamento='GASTO',
        despesa=despesa_no_periodo_2020_1,
        resultado='AJUSTE'
    )


@pytest.fixture
def tipo_devolucao_ao_tesouro_teste():
    return baker.make('TipoDevolucaoAoTesouro', nome='Devolução teste')


@pytest.fixture
def devolucao_ao_tesouro_parcial(prestacao_conta_2020_1_conciliada, tipo_devolucao_ao_tesouro_teste, despesa_no_periodo_2020_1):
    return baker.make(
        'DevolucaoAoTesouro',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        tipo=tipo_devolucao_ao_tesouro_teste,
        data=date(2020, 7, 1),
        despesa=despesa_no_periodo_2020_1,
        devolucao_total=False,
        valor=100.00,
        motivo='teste',
        visao_criacao='DRE'
    )


@pytest.fixture
def tipo_acerto_lancamento_devolucao():
    return baker.make('TipoAcertoLancamento', nome='Devolução', categoria='DEVOLUCAO')


@pytest.fixture
def solicitacao_acerto_lancamento_devolucao(
    analise_lancamento_receita_prestacao_conta_2020_1,
    tipo_acerto_lancamento_devolucao,

):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_receita_prestacao_conta_2020_1,
        tipo_acerto=tipo_acerto_lancamento_devolucao,
        devolucao_ao_tesouro=None,
        detalhamento="teste"
    )


@pytest.fixture
def solicitacao_devolucao_ao_tesouro(
    solicitacao_acerto_lancamento_devolucao,
    tipo_devolucao_ao_tesouro_teste,
):
    return baker.make(
        'SolicitacaoDevolucaoAoTesouro',
        solicitacao_acerto_lancamento=solicitacao_acerto_lancamento_devolucao,
        tipo=tipo_devolucao_ao_tesouro_teste,
        devolucao_total=False,
        valor=100.00,
        motivo='teste',
    )


@pytest.fixture
def tipo_acerto_edicao_de_lancamento():
    return baker.make('TipoAcertoLancamento', nome='Edição de Lançamento', categoria='EDICAO_LANCAMENTO')


@pytest.fixture
def solicitacao_acerto_edicao_lancamento(
    analise_lancamento_receita_prestacao_conta_2020_1,
    tipo_acerto_edicao_de_lancamento,
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_receita_prestacao_conta_2020_1,
        tipo_acerto=tipo_acerto_edicao_de_lancamento,
        detalhamento="teste"
    )


@pytest.fixture
def tipo_acerto_exclusao_de_lancamento():
    return baker.make('TipoAcertoLancamento', nome='Exclusão de Lançamento', categoria='EXCLUSAO_LANCAMENTO')


@pytest.fixture
def solicitacao_acerto_exclusao_lancamento(
    analise_lancamento_receita_prestacao_conta_2020_1,
    tipo_acerto_exclusao_de_lancamento,
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_receita_prestacao_conta_2020_1,
        tipo_acerto=tipo_acerto_exclusao_de_lancamento,
        detalhamento="teste"
    )


@pytest.fixture
def tipo_acerto_requer_ajuste_externo():
    return baker.make('TipoAcertoLancamento', nome='Requer Ajuste Externo', categoria='AJUSTES_EXTERNOS')


@pytest.fixture
def solicitacao_acerto_requer_ajuste_externo(
    analise_lancamento_receita_requer_ajustes_externos,
    tipo_acerto_requer_ajuste_externo,
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_receita_requer_ajustes_externos,
        tipo_acerto=tipo_acerto_requer_ajuste_externo,
        detalhamento="teste"
    )


@pytest.fixture
def tipo_acerto_esclarecimento():
    return baker.make('TipoAcertoLancamento', nome='Requer Esclarecimento', categoria='SOLICITACAO_ESCLARECIMENTO')


@pytest.fixture
def solicitacao_acerto_esclarecimento(
    analise_lancamento_receita_prestacao_conta_2020_1,
    tipo_acerto_esclarecimento,
):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_receita_prestacao_conta_2020_1,
        tipo_acerto=tipo_acerto_esclarecimento,
        detalhamento="teste"
    )


@pytest.fixture
def analise_lancamento_receita_requer_ajustes_externos(
    analise_prestacao_conta_2020_1,
    receita_no_periodo_2020_1
):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_lancamento='CREDITO',
        receita=receita_no_periodo_2020_1,
        resultado='AJUSTE'
    )


@pytest.fixture
def tipo_documento_prestacao_conta_ata():
    return baker.make('TipoDocumentoPrestacaoConta', nome='Cópia da ata da prestação de contas')


@pytest.fixture
def analise_documento_prestacao_conta_2020_1_ata_correta(
    analise_prestacao_conta_2020_1,
    tipo_documento_prestacao_conta_ata,
    conta_associacao_cartao,
    receita_100_no_periodo,
    despesa_no_periodo,
):
    return baker.make(
        'AnaliseDocumentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_documento_prestacao_conta=tipo_documento_prestacao_conta_ata,
        conta_associacao=conta_associacao_cartao,
        resultado='CORRETO',
    )


@pytest.fixture
def analise_documento_prestacao_conta_com_justificativa_2020_1_ata_correta(
    analise_prestacao_conta_2020_1,
    tipo_documento_prestacao_conta_ata,
    conta_associacao_cartao
):
    return baker.make(
        'AnaliseDocumentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_documento_prestacao_conta=tipo_documento_prestacao_conta_ata,
        conta_associacao=conta_associacao_cartao,
        resultado='CORRETO',
    )


@pytest.fixture
def analise_documento_prestacao_conta_2020_1_ata_ajuste(
    analise_prestacao_conta_2020_1,
    tipo_documento_prestacao_conta_ata,
    conta_associacao_cartao
):
    return baker.make(
        'AnaliseDocumentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_documento_prestacao_conta=tipo_documento_prestacao_conta_ata,
        conta_associacao=conta_associacao_cartao,
        resultado='AJUSTE'
    )


@pytest.fixture
def tipo_acerto_documento_assinatura(tipo_documento_prestacao_conta_ata):
    tipo_acerto = baker.make('TipoAcertoDocumento', nome='Enviar com assinatura')
    tipo_acerto.tipos_documento_prestacao.add(tipo_documento_prestacao_conta_ata)
    tipo_acerto.save()
    return tipo_acerto


@pytest.fixture
def tipo_acerto_documento_requer_esclarecimento(tipo_documento_prestacao_conta_ata):
    tipo_acerto = baker.make(
        'TipoAcertoDocumento',
        nome='Esclarecimento',
        categoria=TipoAcertoDocumento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO
    )
    tipo_acerto.tipos_documento_prestacao.add(tipo_documento_prestacao_conta_ata)
    tipo_acerto.save()
    return tipo_acerto


@pytest.fixture
def tipo_acerto_documento_requer_inclusao_credito(tipo_documento_prestacao_conta_ata):
    tipo_acerto = baker.make(
        'TipoAcertoDocumento',
        nome='Esclarecimento',
        categoria=TipoAcertoDocumento.CATEGORIA_INCLUSAO_CREDITO
    )
    tipo_acerto.tipos_documento_prestacao.add(tipo_documento_prestacao_conta_ata)
    tipo_acerto.save()
    return tipo_acerto


@pytest.fixture
def tipo_acerto_documento_requer_inclusao_despesa(tipo_documento_prestacao_conta_ata):
    tipo_acerto = baker.make(
        'TipoAcertoDocumento',
        nome='Esclarecimento',
        categoria=TipoAcertoDocumento.CATEGORIA_INCLUSAO_GASTO
    )
    tipo_acerto.tipos_documento_prestacao.add(tipo_documento_prestacao_conta_ata)
    tipo_acerto.save()
    return tipo_acerto


@pytest.fixture
def tipo_acerto_documento_requer_ajuste_externo(tipo_documento_prestacao_conta_ata):
    tipo_acerto = baker.make(
        'TipoAcertoDocumento',
        nome='Esclarecimento',
        categoria=TipoAcertoDocumento.CATEGORIA_AJUSTES_EXTERNOS
    )
    tipo_acerto.tipos_documento_prestacao.add(tipo_documento_prestacao_conta_ata)
    tipo_acerto.save()
    return tipo_acerto


@pytest.fixture
def solicitacao_acerto_documento_ata(
    analise_documento_prestacao_conta_2020_1_ata_ajuste,
    tipo_acerto_documento_assinatura,
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_prestacao_conta_2020_1_ata_ajuste,
        tipo_acerto=tipo_acerto_documento_assinatura,
        detalhamento="Detalhamento motivo acerto no documento",
    )


# Testes Action Repasses Pendentes
@pytest.fixture
def repasse(associacao, conta_associacao, acao_associacao, periodo):
    return baker.make(
        'Repasse',
        associacao=associacao,
        periodo=periodo,
        valor_custeio=1000.40,
        valor_capital=1000.28,
        valor_livre=0,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        status='PENDENTE'
    )


@pytest.fixture
def solicitacao_acerto_documento_ata_esclarecimentos(
    analise_documento_prestacao_conta_2020_1_ata_ajuste,
    tipo_acerto_documento_requer_esclarecimento,
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_prestacao_conta_2020_1_ata_ajuste,
        tipo_acerto=tipo_acerto_documento_requer_esclarecimento,
        detalhamento="Detalhamento motivo acerto no documento",
    )


@pytest.fixture
def solicitacao_acerto_documento_ata_inclusao_credito(
    analise_documento_prestacao_conta_2020_1_ata_ajuste,
    tipo_acerto_documento_requer_inclusao_credito
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_prestacao_conta_2020_1_ata_ajuste,
        tipo_acerto=tipo_acerto_documento_requer_inclusao_credito,
        detalhamento="Detalhamento motivo acerto no documento",
    )


@pytest.fixture
def solicitacao_acerto_documento_ata_inclusao_despesa(
    analise_documento_prestacao_conta_2020_1_ata_ajuste,
    tipo_acerto_documento_requer_inclusao_despesa
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_prestacao_conta_2020_1_ata_ajuste,
        tipo_acerto=tipo_acerto_documento_requer_inclusao_despesa,
        detalhamento="Detalhamento motivo acerto no documento",
    )


@pytest.fixture
def solicitacao_acerto_documento_ata_ajuste_externo(
    analise_documento_prestacao_conta_2020_1_ata_ajuste,
    tipo_acerto_documento_requer_ajuste_externo
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_prestacao_conta_2020_1_ata_ajuste,
        tipo_acerto=tipo_acerto_documento_requer_ajuste_externo,
        detalhamento="Detalhamento motivo acerto no documento",
    )


@pytest.fixture
def solicitacao_acerto_lancamento_status_realizado(
    analise_lancamento_receita_prestacao_conta_2020_1,
    tipo_acerto_lancamento_devolucao,

):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_receita_prestacao_conta_2020_1,
        tipo_acerto=tipo_acerto_lancamento_devolucao,
        devolucao_ao_tesouro=None,
        detalhamento="teste",
        status_realizacao="REALIZADO"
    )


@pytest.fixture
def solicitacao_acerto_lancamento_status_realizado_02(
    analise_lancamento_receita_prestacao_conta_2020_1,
    tipo_acerto_lancamento_devolucao,

):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_receita_prestacao_conta_2020_1,
        tipo_acerto=tipo_acerto_lancamento_devolucao,
        devolucao_ao_tesouro=None,
        detalhamento="teste",
        status_realizacao="REALIZADO"
    )


@pytest.fixture
def solicitacao_acerto_lancamento_status_justificado(
    analise_lancamento_receita_prestacao_conta_2020_1,
    tipo_acerto_lancamento_devolucao,

):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_receita_prestacao_conta_2020_1,
        tipo_acerto=tipo_acerto_lancamento_devolucao,
        devolucao_ao_tesouro=None,
        detalhamento="teste",
        status_realizacao="JUSTIFICADO"
    )


@pytest.fixture
def solicitacao_acerto_lancamento_status_justificado_02(
    analise_lancamento_receita_prestacao_conta_2020_1,
    tipo_acerto_lancamento_devolucao,

):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_receita_prestacao_conta_2020_1,
        tipo_acerto=tipo_acerto_lancamento_devolucao,
        devolucao_ao_tesouro=None,
        detalhamento="teste",
        status_realizacao="JUSTIFICADO"
    )


@pytest.fixture
def solicitacao_acerto_lancamento_status_nao_realizado(
    analise_lancamento_receita_prestacao_conta_2020_1,
    tipo_acerto_lancamento_devolucao,

):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_receita_prestacao_conta_2020_1,
        tipo_acerto=tipo_acerto_lancamento_devolucao,
        devolucao_ao_tesouro=None,
        detalhamento="teste",
        status_realizacao="PENDENTE"
    )


@pytest.fixture
def solicitacao_acerto_lancamento_status_nao_realizado_02(
    analise_lancamento_receita_prestacao_conta_2020_1,
    tipo_acerto_lancamento_devolucao,

):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_receita_prestacao_conta_2020_1,
        tipo_acerto=tipo_acerto_lancamento_devolucao,
        devolucao_ao_tesouro=None,
        detalhamento="teste",
        status_realizacao="PENDENTE"
    )


@pytest.fixture
def solicitacao_acerto_documento_status_realizado(
    analise_documento_prestacao_conta_2020_1_ata_ajuste,
    tipo_acerto_documento_requer_inclusao_despesa
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_prestacao_conta_2020_1_ata_ajuste,
        tipo_acerto=tipo_acerto_documento_requer_inclusao_despesa,
        detalhamento="Detalhamento motivo acerto no documento",
        status_realizacao="REALIZADO"
    )


@pytest.fixture
def solicitacao_acerto_documento_status_realizado_02(
    analise_documento_prestacao_conta_2020_1_ata_ajuste,
    tipo_acerto_documento_requer_inclusao_despesa
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_prestacao_conta_2020_1_ata_ajuste,
        tipo_acerto=tipo_acerto_documento_requer_inclusao_despesa,
        detalhamento="Detalhamento motivo acerto no documento",
        status_realizacao="REALIZADO"
    )


@pytest.fixture
def solicitacao_acerto_documento_status_justificado(
    analise_documento_prestacao_conta_2020_1_ata_ajuste,
    tipo_acerto_documento_requer_inclusao_despesa
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_prestacao_conta_2020_1_ata_ajuste,
        tipo_acerto=tipo_acerto_documento_requer_inclusao_despesa,
        detalhamento="Detalhamento motivo acerto no documento",
        status_realizacao="JUSTIFICADO"
    )


@pytest.fixture
def solicitacao_acerto_documento_status_justificado_02(
    analise_documento_prestacao_conta_2020_1_ata_ajuste,
    tipo_acerto_documento_requer_inclusao_despesa
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_prestacao_conta_2020_1_ata_ajuste,
        tipo_acerto=tipo_acerto_documento_requer_inclusao_despesa,
        detalhamento="Detalhamento motivo acerto no documento",
        status_realizacao="JUSTIFICADO"
    )


@pytest.fixture
def permissoes_dadosdiretoria_dre():
    from django.contrib.auth.models import Permission

    permissoes = [
        Permission.objects.filter(codename='dre_leitura').first(),
        Permission.objects.filter(codename='dre_gravacao').first()
    ]

    return permissoes


@pytest.fixture
def grupo_dados_diretoria_dre(permissoes_dadosdiretoria_dre):
    from sme_ptrf_apps.users.models import Grupo

    g = Grupo.objects.create(name="dados_diretoria_dre")
    g.permissions.add(*permissoes_dadosdiretoria_dre)
    return g


@pytest.fixture
def usuario_permissao_atribuicao(
        unidade,
        grupo_dados_diretoria_dre):

    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.groups.add(grupo_dados_diretoria_dre)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_dre(client, usuario_permissao_atribuicao):
    from unittest.mock import patch

    from rest_framework.test import APIClient
    api_client = APIClient()
    with patch('sme_ptrf_apps.users.api.views.login.AutenticacaoService.autentica') as mock_post:
        data = {
            "nome": "LUCIA HELENA",
            "cpf": "62085077072",
            "email": "luh@gmail.com",
            "login": "7210418"
        }
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = data
        resp = api_client.post('/api/login', {'login': usuario_permissao_atribuicao.username,
                                              'senha': usuario_permissao_atribuicao.password}, format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client


@pytest.fixture
def solicitacao_acerto_documento_status_nao_realizado(
    analise_documento_prestacao_conta_2020_1_ata_ajuste,
    tipo_acerto_documento_requer_inclusao_despesa
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_prestacao_conta_2020_1_ata_ajuste,
        tipo_acerto=tipo_acerto_documento_requer_inclusao_despesa,
        detalhamento="Detalhamento motivo acerto no documento",
        status_realizacao="PENDENTE"
    )


@pytest.fixture
def solicitacao_acerto_documento_status_nao_realizado_02(
    analise_documento_prestacao_conta_2020_1_ata_ajuste,
    tipo_acerto_documento_requer_inclusao_despesa
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_prestacao_conta_2020_1_ata_ajuste,
        tipo_acerto=tipo_acerto_documento_requer_inclusao_despesa,
        detalhamento="Detalhamento motivo acerto no documento",
        status_realizacao="PENDENTE"
    )


# Edição de Informação

@pytest.fixture
def tipo_documento_prestacao_conta_demonstrativo_financeiro():
    return baker.make(
        'TipoDocumentoPrestacaoConta',
        nome='Tipo Documento Demonstrativo Financeiro'
    )


@pytest.fixture
def tipo_acerto_documento_edicao_informacao(tipo_documento_prestacao_conta_demonstrativo_financeiro):
    tipo_acerto = baker.make(
        'TipoAcertoDocumento',
        nome='Edição de Informação',
        categoria=TipoAcertoDocumento.CATEGORIA_EDICAO_INFORMACAO
    )
    tipo_acerto.tipos_documento_prestacao.add(tipo_documento_prestacao_conta_demonstrativo_financeiro)
    tipo_acerto.save()
    return tipo_acerto


@pytest.fixture
def solicitacao_acerto_documento_edicao_informacao(
    analise_documento_prestacao_conta_demonstativo_financeiro_edicao_informacao,
    tipo_acerto_documento_edicao_informacao,
):
    return baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_prestacao_conta_demonstativo_financeiro_edicao_informacao,
        tipo_acerto=tipo_acerto_documento_edicao_informacao,
        detalhamento="Detalhamento motivo acerto no documento",
    )


@pytest.fixture
def analise_documento_prestacao_conta_demonstativo_financeiro_edicao_informacao(
    analise_prestacao_conta_2020_1,
    tipo_documento_prestacao_conta_demonstrativo_financeiro,
    conta_associacao_cartao
):
    return baker.make(
        'AnaliseDocumentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_documento_prestacao_conta=tipo_documento_prestacao_conta_demonstrativo_financeiro,
        conta_associacao=conta_associacao_cartao,
        resultado='AJUSTE'
    )


@pytest.fixture
def permissoes_sme():
    from django.contrib.auth.models import Permission
    permissoes = [
        Permission.objects.filter(codename='sme_leitura').first(),
        Permission.objects.filter(codename='sme_gravacao').first()
    ]

    return permissoes


@pytest.fixture
def grupo_sme(permissoes_sme):
    from sme_ptrf_apps.users.models import Grupo
    g = Grupo.objects.create(name="sme")
    g.permissions.add(*permissoes_sme)
    return g


@pytest.fixture
def usuario_permissao_sme(unidade, grupo_sme):
    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '1235678'
    email = 'usuario.sme@gmail.com'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.groups.add(grupo_sme)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_sme(client, usuario_permissao_sme):
    api_client = APIClient()
    api_client.force_authenticate(user=usuario_permissao_sme)
    return api_client


@pytest.fixture
def task_celery_criada(periodo_2020_1, associacao):
    return baker.make(
        'TaskCelery',
        nome_task='concluir_prestacao_de_contas_async',
        associacao=associacao,
        periodo=periodo_2020_1
    )


@pytest.fixture
def task_celery_criada_2(periodo_2020_1, associacao):
    return baker.make(
        'TaskCelery',
        nome_task='concluir_prestacao_de_contas_async',
        associacao=associacao,
        periodo=periodo_2020_1
    )
