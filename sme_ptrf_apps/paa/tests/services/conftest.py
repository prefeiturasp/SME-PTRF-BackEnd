import pytest
from model_bakery import baker

from sme_ptrf_apps.paa.enums import PaaStatusEnum


@pytest.fixture
def receita_prevista_pdde_resumo_recursos(resumo_recursos_paa, acao_pdde):
    return baker.make(
        'ReceitaPrevistaPdde',
        paa=resumo_recursos_paa,
        acao_pdde=acao_pdde,
        previsao_valor_custeio=1000.,
        previsao_valor_capital=1000.,
        previsao_valor_livre=1000.,
        saldo_custeio=1000.,
        saldo_capital=1000.,
        saldo_livre=1000.)


@pytest.fixture(
    params=[
        (PaaStatusEnum.EM_ELABORACAO.name, PaaStatusEnum.GERADO.name),
        (PaaStatusEnum.EM_RETIFICACAO.name, PaaStatusEnum.RETIFICADO.name),
    ],
    ids=['em_elaboracao_para_gerado', 'em_retificacao_para_retificado'],
)
def paa_concluir_com_status_esperado(request, paa_factory, periodo_paa_1):
    """
    Cenários de conclusão do PAA (PaaService.concluir_paa).

    Retorna uma tupla (paa, status_esperado):
        - EM_ELABORACAO -> GERADO
        - EM_RETIFICACAO -> RETIFICADO
    """
    status_inicial, status_esperado = request.param
    paa = paa_factory.create(periodo_paa=periodo_paa_1, status=status_inicial)
    return paa, status_esperado
