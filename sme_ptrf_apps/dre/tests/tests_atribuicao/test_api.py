import json

import pytest
from model_bakery import baker
from rest_framework import status

from sme_ptrf_apps.dre.models import Atribuicao

pytestmark = pytest.mark.django_db


@pytest.fixture
def tecnico_dre(dre):
    return baker.make(
        'TecnicoDre',
        dre=dre,
        nome='Armand0 Toda',
        rf='666171',
    )


@pytest.fixture
def tecnico_dre2(dre):
    return baker.make(
        'TecnicoDre',
        dre=dre,
        nome='Aslan Knight',
        rf='676171',
    )


@pytest.fixture
def unidade_2(dre):
    return baker.make(
        'Unidade',
        nome='Escola Unidade 2',
        tipo_unidade='EMEI',
        codigo_eol='123459',
        dre=dre,
        sigla='ET2',
        cep='5868120',
        tipo_logradouro='Travessa',
        logradouro='dos Testes',
        bairro='COHAB INSTITUTO ADVENTISTA',
        numero='100',
        complemento='fundos',
        telefone='99212627',
        email='emeijopfilho@sme.prefeitura.sp.gov.br',
        qtd_alunos=1200,
        diretor_nome='Amaro Pedro',
        dre_cnpj='63.058.286/0001-86',
        dre_diretor_regional_rf='1234567',
        dre_diretor_regional_nome='Anthony Edward Stark',
        dre_designacao_portaria='Portaria nº 0.000',
        dre_designacao_ano='2017',
    )


@pytest.fixture
def atribuicao1(tecnico_dre, unidade, periodo):
    return baker.make(
        'Atribuicao',
        tecnico=tecnico_dre,
        unidade=unidade,
        periodo=periodo,
    )


@pytest.fixture
def atribuicao2(tecnico_dre, unidade_2, periodo):
    return baker.make(
        'Atribuicao',
        tecnico=tecnico_dre,
        unidade=unidade_2,
        periodo=periodo,
    )


def test_criar_atribuicoes_em_lote(jwt_authenticated_client_dre, unidade, unidade_2, periodo, tecnico_dre):
    payload = {
        "periodo": str(periodo.uuid),
        "tecnico": str(tecnico_dre.uuid),
        "unidades": [
            {"uuid": str(unidade.uuid)},
            {"uuid": str(unidade_2.uuid)}
        ]
    }

    response = jwt_authenticated_client_dre.post(
        '/api/atribuicoes/lote/', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED
    assert Atribuicao.objects.filter(unidade__uuid=unidade.uuid).first()
    assert Atribuicao.objects.filter(unidade__uuid=unidade_2.uuid).first()


def test_desatribuir_atribuicoes_em_lote(jwt_authenticated_client_dre, unidade, unidade_2, periodo, tecnico_dre, atribuicao1, atribuicao2):
    payload = {
        "periodo": str(periodo.uuid),
        "unidades": [
            {"uuid": str(unidade.uuid)},
            {"uuid": str(unidade_2.uuid)}
        ]
    }

    response = jwt_authenticated_client_dre.post(
        '/api/atribuicoes/desfazer-lote/', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    assert not Atribuicao.objects.filter(unidade__uuid=unidade.uuid).first()
    assert not Atribuicao.objects.filter(unidade__uuid=unidade_2.uuid).first()


def test_troca_atribuicoes_em_lote(jwt_authenticated_client_dre, unidade, unidade_2, periodo, tecnico_dre, tecnico_dre2, atribuicao1, atribuicao2):
    payload = {
        "tecnico_atual": str(tecnico_dre.uuid),
        "tecnico_novo": str(tecnico_dre2.uuid),
    }

    response = jwt_authenticated_client_dre.post(
        '/api/atribuicoes/troca-lote/', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    assert not Atribuicao.objects.filter(tecnico__uuid=tecnico_dre.uuid).exists()
    assert Atribuicao.objects.filter(tecnico__uuid=tecnico_dre2.uuid).exists()


def test_copiar_atribuicoes(jwt_authenticated_client_dre, unidade, unidade_2, periodo, periodo_2020_1, tecnico_dre, tecnico_dre2, atribuicao1, atribuicao2):
    payload = {
        "periodo_atual": str(periodo_2020_1.uuid),
        "periodo_copiado": str(periodo.uuid),
        "dre_uuid": str(unidade.dre.uuid)
    }

    response = jwt_authenticated_client_dre.post(
        '/api/atribuicoes/copia-periodo/', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    assert Atribuicao.objects.filter(periodo__uuid=periodo_2020_1.uuid).exists()
    assert Atribuicao.objects.filter(periodo__uuid=periodo_2020_1.uuid).count() == 2