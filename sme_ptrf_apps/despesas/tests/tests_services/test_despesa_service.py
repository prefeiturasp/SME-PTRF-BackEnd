"""
Testes para DespesaService, em especial a correção CAPITAL→CUSTEIO.
"""
import datetime

import pytest
from rest_framework import serializers

from sme_ptrf_apps.despesas.services.despesa_service import DespesaService
from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL, APLICACAO_CUSTEIO

pytestmark = pytest.mark.django_db


@pytest.fixture
def despesa_com_rateio_capital(
    despesa_factory,
    rateio_despesa_factory,
    associacao,
    tipo_documento,
    tipo_transacao,
    conta_associacao,
    acao_associacao,
    tipo_aplicacao_recurso_capital,
    especificacao_capital,
):
    """Despesa com um único rateio do tipo CAPITAL."""
    despesa = despesa_factory(
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
        valor_recursos_proprios=0,
        eh_despesa_sem_comprovacao_fiscal=False,
    )
    rateio_despesa_factory(
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_capital,
        tipo_custeio=None,
        especificacao_material_servico=especificacao_capital,
        valor_rateio=100.00,
        quantidade_itens_capital=1,
        valor_item_capital=100.00,
        numero_processo_incorporacao_capital='123456',
    )
    return despesa


def _validated_data_base(despesa, associacao):
    return {
        "associacao": associacao,
        "tipo_documento": despesa.tipo_documento,
        "tipo_transacao": despesa.tipo_transacao,
        "numero_documento": despesa.numero_documento,
        "data_documento": despesa.data_documento,
        "data_transacao": despesa.data_transacao,
        "cpf_cnpj_fornecedor": despesa.cpf_cnpj_fornecedor,
        "nome_fornecedor": despesa.nome_fornecedor,
        "valor_total": 100.00,
        "valor_recursos_proprios": 0,
        "confirmar_limpeza_prioridades_paa": False,
    }


def test_update_capital_para_custeio_com_tipo_e_especificacao_sucesso(
    despesa_com_rateio_capital,
    associacao,
    conta_associacao,
    acao_associacao,
    tipo_custeio_servico,
    especificacao_custeio_servico,
):
    """
    Ao alterar CAPITAL→CUSTEIO com tipo_custeio e especificacao_material_servico
    preenchidos, a atualização deve ser concluída com sucesso.
    """
    despesa = despesa_com_rateio_capital
    rateio = despesa.rateios.first()
    assert rateio.aplicacao_recurso == APLICACAO_CAPITAL

    validated_data = {
        **_validated_data_base(despesa, associacao),
        "rateios": [
            {
                "uuid": str(rateio.uuid),
                "associacao": associacao,
                "conta_associacao": conta_associacao,
                "acao_associacao": acao_associacao,
                "aplicacao_recurso": APLICACAO_CUSTEIO,
                "tipo_custeio": tipo_custeio_servico,
                "especificacao_material_servico": especificacao_custeio_servico,
                "valor_rateio": 100.00,
            }
        ],
    }

    result = DespesaService.update(despesa, validated_data)

    rateio_atualizado = result.rateios.first()
    assert rateio_atualizado.aplicacao_recurso == APLICACAO_CUSTEIO
    assert rateio_atualizado.tipo_custeio == tipo_custeio_servico
    assert rateio_atualizado.especificacao_material_servico == especificacao_custeio_servico
    assert rateio_atualizado.numero_processo_incorporacao_capital == ""
    assert rateio_atualizado.quantidade_itens_capital == 0


def test_update_capital_para_custeio_sem_tipo_custeio_deve_falhar(
    despesa_com_rateio_capital,
    associacao,
    conta_associacao,
    acao_associacao,
    especificacao_custeio_servico,
):
    """
    Ao alterar CAPITAL→CUSTEIO sem tipo_custeio, deve retornar ValidationError.
    """
    despesa = despesa_com_rateio_capital
    rateio = despesa.rateios.first()

    validated_data = {
        **_validated_data_base(despesa, associacao),
        "rateios": [
            {
                "uuid": str(rateio.uuid),
                "associacao": associacao,
                "conta_associacao": conta_associacao,
                "acao_associacao": acao_associacao,
                "aplicacao_recurso": APLICACAO_CUSTEIO,
                "tipo_custeio": None,
                "especificacao_material_servico": especificacao_custeio_servico,
                "valor_rateio": 100.00,
            }
        ],
    }

    with pytest.raises(serializers.ValidationError) as exc_info:
        DespesaService.update(despesa, validated_data)

    assert "mensagem" in exc_info.value.detail
    assert "Capital para Custeio" in str(exc_info.value.detail["mensagem"])
    assert "Tipo de Custeio" in str(exc_info.value.detail["mensagem"])


def test_update_capital_para_custeio_sem_especificacao_deve_falhar(
    despesa_com_rateio_capital,
    associacao,
    conta_associacao,
    acao_associacao,
    tipo_custeio_servico,
):
    """
    Ao alterar CAPITAL→CUSTEIO sem especificacao_material_servico, deve retornar ValidationError.
    """
    despesa = despesa_com_rateio_capital
    rateio = despesa.rateios.first()

    validated_data = {
        **_validated_data_base(despesa, associacao),
        "rateios": [
            {
                "uuid": str(rateio.uuid),
                "associacao": associacao,
                "conta_associacao": conta_associacao,
                "acao_associacao": acao_associacao,
                "aplicacao_recurso": APLICACAO_CUSTEIO,
                "tipo_custeio": tipo_custeio_servico,
                "especificacao_material_servico": None,
                "valor_rateio": 100.00,
            }
        ],
    }

    with pytest.raises(serializers.ValidationError) as exc_info:
        DespesaService.update(despesa, validated_data)

    assert "mensagem" in exc_info.value.detail
    assert "Capital para Custeio" in str(exc_info.value.detail["mensagem"])
    assert "Especificação" in str(exc_info.value.detail["mensagem"])


def test_update_capital_para_custeio_sem_enviar_especificacao_no_payload_deve_falhar(
    despesa_com_rateio_capital,
    associacao,
    conta_associacao,
    acao_associacao,
    tipo_custeio_servico,
):
    """
    Ao alterar CAPITAL→CUSTEIO sem enviar especificacao_material_servico no payload
    (frontend mantém a antiga de Capital), deve retornar ValidationError.
    """
    despesa = despesa_com_rateio_capital
    rateio = despesa.rateios.first()
    # Simula payload que não inclui especificacao (chave omitida - frontend não envia)
    validated_data = {
        **_validated_data_base(despesa, associacao),
        "rateios": [
            {
                "uuid": str(rateio.uuid),
                "associacao": associacao,
                "conta_associacao": conta_associacao,
                "acao_associacao": acao_associacao,
                "aplicacao_recurso": APLICACAO_CUSTEIO,
                "tipo_custeio": tipo_custeio_servico,
                # especificacao_material_servico omitido - mantém a antiga de Capital
                "valor_rateio": 100.00,
            }
        ],
    }

    with pytest.raises(serializers.ValidationError) as exc_info:
        DespesaService.update(despesa, validated_data)

    assert "mensagem" in exc_info.value.detail
    msg = str(exc_info.value.detail["mensagem"])
    assert "Custeio" in msg
    assert "Capital" in msg


def test_update_capital_para_custeio_com_especificacao_de_capital_deve_falhar(
    despesa_com_rateio_capital,
    associacao,
    conta_associacao,
    acao_associacao,
    tipo_custeio_servico,
    especificacao_capital,
):
    """
    Ao alterar CAPITAL→CUSTEIO com especificacao_material_servico de Capital,
    deve retornar ValidationError. As especificações de Custeio são diferentes das de Capital.
    """
    despesa = despesa_com_rateio_capital
    rateio = despesa.rateios.first()

    validated_data = {
        **_validated_data_base(despesa, associacao),
        "rateios": [
            {
                "uuid": str(rateio.uuid),
                "associacao": associacao,
                "conta_associacao": conta_associacao,
                "acao_associacao": acao_associacao,
                "aplicacao_recurso": APLICACAO_CUSTEIO,
                "tipo_custeio": tipo_custeio_servico,
                "especificacao_material_servico": especificacao_capital,
                "valor_rateio": 100.00,
            }
        ],
    }

    with pytest.raises(serializers.ValidationError) as exc_info:
        DespesaService.update(despesa, validated_data)

    assert "mensagem" in exc_info.value.detail
    msg = str(exc_info.value.detail["mensagem"])
    assert "Especificação de Material ou Serviço de Custeio" in msg
    assert "especificação atual é de Capital" in msg or "especificação atual é de capital" in msg.lower()


def test_update_capital_para_custeio_eh_despesa_sem_comprovacao_fiscal_nao_exige_tipo_especificacao(
    despesa_factory,
    rateio_despesa_factory,
    associacao,
    tipo_documento,
    tipo_transacao,
    conta_associacao,
    acao_associacao,
    tipo_aplicacao_recurso_capital,
    especificacao_capital,
):
    """
    Despesa sem comprovação fiscal pode alterar CAPITAL→CUSTEIO sem tipo_custeio/especificacao.
    """
    despesa = despesa_factory(
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2020, 3, 10),
        tipo_documento=tipo_documento,
        tipo_transacao=tipo_transacao,
        data_transacao=datetime.date(2020, 3, 10),
        valor_total=100.00,
        eh_despesa_sem_comprovacao_fiscal=True,
    )
    rateio = rateio_despesa_factory(
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_capital,
        tipo_custeio=None,
        especificacao_material_servico=especificacao_capital,
        valor_rateio=100.00,
        quantidade_itens_capital=1,
        valor_item_capital=100.00,
        numero_processo_incorporacao_capital='123456',
    )

    validated_data = {
        "associacao": associacao,
        "tipo_documento": tipo_documento,
        "tipo_transacao": tipo_transacao,
        "numero_documento": "123456",
        "data_documento": datetime.date(2020, 3, 10),
        "data_transacao": datetime.date(2020, 3, 10),
        "cpf_cnpj_fornecedor": "",
        "nome_fornecedor": "",
        "valor_total": 100.00,
        "valor_recursos_proprios": 0,
        "confirmar_limpeza_prioridades_paa": False,
        "rateios": [
            {
                "uuid": str(rateio.uuid),
                "associacao": associacao,
                "conta_associacao": conta_associacao,
                "acao_associacao": acao_associacao,
                "aplicacao_recurso": APLICACAO_CUSTEIO,
                "tipo_custeio": None,
                "especificacao_material_servico": None,
                "valor_rateio": 100.00,
            }
        ],
    }

    result = DespesaService.update(despesa, validated_data)
    rateio_atualizado = result.rateios.first()
    assert rateio_atualizado.aplicacao_recurso == APLICACAO_CUSTEIO


@pytest.fixture
def despesa_com_rateio_custeio(
    despesa_factory,
    rateio_despesa_factory,
    associacao,
    tipo_documento,
    tipo_transacao,
    conta_associacao,
    acao_associacao,
    tipo_aplicacao_recurso_custeio,
    tipo_custeio_servico,
    especificacao_custeio_servico,
):
    """Despesa com um único rateio do tipo CUSTEIO."""
    despesa = despesa_factory(
        associacao=associacao,
        numero_documento='654321',
        data_documento=datetime.date(2020, 3, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        documento_transacao='',
        data_transacao=datetime.date(2020, 3, 10),
        valor_total=100.00,
        valor_recursos_proprios=0,
        eh_despesa_sem_comprovacao_fiscal=False,
    )
    rateio_despesa_factory(
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_custeio_servico,
        valor_rateio=100.00,
        quantidade_itens_capital=0,
        valor_item_capital=0,
        numero_processo_incorporacao_capital='',
    )
    return despesa


def test_update_custeio_para_capital_com_especificacao_capital_sucesso(
    despesa_com_rateio_custeio,
    associacao,
    conta_associacao,
    acao_associacao,
    especificacao_capital,
):
    """
    Ao alterar CUSTEIO→CAPITAL com especificacao de Capital e campos de capital
    preenchidos, a atualização deve ser concluída com sucesso.
    """
    despesa = despesa_com_rateio_custeio
    rateio = despesa.rateios.first()
    assert rateio.aplicacao_recurso == APLICACAO_CUSTEIO

    validated_data = {
        **_validated_data_base(despesa, associacao),
        "rateios": [
            {
                "uuid": str(rateio.uuid),
                "associacao": associacao,
                "conta_associacao": conta_associacao,
                "acao_associacao": acao_associacao,
                "aplicacao_recurso": APLICACAO_CAPITAL,
                "tipo_custeio": None,
                "especificacao_material_servico": especificacao_capital,
                "valor_rateio": 100.00,
                "quantidade_itens_capital": 2,
                "valor_item_capital": 50.00,
                "numero_processo_incorporacao_capital": "2020/123456",
            }
        ],
    }

    result = DespesaService.update(despesa, validated_data)
    rateio_atualizado = result.rateios.first()
    assert rateio_atualizado.aplicacao_recurso == APLICACAO_CAPITAL
    assert rateio_atualizado.especificacao_material_servico == especificacao_capital
    assert rateio_atualizado.quantidade_itens_capital == 2
    assert rateio_atualizado.valor_item_capital == 50.00
    assert rateio_atualizado.numero_processo_incorporacao_capital == "2020/123456"


def test_update_custeio_para_capital_com_especificacao_de_custeio_deve_falhar(
    despesa_com_rateio_custeio,
    associacao,
    conta_associacao,
    acao_associacao,
    especificacao_custeio_servico,
):
    """
    Ao alterar CUSTEIO→CAPITAL com especificacao_material_servico de Custeio,
    deve retornar ValidationError. As especificações de Capital são diferentes das de Custeio.
    """
    despesa = despesa_com_rateio_custeio
    rateio = despesa.rateios.first()

    validated_data = {
        **_validated_data_base(despesa, associacao),
        "rateios": [
            {
                "uuid": str(rateio.uuid),
                "associacao": associacao,
                "conta_associacao": conta_associacao,
                "acao_associacao": acao_associacao,
                "aplicacao_recurso": APLICACAO_CAPITAL,
                "tipo_custeio": None,
                "especificacao_material_servico": especificacao_custeio_servico,
                "valor_rateio": 100.00,
                "quantidade_itens_capital": 2,
                "valor_item_capital": 50.00,
                "numero_processo_incorporacao_capital": "2020/123456",
            }
        ],
    }

    with pytest.raises(serializers.ValidationError) as exc_info:
        DespesaService.update(despesa, validated_data)

    assert "mensagem" in exc_info.value.detail
    msg = str(exc_info.value.detail["mensagem"])
    assert "Especificação de Material ou Serviço de Capital" in msg
    assert "especificação atual é de Custeio" in msg or "especificação atual é de custeio" in msg.lower()


def test_update_custeio_para_capital_sem_quantidade_valor_sucesso(
    despesa_com_rateio_custeio,
    associacao,
    conta_associacao,
    acao_associacao,
    especificacao_capital,
):
    """
    Ao alterar CUSTEIO→CAPITAL com quantidade_itens_capital=0 e valor_item_capital=0,
    a atualização é concluída com sucesso (validação desses campos não é feita no service).
    """
    despesa = despesa_com_rateio_custeio
    rateio = despesa.rateios.first()

    validated_data = {
        **_validated_data_base(despesa, associacao),
        "rateios": [
            {
                "uuid": str(rateio.uuid),
                "associacao": associacao,
                "conta_associacao": conta_associacao,
                "acao_associacao": acao_associacao,
                "aplicacao_recurso": APLICACAO_CAPITAL,
                "tipo_custeio": None,
                "especificacao_material_servico": especificacao_capital,
                "valor_rateio": 100.00,
                "quantidade_itens_capital": 0,
                "valor_item_capital": 0,
                "numero_processo_incorporacao_capital": "2020/123456",
            }
        ],
    }

    result = DespesaService.update(despesa, validated_data)
    rateio_atualizado = result.rateios.first()
    assert rateio_atualizado.aplicacao_recurso == APLICACAO_CAPITAL
    assert rateio_atualizado.especificacao_material_servico == especificacao_capital
    assert rateio_atualizado.quantidade_itens_capital == 0
    assert rateio_atualizado.valor_item_capital == 0


def test_update_custeio_para_capital_sem_numero_processo_sucesso(
    despesa_com_rateio_custeio,
    associacao,
    conta_associacao,
    acao_associacao,
    especificacao_capital,
):
    """
    Ao alterar CUSTEIO→CAPITAL sem numero_processo_incorporacao_capital (vazio),
    a atualização é concluída com sucesso (validação desse campo não é feita no service).
    """
    despesa = despesa_com_rateio_custeio
    rateio = despesa.rateios.first()

    validated_data = {
        **_validated_data_base(despesa, associacao),
        "rateios": [
            {
                "uuid": str(rateio.uuid),
                "associacao": associacao,
                "conta_associacao": conta_associacao,
                "acao_associacao": acao_associacao,
                "aplicacao_recurso": APLICACAO_CAPITAL,
                "tipo_custeio": None,
                "especificacao_material_servico": especificacao_capital,
                "valor_rateio": 100.00,
                "quantidade_itens_capital": 2,
                "valor_item_capital": 50.00,
                "numero_processo_incorporacao_capital": "",
            }
        ],
    }

    result = DespesaService.update(despesa, validated_data)
    rateio_atualizado = result.rateios.first()
    assert rateio_atualizado.aplicacao_recurso == APLICACAO_CAPITAL
    assert rateio_atualizado.especificacao_material_servico == especificacao_capital
    assert rateio_atualizado.numero_processo_incorporacao_capital == ""


def test_update_custeio_para_capital_eh_despesa_sem_comprovacao_fiscal_nao_exige_especificacao_capital(
    despesa_factory,
    rateio_despesa_factory,
    associacao,
    tipo_documento,
    tipo_transacao,
    conta_associacao,
    acao_associacao,
    tipo_aplicacao_recurso_custeio,
    tipo_custeio_servico,
    especificacao_custeio_servico,
):
    """
    Despesa sem comprovação fiscal pode alterar CUSTEIO→CAPITAL sem especificação de Capital
    e sem campos de capital (quantidade, valor, número processo).
    """
    despesa = despesa_factory(
        associacao=associacao,
        numero_documento='789012',
        data_documento=datetime.date(2020, 3, 10),
        tipo_documento=tipo_documento,
        tipo_transacao=tipo_transacao,
        data_transacao=datetime.date(2020, 3, 10),
        valor_total=100.00,
        eh_despesa_sem_comprovacao_fiscal=True,
    )
    rateio = rateio_despesa_factory(
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_custeio_servico,
        valor_rateio=100.00,
        quantidade_itens_capital=0,
        valor_item_capital=0,
        numero_processo_incorporacao_capital='',
    )

    validated_data = {
        "associacao": associacao,
        "tipo_documento": tipo_documento,
        "tipo_transacao": tipo_transacao,
        "numero_documento": "789012",
        "data_documento": datetime.date(2020, 3, 10),
        "data_transacao": datetime.date(2020, 3, 10),
        "cpf_cnpj_fornecedor": "",
        "nome_fornecedor": "",
        "valor_total": 100.00,
        "valor_recursos_proprios": 0,
        "confirmar_limpeza_prioridades_paa": False,
        "rateios": [
            {
                "uuid": str(rateio.uuid),
                "associacao": associacao,
                "conta_associacao": conta_associacao,
                "acao_associacao": acao_associacao,
                "aplicacao_recurso": APLICACAO_CAPITAL,
                "tipo_custeio": None,
                "especificacao_material_servico": None,
                "valor_rateio": 100.00,
                "quantidade_itens_capital": 0,
                "valor_item_capital": 0,
                "numero_processo_incorporacao_capital": "",
            }
        ],
    }

    result = DespesaService.update(despesa, validated_data)
    rateio_atualizado = result.rateios.first()
    assert rateio_atualizado.aplicacao_recurso == APLICACAO_CAPITAL
