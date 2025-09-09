import json
import pytest

from datetime import date, time

from model_bakery import baker
from rest_framework import status

from ...models import PrestacaoConta, Ata
from sme_ptrf_apps.core.models.proccessos_associacao import ProcessoAssociacao

pytestmark = pytest.mark.django_db


@pytest.fixture
def prestacao_conta_nao_recebida(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        status=PrestacaoConta.STATUS_NAO_RECEBIDA
    )


@pytest.fixture
def ata(prestacao_conta_nao_recebida):
    return baker.make(
        'Ata',
        prestacao_conta=prestacao_conta_nao_recebida,
        periodo=prestacao_conta_nao_recebida.periodo,
        associacao=prestacao_conta_nao_recebida.associacao,
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
        hora_reuniao=time(0, 0),
        status_geracao_pdf=Ata.STATUS_CONCLUIDO
    )


@pytest.fixture
def ata_retificacao(ata_factory, prestacao_conta_nao_recebida):
    return ata_factory.create(
        prestacao_conta=prestacao_conta_nao_recebida,
        tipo_ata='RETIFICACAO',
        periodo=prestacao_conta_nao_recebida.periodo,
        status_geracao_pdf=Ata.STATUS_CONCLUIDO
    )


def test_api_recebe_prestacao_conta(jwt_authenticated_client_a, prestacao_conta_nao_recebida, ata, ata_retificacao):

    payload = {
        'data_recebimento': '2020-10-01',
        'processo_sei': '1234.5678/9101112-1',
        'acao_processo_sei': None
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_nao_recebida.uuid}/receber/'

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    prestacao_atualizada = PrestacaoConta.by_uuid(prestacao_conta_nao_recebida.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_RECEBIDA, 'Status não atualizado para RECEBIDA.'
    assert prestacao_atualizada.data_recebimento == date(2020, 10, 1), 'Data de recebimento não atualizada.'


def test_api_recebe_prestacao_conta_exige_data_recebimento(jwt_authenticated_client_a, prestacao_conta_nao_recebida, ata, ata_retificacao):

    url = f'/api/prestacoes-contas/{prestacao_conta_nao_recebida.uuid}/receber/'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{prestacao_conta_nao_recebida.uuid}',
        'erro': 'falta_de_informacoes',
        'operacao': 'receber',
        'mensagem': 'Faltou informar a data de recebimento da Prestação de Contas.'
    }

    assert result == result_esperado, "Deveria ter retornado erro falta_de_informacoes."

    prestacao_atualizada = PrestacaoConta.by_uuid(prestacao_conta_nao_recebida.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_NAO_RECEBIDA, 'Status não deveria ter sido alterado.'


@pytest.fixture
def prestacao_conta_em_analise(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        status=PrestacaoConta.STATUS_EM_ANALISE
    )


def test_api_recebe_prestacao_conta_nao_pode_aceitar_status_diferente_de_nao_recebida(jwt_authenticated_client_a,
                                                                                      prestacao_conta_em_analise):
    payload = {
        'data_recebimento': '2020-10-01',
        'processo_sei': '1234.5678/9101112-1',
        'acao_processo_sei': None
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_em_analise.uuid}/receber/'

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    result_esperado = {
        'uuid': f'{prestacao_conta_em_analise.uuid}',
        'erro': 'status_nao_permite_operacao',
        'status': PrestacaoConta.STATUS_EM_ANALISE,
        'operacao': 'receber',
        'mensagem': 'Você não pode receber uma prestação de contas com status diferente de NAO_RECEBIDA.'
    }

    assert result == result_esperado, "Deveria ter retornado erro status_nao_permite_operacao."

    prestacao_atualizada = PrestacaoConta.by_uuid(prestacao_conta_em_analise.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_EM_ANALISE, 'Status não deveria ter sido alterado.'


def test_api_recebe_prestacao_conta_exige_processo_sei(jwt_authenticated_client_a, prestacao_conta_nao_recebida):
    payload = {
        'data_recebimento': '2020-10-01',
        'acao_processo_sei': None
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_nao_recebida.uuid}/receber/'

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    resultado_esperado = {
        'uuid': f'{prestacao_conta_nao_recebida.uuid}',
        'erro': 'falta_de_informacoes_processo_sei',
        'operacao': 'receber',
        'mensagem': 'Faltou informar o processo SEI de recebimento da Prestação de Contas.'
    }

    assert result == resultado_esperado, "Deveria ter retornado erro falta_de_informacoes_processo_sei."
    prestacao_atualizada = PrestacaoConta.by_uuid(prestacao_conta_nao_recebida.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_NAO_RECEBIDA, 'Status não deveria ter sido alterado.'


def test_api_recebe_prestacao_conta_e_edita_processo_sei(jwt_authenticated_client_a, prestacao_conta_nao_recebida, ata, ata_retificacao, processo_associacao_factory):
    ano = prestacao_conta_nao_recebida.periodo.referencia[0:4]
    associacao = prestacao_conta_nao_recebida.associacao
    numero_processo = '1111.1111/1111111-1'
    processo_associacao = processo_associacao_factory.create(
        associacao=associacao, ano=ano, numero_processo=numero_processo)

    payload = {
        'data_recebimento': '2020-10-01',
        'processo_sei': '2222.2222/2222111-1',
        'acao_processo_sei': 'editar'
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_nao_recebida.uuid}/receber/'

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    processo_editado = ProcessoAssociacao.objects.get(uuid=processo_associacao.uuid)

    assert processo_editado.numero_processo == '2222.2222/2222111-1'


def test_api_recebe_prestacao_conta_e_inclui_novo_processo_sei(jwt_authenticated_client_a, prestacao_conta_nao_recebida, ata, ata_retificacao, processo_associacao_factory):
    ano = prestacao_conta_nao_recebida.periodo.referencia[0:4]
    associacao = prestacao_conta_nao_recebida.associacao
    numero_processo = '1111.1111/1111111-1'
    processo_associacao = processo_associacao_factory.create(
        associacao=associacao, ano=ano, numero_processo=numero_processo)

    processos_antes_de_receber_pc = ProcessoAssociacao.objects.all()
    assert processos_antes_de_receber_pc.count() == 1

    payload = {
        'data_recebimento': '2020-10-01',
        'processo_sei': '2222.2222/2222111-1',
        'acao_processo_sei': 'incluir'
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_nao_recebida.uuid}/receber/'

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    processos_depois_de_receber_pc = ProcessoAssociacao.objects.all()
    assert processos_depois_de_receber_pc.count() == 2


def test_api_recebe_prestacao_conta_e_mantem_processo_sei(jwt_authenticated_client_a, prestacao_conta_nao_recebida, ata, ata_retificacao, processo_associacao_factory):
    ano = prestacao_conta_nao_recebida.periodo.referencia[0:4]
    associacao = prestacao_conta_nao_recebida.associacao
    numero_processo = '1111.1111/1111111-1'
    processo_associacao = processo_associacao_factory.create(
        associacao=associacao, ano=ano, numero_processo=numero_processo)

    processos_antes_de_receber_pc = ProcessoAssociacao.objects.all()
    assert processos_antes_de_receber_pc.count() == 1

    payload = {
        'data_recebimento': '2020-10-01',
        'processo_sei': '2222.2222/2222111-1',
        'acao_processo_sei': None
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_nao_recebida.uuid}/receber/'

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    processo_nao_editado = ProcessoAssociacao.objects.get(uuid=processo_associacao.uuid)

    assert processo_nao_editado.numero_processo == '1111.1111/1111111-1'


def test_api_recebe_prestacao_conta_exige_ata_apresentacao_gerada(jwt_authenticated_client_a, prestacao_conta_nao_recebida):
    payload = {
        'data_recebimento': '2020-10-01',
        'processo_sei': '2222.2222/2222111-1',
        'acao_processo_sei': None
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_nao_recebida.uuid}/receber/'

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    resultado_esperado = {
        'uuid': f'{prestacao_conta_nao_recebida.uuid}',
        'erro': 'pendencias',
        'operacao': 'receber',
        'mensagem': 'É necessário gerar ata de apresentação para realizar o recebimento.'
    }

    assert result == resultado_esperado
    prestacao_atualizada = PrestacaoConta.by_uuid(prestacao_conta_nao_recebida.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_NAO_RECEBIDA, 'Status não deveria ter sido alterado.'


def test_api_recebe_prestacao_conta_exige_ata_retificacao_gerada(jwt_authenticated_client_a, ata, prestacao_conta_nao_recebida):
    payload = {
        'data_recebimento': '2020-10-01',
        'processo_sei': '2222.2222/2222111-1',
        'acao_processo_sei': None
    }

    url = f'/api/prestacoes-contas/{prestacao_conta_nao_recebida.uuid}/receber/'

    response = jwt_authenticated_client_a.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    resultado_esperado = {
        'uuid': f'{prestacao_conta_nao_recebida.uuid}',
        'erro': 'pendencias',
        'operacao': 'receber',
        'mensagem': 'É necessário gerar ata de retificação para realizar o recebimento.'
    }

    assert result == resultado_esperado
    prestacao_atualizada = PrestacaoConta.by_uuid(prestacao_conta_nao_recebida.uuid)
    assert prestacao_atualizada.status == PrestacaoConta.STATUS_NAO_RECEBIDA, 'Status não deveria ter sido alterado.'
