import json
from datetime import date

import pytest
from model_bakery import baker

from sme_ptrf_apps.core.models import PrestacaoConta

from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def motivo_pagamento_adiantado_01_teste_ata():
    return baker.make(
        'MotivoPagamentoAntecipado',
        motivo="Motivo de pagamento adiantado 01"
    )


@pytest.fixture
def motivo_pagamento_adiantado_02_teste_ata():
    return baker.make(
        'MotivoPagamentoAntecipado',
        motivo="Motivo de pagamento adiantado 02"
    )


@pytest.fixture
def associacao_teste_ata(unidade, periodo_anterior):
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
def periodo_2022_1_teste_ata(periodo):
    return baker.make(
        'Periodo',
        referencia='2022.1',
        data_inicio_realizacao_despesas=date(2022, 1, 1),
        data_fim_realizacao_despesas=date(2022, 12, 31),
        data_prevista_repasse=None,
        data_inicio_prestacao_contas=None,
        data_fim_prestacao_contas=None,
        periodo_anterior=periodo
    )


@pytest.fixture
def prestacao_conta_2022_1_conciliada_teste_ata(periodo_2022_1_teste_ata, associacao_teste_ata):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2022_1_teste_ata,
        associacao=associacao_teste_ata,
        status=PrestacaoConta.STATUS_NAO_RECEBIDA
    )


@pytest.fixture
def ata_2022_1_teste_ata(prestacao_conta_2022_1_conciliada_teste_ata):
    return baker.make(
        'Ata',
        arquivo_pdf=None,
        prestacao_conta=prestacao_conta_2022_1_conciliada_teste_ata,
        periodo=prestacao_conta_2022_1_conciliada_teste_ata.periodo,
        associacao=prestacao_conta_2022_1_conciliada_teste_ata.associacao,
        tipo_ata='APRESENTACAO',
        tipo_reuniao='ORDINARIA',
        convocacao='PRIMEIRA',
        status_geracao_pdf='NAO_GERADO',
        data_reuniao=date(2022, 3, 24),
        local_reuniao='Escola Teste',
        presidente_reuniao='José',
        cargo_presidente_reuniao='Presidente',
        secretario_reuniao='Ana',
        cargo_secretaria_reuniao='Secretária',
        comentarios='Teste',
        parecer_conselho='APROVADA',
    )


@pytest.fixture
def despesa_data_transacao_menor_que_data_documento(
    associacao_teste_ata,
    motivo_pagamento_adiantado_01_teste_ata,
    motivo_pagamento_adiantado_02_teste_ata,
):
    return baker.make(
        'Despesa',
        associacao=associacao_teste_ata,
        tipo_documento=None,
        tipo_transacao=None,
        numero_documento="",
        data_documento="2022-03-10",
        cpf_cnpj_fornecedor="36.352.197/0001-75",
        nome_fornecedor="Fornecedor Ollyver",
        data_transacao="2022-03-09",
        valor_total=100,
        valor_recursos_proprios=0,
        motivos_pagamento_antecipado=[motivo_pagamento_adiantado_01_teste_ata, motivo_pagamento_adiantado_02_teste_ata],
        outros_motivos_pagamento_antecipado="Este é o motivo de pagamento antecipado",
    )


def test_retorna_despesa_com_pagamento_antecipado(
    associacao_teste_ata,
    despesa_data_transacao_menor_que_data_documento,
    ata_2022_1_teste_ata,
    prestacao_conta_2022_1_conciliada_teste_ata,
    periodo_2022_1_teste_ata,
    motivo_pagamento_adiantado_02_teste_ata,
    motivo_pagamento_adiantado_01_teste_ata,
    jwt_authenticated_client_a
):
    ata_uuid = ata_2022_1_teste_ata.uuid
    response = jwt_authenticated_client_a.get(
        f'/api/atas-associacao/ata-despesas-com-pagamento-antecipado/?ata-uuid={ata_uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'nome_fornecedor': despesa_data_transacao_menor_que_data_documento.nome_fornecedor,
            'cpf_cnpj_fornecedor': despesa_data_transacao_menor_que_data_documento.cpf_cnpj_fornecedor,
            'tipo_documento': '',
            'numero_documento': despesa_data_transacao_menor_que_data_documento.numero_documento,
            'data_documento': '10/03/2022',
            'tipo_transacao': '',
            'data_transacao': '09/03/2022',
            'valor_total': 100.0,
            'motivos_pagamento_antecipado': [
                {'motivo': 'Motivo de pagamento adiantado 01'},
                {'motivo': 'Motivo de pagamento adiantado 02'}
            ],
            'outros_motivos_pagamento_antecipado': 'Este é o motivo de pagamento antecipado'
        }]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
