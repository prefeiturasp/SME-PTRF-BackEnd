import datetime

import pytest
from model_bakery import baker
from rest_framework import status

from sme_ptrf_apps.core.choices import StatusTag

pytestmark = pytest.mark.django_db


@pytest.fixture
def tag_1():
    return baker.make(
        'Tag',
        id=1,
        nome="TAG TESTE 1",
        status=StatusTag.ATIVO.name
    )


@pytest.fixture
def tag_2():
    return baker.make(
        'Tag',
        id=2,
        nome="TAG TESTE 2",
        status=StatusTag.ATIVO.name
    )


@pytest.fixture
def tag_teste_filtro_por_tag():
    return baker.make(
        'Tag',
        nome="COVID-19",
        status=StatusTag.ATIVO.name
    )


@pytest.fixture
def _despesa_factory(despesa_factory, associacao, tipo_documento, tipo_transacao):
    def _factory(**kwargs):
        defaults = dict(
            associacao=associacao,
            tipo_documento=tipo_documento,
            tipo_transacao=tipo_transacao,
            data_documento=datetime.date(2020, 3, 10),
            data_transacao=datetime.date(2020, 3, 10),
            valor_total=100,
            valor_recursos_proprios=10,
        )
        defaults.update(kwargs)
        return despesa_factory(**defaults)
    return _factory


@pytest.fixture
def rateio_factory(associacao, conta_associacao, acao_associacao_ptrf):
    def _factory(despesa, tag=None, **kwargs):
        return baker.make(
            "RateioDespesa",
            despesa=despesa,
            associacao=associacao,
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao_ptrf,
            conferido=True,
            tag=tag,
            **kwargs,
        )
    return _factory


def get_despesas(client, **params):
    query = "&".join(f"{k}={v}" for k, v in params.items())
    response = client.get(f"/api/despesas/?{query}", content_type="application/json")
    assert response.status_code == status.HTTP_200_OK
    return response.json()["results"]


@pytest.mark.parametrize(
    "cpf_cnpj, esperado",
    [
        ("11.478.276/0001-04", 1),
        ("517.870.110-03", 1),
        ("00000000000", 0),
    ],
)
def test_filtro_por_cpf_cnpj_fornecedor(
    jwt_authenticated_client_d,
    _despesa_factory,
    rateio_factory,
    associacao,
    cpf_cnpj,
    esperado,
):
    d1 = _despesa_factory(cpf_cnpj_fornecedor="11.478.276/0001-04")
    d2 = _despesa_factory(cpf_cnpj_fornecedor="517.870.110-03")
    rateio_factory(d1)
    rateio_factory(d2)

    result = get_despesas(
        jwt_authenticated_client_d,
        associacao__uuid=associacao.uuid,
        cpf_cnpj_fornecedor=cpf_cnpj,
    )

    assert len(result) == esperado


@pytest.mark.parametrize("campo", ["uuid", "id"])
def test_filtro_por_tipo_documento(
    jwt_authenticated_client_d,
    _despesa_factory,
    rateio_factory,
    tipo_documento,
    campo,
):
    d1 = _despesa_factory()
    d2 = _despesa_factory()
    rateio_factory(d1)
    rateio_factory(d2)

    valor = getattr(tipo_documento, campo)
    result = get_despesas(
        jwt_authenticated_client_d,
        **{f"tipo_documento__{campo}": valor},
    )

    assert len(result) == 2


def test_filtro_por_tag(
    jwt_authenticated_client_d,
    _despesa_factory,
    rateio_factory,
    tag_teste_filtro_por_tag,
):
    d1 = _despesa_factory()
    d2 = _despesa_factory()

    rateio_factory(d1, tag=tag_teste_filtro_por_tag)
    rateio_factory(d2)

    result = get_despesas(
        jwt_authenticated_client_d,
        rateios__tag__uuid=tag_teste_filtro_por_tag.uuid,
    )

    assert len(result) == 1


@pytest.mark.parametrize(
    "filtro, esperado",
    [
        ("", 3),
        ("1,2", 2),
    ],
)
def test_filtro_vinculo_atividades(
    jwt_authenticated_client_d,
    _despesa_factory,
    rateio_factory,
    tag_1,
    tag_2,
    filtro,
    esperado,
):
    d1 = _despesa_factory()
    d2 = _despesa_factory()
    d3 = _despesa_factory()

    rateio_factory(d1, tag=tag_1)
    rateio_factory(d2, tag=tag_2)
    rateio_factory(d3)

    result = get_despesas(
        jwt_authenticated_client_d,
        filtro_vinculo_atividades=filtro,
    )

    assert len(result) == esperado
