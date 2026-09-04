from sme_ptrf_apps.despesas.validators.pipelines import (
    CREATE_PIPELINE,
    UPDATE_PIPELINE,
    CREATE_ACERTO_PIPELINE,
    UPDATE_ACERTO_PIPELINE,
)
from sme_ptrf_apps.despesas.validators.r70_associacao_imutavel import AssociacaoImutavelValidator
from sme_ptrf_apps.despesas.validators.r71_conta_acao_mesma_associacao import ContaAcaoMesmaAssociacaoValidator


def _tipos(pipeline):
    return [type(v) for v in pipeline._validators]


def test_reg071_esta_no_core_dos_quatro_fluxos():
    for pipeline in (CREATE_PIPELINE, UPDATE_PIPELINE, CREATE_ACERTO_PIPELINE, UPDATE_ACERTO_PIPELINE):
        assert ContaAcaoMesmaAssociacaoValidator in _tipos(pipeline)


def test_reg070_so_nos_fluxos_de_edicao():
    assert AssociacaoImutavelValidator in _tipos(UPDATE_PIPELINE)
    assert AssociacaoImutavelValidator in _tipos(UPDATE_ACERTO_PIPELINE)
    assert AssociacaoImutavelValidator not in _tipos(CREATE_PIPELINE)
    assert AssociacaoImutavelValidator not in _tipos(CREATE_ACERTO_PIPELINE)


def test_reg070_precede_core_no_update():
    tipos = _tipos(UPDATE_PIPELINE)
    assert tipos[0] is AssociacaoImutavelValidator
