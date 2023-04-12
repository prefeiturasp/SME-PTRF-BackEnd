import pytest
from django.contrib import admin

from ...models import AnalisePrestacaoConta, TipoDocumentoPrestacaoConta, AnaliseDocumentoPrestacaoConta, ContaAssociacao

from sme_ptrf_apps.receitas.models import Receita
from sme_ptrf_apps.despesas.models import Despesa

pytestmark = pytest.mark.django_db


def test_instance_model(analise_documento_prestacao_conta_2020_1_ata_correta):
    model = analise_documento_prestacao_conta_2020_1_ata_correta
    assert isinstance(model, AnaliseDocumentoPrestacaoConta)
    assert isinstance(model.analise_prestacao_conta, AnalisePrestacaoConta)
    assert isinstance(model.tipo_documento_prestacao_conta, TipoDocumentoPrestacaoConta)
    assert isinstance(model.conta_associacao, ContaAssociacao)
    assert model.resultado == AnaliseDocumentoPrestacaoConta.RESULTADO_CORRETO
    assert model.status_realizacao == AnaliseDocumentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE


def test_srt_model(analise_documento_prestacao_conta_2020_1_ata_correta):
    esperado = f'Análise de documento {analise_documento_prestacao_conta_2020_1_ata_correta.uuid} - Resultado:CORRETO'
    assert analise_documento_prestacao_conta_2020_1_ata_correta.__str__() == esperado


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[AnaliseDocumentoPrestacaoConta]


def test_audit_log(analise_documento_prestacao_conta_2020_1_ata_correta):
    assert analise_documento_prestacao_conta_2020_1_ata_correta.history.count() == 1  # Um log de inclusão
    assert analise_documento_prestacao_conta_2020_1_ata_correta.history.latest().action == 0  # 0-Inclusão

    analise_documento_prestacao_conta_2020_1_ata_correta.resultado = "AJUSTE"
    analise_documento_prestacao_conta_2020_1_ata_correta.save()
    assert analise_documento_prestacao_conta_2020_1_ata_correta.history.count() == 2  # Um log de inclusão e outro de edição
    assert analise_documento_prestacao_conta_2020_1_ata_correta.history.latest().action == 1  # 1-Edição


def test_model_property_requer_esclarecimentos(
    analise_documento_prestacao_conta_2020_1_ata_ajuste,
    solicitacao_acerto_documento_ata_esclarecimentos,
):
    assert analise_documento_prestacao_conta_2020_1_ata_ajuste.requer_esclarecimentos


def test_model_property_requer_inclusao_credito(
    analise_documento_prestacao_conta_2020_1_ata_ajuste,
    solicitacao_acerto_documento_ata_inclusao_credito,
):
    assert analise_documento_prestacao_conta_2020_1_ata_ajuste.requer_inclusao_credito


def test_model_property_requer_inclusao_gasto(
    analise_documento_prestacao_conta_2020_1_ata_ajuste,
    solicitacao_acerto_documento_ata_inclusao_despesa,
):
    assert analise_documento_prestacao_conta_2020_1_ata_ajuste.requer_inclusao_gasto


def test_model_property_requer_ajuste_externo(
    analise_documento_prestacao_conta_2020_1_ata_ajuste,
    solicitacao_acerto_documento_ata_ajuste_externo,
):
    assert analise_documento_prestacao_conta_2020_1_ata_ajuste.requer_ajuste_externo


def test_model_property_requer_edicao_informacao(
    analise_documento_prestacao_conta_demonstativo_financeiro_edicao_informacao,
    solicitacao_acerto_documento_edicao_informacao,
):
    assert analise_documento_prestacao_conta_demonstativo_financeiro_edicao_informacao.requer_edicao_informacao_conciliacao


def test_get_tags_informacoes_conferencia_list():
    tags = AnaliseDocumentoPrestacaoConta.get_tags_informacoes_de_conferencia_list()
    assert tags == [
        {
            'id': '1',
            'nome': 'AJUSTE',
            'descricao': 'O documento possui acertos para serem conferidos.',
        },
        {
            'id': '2',
            'nome': 'CORRETO',
            'descricao': 'O documento está correto e/ou os acertos foram conferidos.',
        },
        {
            'id': '3',
            'nome': 'NAO_CONFERIDO',
            'descricao': 'Não conferido.',
        }
    ]
