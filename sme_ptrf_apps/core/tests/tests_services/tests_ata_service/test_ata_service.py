import pytest
from sme_ptrf_apps.core.services.ata_service import (
    validar_campos_ata,
    unidade_precisa_professor_gremio,
    verifica_precisa_professor_gremio_ata
)


@pytest.mark.django_db(transaction=False)
def test_validar_campos_ata_completa(ata_2022_2_teste_valido, presente_ata_membro_arnaldo, presente_ata_membro_falcao):
    result = validar_campos_ata(ata_2022_2_teste_valido)
    expected_result = {'is_valid': True}
    assert result == expected_result

@pytest.mark.django_db(transaction=False)
def test_validar_campos_invalidos(ata_2022_test_campos_invalidos, presente_ata_membro_arnaldo, presente_ata_membro_falcao):
    ata_2022_test_campos_invalidos.justificativa_repasses_pendentes = ''
    ata_2022_test_campos_invalidos.data_reuniao = ''
    result = validar_campos_ata(ata_2022_test_campos_invalidos)
    expected_result = {
        'is_valid': False,
        'campos': [
            'Cargo Presidente',
            'Cargo Secretário',
            'Data',
            'Local da reunião',
            'Presidente da reunião',
            'Secretário da reunião'
        ]}
    assert result == expected_result


@pytest.mark.django_db(transaction=False)
def test_validar_campos_ata_sem_presidente_e_secretario(ata_2020_1_teste):
    result = validar_campos_ata(ata_2020_1_teste)
    expected_result = {
        'is_valid': False,
        'campos': [{'msg_presente': 'informe um presidente presente, informe um secretário presente'}]
        }
    assert result == expected_result


@pytest.mark.django_db
def test_unidade_precisa_professor_gremio_com_tipo_configurado(parametros):
    """Testa se unidade_precisa_professor_gremio retorna True quando tipo está configurado"""
    parametros.tipos_unidades_professor_gremio = ['EMEF', 'EMEI']
    parametros.save()
    
    assert unidade_precisa_professor_gremio('EMEF') is True
    assert unidade_precisa_professor_gremio('EMEI') is True
    assert unidade_precisa_professor_gremio('CEU') is False


@pytest.mark.django_db
def test_unidade_precisa_professor_gremio_sem_configuracao(parametros):
    """Testa se unidade_precisa_professor_gremio retorna False quando não há configuração"""
    parametros.tipos_unidades_professor_gremio = []
    parametros.save()
    
    assert unidade_precisa_professor_gremio('EMEF') is False


@pytest.mark.django_db
def test_unidade_precisa_professor_gremio_sem_parametros():
    """Testa se unidade_precisa_professor_gremio retorna False quando não há parâmetros"""
    from sme_ptrf_apps.core.models import Parametros
    Parametros.objects.all().delete()
    
    assert unidade_precisa_professor_gremio('EMEF') is False

@pytest.mark.django_db
def test_verifica_precisa_professor_gremio_ata_sem_tipo_configurado(ata_prestacao_conta_iniciada, parametros):
    """Testa se verifica_precisa_professor_gremio_ata retorna False quando tipo não está configurado"""
    parametros.tipos_unidades_professor_gremio = []
    parametros.save()
    
    assert verifica_precisa_professor_gremio_ata(ata_prestacao_conta_iniciada) is False


@pytest.mark.django_db
def test_verifica_precisa_professor_gremio_ata_com_tipo_configurado_sem_despesas(ata_prestacao_conta_iniciada, parametros):
    """Testa se verifica_precisa_professor_gremio_ata retorna False quando tipo está configurado mas não há despesas"""
    tipo_unidade = ata_prestacao_conta_iniciada.associacao.unidade.tipo_unidade
    parametros.tipos_unidades_professor_gremio = [tipo_unidade]
    parametros.save()
    
    assert verifica_precisa_professor_gremio_ata(ata_prestacao_conta_iniciada) is False


@pytest.mark.django_db
def test_verifica_precisa_professor_gremio_ata_com_despesas_completas_gremio_no_periodo(
    ata_prestacao_conta_iniciada, parametros, acao_factory, acao_associacao_factory, 
    despesa_factory, rateio_despesa_factory
):
    """Testa se verifica_precisa_professor_gremio_ata retorna True quando há despesas completas com ação grêmio no período"""
    tipo_unidade = ata_prestacao_conta_iniciada.associacao.unidade.tipo_unidade
    parametros.tipos_unidades_professor_gremio = [tipo_unidade]
    parametros.save()
    
    # Cria ação "Orçamento Grêmio Estudantil"
    acao_gremio = acao_factory(nome='Orçamento Grêmio Estudantil')
    acao_associacao = acao_associacao_factory(
        associacao=ata_prestacao_conta_iniciada.associacao,
        acao=acao_gremio,
        status='ATIVA'
    )
    
    # Cria despesa completa no período
    periodo = ata_prestacao_conta_iniciada.periodo
    despesa = despesa_factory(
        associacao=ata_prestacao_conta_iniciada.associacao,
        data_transacao=periodo.data_inicio_realizacao_despesas
    )
    
    rateio_despesa_factory(
        despesa=despesa,
        acao_associacao=acao_associacao,
        associacao=ata_prestacao_conta_iniciada.associacao,
        conferido=True,
        valor_rateio=100.00
    )
    
    assert verifica_precisa_professor_gremio_ata(ata_prestacao_conta_iniciada) is True


@pytest.mark.django_db
def test_verifica_precisa_professor_gremio_ata_sem_acao_gremio(ata_prestacao_conta_iniciada, parametros):
    """Testa se verifica_precisa_professor_gremio_ata retorna False quando não há ação grêmio"""
    tipo_unidade = ata_prestacao_conta_iniciada.associacao.unidade.tipo_unidade
    parametros.tipos_unidades_professor_gremio = [tipo_unidade]
    parametros.save()
    
    assert verifica_precisa_professor_gremio_ata(ata_prestacao_conta_iniciada) is False
