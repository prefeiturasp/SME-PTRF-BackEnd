import datetime

import pytest

from sme_ptrf_apps.core.models import Associacao, PeriodoInicialAssociacao
from sme_ptrf_apps.core.fixtures.factories.periodo_factory import PeriodoFactory
from sme_ptrf_apps.core.fixtures.factories.recurso_factory import RecursoFactory
from sme_ptrf_apps.core.models.transferencia_eol import TransferenciaEol

pytestmark = pytest.mark.django_db


def test_clonar_associacao(
    transf_eol_unidade_eol_transferido,  # Eol 400232
    transf_eol_unidade_eol_historico,    # Eol 900232
    transferencia_eol,
    transf_eol_associacao_eol_transferido,  # -> unidade_eol_transferido
):
    assert transf_eol_associacao_eol_transferido.unidade == transf_eol_unidade_eol_transferido

    # Deve clonar associacao da unidade de código transferido para uma nova associação
    associacao_clonada = transferencia_eol.clonar_associacao(
        transf_eol_associacao_eol_transferido.uuid,
        transf_eol_unidade_eol_historico,
    )
    assert associacao_clonada.unidade == transf_eol_unidade_eol_transferido, "Deve apontar para a unidade original."
    assert associacao_clonada.uuid is not None
    assert associacao_clonada.uuid != transf_eol_associacao_eol_transferido.uuid
    assert associacao_clonada.nome == transf_eol_associacao_eol_transferido.nome
    assert associacao_clonada.cnpj == transferencia_eol.cnpj_nova_associacao

    associacao_original = Associacao.by_uuid(transf_eol_associacao_eol_transferido.uuid)
    assert associacao_original.unidade == transf_eol_unidade_eol_historico, "Deve apontar para a unidade de histórico."


def _cria_periodo(referencia, recurso):
    return PeriodoFactory(
        referencia=referencia,
        data_inicio_realizacao_despesas=datetime.date(2022, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2022, 6, 30),
        recurso=recurso,
    )


def test_clonar_associacao_copia_periodos_iniciais_quando_nao_informa_periodo_inicial(
    transf_eol_unidade_eol_transferido,
    transf_eol_unidade_eol_historico,
    transf_eol_associacao_eol_transferido,
):
    recurso_a = RecursoFactory(nome="Recurso A")
    recurso_b = RecursoFactory(nome="Recurso B")

    periodo_a_2021_1 = _cria_periodo("2021.1", recurso_a)
    periodo_b_2023_2 = _cria_periodo("2023.2", recurso_b)

    PeriodoInicialAssociacao.objects.create(
        associacao=transf_eol_associacao_eol_transferido,
        recurso=recurso_a,
        periodo_inicial=periodo_a_2021_1,
    )
    PeriodoInicialAssociacao.objects.create(
        associacao=transf_eol_associacao_eol_transferido,
        recurso=recurso_b,
        periodo_inicial=periodo_b_2023_2,
    )

    transferencia = TransferenciaEol.objects.create(
        eol_transferido=transf_eol_unidade_eol_transferido.codigo_eol,
        eol_historico=transf_eol_unidade_eol_historico.codigo_eol,
        data_inicio_atividades=datetime.date(2022, 7, 1),
        periodo_inicial_associacao=None,
    )

    associacao_clonada = transferencia.clonar_associacao(
        transf_eol_associacao_eol_transferido.uuid,
        transf_eol_unidade_eol_historico,
    )

    periodos_iniciais_novos = PeriodoInicialAssociacao.objects.filter(
        associacao=associacao_clonada
    )

    assert periodos_iniciais_novos.filter(
        recurso=recurso_a,
        periodo_inicial=periodo_a_2021_1,
    ).exists()
    assert periodos_iniciais_novos.filter(
        recurso=recurso_b,
        periodo_inicial=periodo_b_2023_2,
    ).exists()


def test_clonar_associacao_cria_periodo_inicial_para_recurso_do_periodo_quando_informa_periodo_inicial(
    transf_eol_unidade_eol_transferido,
    transf_eol_unidade_eol_historico,
    transf_eol_associacao_eol_transferido,
):
    recurso_a = RecursoFactory(nome="Recurso A")
    recurso_b = RecursoFactory(nome="Recurso B")

    periodo_a_2021_1 = _cria_periodo("2021.1", recurso_a)
    periodo_b_2023_2 = _cria_periodo("2023.2", recurso_b)

    PeriodoInicialAssociacao.objects.create(
        associacao=transf_eol_associacao_eol_transferido,
        recurso=recurso_a,
        periodo_inicial=periodo_a_2021_1,
    )
    PeriodoInicialAssociacao.objects.create(
        associacao=transf_eol_associacao_eol_transferido,
        recurso=recurso_b,
        periodo_inicial=periodo_b_2023_2,
    )

    periodo_a_2024_2 = _cria_periodo("2024.2", recurso_a)

    transferencia = TransferenciaEol.objects.create(
        eol_transferido=transf_eol_unidade_eol_transferido.codigo_eol,
        eol_historico=transf_eol_unidade_eol_historico.codigo_eol,
        data_inicio_atividades=datetime.date(2022, 7, 1),
        periodo_inicial_associacao=periodo_a_2024_2,
    )

    associacao_clonada = transferencia.clonar_associacao(
        transf_eol_associacao_eol_transferido.uuid,
        transf_eol_unidade_eol_historico,
    )

    periodos_iniciais_novos = PeriodoInicialAssociacao.objects.filter(
        associacao=associacao_clonada
    )

    # Deve existir apenas um PeriodoInicialAssociacao, para o recurso
    # do período informado na transferência.
    assert periodos_iniciais_novos.count() == 1
    periodo_inicial_novo = periodos_iniciais_novos.first()

    assert periodo_inicial_novo.recurso == recurso_a
    assert periodo_inicial_novo.periodo_inicial == periodo_a_2024_2
