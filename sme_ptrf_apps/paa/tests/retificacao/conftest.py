import pytest

from sme_ptrf_apps.paa.enums import PaaStatusEnum
from sme_ptrf_apps.paa.models import AtaPaa, DocumentoPaa, Paa


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
    'documento_original': {'uuid': None},
    'documento_retificado': {'uuid': None, 'versao': None},
    'ata_original': {'uuid': None},
    'ata_retificada': {'uuid': None}
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


@pytest.fixture
def paa_gerado(paa_factory, ata_paa_factory, documento_paa_factory):
    """PAA GERADO com documento final e ata de apresentação concluídos (status_andamento=GERADO)."""
    paa = paa_factory(status=PaaStatusEnum.GERADO.name)
    documento_paa_factory.create(
        paa=paa,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        retificacao=False,
    )
    ata_paa_factory.create(
        paa=paa,
        tipo_ata=AtaPaa.ATA_APRESENTACAO,
        status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
    )
    return paa


@pytest.fixture
def paa_retificado(paa_factory, ata_paa_factory, documento_paa_factory):
    """
    PAA RETIFICADO com documento final de retificação e ata de retificação
    concluídos (status_andamento=RETIFICADO).
    """
    paa = paa_factory(status=PaaStatusEnum.RETIFICADO.name)
    documento_paa_factory.create(
        paa=paa,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        retificacao=True,
    )
    ata_paa_factory.create(
        paa=paa,
        tipo_ata=AtaPaa.ATA_RETIFICACAO,
        status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
        pdf_gerado_previamente=True,
    )
    return paa


def _paa_anotado(paa):
    """
    Recarrega o PAA pelo PaaManager para incluir os campos anotados
    (ex.: tem_doc_final_retificacao, status_andamento), como ocorre na API.
    """
    return Paa.objects.get(pk=paa.pk)


@pytest.fixture
def paa_em_retificacao_cancelamento(paa_retificacao, replica_paa):
    """
    PAA EM_RETIFICACAO com réplica e sem documento final de retificação.
    Ao cancelar a retificação, deve voltar para GERADO.
    """
    paa_retificacao.set_paa_status_em_retificacao()
    return _paa_anotado(paa_retificacao)


@pytest.fixture
def paa_em_retificacao_cancelamento_com_doc_final_retificacao(
    paa_retificacao, replica_paa, documento_paa_factory
):
    """
    PAA EM_RETIFICACAO com réplica e documento final de retificação concluído
    (retificação anterior). Ao cancelar a retificação, deve voltar para RETIFICADO.

    O snapshot da réplica referencia o mesmo documento final de retificação,
    condição exigida por valida_pode_cancelar_retificacao.
    """
    paa_retificacao.set_paa_status_em_retificacao()

    documento_final_retificacao = documento_paa_factory.create(
        paa=paa_retificacao,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        retificacao=True,
    )

    replica_paa.historico = {
        **replica_paa.historico,
        'documento_retificado': {'uuid': str(documento_final_retificacao.uuid), 'versao': 1},
    }
    replica_paa.save()

    return _paa_anotado(paa_retificacao)
