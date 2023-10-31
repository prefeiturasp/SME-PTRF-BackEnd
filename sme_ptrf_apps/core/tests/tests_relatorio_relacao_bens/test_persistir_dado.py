import pytest
from sme_ptrf_apps.core.services.relacao_bens_dados_service import persistir_dados_relacao_bens
from sme_ptrf_apps.core.models.relatorio_relacao_bens import RelatorioRelacaoBens
from sme_ptrf_apps.core.fixtures.factories.relacao_bens_factory import RelacaoBensFactory, RelatorioRelacaoBensFactory, ItemRelatorioRelacaoDeBensFactory
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

def test_persistir_relatorio_relacao_bens(usuario):
    relacao_bens = RelacaoBensFactory()
    persistir_dados_relacao_bens(dados_relacao_bens, relacao_bens, usuario)
    relatorio = RelatorioRelacaoBens.objects.get(relacao_bens=relacao_bens)

    assert relatorio

def test_persistir_relatorio_final_relacao_bens_com_relatorios_anteriores(usuario):
    relacao_bens = RelacaoBensFactory()
    relatorio_instance = RelatorioRelacaoBensFactory(relacao_bens=relacao_bens)
    ItemRelatorioRelacaoDeBensFactory(relatorio=relatorio_instance)

    persistir_dados_relacao_bens(dados_relacao_bens, relacao_bens, usuario)

    relatorio = RelatorioRelacaoBens.objects.filter(relacao_bens=relacao_bens)

    assert relatorio.count() == 1