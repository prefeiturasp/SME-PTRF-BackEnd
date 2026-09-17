from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict

from sme_ptrf_apps.core.admin import (
    AcaoAdminForm,
    PeriodoAdminForm,
    ProcessoAssociacaoAdminForm,
    TipoContaAdminForm,
    AcaoAssociacaoForm,
    ParametrosAdminForm,
)
from sme_ptrf_apps.core.models import Acao, Periodo, ProcessoAssociacao, TipoConta

pytestmark = pytest.mark.django_db


# clean_recurso: instância não salva (pk=None) faz o validador retornar sem erro
def test_acao_admin_form_clean_recurso_retorna_recurso(recurso):
    form = AcaoAdminForm(instance=Acao())
    form.cleaned_data = {'recurso': recurso}
    assert form.clean_recurso() == recurso


def test_acao_admin_form_clean_recurso_propaga_erro_do_validador(recurso):
    form = AcaoAdminForm(instance=Acao())
    form.cleaned_data = {'recurso': recurso}
    with patch(
        'sme_ptrf_apps.core.services.acao_associacao_service.validar_troca_recurso',
        side_effect=ValidationError('Não é possível alterar o recurso de uma ação já utilizada.'),
    ):
        with pytest.raises(ValidationError):
            form.clean_recurso()


def test_periodo_admin_form_clean_recurso_retorna_recurso(recurso):
    form = PeriodoAdminForm(instance=Periodo())
    form.cleaned_data = {'recurso': recurso}
    assert form.clean_recurso() == recurso


def test_periodo_admin_form_clean_recurso_propaga_erro_do_validador(recurso):
    form = PeriodoAdminForm(instance=Periodo())
    form.cleaned_data = {'recurso': recurso}
    with patch(
        'sme_ptrf_apps.core.services.periodo_services.validar_troca_recurso',
        side_effect=ValidationError('Não é possível alterar o recurso de um período já utilizado.'),
    ):
        with pytest.raises(ValidationError):
            form.clean_recurso()


def test_processo_associacao_admin_form_clean_recurso_retorna_recurso(recurso):
    form = ProcessoAssociacaoAdminForm(instance=ProcessoAssociacao())
    form.cleaned_data = {'recurso': recurso}
    assert form.clean_recurso() == recurso


def test_processo_associacao_admin_form_clean_recurso_propaga_erro_do_validador(recurso):
    form = ProcessoAssociacaoAdminForm(instance=ProcessoAssociacao())
    form.cleaned_data = {'recurso': recurso}
    with patch(
        'sme_ptrf_apps.core.services.processos_services.validar_troca_recurso_em_processo_associacao',
        side_effect=ValidationError('Não é possível alterar o recurso de um processo de associação já utilizado.'),
    ):
        with pytest.raises(ValidationError):
            form.clean_recurso()


def test_tipo_conta_admin_form_clean_recurso_retorna_recurso(recurso):
    form = TipoContaAdminForm(instance=TipoConta())
    form.cleaned_data = {'recurso': recurso}
    assert form.clean_recurso() == recurso


def test_tipo_conta_admin_form_clean_recurso_propaga_erro_do_validador(recurso):
    form = TipoContaAdminForm(instance=TipoConta())
    form.cleaned_data = {'recurso': recurso}
    with patch(
        'sme_ptrf_apps.core.services.tipo_conta_service.validar_troca_recurso',
        side_effect=ValidationError('Não é possível alterar o recurso de um tipo de conta já utilizado.'),
    ):
        with pytest.raises(ValidationError):
            form.clean_recurso()


def _nova_acao_associacao_form():
    form = AcaoAssociacaoForm.__new__(AcaoAssociacaoForm)
    form.instance = MagicMock()
    return form


def test_acao_associacao_form_clean_sem_associacao_ou_acao_nao_valida():
    form = _nova_acao_associacao_form()
    form.cleaned_data = {'associacao': None, 'acao': None}
    with patch('sme_ptrf_apps.core.services.acoes_associacoes_service.validate_acao_associacao') as mock_validate:
        resultado = form.clean()
    mock_validate.assert_not_called()
    assert resultado == {'associacao': None, 'acao': None}


def test_acao_associacao_form_clean_valida_com_sucesso():
    associacao = MagicMock()
    acao = MagicMock()
    form = _nova_acao_associacao_form()
    form.cleaned_data = {'associacao': associacao, 'acao': acao}
    with patch('sme_ptrf_apps.core.services.acoes_associacoes_service.validate_acao_associacao') as mock_validate:
        resultado = form.clean()
    mock_validate.assert_called_once_with(associacao, acao, form.instance)
    assert resultado == {'associacao': associacao, 'acao': acao}


def test_acao_associacao_form_clean_propaga_erro_como_validation_error():
    associacao = MagicMock()
    acao = MagicMock()
    form = _nova_acao_associacao_form()
    form.cleaned_data = {'associacao': associacao, 'acao': acao}
    with patch(
        'sme_ptrf_apps.core.services.acoes_associacoes_service.validate_acao_associacao',
        side_effect=Exception('associação e ação incompatíveis'),
    ):
        with pytest.raises(ValidationError):
            form.clean()


# ParametrosAdminForm
def test_parametros_admin_form_init_carrega_valor_inicial(parametros):
    parametros.tipos_unidades_professor_gremio = ['EMEF', 'EMEI']
    parametros.save()

    form = ParametrosAdminForm(instance=parametros)

    assert form.fields['tipos_unidades_professor_gremio'].initial == ['EMEF', 'EMEI']


def test_parametros_admin_form_save_grava_tipos_unidades(parametros):
    dados = model_to_dict(parametros)
    dados['tipos_unidades_professor_gremio'] = ['CEU']
    dados['fique_de_olho'] = dados['fique_de_olho'] or 'texto'
    dados['fique_de_olho_relatorio_dre'] = dados['fique_de_olho_relatorio_dre'] or 'texto'

    form = ParametrosAdminForm(data=dados, instance=parametros)
    assert form.is_valid(), form.errors

    instancia = form.save(commit=True)

    instancia.refresh_from_db()
    assert instancia.tipos_unidades_professor_gremio == ['CEU']
