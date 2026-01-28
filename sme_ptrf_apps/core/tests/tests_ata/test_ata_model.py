import pytest
from datetime import date, time
from django.contrib import admin

from ...models import PrestacaoConta, Associacao, Periodo, Ata

pytestmark = pytest.mark.django_db


def test_instance_model(ata_2020_1_cheque_aprovada):
    model = ata_2020_1_cheque_aprovada
    assert isinstance(model, Ata)
    assert isinstance(model.prestacao_conta, PrestacaoConta)
    assert isinstance(model.associacao, Associacao)
    assert isinstance(model.periodo, Periodo)
    assert f'{model.arquivo_pdf}.arquivo_pdf'
    assert model.tipo_ata
    assert model.tipo_reuniao
    assert model.convocacao
    assert model.status_geracao_pdf
    assert model.data_reuniao
    assert model.local_reuniao
    assert model.presidente_reuniao
    assert model.cargo_presidente_reuniao
    assert model.secretario_reuniao
    assert model.cargo_secretaria_reuniao
    assert model.comentarios
    assert model.parecer_conselho
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.preenchida_em is None
    assert model.justificativa_repasses_pendentes is ''


def test_instance_mode_ata_retificacao(ata_2020_1_retificacao):
    model = ata_2020_1_retificacao
    assert isinstance(model, Ata)
    assert model.retificacoes


def test_srt_model(ata_2020_1_cheque_aprovada):
    assert ata_2020_1_cheque_aprovada.__str__() == 'Ata 2020.1 - Apresentação - 2020-07-01'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Ata]


def test_iniciar_ata(prestacao_conta_2020_1_conciliada):
    ata = Ata.iniciar(prestacao_conta_2020_1_conciliada)
    assert ata.prestacao_conta == prestacao_conta_2020_1_conciliada
    assert ata.periodo == prestacao_conta_2020_1_conciliada.periodo
    assert ata.associacao == prestacao_conta_2020_1_conciliada.associacao


def test_preenchida_em(ata_prestacao_conta_iniciada):
    ata_prestacao_conta_iniciada.local_reuniao = 'teste'
    ata_prestacao_conta_iniciada.save()
    ata = Ata.by_id(ata_prestacao_conta_iniciada.id)
    assert ata.preenchida_em is not None


@pytest.mark.django_db
def test_completa_com_novos_campos_com_flag_ativa(ata_prestacao_conta_iniciada, associacao, periodo):
    from model_bakery import baker
    from waffle.models import Flag
    
    # Cria flag ativa
    Flag.objects.create(name='historico-de-membros', everyone=True)
    
    # Cria participantes
    presidente = baker.make('Participante', nome='Presidente Teste')
    secretario = baker.make('Participante', nome='Secretario Teste')
    
    # Preenche ata com novos campos
    ata_prestacao_conta_iniciada.presidente_da_reuniao = presidente
    ata_prestacao_conta_iniciada.secretario_da_reuniao = secretario
    ata_prestacao_conta_iniciada.tipo_ata = Ata.ATA_APRESENTACAO
    ata_prestacao_conta_iniciada.tipo_reuniao = Ata.REUNIAO_ORDINARIA
    ata_prestacao_conta_iniciada.convocacao = Ata.CONVOCACAO_PRIMEIRA
    ata_prestacao_conta_iniciada.data_reuniao = date(2024, 1, 1)
    ata_prestacao_conta_iniciada.local_reuniao = 'Local Teste'
    ata_prestacao_conta_iniciada.hora_reuniao = time(10, 0)
    ata_prestacao_conta_iniciada.save()
    
    assert ata_prestacao_conta_iniciada.completa is True


@pytest.mark.django_db
def test_completa_com_campos_legados_com_flag_ativa(ata_prestacao_conta_iniciada, associacao, periodo):
    from waffle.models import Flag
    
    # Cria flag ativa
    Flag.objects.create(name='historico-de-membros', everyone=True)
    
    # Preenche ata com campos legados (não precisa verificar se estão na lista de presentes)
    ata_prestacao_conta_iniciada.presidente_reuniao = 'Presidente Legado'
    ata_prestacao_conta_iniciada.cargo_presidente_reuniao = 'Cargo Presidente'
    ata_prestacao_conta_iniciada.secretario_reuniao = 'Secretario Legado'
    ata_prestacao_conta_iniciada.cargo_secretaria_reuniao = 'Cargo Secretario'
    ata_prestacao_conta_iniciada.tipo_ata = Ata.ATA_APRESENTACAO
    ata_prestacao_conta_iniciada.tipo_reuniao = Ata.REUNIAO_ORDINARIA
    ata_prestacao_conta_iniciada.convocacao = Ata.CONVOCACAO_PRIMEIRA
    ata_prestacao_conta_iniciada.data_reuniao = date(2024, 1, 1)
    ata_prestacao_conta_iniciada.local_reuniao = 'Local Teste'
    ata_prestacao_conta_iniciada.hora_reuniao = time(10, 0)
    ata_prestacao_conta_iniciada.save()
    
    assert ata_prestacao_conta_iniciada.completa is True


@pytest.mark.django_db
def test_completa_sem_campos_com_flag_ativa(ata_prestacao_conta_iniciada, associacao, periodo):
    from waffle.models import Flag
    
    # Cria flag ativa
    Flag.objects.create(name='historico-de-membros', everyone=True)
    
    # Limpa campos de presidente/secretário (novos e legados)
    ata_prestacao_conta_iniciada.presidente_da_reuniao = None
    ata_prestacao_conta_iniciada.secretario_da_reuniao = None
    ata_prestacao_conta_iniciada.presidente_reuniao = ''
    ata_prestacao_conta_iniciada.cargo_presidente_reuniao = ''
    ata_prestacao_conta_iniciada.secretario_reuniao = ''
    ata_prestacao_conta_iniciada.cargo_secretaria_reuniao = ''
    
    # Preenche apenas campos básicos, sem presidente/secretário
    ata_prestacao_conta_iniciada.tipo_ata = Ata.ATA_APRESENTACAO
    ata_prestacao_conta_iniciada.tipo_reuniao = Ata.REUNIAO_ORDINARIA
    ata_prestacao_conta_iniciada.convocacao = Ata.CONVOCACAO_PRIMEIRA
    ata_prestacao_conta_iniciada.data_reuniao = date(2024, 1, 1)
    ata_prestacao_conta_iniciada.local_reuniao = 'Local Teste'
    ata_prestacao_conta_iniciada.hora_reuniao = time(10, 0)
    ata_prestacao_conta_iniciada.save()
    
    assert ata_prestacao_conta_iniciada.completa is False


def test_precisa_professor_gremio_retorna_bool(ata_prestacao_conta_iniciada):
    """Testa se precisa_professor_gremio retorna um booleano"""
    assert isinstance(ata_prestacao_conta_iniciada.precisa_professor_gremio, bool)


def test_precisa_professor_gremio_sem_periodo(ata_prestacao_conta_iniciada):
    """Testa se precisa_professor_gremio retorna False quando não há período"""
    periodo_original = ata_prestacao_conta_iniciada.periodo
    ata_prestacao_conta_iniciada.periodo = None
    assert ata_prestacao_conta_iniciada.precisa_professor_gremio is False
    ata_prestacao_conta_iniciada.periodo = periodo_original


def test_precisa_professor_gremio_sem_tipo_configurado(ata_prestacao_conta_iniciada, parametros):
    """Testa se precisa_professor_gremio retorna False quando tipo de unidade não está configurado"""
    parametros.tipos_unidades_professor_gremio = []
    parametros.save()
    
    assert ata_prestacao_conta_iniciada.precisa_professor_gremio is False


def test_precisa_professor_gremio_com_tipo_configurado_sem_despesas(ata_prestacao_conta_iniciada, parametros):
    """Testa se precisa_professor_gremio retorna False quando tipo está configurado mas não há despesas"""
    tipo_unidade = ata_prestacao_conta_iniciada.associacao.unidade.tipo_unidade
    parametros.tipos_unidades_professor_gremio = [tipo_unidade]
    parametros.save()
    
    assert ata_prestacao_conta_iniciada.precisa_professor_gremio is False


def test_precisa_professor_gremio_com_despesas_completas_gremio_no_periodo(
    ata_prestacao_conta_iniciada, parametros, acao_factory, acao_associacao_factory, 
    despesa_factory, rateio_despesa_factory
):
    """Testa se precisa_professor_gremio retorna True quando há despesas completas com ação grêmio no período"""
    from sme_ptrf_apps.despesas.models import RateioDespesa
    
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
    
    assert ata_prestacao_conta_iniciada.precisa_professor_gremio is True


def test_precisa_professor_gremio_sem_acao_gremio(ata_prestacao_conta_iniciada, parametros):
    """Testa se precisa_professor_gremio retorna False quando não há ação grêmio"""
    tipo_unidade = ata_prestacao_conta_iniciada.associacao.unidade.tipo_unidade
    parametros.tipos_unidades_professor_gremio = [tipo_unidade]
    parametros.save()
    
    assert ata_prestacao_conta_iniciada.precisa_professor_gremio is False
