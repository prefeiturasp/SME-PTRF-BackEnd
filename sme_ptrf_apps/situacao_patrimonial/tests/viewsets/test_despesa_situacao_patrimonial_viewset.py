import pytest
from rest_framework import status
from sme_ptrf_apps.despesas.models.despesa import Despesa

pytestmark = pytest.mark.django_db


@pytest.fixture
def response_situacao_patrimonial(jwt_authenticated_client_sme, bem_produzido_despesa_1, flag_situacao_patrimonial, bem_produzido_rateio_1):
    url = f"/api/despesa-situacao-patrimonial/?associacao__uuid={bem_produzido_despesa_1.bem_produzido.associacao.uuid}"
    return jwt_authenticated_client_sme.get(url)


def test_get_sucesso(response_situacao_patrimonial):
    """Testa se a resposta retorna com sucesso e contém apenas um resultado."""
    content = response_situacao_patrimonial.data

    assert response_situacao_patrimonial.status_code == status.HTTP_200_OK, \
        f"Status esperado 200, obtido {response_situacao_patrimonial.status_code}"

    assert content["count"] == 1, f"Esperado count == 1, obtido {content['count']}"
    assert len(content["results"]) == 1, f"Esperado 1 resultado, obtido {len(content['results'])}"


def test_assert_valor_utilizado(response_situacao_patrimonial):
    """Verifica se o valor utilizado no rateio está correto."""
    valor_utilizado = response_situacao_patrimonial.data["results"][0]["rateios"][0]["valor_utilizado"]
    assert valor_utilizado == 120.0, f"Esperado valor_utilizado == 120.0, obtido {valor_utilizado}"


def test_assert_valor_disponivel(response_situacao_patrimonial):
    """Verifica se o valor disponível no rateio está correto."""
    valor_disponivel = response_situacao_patrimonial.data["results"][0]["rateios"][0]["valor_disponivel"]
    assert valor_disponivel == 80.0, f"Esperado valor_disponivel == 80.0, obtido {valor_disponivel}"


def test_queryset_exclui_despesas_ja_vinculadas(
    jwt_authenticated_client_sme,
    flag_situacao_patrimonial,
    bem_produzido_despesa_1
):
    bem = bem_produzido_despesa_1.bem_produzido
    url = f"/api/despesa-situacao-patrimonial/?associacao__uuid={bem.associacao.uuid}&bem_produzido_uuid={bem.uuid}"
    resp = jwt_authenticated_client_sme.get(url)
    uuids = [r['uuid'] for r in resp.data['results']]
    assert str(bem_produzido_despesa_1.despesa.uuid) not in uuids


def test_listagem_exclui_despesas_incompletas_e_ordena_por_data_documento_desc(
    jwt_authenticated_client_sme,
    flag_situacao_patrimonial,
    associacao_1,
    despesa_factory
):
    d_old = despesa_factory(associacao=associacao_1, data_documento='2024-01-01', status='ATIVO')
    d_new = despesa_factory(associacao=associacao_1, data_documento='2024-02-01', status='ATIVO')
    d_incompleto = despesa_factory(
        associacao=associacao_1,
        data_documento='2024-03-01',
        data_transacao=None,
        valor_total=0,
        nome_fornecedor='',
        cpf_cnpj_fornecedor='',
        tipo_transacao=None,
        tipo_documento=None,
    )
    url = f"/api/despesa-situacao-patrimonial/?associacao__uuid={associacao_1.uuid}"
    resp = jwt_authenticated_client_sme.get(url)
    uuids = [r['uuid'] for r in resp.data['results']]
    datas = [r['data_documento'] for r in resp.data['results']]
    assert str(d_incompleto.uuid) not in uuids
    # Deve conter ambas despesas ativas e estar ordenado por data_documento desc
    assert d_new.data_documento in datas and d_old.data_documento in datas
    assert datas == sorted(datas, reverse=True)
