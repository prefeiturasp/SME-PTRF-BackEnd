import json

import pytest
from rest_framework import status

from model_bakery import baker

from ...models import Despesa

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_despesa_com_imposto(
    associacao,
    tipo_documento,
    tipo_transacao,
    tipo_custeio,
    especificacao_material_servico,
    acao_associacao,
    conta_associacao
):
    payload = {
        "associacao": f'{associacao.uuid}',
        "tipo_documento": None,
        "tipo_transacao": None,
        "numero_documento": "",
        "data_documento": None,
        "cpf_cnpj_fornecedor": "",
        "nome_fornecedor": "",
        "data_transacao": "2022-03-10",
        "valor_total": 100,
        "valor_recursos_proprios": 0,
        "motivos_pagamento_antecipado": [],
        "outros_motivos_pagamento_antecipado": "",
        "despesas_impostos": [
            {
                "associacao": f'{associacao.uuid}',
                "tipo_documento": tipo_documento.id,
                "data_transacao": None,
                "tipo_transacao": tipo_transacao.id,

                "rateios": [{
                    "tipo_custeio": tipo_custeio.id,
                    "especificacao_material_servico": especificacao_material_servico.id,
                    "acao_associacao": f"{acao_associacao.uuid}",
                    "aplicacao_recurso": "CUSTEIO",
                    "associacao": f'{associacao.uuid}',
                    "conta_associacao": f"{conta_associacao.uuid}",
                    "escolha_tags": "nao",
                    "numero_processo_incorporacao_capital": "",
                    "quantidade_itens_capital": 0,
                    "valor_item_capital": 0,
                    "valor_original": 222,
                    "valor_rateio": 222
                }]
            }
        ],
        "rateios": [
            {
                "associacao": f'{associacao.uuid}',
                "conta_associacao": None,
                "acao_associacao": None,
                "aplicacao_recurso": None,
                "tipo_custeio": None,
                "especificacao_material_servico": None,
                "valor_rateio": 100,
                "quantidade_itens_capital": 0,
                "valor_item_capital": 100,
                "numero_processo_incorporacao_capital": ""
            }
        ]
    }
    return payload


@pytest.fixture
def payload_despesa_remove_vinculo_com_imposto(
    associacao,
    tipo_documento,
    tipo_transacao,
    tipo_custeio,
    especificacao_material_servico,
    acao_associacao,
    conta_associacao
):
    payload = {
        "associacao": f'{associacao.uuid}',
        "tipo_documento": None,
        "tipo_transacao": None,
        "numero_documento": "",
        "data_documento": None,
        "cpf_cnpj_fornecedor": "",
        "nome_fornecedor": "",
        "data_transacao": "2022-03-10",
        "valor_total": 100,
        "valor_recursos_proprios": 0,
        "despesas_impostos": [],
        "motivos_pagamento_antecipado": [],
        "outros_motivos_pagamento_antecipado": "",
        "rateios": [
            {
                "associacao": f'{associacao.uuid}',
                "conta_associacao": None,
                "acao_associacao": None,
                "aplicacao_recurso": None,
                "tipo_custeio": None,
                "especificacao_material_servico": None,
                "valor_rateio": 100,
                "quantidade_itens_capital": 0,
                "valor_item_capital": 100,
                "numero_processo_incorporacao_capital": ""
            }
        ]
    }
    return payload


@pytest.fixture
def rateio_despesa_despesa_imposto(associacao, tipo_custeio, especificacao_material_servico, acao_associacao,
                                   conta_associacao, despesa_despesa_imposto):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_despesa_imposto,
        tipo_custeio=tipo_custeio,
        especificacao_material_servico=especificacao_material_servico,
        acao_associacao=acao_associacao,
        aplicacao_recurso="CUSTEIO",
        associacao=associacao,
        conta_associacao=conta_associacao,
        numero_processo_incorporacao_capital="",
        quantidade_itens_capital=0,
        valor_item_capital=0,
        valor_original=222,
        valor_rateio=222
    )


@pytest.fixture
def despesa_despesa_imposto(
    associacao,
    tipo_documento,
    tipo_transacao,
    tipo_custeio,
    especificacao_material_servico,
    acao_associacao,
    conta_associacao,
):
    return baker.make(
        'Despesa',
        associacao=associacao,
        tipo_documento=tipo_documento,
        tipo_transacao=tipo_transacao,
    )


@pytest.fixture
def rateio_despesa_com_imposto(associacao, despesa_com_imposto):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_com_imposto,
        associacao=associacao,
        conta_associacao=None,
        acao_associacao=None,
        aplicacao_recurso=None,
        tipo_custeio=None,
        especificacao_material_servico=None,
        valor_rateio=100,
        quantidade_itens_capital=0,
        valor_item_capital=100,
        numero_processo_incorporacao_capital=""
    )


@pytest.fixture
def despesa_com_imposto(
    associacao,
    tipo_documento,
    tipo_transacao,
    tipo_custeio,
    especificacao_material_servico,
    acao_associacao,
    conta_associacao,
    despesa_despesa_imposto
):
    return baker.make(
        'Despesa',
        associacao=associacao,
        tipo_documento=None,
        tipo_transacao=None,
        numero_documento="",
        data_documento=None,
        cpf_cnpj_fornecedor="",
        nome_fornecedor="",
        data_transacao="2022-03-10",
        valor_total=100,
        valor_recursos_proprios=0,
        despesas_impostos=[despesa_despesa_imposto,]
    )


def monta_result_esperado(
    despesa_com_imposto,
    despesa_despesa_imposto,
    associacao,
    tipo_documento,
    tipo_transacao,
    rateio_despesa_com_imposto,
    rateio_despesa_despesa_imposto,
):
    resultado_esperado = {
        'alterado_em': despesa_com_imposto.alterado_em.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        'associacao': {
            'ccm': f"{associacao.ccm}",
            'cnpj': f"{associacao.cnpj}",
            'email': f"{associacao.email}",
            'id': associacao.id,
            'nome': f"{associacao.nome}",
            'processo_regularidade': f"{associacao.processo_regularidade}",
            'unidade': {'codigo_eol': f"{associacao.unidade.codigo_eol}",
                        'dre': {
                            'codigo_eol': f"{associacao.unidade.dre.codigo_eol}",
                            'nome': f"{associacao.unidade.dre.nome}",
                            'sigla': f"{associacao.unidade.dre.sigla}",
                            'tipo_unidade': f"{associacao.unidade.dre.tipo_unidade}",
                            'uuid': f"{associacao.unidade.dre.uuid}"
                        },
                        'nome': f"{associacao.unidade.nome}",
                        'sigla': f"{associacao.unidade.sigla}",
                        'tipo_unidade': f"{associacao.unidade.tipo_unidade}",
                        'uuid': f"{associacao.unidade.uuid}"
                        },
            'uuid': f"{associacao.uuid}",
        },
        'cpf_cnpj_fornecedor': f"{despesa_com_imposto.cpf_cnpj_fornecedor}",
        'criado_em': despesa_com_imposto.criado_em.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        'data_documento': None,
        'data_transacao': f"{despesa_com_imposto.data_transacao}",
        'despesa_geradora_do_imposto': None,
        'despesas_impostos': [{
            'alterado_em': despesa_despesa_imposto.alterado_em.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "associacao": f'{associacao.uuid}',
            'cpf_cnpj_fornecedor': f"{despesa_com_imposto.cpf_cnpj_fornecedor}",
            'criado_em': despesa_despesa_imposto.criado_em.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            'data_documento': None,
            'data_transacao': None,
            'despesas_impostos': [],
            'documento_transacao': '',
            'eh_despesa_reconhecida_pela_associacao': True,
            'eh_despesa_sem_comprovacao_fiscal': False,
            'id': despesa_despesa_imposto.id,
            'motivos_pagamento_antecipado': [],
            'outros_motivos_pagamento_antecipado': '',
            'nome_fornecedor': f"{despesa_com_imposto.nome_fornecedor}",
            'numero_boletim_de_ocorrencia': f"{despesa_com_imposto.numero_boletim_de_ocorrencia}",
            'numero_documento': f"{despesa_com_imposto.numero_documento}",
            'rateios': [
                {
                    'acao_associacao': f"{rateio_despesa_despesa_imposto.acao_associacao.uuid}",
                    'alterado_em': rateio_despesa_despesa_imposto.alterado_em.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                    'aplicacao_recurso': 'CUSTEIO',
                    'associacao': f"{rateio_despesa_despesa_imposto.associacao.uuid}",
                    'conferido': False,
                    'conta_associacao': f"{rateio_despesa_despesa_imposto.conta_associacao.uuid}",
                    'criado_em': rateio_despesa_despesa_imposto.criado_em.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                    'eh_despesa_sem_comprovacao_fiscal': False,
                    'especificacao_material_servico': rateio_despesa_despesa_imposto.especificacao_material_servico.id,
                    'numero_processo_incorporacao_capital': '',
                    'periodo_conciliacao': None,
                    'quantidade_itens_capital': 0,
                    'saida_de_recurso_externo': False,
                    'status': 'COMPLETO',
                    'tag': None,
                    'tipo_custeio': rateio_despesa_despesa_imposto.tipo_custeio.id,
                    'update_conferido': False,
                    'uuid': f"{rateio_despesa_despesa_imposto.uuid}",
                    'valor_item_capital': '0.00',
                    'valor_original': '222.00',
                    'valor_rateio': '222.00'
                }
            ],
            'retem_imposto': False,
            'status': 'INCOMPLETO',
            "tipo_documento": tipo_documento.id,
            "tipo_transacao": tipo_transacao.id,
            'uuid': f"{despesa_despesa_imposto.uuid}",
            'valor_original': '0.00',
            'valor_recursos_proprios': '0.00',
            'valor_total': '0.00'
        },],
        'documento_transacao': '',
        'eh_despesa_reconhecida_pela_associacao': True,
        'eh_despesa_sem_comprovacao_fiscal': False,
        'id': despesa_com_imposto.id,
        'motivos_pagamento_antecipado': [],
        'outros_motivos_pagamento_antecipado': '',
        'nome_fornecedor': '',
        'numero_boletim_de_ocorrencia': '',
        'numero_documento': '',
        'rateios': [
            {
                'acao_associacao': None,
                'alterado_em': rateio_despesa_com_imposto.alterado_em.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                'aplicacao_recurso': rateio_despesa_com_imposto.aplicacao_recurso,
                'associacao': {
                    'ccm': '0.000.00-0',
                    'cnpj': '52.302.275/0001-83',
                    'email': 'ollyverottoboni@gmail.com',
                    'id': associacao.id,
                    'nome': 'Escola Teste',
                    'processo_regularidade': '123456',
                    'unidade': {
                        'codigo_eol': f"{associacao.unidade.codigo_eol}",
                        'dre': {
                            'codigo_eol': f"{associacao.unidade.dre.codigo_eol}",
                            'nome': f"{associacao.unidade.dre.nome}",
                            'sigla': f"{associacao.unidade.dre.sigla}",
                            'tipo_unidade': f"{associacao.unidade.dre.tipo_unidade}",
                            'uuid': f"{associacao.unidade.dre.uuid}"
                        },
                        'nome': f"{associacao.unidade.nome}",
                        'sigla': f"{associacao.unidade.sigla}",
                        'tipo_unidade': f"{associacao.unidade.tipo_unidade}",
                        'uuid': f"{associacao.unidade.uuid}"
                    },
                    'uuid': f"{associacao.uuid}"
                },
                'conferido': False,
                'conta_associacao': None,
                'criado_em': rateio_despesa_com_imposto.criado_em.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                'despesa': despesa_com_imposto.id,
                'eh_despesa_sem_comprovacao_fiscal': False,
                'especificacao_material_servico': None,
                'estorno': {
                    'categoria_receita': None,
                    'data': None,
                    'detalhe_outros': '',
                    'detalhe_tipo_receita': None,
                    'tipo_receita': {
                        'aceita_capital': False,
                        'aceita_custeio': False,
                        'aceita_livre': False,
                        'e_devolucao': False,
                        'e_recursos_proprios': False,
                        'e_repasse': False,
                        'nome': ''
                    },
                    'valor': None
                },
                'id': rateio_despesa_com_imposto.id,
                'numero_processo_incorporacao_capital': '',
                'periodo_conciliacao': None,
                'quantidade_itens_capital': 0,
                'saida_de_recurso_externo': False,
                'status': 'INCOMPLETO',
                'tag': None,
                'tipo_custeio': None,
                'update_conferido': False,
                'uuid': f"{rateio_despesa_com_imposto.uuid}",
                'valor_item_capital': '100.00',
                'valor_original': '0.00',
                'valor_rateio': '100.00'
            }],
        'retem_imposto': False,
        'status': 'INCOMPLETO',
        'tipo_documento': None,
        'tipo_transacao': None,
        'uuid': f"{despesa_com_imposto.uuid}",
        'valor_original': '0.00',
        'valor_recursos_proprios': '0.00',
        'valor_total': '100.00',
    }

    return resultado_esperado


def test_retrieve_despesa_com_imposto(
    associacao,
    tipo_documento,
    tipo_transacao,
    tipo_custeio,
    especificacao_material_servico,
    acao_associacao,
    conta_associacao,
    payload_despesa_com_imposto,
    jwt_authenticated_client_d,
    despesa_com_imposto,
    despesa_despesa_imposto,
    rateio_despesa_com_imposto,
    rateio_despesa_despesa_imposto,
):
    result_esperado = monta_result_esperado(
        despesa_com_imposto=despesa_com_imposto,
        despesa_despesa_imposto=despesa_despesa_imposto,
        associacao=associacao,
        tipo_documento=tipo_documento,
        tipo_transacao=tipo_transacao,
        rateio_despesa_com_imposto=rateio_despesa_com_imposto,
        rateio_despesa_despesa_imposto=rateio_despesa_despesa_imposto
    )

    uuid_despesa = despesa_com_imposto.uuid
    response = jwt_authenticated_client_d.get(f'/api/despesas/{uuid_despesa}/', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


def test_put_despesa_remove_vinculo_com_a_despesa_de_imposto(
    associacao,
    tipo_documento,
    tipo_transacao,
    tipo_custeio,
    especificacao_material_servico,
    acao_associacao,
    conta_associacao,
    payload_despesa_remove_vinculo_com_imposto,
    jwt_authenticated_client_d,
    despesa_com_imposto,
    despesa_despesa_imposto,
    rateio_despesa_com_imposto,
    rateio_despesa_despesa_imposto,
):
    response = jwt_authenticated_client_d.put(
        f'/api/despesas/{despesa_com_imposto.uuid}/',
        data=json.dumps(payload_despesa_remove_vinculo_com_imposto),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK

    result = json.loads(response.content)

    despesa = Despesa.objects.get(uuid=result["uuid"])

    assert not despesa.despesas_impostos.exists()


def test_post_despesa_com_imposto_e_deve_criar_vinculo_com_a_despesa_de_imposto(
    associacao,
    tipo_documento,
    tipo_transacao,
    tipo_custeio,
    especificacao_material_servico,
    acao_associacao,
    conta_associacao,
    payload_despesa_com_imposto,
    jwt_authenticated_client_d,
    despesa_com_imposto,
    despesa_despesa_imposto,
    rateio_despesa_com_imposto,
    rateio_despesa_despesa_imposto,
):
    response = jwt_authenticated_client_d.post('/api/despesas/', data=json.dumps(payload_despesa_com_imposto),
                                               content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert Despesa.objects.filter(uuid=result["uuid"]).exists()

    despesa = Despesa.objects.get(uuid=result["uuid"])

    assert despesa.associacao.uuid == associacao.uuid

    assert Despesa.objects.filter(uuid=despesa_despesa_imposto.uuid).exists()

    despesa_imposto = Despesa.objects.get(uuid=despesa_despesa_imposto.uuid)

    assert despesa_imposto.associacao.uuid == associacao.uuid


def test_delete_despesa_geradora_de_imposto_e_com_isso_deve_apagar_despesa_de_imposto_vinculada(
    associacao,
    tipo_documento,
    tipo_transacao,
    tipo_custeio,
    especificacao_material_servico,
    acao_associacao,
    conta_associacao,
    payload_despesa_remove_vinculo_com_imposto,
    jwt_authenticated_client_d,
    despesa_com_imposto,
    despesa_despesa_imposto,
    rateio_despesa_com_imposto,
    rateio_despesa_despesa_imposto,
):
    despesa_imposto_uuid = despesa_despesa_imposto.uuid
    despesa_com_imposto_uuid = despesa_com_imposto.uuid

    assert Despesa.objects.filter(uuid=despesa_com_imposto_uuid).exists()
    assert Despesa.objects.filter(uuid=despesa_imposto_uuid).exists()

    response = jwt_authenticated_client_d.delete(f'/api/despesas/{despesa_com_imposto.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Despesa.objects.filter(uuid=despesa_com_imposto_uuid).exists()
    assert not Despesa.objects.filter(uuid=despesa_imposto_uuid).exists()
