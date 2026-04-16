import pytest

from sme_ptrf_apps.paa.models import AtaPaa


@pytest.fixture
def flag_paa_retificacao(flag_factory):
    return flag_factory.create(name='paa-retificacao')


HISTORICO_PADRAO = {
    'texto_introducao': 'Introducao original.',
    'texto_conclusao': 'Conclusao original.',
    'objetivos': {},
    'receitas_ptrf': {},
    'receitas_pdde': {},
    'receitas_outros_recursos': {},
    'prioridades': {},
}


@pytest.fixture
def paa_retificacao(paa_factory):
    return paa_factory(
        texto_introducao='Introducao original.',
        texto_conclusao='Conclusao original.',
    )


@pytest.fixture
def replica_paa(paa_retificacao, replica_paa_factory):
    return replica_paa_factory(
        paa=paa_retificacao,
        historico=HISTORICO_PADRAO.copy(),
    )


@pytest.fixture
def ata_retificacao(paa_retificacao, ata_paa_factory):
    return ata_paa_factory(
        paa=paa_retificacao,
        tipo_ata=AtaPaa.ATA_RETIFICACAO,
        justificativa='Justificativa de teste.',
    )


@pytest.fixture
def objetivo_no_paa(paa_retificacao, objetivo_paa_factory):
    objetivo = objetivo_paa_factory(paa=paa_retificacao)
    paa_retificacao.objetivos.add(objetivo)
    return objetivo


@pytest.fixture
def receita_ptrf_no_paa(paa_retificacao, receita_prevista_paa_factory):
    return receita_prevista_paa_factory(
        paa=paa_retificacao,
        previsao_valor_custeio='500.00',
        previsao_valor_capital='200.00',
        previsao_valor_livre='100.00',
        saldo_congelado_custeio='0.00',
        saldo_congelado_capital='0.00',
        saldo_congelado_livre='0.00',
    )


@pytest.fixture
def receita_pdde_no_paa(paa_retificacao, receita_prevista_pdde_factory):
    return receita_prevista_pdde_factory(
        paa=paa_retificacao,
        previsao_valor_custeio='300.00',
        previsao_valor_capital='100.00',
        previsao_valor_livre='50.00',
        saldo_custeio='0.00',
        saldo_capital='0.00',
        saldo_livre='0.00',
    )


@pytest.fixture
def prioridade_no_paa(paa_retificacao, prioridade_paa_factory):
    return prioridade_paa_factory(paa=paa_retificacao, valor_total='1000.00')
