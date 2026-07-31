"""
Testes para DespesaService, em especial a correção CAPITAL→CUSTEIO.
"""
import datetime

import pytest
from rest_framework import serializers

from sme_ptrf_apps.despesas.services.despesa_service import DespesaService
from sme_ptrf_apps.despesas.status_cadastro_completo import STATUS_COMPLETO, STATUS_INCOMPLETO
from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL, APLICACAO_CUSTEIO

from sme_ptrf_apps.core.models import (
    PrestacaoConta,
    AnaliseLancamentoPrestacaoConta,
    TipoAcertoLancamento,
    SolicitacaoAcertoLancamento,
)


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


@pytest.fixture
def despesa_conciliada_com_rateio(
    despesa_factory,
    rateio_despesa_factory,
    associacao,
    tipo_documento,
    tipo_transacao,
    conta_associacao,
    acao_associacao,
    prestacao_conta_devolvida,
):

    despesa = despesa_factory(
        associacao=prestacao_conta_devolvida.associacao,
        numero_documento='123456',
        data_documento=prestacao_conta_devolvida.periodo.data_inicio_realizacao_despesas,
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        documento_transacao='',
        data_transacao=prestacao_conta_devolvida.periodo.data_inicio_realizacao_despesas,
        valor_total=100.00,
        retem_imposto=True,
        valor_recursos_proprios=0,
        eh_despesa_sem_comprovacao_fiscal=False,
    )

    rateio_despesa_factory.create(
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso="CUSTEIO",
        valor_rateio=25000,
        valor_original=25000,
        status="COMPLETO",
        conferido=True,
        update_conferido=True,
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


def test_update_recalcula_status_de_rateio_incompleto_ao_preencher_campos_capital(
    despesa_com_rateio_custeio,
    associacao,
    conta_associacao,
    acao_associacao,
    especificacao_capital,
):
    """
    Regressão: rateio atualizado por QuerySet.update() mantinha status INCOMPLETO
    mesmo após preencher todos os campos obrigatórios de CAPITAL.
    """
    despesa = despesa_com_rateio_custeio
    rateio = despesa.rateios.first()

    rateio.__class__.objects.filter(uuid=rateio.uuid).update(status=STATUS_INCOMPLETO)
    despesa.atualiza_status()
    rateio.refresh_from_db()
    despesa.refresh_from_db()

    assert rateio.status == STATUS_INCOMPLETO
    assert despesa.status == STATUS_INCOMPLETO

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
    rateio_atualizado.refresh_from_db()
    despesa.refresh_from_db()

    assert rateio_atualizado.status == STATUS_COMPLETO
    assert despesa.status == STATUS_COMPLETO


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


def test_update_imposto_herda_conciliacao_quando_pc_devolvida(
    tipo_documento,
    despesa_conciliada_com_rateio,
):
    despesa = despesa_conciliada_com_rateio

    rateio_origem = (
        despesa.rateios
        .order_by("periodo_conciliacao")
        .last()
    )

    validated_data = {
        "despesas_impostos": [
            {
                "tipo_documento": tipo_documento,
                "valor_total": 10,
                "rateios": [
                    {
                        "valor_rateio": 10,
                        "conferido": False,
                    }
                ],
            }
        ]
    }

    DespesaService._processar_impostos_update(
        despesa,
        validated_data["despesas_impostos"],
    )

    despesa.refresh_from_db()

    assert despesa.despesas_impostos.exists()
    despesa_imposto = despesa.despesas_impostos.first()
    rateio_imposto = despesa_imposto.rateios.first()
    assert despesa_imposto is not None

    assert rateio_imposto.conferido is True
    assert (
        rateio_imposto.periodo_conciliacao_id ==
        rateio_origem.periodo_conciliacao_id
    )


def criar_cenario_marcar_lancamento_como_atualizado(
    prestacao_conta_factory,
    solicitacao_acerto_lancamento_factory,
    analise_prestacao_conta_factory,
    tipo_acerto_lancamento_factory,
    analise_lancamento_prestacao_conta_factory,
    despesa_factory,
    associacao,
    periodo_2020_2,
    status_prestacao=PrestacaoConta.STATUS_DEVOLVIDA,
    lancamento_atualizado=False,
):
    prestacao_conta_factory(
        status=status_prestacao,
        periodo=periodo_2020_2,
        associacao=associacao,
    )

    analise_prestacao = analise_prestacao_conta_factory()

    tipo_acerto = tipo_acerto_lancamento_factory(
        categoria=TipoAcertoLancamento.CATEGORIA_EDICAO_LANCAMENTO
    )

    despesa = despesa_factory(
        associacao=associacao,
        numero_documento="123456",
        cpf_cnpj_fornecedor="11.478.276/0001-04",
        data_transacao=periodo_2020_2.data_inicio_realizacao_despesas + datetime.timedelta(days=3),
        data_documento=periodo_2020_2.data_inicio_realizacao_despesas + datetime.timedelta(days=3),
        nome_fornecedor="Fornecedor SA",
        valor_total=50.00,
        valor_recursos_proprios=0,
    )

    analise_lancamento = analise_lancamento_prestacao_conta_factory(
        analise_prestacao_conta=analise_prestacao,
        despesa=despesa,
        lancamento_atualizado=lancamento_atualizado,
        tipo_lancamento=AnaliseLancamentoPrestacaoConta.TIPO_LANCAMENTO_GASTO,
        status_realizacao=AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE,
    )

    solicitacao_acerto_lancamento_factory(
        analise_lancamento=analise_lancamento,
        tipo_acerto=tipo_acerto,
        status_realizacao=SolicitacaoAcertoLancamento.STATUS_REALIZACAO_PENDENTE,
    )

    return despesa, analise_lancamento


def test_marca_lancamento_como_atualizado_quando_tudo_ok(
    prestacao_conta_factory,
    solicitacao_acerto_lancamento_factory,
    analise_prestacao_conta_factory,
    tipo_acerto_lancamento_factory,
    analise_lancamento_prestacao_conta_factory,
    despesa_factory,
    associacao,
    periodo_2020_2,
):
    despesa, analise_lancamento = criar_cenario_marcar_lancamento_como_atualizado(
        prestacao_conta_factory,
        solicitacao_acerto_lancamento_factory,
        analise_prestacao_conta_factory,
        tipo_acerto_lancamento_factory,
        analise_lancamento_prestacao_conta_factory,
        despesa_factory,
        associacao,
        periodo_2020_2,
        status_prestacao=PrestacaoConta.STATUS_DEVOLVIDA,
        lancamento_atualizado=False,
    )

    assert not analise_lancamento.lancamento_atualizado

    DespesaService._marcar_lancamento_como_atualizado(despesa)

    analise_lancamento.refresh_from_db()

    assert analise_lancamento.lancamento_atualizado


def test_marca_lancamento_como_atualizado_quando_lancamento_atualizado(
    prestacao_conta_factory,
    solicitacao_acerto_lancamento_factory,
    analise_prestacao_conta_factory,
    tipo_acerto_lancamento_factory,
    analise_lancamento_prestacao_conta_factory,
    despesa_factory,
    associacao,
    periodo_2020_2
):
    despesa, analise_lancamento = criar_cenario_marcar_lancamento_como_atualizado(
        prestacao_conta_factory,
        solicitacao_acerto_lancamento_factory,
        analise_prestacao_conta_factory,
        tipo_acerto_lancamento_factory,
        analise_lancamento_prestacao_conta_factory,
        despesa_factory,
        associacao,
        periodo_2020_2,
        status_prestacao=PrestacaoConta.STATUS_DEVOLVIDA,
        lancamento_atualizado=True,
    )

    DespesaService._marcar_lancamento_como_atualizado(despesa)

    analise_lancamento.refresh_from_db()

    assert analise_lancamento.lancamento_atualizado


def test_nao_marca_lancamento_quando_prestacao_em_analise(
    prestacao_conta_factory,
    solicitacao_acerto_lancamento_factory,
    analise_prestacao_conta_factory,
    tipo_acerto_lancamento_factory,
    analise_lancamento_prestacao_conta_factory,
    despesa_factory,
    associacao,
    periodo_2020_2
):
    despesa, analise_lancamento = criar_cenario_marcar_lancamento_como_atualizado(
        prestacao_conta_factory,
        solicitacao_acerto_lancamento_factory,
        analise_prestacao_conta_factory,
        tipo_acerto_lancamento_factory,
        analise_lancamento_prestacao_conta_factory,
        despesa_factory,
        associacao,
        periodo_2020_2,
        status_prestacao=PrestacaoConta.STATUS_EM_ANALISE,
        lancamento_atualizado=False,
    )

    DespesaService._marcar_lancamento_como_atualizado(despesa)

    analise_lancamento.refresh_from_db()

    assert not analise_lancamento.lancamento_atualizado


def criar_cenario_marcar_lancamento_como_excluido(
    prestacao_conta_factory,
    solicitacao_acerto_lancamento_factory,
    analise_prestacao_conta_factory,
    tipo_acerto_lancamento_factory,
    analise_lancamento_prestacao_conta_factory,
    despesa_factory,
    associacao,
    periodo_2020_2,
    status_prestacao=PrestacaoConta.STATUS_DEVOLVIDA,
    lancamento_excluido=False,
):
    prestacao_conta_factory(
        status=status_prestacao,
        periodo=periodo_2020_2,
        associacao=associacao,
    )

    analise_prestacao = analise_prestacao_conta_factory()
    tipo_acerto = tipo_acerto_lancamento_factory(
        categoria=TipoAcertoLancamento.CATEGORIA_EXCLUSAO_LANCAMENTO
    )
    despesa = despesa_factory(
        associacao=associacao,
        numero_documento="654321",
        cpf_cnpj_fornecedor="11.478.276/0001-04",
        data_transacao=periodo_2020_2.data_inicio_realizacao_despesas + datetime.timedelta(days=3),
        data_documento=periodo_2020_2.data_inicio_realizacao_despesas + datetime.timedelta(days=3),
        nome_fornecedor="Fornecedor SA",
        valor_total=50.00,
        valor_recursos_proprios=0,
    )
    analise_lancamento = analise_lancamento_prestacao_conta_factory(
        analise_prestacao_conta=analise_prestacao,
        despesa=despesa,
        lancamento_excluido=lancamento_excluido,
        tipo_lancamento=AnaliseLancamentoPrestacaoConta.TIPO_LANCAMENTO_GASTO,
        status_realizacao=AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE,
    )
    solicitacao_acerto_lancamento_factory(
        analise_lancamento=analise_lancamento,
        tipo_acerto=tipo_acerto,
        status_realizacao=SolicitacaoAcertoLancamento.STATUS_REALIZACAO_PENDENTE,
    )
    return despesa, analise_lancamento


def test_marca_lancamento_como_excluido_com_flag(
    prestacao_conta_factory,
    solicitacao_acerto_lancamento_factory,
    analise_prestacao_conta_factory,
    tipo_acerto_lancamento_factory,
    analise_lancamento_prestacao_conta_factory,
    despesa_factory,
    associacao,
    periodo_2020_2,
    flag_factory,
):
    flag_factory.create(name="despesas-pipeline", everyone=True)
    despesa, analise_lancamento = criar_cenario_marcar_lancamento_como_excluido(
        prestacao_conta_factory,
        solicitacao_acerto_lancamento_factory,
        analise_prestacao_conta_factory,
        tipo_acerto_lancamento_factory,
        analise_lancamento_prestacao_conta_factory,
        despesa_factory,
        associacao,
        periodo_2020_2,
    )

    assert not analise_lancamento.lancamento_excluido

    DespesaService._marcar_lancamento_como_excluido(despesa)

    analise_lancamento.refresh_from_db()
    assert analise_lancamento.lancamento_excluido


def test_nao_marca_lancamento_excluido_sem_flag(
    prestacao_conta_factory,
    solicitacao_acerto_lancamento_factory,
    analise_prestacao_conta_factory,
    tipo_acerto_lancamento_factory,
    analise_lancamento_prestacao_conta_factory,
    despesa_factory,
    associacao,
    periodo_2020_2,
):
    despesa, analise_lancamento = criar_cenario_marcar_lancamento_como_excluido(
        prestacao_conta_factory,
        solicitacao_acerto_lancamento_factory,
        analise_prestacao_conta_factory,
        tipo_acerto_lancamento_factory,
        analise_lancamento_prestacao_conta_factory,
        despesa_factory,
        associacao,
        periodo_2020_2,
    )

    DespesaService._marcar_lancamento_como_excluido(despesa)

    analise_lancamento.refresh_from_db()
    assert not analise_lancamento.lancamento_excluido

