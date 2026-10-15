from datetime import date

import pytest
from freezegun import freeze_time

from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido
from sme_ptrf_apps.situacao_patrimonial.validators import (
    BemProduzidoContextBuilder,
    EDIT_PIPELINE,
    SituacaoPatrimonialValidationError,
)

pytestmark = pytest.mark.django_db


def _bem_com_despesa(
    associacao_factory,
    recurso_factory,
    periodo_factory,
    despesa_factory,
    prestacao_conta_factory,
    bem_produzido_factory,
    bem_produzido_despesa_factory,
    status_bem,
    status_pc,
    fim_periodo,
):
    associacao = associacao_factory.create()
    recurso = recurso_factory.create(legado=False)
    periodo = periodo_factory.create(
        referencia='2025.1',
        data_inicio_realizacao_despesas=date(2025, 1, 1),
        data_fim_realizacao_despesas=fim_periodo,
        recurso=recurso,
    )
    despesa = despesa_factory.create(
        associacao=associacao,
        recurso=recurso,
        data_transacao=date(2025, 1, 15),
        data_documento=date(2025, 1, 15),
    )
    if status_pc is not None:
        prestacao_conta_factory.create(
            periodo=periodo,
            associacao=associacao,
            status=status_pc,
        )
    bem = bem_produzido_factory.create(
        associacao=associacao,
        recurso=recurso,
        status=status_bem,
    )
    bem_produzido_despesa_factory.create(bem_produzido=bem, despesa=despesa)
    return bem


@freeze_time('2025-03-10')
def test_edicao_de_rascunho_em_periodo_fechado_permanece_permitida(
    associacao_factory,
    recurso_factory,
    periodo_factory,
    despesa_factory,
    prestacao_conta_factory,
    bem_produzido_factory,
    bem_produzido_despesa_factory,
):
    bem = _bem_com_despesa(
        associacao_factory, recurso_factory, periodo_factory, despesa_factory,
        prestacao_conta_factory, bem_produzido_factory, bem_produzido_despesa_factory,
        status_bem=BemProduzido.STATUS_INCOMPLETO,
        status_pc='APROVADA',
        fim_periodo=date(2025, 2, 28),
    )
    contexto = BemProduzidoContextBuilder.build(bem_produzido=bem)

    resultado = EDIT_PIPELINE.run(contexto)

    assert resultado.status == BemProduzido.STATUS_INCOMPLETO


@freeze_time('2025-03-10')
def test_edicao_de_rascunho_sem_despesas_e_sem_valores_nao_e_bloqueada_por_falta_de_valores(
    associacao_factory,
    recurso_factory,
    bem_produzido_factory,
):
    associacao = associacao_factory.create()
    recurso = recurso_factory.create(legado=False)
    bem = bem_produzido_factory.create(
        associacao=associacao,
        recurso=recurso,
        status=BemProduzido.STATUS_INCOMPLETO,
    )
    contexto = BemProduzidoContextBuilder.build(bem_produzido=bem)

    resultado = EDIT_PIPELINE.run(contexto)

    assert resultado.bem_produzido == bem


@freeze_time('2025-03-10')
def test_edicao_de_bem_completo_e_bloqueada_quando_pc_da_despesa_mais_recente_esta_fechada(
    associacao_factory,
    recurso_factory,
    periodo_factory,
    despesa_factory,
    prestacao_conta_factory,
    bem_produzido_factory,
    bem_produzido_despesa_factory,
):
    bem = _bem_com_despesa(
        associacao_factory, recurso_factory, periodo_factory, despesa_factory,
        prestacao_conta_factory, bem_produzido_factory, bem_produzido_despesa_factory,
        status_bem=BemProduzido.STATUS_COMPLETO,
        status_pc='APROVADA',
        fim_periodo=date(2025, 2, 28),
    )
    contexto = BemProduzidoContextBuilder.build(bem_produzido=bem)

    with pytest.raises(SituacaoPatrimonialValidationError) as erro:
        EDIT_PIPELINE.run(contexto)

    assert erro.value.detail['validator'] == 'BloqueioEdicaoBemProduzidoCompletoPeriodoFechadoValidator'


@freeze_time('2025-03-10')
def test_edicao_de_bem_completo_em_periodo_aberto_e_permitida(
    associacao_factory,
    recurso_factory,
    periodo_factory,
    despesa_factory,
    prestacao_conta_factory,
    bem_produzido_factory,
    bem_produzido_despesa_factory,
):
    bem = _bem_com_despesa(
        associacao_factory, recurso_factory, periodo_factory, despesa_factory,
        prestacao_conta_factory, bem_produzido_factory, bem_produzido_despesa_factory,
        status_bem=BemProduzido.STATUS_COMPLETO,
        status_pc='NAO_APRESENTADA',
        fim_periodo=date(2025, 2, 28),
    )
    contexto = BemProduzidoContextBuilder.build(bem_produzido=bem)

    resultado = EDIT_PIPELINE.run(contexto)

    assert resultado.status == BemProduzido.STATUS_COMPLETO


def test_edicao_sem_associacao_e_bloqueada(bem_produzido_factory):
    bem = bem_produzido_factory.create(associacao=None)
    contexto = BemProduzidoContextBuilder.build(bem_produzido=bem)

    with pytest.raises(SituacaoPatrimonialValidationError) as erro:
        EDIT_PIPELINE.run(contexto)

    assert erro.value.detail['titulo'] == 'Bem produzido sem associação'
    assert erro.value.detail['validator'] == 'BemProduzidoPossuiAssociacaoValidator'
