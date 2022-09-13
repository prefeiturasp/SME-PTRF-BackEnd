import pytest

from datetime import date

from model_bakery import baker

@pytest.fixture
def payload_despesa_valida(
    associacao,
    tipo_documento,
    tipo_transacao,
    conta_associacao,
    acao_associacao,
    tipo_aplicacao_recurso,
    tipo_custeio,
    especificacao_material_servico,
):
    payload = {
        "associacao": f'{associacao.uuid}',
        "tipo_documento": tipo_documento.id,
        "tipo_transacao": tipo_transacao.id,
        "documento_transacao": "123456789",
        "numero_documento": "634767",
        "data_documento": "2020-03-10",
        "cpf_cnpj_fornecedor": "36.352.197/0001-75",
        "nome_fornecedor": "FORNECEDOR TESTE SA",
        "data_transacao": "2020-03-10",
        "valor_total": 11000.50,
        "valor_recursos_proprios": 1000.50,
        "motivos_pagamento_antecipado": [],
        "outros_motivos_pagamento_antecipado": "",
        "rateios": [
            {
                "associacao": f'{associacao.uuid}',
                "conta_associacao": f'{conta_associacao.uuid}',
                "acao_associacao": f'{acao_associacao.uuid}',
                "aplicacao_recurso": tipo_aplicacao_recurso,
                "tipo_custeio": tipo_custeio.id,
                "especificacao_material_servico": especificacao_material_servico.id,
                "valor_rateio": 1000.00,
                "quantidade_itens_capital": 2,
                "valor_item_capital": 500.00,
                "numero_processo_incorporacao_capital": "6234673223462364632"
            }
        ]
    }
    return payload


@pytest.fixture
def payload_despesa_sem_campos_nao_obrigatorios(
    associacao,
):
    payload = {
        "associacao": f'{associacao.uuid}',
        "tipo_documento": None,
        "tipo_transacao": None,
        "numero_documento": "",
        "data_documento": None,
        "cpf_cnpj_fornecedor": "",
        "nome_fornecedor": "",
        "data_transacao": None,
        "valor_total": 0,
        "valor_recursos_proprios": 0,
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
                "valor_rateio": 0,
                "quantidade_itens_capital": 0,
                "valor_item_capital": 0,
                "numero_processo_incorporacao_capital": ""
            }
        ]
    }
    return payload


@pytest.fixture
def payload_despesa_sem_campos_nao_obrigatorios_sem_rateios(
    associacao,
):
    payload = {
        "associacao": f'{associacao.uuid}',
        "tipo_documento": None,
        "tipo_transacao": None,
        "numero_documento": "",
        "data_documento": None,
        "cpf_cnpj_fornecedor": "",
        "nome_fornecedor": "",
        "data_transacao": None,
        "valor_total": 0,
        "valor_recursos_proprios": 0,
        "motivos_pagamento_antecipado": [],
        "outros_motivos_pagamento_antecipado": "",
        "rateios": []
    }
    return payload


@pytest.fixture
def payload_despesa_valida_rateio_com_tag(
    associacao,
    tipo_documento,
    tipo_transacao,
    conta_associacao,
    acao_associacao,
    tipo_aplicacao_recurso,
    tipo_custeio,
    especificacao_material_servico,
    tag_ativa
):
    payload = {
        "associacao": f'{associacao.uuid}',
        "tipo_documento": tipo_documento.id,
        "tipo_transacao": tipo_transacao.id,
        "documento_transacao": "123456789",
        "numero_documento": "634767",
        "data_documento": "2020-03-10",
        "cpf_cnpj_fornecedor": "36.352.197/0001-75",
        "nome_fornecedor": "FORNECEDOR TESTE SA",
        "data_transacao": "2020-03-10",
        "valor_total": 11000.50,
        "valor_recursos_proprios": 1000.50,
        "motivos_pagamento_antecipado": [],
        "outros_motivos_pagamento_antecipado": "",
        "rateios": [
            {
                "associacao": f'{associacao.uuid}',
                "conta_associacao": f'{conta_associacao.uuid}',
                "acao_associacao": f'{acao_associacao.uuid}',
                "aplicacao_recurso": tipo_aplicacao_recurso,
                "tipo_custeio": tipo_custeio.id,
                "especificacao_material_servico": especificacao_material_servico.id,
                "valor_rateio": 1000.00,
                "quantidade_itens_capital": 2,
                "valor_item_capital": 500.00,
                "numero_processo_incorporacao_capital": "6234673223462364632",
                "tag": f'{tag_ativa.uuid}'
            }
        ]
    }
    return payload


@pytest.fixture
def payload_despesa_status_incompleto_eh_despesa_sem_comprovacao_fiscal(
    associacao,
):
    payload = {
        "associacao": f'{associacao.uuid}',
        "tipo_documento": None,
        "tipo_transacao": None,
        "numero_documento": "",
        "data_documento": None,
        "cpf_cnpj_fornecedor": "",
        "nome_fornecedor": "",
        "data_transacao": None,
        "valor_total": 0,
        "valor_recursos_proprios": 0,
        "eh_despesa_sem_comprovacao_fiscal": True,
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
                "valor_rateio": 0,
                "quantidade_itens_capital": 0,
                "valor_item_capital": 0,
                "numero_processo_incorporacao_capital": ""
            }
        ]
    }
    return payload

@pytest.fixture
def payload_despesa_status_completo_eh_despesa_sem_comprovacao_fiscal(
    associacao,
    conta_associacao,
    acao_associacao,
):
    payload = {
        "associacao": f'{associacao.uuid}',
        "tipo_documento": None,
        "tipo_transacao": None,
        "numero_documento": "",
        "data_documento": None,
        "cpf_cnpj_fornecedor": "",
        "nome_fornecedor": "",
        "data_transacao": "2022-03-05",
        "valor_total": 100,
        "valor_recursos_proprios": 0,
        "eh_despesa_sem_comprovacao_fiscal": True,
        "motivos_pagamento_antecipado": [],
        "outros_motivos_pagamento_antecipado": "",
        "rateios": [
            {
                "associacao": f'{associacao.uuid}',
                "conta_associacao": f'{conta_associacao.uuid}',
                "acao_associacao": f'{acao_associacao.uuid}',
                "aplicacao_recurso": "CUSTEIO",
                "tipo_custeio": None,
                "especificacao_material_servico": None,
                "valor_rateio": 100,
                "quantidade_itens_capital": 0,
                "valor_item_capital": 0,
                "numero_processo_incorporacao_capital": ""
            }
        ]
    }
    return payload


@pytest.fixture
def tapi_periodo_2019_2():
    return baker.make(
        'Periodo',
        referencia='2019.2',
        data_inicio_realizacao_despesas=date(2019, 9, 1),
        data_fim_realizacao_despesas=date(2019, 11, 30),
    )


@pytest.fixture
def tapi_despesa(associacao, tipo_documento, tipo_transacao, tapi_periodo_2019_2):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=date(2019, 9, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=date(2019, 9, 10),
        valor_total=100.00,
    )


@pytest.fixture
def tapi_rateio_despesa_capital(associacao, tapi_despesa, conta_associacao, tipo_aplicacao_recurso, tipo_custeio, especificacao_material_servico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=tapi_despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso,
        tipo_custeio=tipo_custeio,
        especificacao_material_servico=especificacao_material_servico,
        valor_rateio=100.00,
        quantidade_itens_capital=2,
        valor_item_capital=50.00,
        numero_processo_incorporacao_capital='Teste123456'

    )


@pytest.fixture
def tapi_rateio_despesa_estornada(associacao, tapi_despesa, conta_associacao, tipo_aplicacao_recurso, tipo_custeio, especificacao_material_servico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=tapi_despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso,
        tipo_custeio=tipo_custeio,
        especificacao_material_servico=especificacao_material_servico,
        valor_rateio=100.00,
        quantidade_itens_capital=2,
        valor_item_capital=50.00,
        numero_processo_incorporacao_capital='Teste123456'

    )

@pytest.fixture
def tapi_tipo_receita_estorno(tipo_conta):
    return baker.make('TipoReceita', nome='Estorno', e_estorno=True, tipos_conta=[tipo_conta])


@pytest.fixture
def tapi_receita_estorno(tapi_tipo_receita_estorno, tapi_rateio_despesa_estornada):
    rateio = tapi_rateio_despesa_estornada
    return baker.make(
        'Receita',
        associacao=rateio.despesa.associacao,
        data=rateio.despesa.data_transacao,
        valor=rateio.valor_rateio,
        conta_associacao=rateio.conta_associacao,
        acao_associacao=rateio.acao_associacao,
        tipo_receita=tapi_tipo_receita_estorno,
        conferido=True,
        categoria_receita=rateio.aplicacao_recurso,
        rateio_estornado=rateio
    )


@pytest.fixture
def tapi_prestacao_conta_da_despesa(tapi_periodo_2019_2, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=tapi_periodo_2019_2,
        associacao=associacao,
    )


@pytest.fixture
def tapi_despesa_imposto(
    associacao,
    tipo_documento,
    tipo_transacao,
    tapi_periodo_2019_2
):
    return baker.make(
        'Despesa',
        associacao=associacao,
        tipo_documento=tipo_documento,
        tipo_transacao=tipo_transacao,
        data_documento=date(2019, 9, 10),
        data_transacao=date(2019, 9, 10),
    )


@pytest.fixture
def tapi_rateio_despesa_imposto(associacao, tipo_custeio, especificacao_material_servico, acao_associacao,
                                conta_associacao, tapi_despesa_imposto):
    return baker.make(
        'RateioDespesa',
        despesa=tapi_despesa_imposto,
        tipo_custeio=tipo_custeio,
        especificacao_material_servico=especificacao_material_servico,
        acao_associacao=acao_associacao,
        aplicacao_recurso="CUSTEIO",
        associacao=associacao,
        conta_associacao=conta_associacao,
        valor_original=222,
        valor_rateio=222
    )


@pytest.fixture
def tapi_despesa_com_imposto(associacao, tipo_documento, tipo_transacao, tapi_periodo_2019_2, tapi_despesa_imposto):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=date(2019, 9, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=date(2019, 9, 10),
        valor_total=100.00,
        despesas_impostos=[tapi_despesa_imposto, ]
    )


@pytest.fixture
def tapi_rateio_despesa_com_imposto(associacao, tapi_despesa_com_imposto, conta_associacao, tipo_aplicacao_recurso, tipo_custeio, especificacao_material_servico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=tapi_despesa_com_imposto,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso,
        tipo_custeio=tipo_custeio,
        especificacao_material_servico=especificacao_material_servico,
        valor_rateio=100.00,
        quantidade_itens_capital=2,
        valor_item_capital=50.00,
        numero_processo_incorporacao_capital='Teste123456'

    )
