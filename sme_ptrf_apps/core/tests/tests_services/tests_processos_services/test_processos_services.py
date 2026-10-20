import pytest
from django.core.exceptions import ValidationError

from sme_ptrf_apps.core.models import ProcessoAssociacao
from sme_ptrf_apps.core.services.processos_services import (
    get_processo_sei_da_associacao_no_periodo,
    get_processo_sei_da_prestacao,
    trata_processo_sei_ao_receber_pc,
    trata_processo_sei_ao_receber_pc_v2,
    validar_troca_recurso_em_processo_associacao,
)

pytestmark = pytest.mark.django_db


# get_processo_sei_da_prestacao / get_processo_sei_da_associacao_no_periodo

def test_get_processo_sei_da_prestacao_v1(
    prestacao_conta_factory, processo_associacao_factory, periodo_factory, associacao,
):
    periodo = periodo_factory.create(referencia='2023.1')
    prestacao_conta = prestacao_conta_factory.create(associacao=associacao, periodo=periodo)
    processo = processo_associacao_factory.create(associacao=associacao, ano='2023', numero_processo='111')

    result = get_processo_sei_da_prestacao(prestacao_conta, periodos_processo_sei=False)

    assert result == processo.numero_processo


def test_get_processo_sei_da_prestacao_v2(
    prestacao_conta_factory, processo_associacao_factory, periodo_factory, associacao,
):
    periodo = periodo_factory.create(referencia='2023.1')
    prestacao_conta = prestacao_conta_factory.create(associacao=associacao, periodo=periodo)
    processo = processo_associacao_factory.create(associacao=associacao, ano='2023', numero_processo='222')
    processo.periodos.add(periodo)

    result = get_processo_sei_da_prestacao(prestacao_conta, periodos_processo_sei=True)

    assert result == processo.numero_processo


def test_get_processo_sei_da_associacao_no_periodo_v1(
    processo_associacao_factory, periodo_factory, associacao,
):
    periodo = periodo_factory.create(referencia='2023.1')
    processo = processo_associacao_factory.create(associacao=associacao, ano='2023', numero_processo='333')

    result = get_processo_sei_da_associacao_no_periodo(associacao, periodo, periodos_processo_sei=False)

    assert result == processo.numero_processo


def test_get_processo_sei_da_associacao_no_periodo_v2(
    processo_associacao_factory, periodo_factory, associacao,
):
    periodo = periodo_factory.create(referencia='2023.1')
    processo = processo_associacao_factory.create(associacao=associacao, ano='2023', numero_processo='444')
    processo.periodos.add(periodo)

    result = get_processo_sei_da_associacao_no_periodo(associacao, periodo, periodos_processo_sei=True)

    assert result == processo.numero_processo


# trata_processo_sei_ao_receber_pc

def test_trata_processo_sei_ao_receber_pc_editar(
    prestacao_conta_factory, processo_associacao_factory, periodo_factory, associacao,
):
    periodo = periodo_factory.create(referencia='2023.1')
    prestacao_conta = prestacao_conta_factory.create(associacao=associacao, periodo=periodo)
    processo = processo_associacao_factory.create(associacao=associacao, ano='2023', numero_processo='antigo')

    trata_processo_sei_ao_receber_pc(prestacao_conta, 'novo-numero', 'editar')

    processo.refresh_from_db()
    assert processo.numero_processo == 'novo-numero'


def test_trata_processo_sei_ao_receber_pc_incluir(
    prestacao_conta_factory, periodo_factory, associacao,
):
    periodo = periodo_factory.create(referencia='2023.1')
    prestacao_conta = prestacao_conta_factory.create(associacao=associacao, periodo=periodo)

    assert not ProcessoAssociacao.objects.filter(associacao=associacao, ano='2023').exists()

    trata_processo_sei_ao_receber_pc(prestacao_conta, 'numero-novo', 'incluir')

    processo = ProcessoAssociacao.objects.get(associacao=associacao, ano='2023')
    assert processo.numero_processo == 'numero-novo'
    assert processo.recurso == periodo.recurso


def test_trata_processo_sei_ao_receber_pc_acao_desconhecida_nao_faz_nada(
    prestacao_conta_factory, periodo_factory, associacao,
):
    periodo = periodo_factory.create(referencia='2023.1')
    prestacao_conta = prestacao_conta_factory.create(associacao=associacao, periodo=periodo)

    trata_processo_sei_ao_receber_pc(prestacao_conta, 'numero', 'outra-acao')

    assert not ProcessoAssociacao.objects.filter(associacao=associacao).exists()


# trata_processo_sei_ao_receber_pc_v2

def test_trata_v2_incluir_processo_existente_periodo_ja_vinculado(
    prestacao_conta_factory, processo_associacao_factory, periodo_factory, associacao,
):
    periodo = periodo_factory.create(referencia='2023.1')
    prestacao_conta = prestacao_conta_factory.create(associacao=associacao, periodo=periodo)
    processo = processo_associacao_factory.create(associacao=associacao, ano='2023', numero_processo='555')
    processo.periodos.add(periodo)

    with pytest.raises(Exception, match='já está vinculado ao processo'):
        trata_processo_sei_ao_receber_pc_v2(prestacao_conta, '555', 'incluir')


def test_trata_v2_incluir_processo_existente_periodo_livre(
    prestacao_conta_factory, processo_associacao_factory, periodo_factory, associacao,
):
    periodo = periodo_factory.create(referencia='2023.1')
    prestacao_conta = prestacao_conta_factory.create(associacao=associacao, periodo=periodo)
    processo = processo_associacao_factory.create(associacao=associacao, ano='2023', numero_processo='666')

    trata_processo_sei_ao_receber_pc_v2(prestacao_conta, '666', 'incluir')

    assert periodo in processo.periodos.all()


def test_trata_v2_incluir_processo_novo_periodo_vinculado_a_outro_processo(
    prestacao_conta_factory, processo_associacao_factory, periodo_factory, associacao,
):
    periodo = periodo_factory.create(referencia='2023.1')
    prestacao_conta = prestacao_conta_factory.create(associacao=associacao, periodo=periodo)
    outro_processo = processo_associacao_factory.create(associacao=associacao, ano='2023', numero_processo='777')
    outro_processo.periodos.add(periodo)

    with pytest.raises(Exception, match='já está vinculado ao processo 777'):
        trata_processo_sei_ao_receber_pc_v2(prestacao_conta, '888-novo', 'incluir')


def test_trata_v2_incluir_processo_novo_periodo_livre(
    prestacao_conta_factory, periodo_factory, associacao,
):
    periodo = periodo_factory.create(referencia='2023.1')
    prestacao_conta = prestacao_conta_factory.create(associacao=associacao, periodo=periodo)

    trata_processo_sei_ao_receber_pc_v2(prestacao_conta, '999-novo', 'incluir')

    processo = ProcessoAssociacao.objects.get(associacao=associacao, numero_processo='999-novo')
    assert periodo in processo.periodos.all()
    assert processo.ano == '2023'
    assert processo.recurso == periodo.recurso


def test_trata_v2_editar(
    prestacao_conta_factory, processo_associacao_factory, periodo_factory, associacao,
):
    periodo = periodo_factory.create(referencia='2023.1')
    prestacao_conta = prestacao_conta_factory.create(associacao=associacao, periodo=periodo)
    processo = processo_associacao_factory.create(associacao=associacao, ano='2023', numero_processo='antigo-v2')
    processo.periodos.add(periodo)

    trata_processo_sei_ao_receber_pc_v2(prestacao_conta, 'editado-v2', 'editar')

    processo.refresh_from_db()
    assert processo.numero_processo == 'editado-v2'


# validar_troca_recurso_em_processo_associacao

def test_validar_troca_recurso_processo_sem_pk(processo_associacao_factory):
    processo_nao_salvo = processo_associacao_factory.build()

    assert validar_troca_recurso_em_processo_associacao(processo_nao_salvo) is None


def test_validar_troca_recurso_com_pc_vinculada(
    processo_associacao_factory, prestacao_conta_factory, periodo_factory, associacao,
):
    periodo = periodo_factory.create(referencia='2023.1')
    processo = processo_associacao_factory.create(associacao=associacao, ano='2023')
    processo.periodos.add(periodo)
    prestacao_conta_factory.create(associacao=associacao, periodo=periodo)

    with pytest.raises(ValidationError):
        validar_troca_recurso_em_processo_associacao(processo)


def test_validar_troca_recurso_sem_pc_vinculada(processo_associacao_factory, periodo_factory, associacao):
    periodo = periodo_factory.create(referencia='2023.1')
    processo = processo_associacao_factory.create(associacao=associacao, ano='2023')
    processo.periodos.add(periodo)

    assert validar_troca_recurso_em_processo_associacao(processo) is None
