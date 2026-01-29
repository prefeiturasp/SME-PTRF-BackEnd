import pytest
from datetime import timedelta

from sme_ptrf_apps.paa.services.ata_paa_service import (
    unidade_precisa_professor_gremio,
    verifica_precisa_professor_gremio
)
from sme_ptrf_apps.despesas.status_cadastro_completo import STATUS_COMPLETO

pytestmark = pytest.mark.django_db


def test_unidade_precisa_professor_gremio_com_tipo_configurado(parametros):
    """Testa se unidade_precisa_professor_gremio retorna True quando tipo está configurado"""
    parametros.tipos_unidades_professor_gremio = ['EMEF', 'EMEI']
    parametros.save()
    
    assert unidade_precisa_professor_gremio('EMEF') is True
    assert unidade_precisa_professor_gremio('EMEI') is True
    assert unidade_precisa_professor_gremio('CEU') is False


def test_unidade_precisa_professor_gremio_sem_configuracao(parametros):
    """Testa se unidade_precisa_professor_gremio retorna False quando não há configuração"""
    parametros.tipos_unidades_professor_gremio = []
    parametros.save()
    
    assert unidade_precisa_professor_gremio('EMEF') is False


def test_unidade_precisa_professor_gremio_sem_parametros():
    """Testa se unidade_precisa_professor_gremio retorna False quando não há parâmetros"""
    from sme_ptrf_apps.core.models import Parametros
    Parametros.objects.all().delete()
    
    assert unidade_precisa_professor_gremio('EMEF') is False




def test_verifica_precisa_professor_gremio_sem_associacao(ata_paa):
    """Testa se verifica_precisa_professor_gremio retorna False quando não há associação"""
    associacao_original = ata_paa.paa.associacao
    ata_paa.paa.associacao = None
    ata_paa.paa.save()
    
    assert verifica_precisa_professor_gremio(ata_paa) is False
    
    ata_paa.paa.associacao = associacao_original
    ata_paa.paa.save()


def test_verifica_precisa_professor_gremio_sem_periodo_paa(ata_paa, parametros):
    """Testa se verifica_precisa_professor_gremio retorna False quando não há período PAA"""
    tipo_unidade = ata_paa.paa.associacao.unidade.tipo_unidade
    parametros.tipos_unidades_professor_gremio = [tipo_unidade]
    parametros.save()
    
    periodo_paa_original = ata_paa.paa.periodo_paa
    ata_paa.paa.periodo_paa = None
    ata_paa.paa.save()
    
    assert verifica_precisa_professor_gremio(ata_paa) is False
    
    ata_paa.paa.periodo_paa = periodo_paa_original
    ata_paa.paa.save()


def test_verifica_precisa_professor_gremio_sem_tipo_configurado(ata_paa, parametros):
    """Testa se verifica_precisa_professor_gremio retorna False quando tipo não está configurado"""
    parametros.tipos_unidades_professor_gremio = []
    parametros.save()
    
    assert verifica_precisa_professor_gremio(ata_paa) is False


def test_verifica_precisa_professor_gremio_com_tipo_configurado_sem_despesas(ata_paa, parametros):
    """Testa se verifica_precisa_professor_gremio retorna False quando tipo está configurado mas não há despesas"""
    tipo_unidade = ata_paa.paa.associacao.unidade.tipo_unidade
    parametros.tipos_unidades_professor_gremio = [tipo_unidade]
    parametros.save()
    
    assert verifica_precisa_professor_gremio(ata_paa) is False


def test_verifica_precisa_professor_gremio_com_despesas_completas_gremio_no_periodo(
    ata_paa, parametros, acao_factory, acao_associacao_factory, despesa_factory, rateio_despesa_factory
):
    """Testa se verifica_precisa_professor_gremio retorna True quando há despesas completas com ação grêmio no período"""
    tipo_unidade = ata_paa.paa.associacao.unidade.tipo_unidade
    parametros.tipos_unidades_professor_gremio = [tipo_unidade]
    parametros.save()
    
    # Cria ação "Orçamento Grêmio Estudantil"
    acao_gremio = acao_factory.create(nome='Orçamento Grêmio Estudantil')
    acao_associacao_gremio = acao_associacao_factory.create(
        associacao=ata_paa.paa.associacao,
        acao=acao_gremio,
        status='ATIVA'
    )
    
    # Cria despesa completa no período do PAA
    periodo_paa = ata_paa.paa.periodo_paa
    despesa = despesa_factory.create(
        associacao=ata_paa.paa.associacao,
        data_transacao=periodo_paa.data_inicial + timedelta(days=1),
        status=STATUS_COMPLETO
    )
    
    # Cria rateio completo com a ação do grêmio
    rateio_despesa_factory.create(
        despesa=despesa,
        associacao=ata_paa.paa.associacao,
        acao_associacao=acao_associacao_gremio
    )
    
    assert verifica_precisa_professor_gremio(ata_paa) is True


def test_verifica_precisa_professor_gremio_sem_acao_gremio(ata_paa, parametros):
    """Testa se verifica_precisa_professor_gremio retorna False quando não há ação grêmio"""
    tipo_unidade = ata_paa.paa.associacao.unidade.tipo_unidade
    parametros.tipos_unidades_professor_gremio = [tipo_unidade]
    parametros.save()
    
    assert verifica_precisa_professor_gremio(ata_paa) is False


def test_verifica_precisa_professor_gremio_com_despesas_fora_do_periodo(
    ata_paa, parametros, acao_factory, acao_associacao_factory, despesa_factory, rateio_despesa_factory
):
    """Testa se verifica_precisa_professor_gremio retorna False quando há despesas fora do período"""
    tipo_unidade = ata_paa.paa.associacao.unidade.tipo_unidade
    parametros.tipos_unidades_professor_gremio = [tipo_unidade]
    parametros.save()
    
    # Cria ação "Orçamento Grêmio Estudantil"
    acao_gremio = acao_factory.create(nome='Orçamento Grêmio Estudantil')
    acao_associacao_gremio = acao_associacao_factory.create(
        associacao=ata_paa.paa.associacao,
        acao=acao_gremio,
        status='ATIVA'
    )
    
    # Cria despesa completa FORA do período do PAA (antes do período)
    periodo_paa = ata_paa.paa.periodo_paa
    despesa = despesa_factory.create(
        associacao=ata_paa.paa.associacao,
        data_transacao=periodo_paa.data_inicial - timedelta(days=1),
        status=STATUS_COMPLETO
    )
    
    # Cria rateio completo com a ação do grêmio
    rateio_despesa_factory.create(
        despesa=despesa,
        associacao=ata_paa.paa.associacao,
        acao_associacao=acao_associacao_gremio
    )
    
    assert verifica_precisa_professor_gremio(ata_paa) is False
