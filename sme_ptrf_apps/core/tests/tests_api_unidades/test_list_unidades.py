import json

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def dre_01():
    return baker.make(
        'Unidade',
        uuid='f92d2caf-d71f-4ed0-87b2-6d326fb648a7',
        codigo_eol='108500',
        tipo_unidade='DRE',
        nome='GUAIANASES',
        sigla='G'
    )


@pytest.fixture
def unidade_paulo_camilhier_florencano_dre_1(dre_01):
    return baker.make(
        'Unidade',
        uuid="ae06f0f7-0aca-41d6-94c3-dea20558627d",
        codigo_eol="000086",
        tipo_unidade="EMEI",
        nome="PAULO CAMILHIER FLORENCANO",
        sigla="",
        dre=dre_01,
        email="",
        telefone="",
        tipo_logradouro="",
        logradouro="",
        numero="",
        complemento="",
        bairro="",
        cep="",
        qtd_alunos=0,
        diretor_nome="",
        dre_cnpj="",
        dre_diretor_regional_rf="",
        dre_diretor_regional_nome="",
        dre_designacao_portaria="",
        dre_designacao_ano=""
    )


def test_api_list_unidades_todas(client, unidade_paulo_camilhier_florencano_dre_1, dre_01):
    response = client.get(f'/api/unidades/', content_type='application/json')
    result = json.loads(response.content)

    result_esperado = [
        {
            "uuid": f'{dre_01.uuid}',
            "codigo_eol": f'{dre_01.codigo_eol}',
            "tipo_unidade": f'{dre_01.tipo_unidade}',
            "nome": f'{dre_01.nome}',
            "sigla": f'{dre_01.sigla}',
            "dre": None,
            "email": f'{dre_01.email}',
            "telefone": f'{dre_01.telefone}',
            "tipo_logradouro": f'{dre_01.tipo_logradouro}',
            "logradouro": f'{dre_01.logradouro}',
            "numero": f'{dre_01.numero}',
            "complemento": f'{dre_01.complemento}',
            "bairro": f'{dre_01.bairro}',
            "cep": f'{dre_01.cep}',
            "qtd_alunos": 0,
            "diretor_nome": f'{dre_01.diretor_nome}',
            "dre_cnpj": f'{dre_01.dre_cnpj}',
            "dre_diretor_regional_rf": f'{dre_01.dre_diretor_regional_rf}',
            "dre_diretor_regional_nome": f'{dre_01.dre_diretor_regional_nome}',
            "dre_designacao_portaria": f'{dre_01.dre_designacao_portaria}',
            "dre_designacao_ano": f'{dre_01.dre_designacao_ano}',
        },
        {
            "uuid": f'{unidade_paulo_camilhier_florencano_dre_1.uuid}',
            "codigo_eol": f'{unidade_paulo_camilhier_florencano_dre_1.codigo_eol}',
            "tipo_unidade": f'{unidade_paulo_camilhier_florencano_dre_1.tipo_unidade}',
            "nome": f'{unidade_paulo_camilhier_florencano_dre_1.nome}',
            "sigla": f'{unidade_paulo_camilhier_florencano_dre_1.sigla}',
            "dre": {
                'uuid': f'{unidade_paulo_camilhier_florencano_dre_1.dre.uuid}',
                'codigo_eol': f'{unidade_paulo_camilhier_florencano_dre_1.dre.codigo_eol}',
                'tipo_unidade': f'{unidade_paulo_camilhier_florencano_dre_1.dre.tipo_unidade}',
                'nome': f'{unidade_paulo_camilhier_florencano_dre_1.dre.nome}',
                'sigla': f'{unidade_paulo_camilhier_florencano_dre_1.dre.sigla}',
            },
            "email": f'{unidade_paulo_camilhier_florencano_dre_1.email}',
            "telefone": f'{unidade_paulo_camilhier_florencano_dre_1.telefone}',
            "tipo_logradouro": f'{unidade_paulo_camilhier_florencano_dre_1.tipo_logradouro}',
            "logradouro": f'{unidade_paulo_camilhier_florencano_dre_1.logradouro}',
            "numero": f'{unidade_paulo_camilhier_florencano_dre_1.numero}',
            "complemento": f'{unidade_paulo_camilhier_florencano_dre_1.complemento}',
            "bairro": f'{unidade_paulo_camilhier_florencano_dre_1.bairro}',
            "cep": f'{unidade_paulo_camilhier_florencano_dre_1.cep}',
            "qtd_alunos": 0,
            "diretor_nome": f'{unidade_paulo_camilhier_florencano_dre_1.diretor_nome}',
            "dre_cnpj": f'{unidade_paulo_camilhier_florencano_dre_1.dre_cnpj}',
            "dre_diretor_regional_rf": f'{unidade_paulo_camilhier_florencano_dre_1.dre_diretor_regional_rf}',
            "dre_diretor_regional_nome": f'{unidade_paulo_camilhier_florencano_dre_1.dre_diretor_regional_nome}',
            "dre_designacao_portaria": f'{unidade_paulo_camilhier_florencano_dre_1.dre_designacao_portaria}',
            "dre_designacao_ano": f'{unidade_paulo_camilhier_florencano_dre_1.dre_designacao_ano}',
        }

    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


@pytest.fixture
def tecnico_dre(dre):
    return baker.make(
        'TecnicoDre',
        dre=dre,
        nome='José Testando',
        rf='271170',
    )


@pytest.fixture
def atribuicao(tecnico_dre, unidade, periodo):
    return baker.make(
        'Atribuicao',
        tecnico=tecnico_dre,
        unidade=unidade,
        periodo=periodo,
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


def test_unidades_para_atribuicao(jwt_authenticated_client, unidade, periodo, tecnico_dre, atribuicao):
    response = jwt_authenticated_client.get(
        f'/api/unidades/para-atribuicao/?dre_uuid={unidade.dre.uuid}&periodo={periodo.uuid}', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'uuid': str(unidade.uuid),
            'codigo_eol': unidade.codigo_eol,
            'nome': f'{unidade.tipo_unidade} {unidade.nome}',
            'atribuicao': {
                'id': atribuicao.id,
                'tecnico': {
                    'uuid': str(tecnico_dre.uuid),
                    'rf': tecnico_dre.rf,
                    'nome': tecnico_dre.nome,
                    'email': tecnico_dre.email
                }
            }
        }]

    assert response.status_code == 200
    assert resultado_esperado == result


def test_unidades_para_atribuicao_filtro_tipo_unidade(jwt_authenticated_client, unidade, unidade_2, periodo, tecnico_dre, atribuicao):
    response = jwt_authenticated_client.get(
        f'/api/unidades/para-atribuicao/?dre_uuid={unidade.dre.uuid}&periodo={periodo.uuid}&tipo_unidade={unidade.tipo_unidade}', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'uuid': str(unidade.uuid),
            'codigo_eol': unidade.codigo_eol,
            'nome': f'{unidade.tipo_unidade} {unidade.nome}',
            'atribuicao': {
                'id': atribuicao.id,
                'tecnico': {
                    'uuid': str(tecnico_dre.uuid),
                    'rf': tecnico_dre.rf,
                    'nome': tecnico_dre.nome,
                    'email': tecnico_dre.email
                }
            }
        }]

    assert response.status_code == 200
    assert resultado_esperado == result


def test_unidades_para_atribuicao_filtro_nome_unidade_qualquer_termo(jwt_authenticated_client, unidade, unidade_2, periodo, tecnico_dre, atribuicao):
    response = jwt_authenticated_client.get(
        f'/api/unidades/para-atribuicao/?dre_uuid={unidade.dre.uuid}&periodo={periodo.uuid}&search=Unid', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == 200
    assert len(result) == 1
    assert result[0]['nome'] == f'{unidade_2.tipo_unidade} {unidade_2.nome}'
