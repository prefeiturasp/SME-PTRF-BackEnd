
import pytest
from sme_ptrf_apps.core.models.unidade import Unidade

from sme_ptrf_apps.dre.services.ata_parecer_tecnico_service import informacoes_pcs_aprovadas_aprovadas_com_ressalva_reprovadas_consolidado_dre


pytestmark = pytest.mark.django_db

def test_ordenacao_unidades_por_tipo_e_nome_na_ata(
    dre,
    periodo,
    ata_parecer_tecnico,
    consolidado_dre_com_pc
):
    dados = informacoes_pcs_aprovadas_aprovadas_com_ressalva_reprovadas_consolidado_dre(
        dre,
        periodo,
        ata_parecer_tecnico,
    )

    unidades_ata = []
    for dado in dados:
        unidades_ata.append(
            {"tipo": dado['unidade']['tipo_unidade'], 
             "nome": dado['unidade']['nome']})


    unidades = Unidade.objects.exclude(dre__isnull=True).order_by("tipo_unidade", "nome")
    resultado_esperado = []
    for unidade in unidades:
        resultado_esperado.append({'tipo': unidade.tipo_unidade, 'nome': unidade.nome})

    assert unidades_ata == resultado_esperado


