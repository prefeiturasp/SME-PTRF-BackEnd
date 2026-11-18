"""Compara o ResumoPrioridadesService atual com a cópia congelada do comportamento original."""
from decimal import Decimal

import pytest

from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum
from sme_ptrf_apps.paa.services.resumo_prioridades_service import ResumoPrioridadesService
from sme_ptrf_apps.paa.tests.services._resumo_prioridades_legacy import (
    ResumoPrioridadesService as ResumoPrioridadesServiceLegado,
)


@pytest.fixture
def paa_com_todos_os_recursos(
    resumo_recursos_paa,
    receita_prevista_pdde_resumo_recursos,
    recurso_proprio_paa_factory,
    prioridade_paa_factory,
):
    from sme_ptrf_apps.paa.fixtures.factories import ReceitaPrevistaPaaFactory
    from sme_ptrf_apps.core.fixtures.factories.acao_associacao_factory import AcaoAssociacaoFactory

    acao_associacao = AcaoAssociacaoFactory.create(associacao=resumo_recursos_paa.associacao)
    ReceitaPrevistaPaaFactory.create(
        paa=resumo_recursos_paa,
        acao_associacao=acao_associacao,
        previsao_valor_custeio=1001,
        previsao_valor_capital=1002,
        previsao_valor_livre=1003,
    )
    prioridade_paa_factory.create(
        paa=resumo_recursos_paa,
        recurso=RecursoOpcoesEnum.PTRF.name,
        acao_associacao=acao_associacao,
        acao_pdde=None,
        tipo_aplicacao='CUSTEIO',
        valor_total=300,
    )
    recurso_proprio_paa_factory.create(paa=resumo_recursos_paa, descricao="ABC 007", valor=1000.00)
    prioridade_paa_factory.create(
        paa=resumo_recursos_paa,
        recurso=RecursoOpcoesEnum.RECURSO_PROPRIO.name,
        valor_total=200,
        acao_pdde=None,
        acao_associacao=None,
    )
    return resumo_recursos_paa, acao_associacao, receita_prevista_pdde_resumo_recursos


def _executar(funcao):
    try:
        return ('ok', funcao())
    except Exception as ex:
        detalhe = getattr(ex, 'detail', None)
        return ('erro', type(ex).__name__, str(detalhe if detalhe is not None else ex))


@pytest.mark.django_db
def test_resumo_prioridades_identico_ao_legado(paa_com_todos_os_recursos):
    paa, _, _ = paa_com_todos_os_recursos

    assert ResumoPrioridadesService(paa).resumo_prioridades() == \
        ResumoPrioridadesServiceLegado(paa).resumo_prioridades()


@pytest.mark.django_db
def test_resumo_prioridades_identico_ao_legado_com_saldo_congelado(paa_com_todos_os_recursos):
    from datetime import datetime
    paa, _, _ = paa_com_todos_os_recursos
    paa.saldo_congelado_em = datetime.now()
    paa.save()

    assert ResumoPrioridadesService(paa).resumo_prioridades() == \
        ResumoPrioridadesServiceLegado(paa).resumo_prioridades()


@pytest.mark.django_db
@pytest.mark.parametrize('recurso', ['PTRF', 'PDDE', 'RECURSO_PROPRIO', 'OUTRO_RECURSO', 'INEXISTENTE'])
@pytest.mark.parametrize('tipo_aplicacao', ['CUSTEIO', 'CAPITAL'])
@pytest.mark.parametrize('valor_total', [Decimal('1.00'), Decimal('999999.00')])
@pytest.mark.parametrize('edicao', [False, True])
def test_validar_valor_prioridade_identico_ao_legado(
    paa_com_todos_os_recursos, acao_pdde, recurso, tipo_aplicacao, valor_total, edicao
):
    paa, acao_associacao, _ = paa_com_todos_os_recursos
    acao_uuid = {
        'PTRF': str(acao_associacao.uuid),
        'PDDE': str(acao_pdde.uuid),
        'OUTRO_RECURSO': 'uuid-que-nao-existe',
    }.get(recurso)

    kwargs = dict(
        valor_total=valor_total,
        acao_uuid=acao_uuid,
        tipo_aplicacao=tipo_aplicacao,
        recurso=recurso,
        prioridade_uuid='uuid-prioridade' if edicao else None,
        valor_atual_prioridade=Decimal('50.00') if edicao else None,
    )

    novo = _executar(lambda: ResumoPrioridadesService(paa).validar_valor_prioridade(**kwargs))
    legado = _executar(lambda: ResumoPrioridadesServiceLegado(paa).validar_valor_prioridade(**kwargs))

    assert novo == legado


@pytest.mark.django_db
@pytest.mark.parametrize('kwargs', [
    dict(valor_total=None, acao_uuid=None, tipo_aplicacao='CUSTEIO', recurso='PTRF'),
    dict(valor_total=Decimal('1'), acao_uuid=None, tipo_aplicacao=None, recurso='PTRF'),
    dict(valor_total=Decimal('1'), acao_uuid=None, tipo_aplicacao='CUSTEIO', recurso=None),
])
def test_validar_valor_prioridade_parametros_invalidos_retorna_none(paa_com_todos_os_recursos, kwargs):
    paa, _, _ = paa_com_todos_os_recursos
    assert ResumoPrioridadesService(paa).validar_valor_prioridade(**kwargs) is None
