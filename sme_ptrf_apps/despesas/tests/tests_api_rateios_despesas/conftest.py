import pytest
import datetime

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
        "numero_documento": "634767",
        "data_documento": "2020-03-10",
        "cpf_cnpj_fornecedor": "36.352.197/0001-75",
        "nome_fornecedor": "FORNECEDOR TESTE SA",
        "data_transacao": "2020-03-10",
        "valor_total": 11000.50,
        "valor_recursos_proprios": 1000.50,
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
        "rateios": []
    }
    return payload


@pytest.fixture
def payload_despesa_valida_anterior_periodo_inicial(
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
        "numero_documento": "634767",
        "data_documento": "2000-03-10", # Data anterior ao período inicial da associação
        "cpf_cnpj_fornecedor": "36.352.197/0001-75",
        "nome_fornecedor": "FORNECEDOR TESTE SA",
        "data_transacao": "2000-03-10",
        "valor_total": 11000.50,
        "valor_recursos_proprios": 1000.50,
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
def payload_despesa_justa(
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
        "numero_documento": "634767",
        "data_documento": "2020-03-10",
        "cpf_cnpj_fornecedor": "36.352.197/0001-75",
        "nome_fornecedor": "FORNECEDOR TESTE SA",
        "data_transacao": "2020-03-10",
        "valor_total": 110.50,
        "valor_recursos_proprios": 10.50,
        "rateios": [
            {
                "associacao": f'{associacao.uuid}',
                "conta_associacao": f'{conta_associacao.uuid}',
                "acao_associacao": f'{acao_associacao.uuid}',
                "aplicacao_recurso": tipo_aplicacao_recurso,
                "tipo_custeio": tipo_custeio.id,
                "especificacao_material_servico": especificacao_material_servico.id,
                "valor_rateio": 100.00,
                "quantidade_itens_capital": 2,
                "valor_item_capital": 50.00,
                "numero_processo_incorporacao_capital": "6234673223462364632"
            }
        ]
    }
    return payload


@pytest.fixture
def despesa_justa(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2020, 3, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        documento_transacao='',
        data_transacao=datetime.date(2020, 3, 10),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
        valor_original=90.00,
    )

@pytest.fixture
def rateio_despesa_justa(associacao, despesa_justa, conta_associacao, acao, tipo_aplicacao_recurso, tipo_custeio,
                         especificacao_material_servico, acao_associacao, periodo_2020_1):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_justa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso,
        tipo_custeio=tipo_custeio,
        especificacao_material_servico=especificacao_material_servico,
        valor_rateio=100.00,
        quantidade_itens_capital=2,
        valor_item_capital=50.00,
        numero_processo_incorporacao_capital='Teste123456',
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=periodo_2020_1,
        valor_original=90.00,
    )

@pytest.fixture
def fechamento_periodo_com_saldo_justo(periodo_2020_1, associacao, conta_associacao, acao_associacao, ):
    from sme_ptrf_apps.core.models import STATUS_FECHADO
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_capital=0,
        total_repasses_capital=0,
        total_despesas_capital=0,
        total_receitas_custeio=100,
        total_repasses_custeio=100,
        total_despesas_custeio=100,
        status=STATUS_FECHADO
    )

@pytest.fixture
def fechamento_periodo_com_saldo_justo_outra_acao(periodo_2020_1, associacao, conta_associacao, acao_associacao_role_cultural, ):
    from sme_ptrf_apps.core.models import STATUS_FECHADO
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        fechamento_anterior=None,
        total_receitas_capital=0,
        total_repasses_capital=0,
        total_despesas_capital=0,
        total_receitas_custeio=100,
        total_repasses_custeio=100,
        total_despesas_custeio=0,
        status=STATUS_FECHADO
    )

@pytest.fixture
def payload_despesa_maior(
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
        "numero_documento": "634767",
        "data_documento": "2020-03-10",
        "cpf_cnpj_fornecedor": "36.352.197/0001-75",
        "nome_fornecedor": "FORNECEDOR TESTE SA",
        "data_transacao": "2020-03-10",
        "valor_total": 112.50,
        "valor_recursos_proprios": 10.50,
        "rateios": [
            {
                "associacao": f'{associacao.uuid}',
                "conta_associacao": f'{conta_associacao.uuid}',
                "acao_associacao": f'{acao_associacao.uuid}',
                "aplicacao_recurso": tipo_aplicacao_recurso,
                "tipo_custeio": tipo_custeio.id,
                "especificacao_material_servico": especificacao_material_servico.id,
                "valor_rateio": 102.00,
                "quantidade_itens_capital": 2,
                "valor_item_capital": 51.00,
                "numero_processo_incorporacao_capital": "6234673223462364632"
            }
        ]
    }
    return payload
