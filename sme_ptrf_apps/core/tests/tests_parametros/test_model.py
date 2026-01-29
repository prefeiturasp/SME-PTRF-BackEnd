import pytest

from ...models import Parametros

pytestmark = pytest.mark.django_db


def test_parametros_model(parametros):
    assert isinstance(parametros, Parametros)
    assert parametros.permite_saldo_conta_negativo
    assert parametros.fique_de_olho == ''
    assert parametros.tempo_aguardar_conclusao_pc == 1
    assert parametros.quantidade_tentativas_concluir_pc == 3
    assert parametros.periodo_de_tempo_tentativas_concluir_pc == 120
    assert parametros.tempo_notificar_nao_demonstrados == 0
    assert parametros.fique_de_olho_relatorio_dre == ''
    assert parametros.dias_antes_inicio_periodo_pc_para_notificacao == 5
    assert parametros.enviar_email_notificacao
    assert parametros.texto_pagina_suporte_dre == 'Teste DRE'
    assert parametros.texto_pagina_suporte_sme == 'Teste SME'
    assert parametros.texto_pagina_valores_reprogramados_ue == 'Teste UE'
    assert parametros.texto_pagina_valores_reprogramados_dre == 'Teste DRE'
    assert parametros.tipos_unidades_professor_gremio == []


def test_parametros_tipos_unidades_professor_gremio(parametros):
    """Testa se o campo tipos_unidades_professor_gremio pode ser definido e recuperado"""
    parametros.tipos_unidades_professor_gremio = ['EMEF', 'EMEI']
    parametros.save()
    
    parametros.refresh_from_db()
    assert parametros.tipos_unidades_professor_gremio == ['EMEF', 'EMEI']
    
    parametros.tipos_unidades_professor_gremio = ['EMEF', 'EMEI', 'CEU']
    parametros.save()
    
    parametros.refresh_from_db()
    assert len(parametros.tipos_unidades_professor_gremio) == 3
    assert 'CEU' in parametros.tipos_unidades_professor_gremio
