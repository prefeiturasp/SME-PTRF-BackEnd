import pytest
import uuid
from sme_ptrf_apps.paa.services.paa_dre_service import PaaDreService, ValidacaoPaaDre
from sme_ptrf_apps.paa.enums import PaaStatusEnum

# Fixtures
@pytest.fixture
def dre_context(unidade_factory, associacao_factory):
    dre = unidade_factory.create(tipo_unidade="DRE")
    unidade = unidade_factory.create(dre=dre)
    associacao = associacao_factory.create(unidade=unidade)
    return dre, unidade, associacao


@pytest.fixture
def dre_com_periodo(dre_context, periodo_paa_factory):
    dre, unidade, associacao = dre_context
    periodo = periodo_paa_factory.create()
    return dre, unidade, associacao, periodo


# Testes
@pytest.mark.django_db
def test_listar_paas_com_paa(
    dre_com_periodo,
    paa_factory,
):
    dre, unidade, associacao, periodo = dre_com_periodo

    paa_factory.create(
        associacao=associacao,
        periodo_paa=periodo,
        status=PaaStatusEnum.GERADO.name
    )

    result = PaaDreService.listar_paas(dre.uuid)

    assert len(result) == 1
    assert result[0]["status"] == PaaStatusEnum.GERADO.name


@pytest.mark.django_db
def test_listar_paas_nao_iniciado(
    dre_context,
    periodo_paa_factory,
):
    dre, unidade, associacao = dre_context
    periodo_paa_factory.create()

    result = PaaDreService.listar_paas(dre.uuid)

    assert len(result) == 1
    assert result[0]["status"] == PaaStatusEnum.NAO_INICIADO.name


@pytest.mark.django_db
def test_filtrar_por_status(
    dre_com_periodo,
    paa_factory,
):
    dre, unidade, associacao, periodo = dre_com_periodo

    paa_factory.create(
        associacao=associacao,
        periodo_paa=periodo,
        status=PaaStatusEnum.GERADO.name
    )

    result = PaaDreService.listar_paas(
        dre.uuid,
        filtros={"status": ["GERADO"]}
    )

    assert len(result) == 1
    assert result[0]["status"] == PaaStatusEnum.GERADO.name


@pytest.mark.django_db
def test_nao_traz_nao_iniciado_quando_filtrado(
    dre_context,
    periodo_paa_factory,
):
    dre, unidade, associacao = dre_context
    periodo_paa_factory.create()

    result = PaaDreService.listar_paas(
        dre.uuid,
        filtros={"status": ["GERADO"]}
    )

    assert len(result) == 0


@pytest.mark.django_db
def test_status_invalido(unidade_factory):
    dre = unidade_factory.create(tipo_unidade="DRE")

    with pytest.raises(ValidacaoPaaDre):
        PaaDreService.listar_paas(
            dre.uuid,
            filtros={"status": ["INVALIDO"]}
        )


@pytest.mark.django_db
def test_dre_nao_encontrada():
    uuid_inexistente = uuid.uuid4()

    with pytest.raises(ValidacaoPaaDre):
        PaaDreService.listar_paas(str(uuid_inexistente))


@pytest.mark.django_db
def test_obter_tabelas(
    dre_context,
    periodo_paa_factory,
):
    dre, unidade, associacao = dre_context
    periodo_paa_factory.create()

    result = PaaDreService.obter_tabelas(dre.uuid)

    assert "periodos" in result
    assert "unidades" in result
    assert "tipos_unidade" in result
    assert "status" in result
