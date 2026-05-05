import json
from datetime import date

import pytest
from freezegun import freeze_time
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def periodo_2018_1(periodo_factory):
    return periodo_factory(
        referencia='2018.1',
        data_inicio_realizacao_despesas=date(2018, 1, 1),
        data_fim_realizacao_despesas=date(2018, 12, 31),
        periodo_anterior=None
    )


@pytest.fixture
def periodo_2019_1(periodo_factory, periodo_2018_1):
    return periodo_factory(
        referencia='2019.1',
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 6, 30),
        periodo_anterior=periodo_2018_1
    )


@pytest.fixture
def periodo_2019_2(periodo_factory, periodo_2019_1):
    return periodo_factory(
        referencia='2019.2',
        data_inicio_realizacao_despesas=date(2019, 7, 1),
        data_fim_realizacao_despesas=date(2019, 12, 31),
        periodo_anterior=periodo_2019_1
    )


@pytest.fixture
def periodo_2020_1(periodo_factory, periodo_2019_2):
    return periodo_factory(
        referencia='2020.1',
        data_inicio_realizacao_despesas=date(2020, 1, 1),
        data_fim_realizacao_despesas=date(2020, 6, 30),
        periodo_anterior=periodo_2019_2
    )


@pytest.fixture
def periodo_2020_2(periodo_factory, periodo_2020_1):
    return periodo_factory(
        referencia='2020.2',
        data_inicio_realizacao_despesas=date(2020, 7, 1),
        data_fim_realizacao_despesas=date(2020, 12, 31),
        periodo_anterior=periodo_2020_1
    )


@pytest.fixture
def associacao_teste(unidade, periodo_2019_1):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='52.302.275/0001-83',
        unidade=unidade,
        periodo_inicial=periodo_2019_1,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456',
    )


@pytest.fixture
def associacao_encerrada_teste(unidade, periodo_2019_1, periodo_2019_2):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='52.302.275/0001-83',
        unidade=unidade,
        periodo_inicial=periodo_2019_1,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456',
        data_de_encerramento=date(2019, 12, 10)
    )


@freeze_time('2020-06-15')
def test_get_periodos_ate_agora_fora_implantacao_da_associacao(
    jwt_authenticated_client_a,
    associacao_teste,
    periodo_inicial_associacao_teste,
    periodo_2018_1,
    periodo_2019_1,
    periodo_2019_2,
    periodo_2020_1,
    periodo_2020_2,
):
    response = jwt_authenticated_client_a.get(
        f'/api/associacoes/{associacao_teste.uuid}/periodos-ate-agora-fora-implantacao/',
        content_type='application/json')

    result = json.loads(response.content)

    esperados = [
        {
            'id': periodo_2020_1.id,
            'uuid': f'{periodo_2020_1.uuid}',
            'data_fim_realizacao_despesas': f'{periodo_2020_1.data_fim_realizacao_despesas}',
            'data_inicio_realizacao_despesas': f'{periodo_2020_1.data_inicio_realizacao_despesas}',
            'referencia': '2020.1',
            'referencia_por_extenso': periodo_2020_1.referencia_por_extenso,
            'recurso': {
                'id': periodo_2020_1.recurso.id,
                'uuid': f'{periodo_2020_1.recurso.uuid}',
                'nome': periodo_2020_1.recurso.nome,
                'nome_exibicao': periodo_2020_1.recurso.nome_exibicao,
                'criado_em': periodo_2020_1.recurso.criado_em.isoformat() if periodo_2020_1.recurso.criado_em else None,
                'alterado_em': periodo_2020_1.recurso.alterado_em.isoformat() if periodo_2020_1.recurso.alterado_em else None,
                'cor': periodo_2020_1.recurso.cor,
                'icone': periodo_2020_1.recurso.icone if periodo_2020_1.recurso.icone else None,
                'ativo': periodo_2020_1.recurso.ativo,
                'legado': periodo_2020_1.recurso.legado,
                'exibe_valores_reprogramados': periodo_2020_1.recurso.exibe_valores_reprogramados,
            },
        },
        {
            'id': periodo_2019_2.id,
            'uuid': f'{periodo_2019_2.uuid}',
            'data_fim_realizacao_despesas': f'{periodo_2019_2.data_fim_realizacao_despesas}',
            'data_inicio_realizacao_despesas': f'{periodo_2019_2.data_inicio_realizacao_despesas}',
            'referencia': '2019.2',
            'referencia_por_extenso': periodo_2019_2.referencia_por_extenso,
            'recurso': {
                'id': periodo_2019_2.recurso.id,
                'uuid': f'{periodo_2019_2.recurso.uuid}',
                'nome': periodo_2019_2.recurso.nome,
                'nome_exibicao': periodo_2019_2.recurso.nome_exibicao,
                'criado_em': periodo_2019_2.recurso.criado_em.isoformat() if periodo_2019_2.recurso.criado_em else None,
                'alterado_em': periodo_2019_2.recurso.alterado_em.isoformat() if periodo_2019_2.recurso.alterado_em else None,
                'cor': periodo_2019_2.recurso.cor,
                'icone': periodo_2019_2.recurso.icone if periodo_2019_2.recurso.icone else None,
                'ativo': periodo_2019_2.recurso.ativo,
                'legado': periodo_2019_2.recurso.legado,
                'exibe_valores_reprogramados': periodo_2019_2.recurso.exibe_valores_reprogramados,
            },
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperados


@freeze_time('2020-06-15')
def test_get_periodos_ate_encerramento_da_associacao_e_fora_implantacao_da_associacao(
    jwt_authenticated_client_a,
    associacao_encerrada_teste,
    periodo_inicial_associacao_encerrada_teste,
    periodo_2018_1,
    periodo_2019_1,
    periodo_2019_2,
    periodo_2020_1,
    periodo_2020_2,
):
    response = jwt_authenticated_client_a.get(
        f'/api/associacoes/{associacao_encerrada_teste.uuid}/periodos-ate-agora-fora-implantacao/',
        content_type='application/json')

    result = json.loads(response.content)

    esperados = [
        {
            'id': periodo_2019_2.id,
            'uuid': f'{periodo_2019_2.uuid}',
            'data_fim_realizacao_despesas': f'{periodo_2019_2.data_fim_realizacao_despesas}',
            'data_inicio_realizacao_despesas': f'{periodo_2019_2.data_inicio_realizacao_despesas}',
            'referencia': '2019.2',
            'referencia_por_extenso': periodo_2019_2.referencia_por_extenso,
            'recurso': {
                'id': periodo_2019_2.recurso.id,
                'uuid': f'{periodo_2019_2.recurso.uuid}',
                'nome': periodo_2019_2.recurso.nome,
                'nome_exibicao': periodo_2019_2.recurso.nome_exibicao,
                'criado_em': periodo_2019_2.recurso.criado_em.isoformat() if periodo_2019_2.recurso.criado_em else None,
                'alterado_em': periodo_2019_2.recurso.alterado_em.isoformat() if periodo_2019_2.recurso.alterado_em else None,
                'cor': periodo_2019_2.recurso.cor,
                'icone': periodo_2019_2.recurso.icone if periodo_2019_2.recurso.icone else None,
                'ativo': periodo_2019_2.recurso.ativo,
                'legado': periodo_2019_2.recurso.legado,
                'exibe_valores_reprogramados': periodo_2019_2.recurso.exibe_valores_reprogramados,
            },
        },
    ]

    assert response.status_code == status.HTTP_200_OK

    assert result == esperados
