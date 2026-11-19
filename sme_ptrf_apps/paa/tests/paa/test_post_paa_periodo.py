import json
from datetime import date

import pytest
from freezegun import freeze_time
from rest_framework import status

from sme_ptrf_apps.paa import constantes
from sme_ptrf_apps.paa.models import DocumentoPaa, Paa

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def parametro_outubro(parametro_paa_factory):
    return parametro_paa_factory.create(mes_elaboracao_paa=10)


@pytest.fixture
def periodo_vigente(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia='2026', data_inicial=date(2026, 5, 1), data_final=date(2027, 4, 30))


@pytest.fixture
def periodo_proxima_vigencia(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia='2027', data_inicial=date(2027, 8, 1), data_final=date(2027, 12, 31))


def _post(cliente, associacao, periodo=None):
    payload = {'associacao': str(associacao.uuid)}
    if periodo is not None:
        payload['periodo'] = str(periodo)
    return cliente.post('/api/paa/', content_type='application/json', data=json.dumps(payload))


def _vigente_com_plano_gerado(paa_factory, documento_paa_factory, associacao, periodo_vigente):
    paa = paa_factory.create(periodo_paa=periodo_vigente, associacao=associacao)
    documento_paa_factory.create(
        paa=paa, versao=DocumentoPaa.VersaoChoices.FINAL,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO, retificacao=False)
    return paa


@freeze_time('2026-10-28')
def test_cria_no_periodo_vigente_informado(
        jwt_authenticated_client_sme, flag_paa, flag_paa_proxima_vigencia, associacao,
        periodo_vigente, periodo_proxima_vigencia):
    response = _post(jwt_authenticated_client_sme, associacao, periodo_vigente.uuid)

    assert response.status_code == status.HTTP_201_CREATED, response.content
    assert Paa.objects.get().periodo_paa == periodo_vigente


@freeze_time('2026-10-28')
def test_cria_o_paa_da_proxima_vigencia_com_vigente_gerado_parcialmente(
        jwt_authenticated_client_sme, flag_paa, flag_paa_proxima_vigencia, paa_factory, documento_paa_factory,
        associacao, periodo_vigente, periodo_proxima_vigencia):
    paa_vigente = _vigente_com_plano_gerado(paa_factory, documento_paa_factory, associacao, periodo_vigente)

    response = _post(jwt_authenticated_client_sme, associacao, periodo_proxima_vigencia.uuid)

    assert response.status_code == status.HTTP_201_CREATED, response.content
    assert Paa.objects.count() == 2
    proximo = Paa.objects.get(periodo_paa=periodo_proxima_vigencia)
    assert proximo.associacao == associacao
    assert proximo.status_em_elaboracao
    paa_vigente.refresh_from_db()
    assert paa_vigente.get_status_andamento() == 'GERADO_PARCIALMENTE'


@freeze_time('2026-10-28')
def test_com_a_flag_desligada_o_periodo_informado_e_ignorado(
        jwt_authenticated_client_sme, flag_paa, paa_factory, documento_paa_factory,
        associacao, periodo_vigente, periodo_proxima_vigencia):
    _vigente_com_plano_gerado(paa_factory, documento_paa_factory, associacao, periodo_vigente)

    response = _post(jwt_authenticated_client_sme, associacao, periodo_proxima_vigencia.uuid)

    # segue o fluxo legado: tenta criar no período vigente, onde o PAA já existe
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'non_field_errors': ['Já existe um PAA para a Associação informada.']}
    assert Paa.objects.count() == 1
    assert not Paa.objects.filter(periodo_paa=periodo_proxima_vigencia).exists()


@freeze_time('2026-10-28')
def test_com_a_flag_desligada_periodo_encerrado_informado_e_ignorado(
        jwt_authenticated_client_sme, flag_paa, associacao, periodo_vigente, periodo_paa_factory):
    encerrado = periodo_paa_factory.create(
        referencia='2025', data_inicial=date(2025, 1, 1), data_final=date(2025, 12, 31))

    response = _post(jwt_authenticated_client_sme, associacao, encerrado.uuid)

    assert response.status_code == status.HTTP_201_CREATED, response.content
    assert Paa.objects.get().periodo_paa == periodo_vigente


@freeze_time('2026-10-28')
def test_proxima_vigencia_recusada_quando_a_exigencia_parametrizada_nao_e_atendida(
        monkeypatch, jwt_authenticated_client_sme, flag_paa, flag_paa_proxima_vigencia, paa_factory,
        associacao, periodo_vigente, periodo_proxima_vigencia):
    monkeypatch.setattr(
        constantes, 'STATUS_VIGENTE_EXIGIDOS_PARA_INICIAR_PROXIMA_VIGENCIA', ('GERADO_PARCIALMENTE', 'GERADO'))
    paa_factory.create(periodo_paa=periodo_vigente, associacao=associacao)

    response = _post(jwt_authenticated_client_sme, associacao, periodo_proxima_vigencia.uuid)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'non_field_errors': ['O PAA anterior ainda não está na situação exigida para iniciar o da próxima vigência.']}
    assert Paa.objects.count() == 1


@freeze_time('2026-10-28')
def test_periodo_encerrado_recusado(
        jwt_authenticated_client_sme, flag_paa, flag_paa_proxima_vigencia, associacao,
        periodo_vigente, periodo_paa_factory):
    encerrado = periodo_paa_factory.create(
        referencia='2025', data_inicial=date(2025, 1, 1), data_final=date(2025, 12, 31))

    response = _post(jwt_authenticated_client_sme, associacao, encerrado.uuid)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'non_field_errors': ['O período informado já foi encerrado.']}
    assert Paa.objects.count() == 0


@freeze_time('2026-10-28')
def test_periodo_inexistente_recusado(
        jwt_authenticated_client_sme, flag_paa, flag_paa_proxima_vigencia, associacao, periodo_vigente):
    response = _post(jwt_authenticated_client_sme, associacao, '00000000-0000-0000-0000-000000000000')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'periodo' in response.json()
    assert Paa.objects.count() == 0


def test_associacao_de_outra_unidade_responde_404(
        jwt_authenticated_client_dre, flag_paa, flag_paa_proxima_vigencia, associacao_factory, unidade_factory,
        periodo_vigente):
    de_outra_unidade = associacao_factory.create(unidade=unidade_factory.create(tipo_unidade='CEU'))

    response = _post(jwt_authenticated_client_dre, de_outra_unidade, periodo_vigente.uuid)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert Paa.objects.count() == 0


@pytest.mark.parametrize('informa_periodo', [True, False])
def test_com_a_flag_desligada_associacao_de_outra_unidade_responde_404(
        jwt_authenticated_client_dre, flag_paa, associacao_factory, unidade_factory, periodo_vigente,
        informa_periodo):
    de_outra_unidade = associacao_factory.create(unidade=unidade_factory.create(tipo_unidade='CEU'))

    response = _post(
        jwt_authenticated_client_dre, de_outra_unidade, periodo_vigente.uuid if informa_periodo else None)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert Paa.objects.count() == 0


@freeze_time('2026-10-28')
def test_sem_periodo_no_payload_mantem_o_comportamento_atual(
        jwt_authenticated_client_sme, flag_paa, associacao, periodo_vigente):
    response = _post(jwt_authenticated_client_sme, associacao)

    assert response.status_code == status.HTTP_201_CREATED, response.content
    assert Paa.objects.get().periodo_paa == periodo_vigente
