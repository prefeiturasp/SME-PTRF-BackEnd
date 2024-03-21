import pytest

from model_bakery import baker

from sme_ptrf_apps.core.services.relacao_bens_dados_service import persistir_dados_relacao_bens, formatar_e_retornar_dados_relatorio_relacao_bens
from sme_ptrf_apps.core.services.relacao_bens import apagar_previas_relacao_de_bens
from sme_ptrf_apps.core.models.relatorio_relacao_bens import RelatorioRelacaoBens

pytestmark = pytest.mark.django_db

dados_relacao_bens = {
  "cabecalho": {
    "periodo_referencia": "2023.2",
    "periodo_data_inicio": "2023-5-1",
    "periodo_data_fim": "2023-8-31",
    "conta": "Cheque"
  },
  "identificacao_apm": {
    "nome_associacao": "APM DA EMEF JOAO DA SILVA",
    "cnpj_associacao": "04442788000147",
    "codigo_eol_associacao": "019305",
    "nome_dre_associacao": "DIRETORIA REGIONAL DE EDUCACAO CAPELA DO SOCORRO",
    "presidente_diretoria_executiva": "GERALDO NUNES AGUILAR",
    "tipo_unidade": "EMEF",
    "nome_unidade": "JOAO DA SILVA",
    "cargo_substituto_presidente_ausente": "Presidente da diretoria executiva"
  },
  "relacao_de_bens_adquiridos_ou_produzidos": {
    "linhas": [
      {
        "tipo_documento": "DANFE",
        "numero_documento": "83601",
        "especificacao_material": "Caixa acustica",
        "numero_documento_incorporacao": "6016.2023/0108658-6",
        "quantidade": 1,
        "data_documento": "2023-6-28",
        "valor_item": 2000,
        "valor_rateio": 2000
      },
      {
        "tipo_documento": "DANFE",
        "numero_documento": "83601",
        "especificacao_material": "Caixa acustica",
        "numero_documento_incorporacao": "6016.2023/0108658-6",
        "quantidade": 1,
        "data_documento": "2023-06-28",
        "valor_item": 2400,
        "valor_rateio": 2400
      },
      {
        "tipo_documento": "DANFE",
        "numero_documento": "137865",
        "especificacao_material": "Gravador digital dvr",
        "numero_documento_incorporacao": "6016.2023/0108658-6",
        "quantidade": 1,
        "data_documento": "2023-7-4",
        "valor_item": 3019.777,
        "valor_rateio": 3019.77
      },
      {
        "tipo_documento": "DANFE",
        "numero_documento": "137865",
        "especificacao_material": "Modulo de potencia",
        "numero_documento_incorporacao": "6016.2023/0108658-6",
        "quantidade": 1,
        "data_documento": "2023-7-4",
        "valor_item": 429.56,
        "valor_rateio": 429.56
      },
      {
        "tipo_documento": "DANFE",
        "numero_documento": "137865",
        "especificacao_material": "Vídeo porteiro",
        "numero_documento_incorporacao": "6016.2023/0108658-6",
        "quantidade": 1,
        "data_documento": "2023-7-4",
        "valor_item": 648.91,
        "valor_rateio": 648.91
      }
    ],
    "valor_total": 8498.24
  }
}

def test_persistir_relatorio_relacao_bens(periodo, conta_associacao, despesa, rateio_despesa_01, rateio_despesa_02, usuario, relacao_bens_factory):
    relacao_bens = relacao_bens_factory.create()

    persistir_dados_relacao_bens(periodo, conta_associacao, despesa.rateios.all(), relacao_bens, usuario)
    relatorio = RelatorioRelacaoBens.objects.get(relacao_bens=relacao_bens)

    assert relatorio

@pytest.fixture
def rateio_despesa_01(associacao, despesa, conta_associacao, acao, tipo_aplicacao_recurso_custeio, tipo_custeio_material, especificacao_material_eletrico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_material,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=200.00,
        valor_original=200.00,
        quantidade_itens_capital=2,
        valor_item_capital=100.00
    )


@pytest.fixture
def rateio_despesa_02(associacao, despesa, conta_associacao, acao, tipo_aplicacao_recurso_custeio, tipo_custeio, tipo_custeio_material, especificacao_material_eletrico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio,
        valor_rateio=100.00,
        valor_original=100.00,
    )

def test_persistir_relatorio_final_relacao_bens_com_relatorios_anteriores(periodo, conta_associacao, despesa, rateio_despesa_01, rateio_despesa_02, usuario, relacao_bens_factory, item_relatorio_relacao_de_bens_factory, relatorio_relacao_bens_factory):
    relacao_bens_anterior = relacao_bens_factory.create()
    relatorio_anterior = relatorio_relacao_bens_factory.create(relacao_bens=relacao_bens_anterior)
    item_relatorio_relacao_de_bens_factory.create(relatorio=relatorio_anterior)

    apagar_previas_relacao_de_bens(relacao_bens_anterior.periodo_previa, relacao_bens_anterior.conta_associacao)

    relacao_bens = relacao_bens_factory.create()

    persistir_dados_relacao_bens(periodo, conta_associacao, despesa.rateios.all(), relacao_bens, usuario)

    relatorio = RelatorioRelacaoBens.objects.filter(relacao_bens=relacao_bens)

    assert relatorio.count() == 1


def test_formatar_e_retornar_dados_relatorio_relacao_bens(relacao_bens_factory, item_relatorio_relacao_de_bens_factory, relatorio_relacao_bens_factory):
    relacao_bens = relacao_bens_factory.create()
    relatorio_instance = relatorio_relacao_bens_factory.create(relacao_bens=relacao_bens)
    item_relatorio_relacao_de_bens_factory.create(relatorio=relatorio_instance)

    resultado = formatar_e_retornar_dados_relatorio_relacao_bens(relatorio_instance)

    assert 'cabecalho' in resultado
    assert 'periodo_referencia' in resultado['cabecalho']
    assert 'periodo_data_inicio' in resultado['cabecalho']
    assert 'periodo_data_fim' in resultado['cabecalho']
    assert 'conta' in resultado['cabecalho']

    assert 'identificacao_apm' in resultado
    assert 'nome_associacao' in resultado['identificacao_apm']
    assert 'cnpj_associacao' in resultado['identificacao_apm']
    assert 'codigo_eol_associacao' in resultado['identificacao_apm']
    assert 'nome_dre_associacao' in resultado['identificacao_apm']
    assert 'presidente_diretoria_executiva' in resultado['identificacao_apm']
    assert 'tipo_unidade' in resultado['identificacao_apm']
    assert 'nome_unidade' in resultado['identificacao_apm']
    assert  'cargo_substituto_presidente_ausente' in resultado['identificacao_apm']

    assert 'data_geracao' in resultado
    assert 'relacao_de_bens_adquiridos_ou_produzidos' in resultado
    assert 'valor_total' in resultado['relacao_de_bens_adquiridos_ou_produzidos']
    assert 'linhas' in resultado['relacao_de_bens_adquiridos_ou_produzidos']
    assert len(resultado['relacao_de_bens_adquiridos_ou_produzidos']['linhas']) == 1
    assert 'data_geracao_documento' in resultado
    assert 'previa' in resultado
