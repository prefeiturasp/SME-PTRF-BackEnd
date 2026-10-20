import pytest
from django.core.exceptions import ValidationError

from sme_ptrf_apps.dre.fixtures.factories.comissao_factory import ComissaoFactory
from sme_ptrf_apps.dre.forms import ComissaoAdminForm
from sme_ptrf_apps.dre.models import Comissao


pytestmark = pytest.mark.django_db


def test_comissao_admin_form_validates_recursos_without_saved_instance(recurso_legado):
    form = ComissaoAdminForm(
        data={
            'nome': '  Comissão  Teste  ',
            'recursos': [recurso_legado.pk],
            'responsavel_analise_pc': True,
        }
    )

    assert form.is_valid()

    comissao = form.save(commit=False)

    assert isinstance(comissao, Comissao)
    assert comissao.nome == 'Comissão Teste'


def test_comissao_is_valid_data_accepts_nome_com_espacos_e_recursos(recurso_legado):
    is_valid, error_message = Comissao.is_valid_data(
        nome='  Comissão  Teste  ',
        recursos=[recurso_legado],
    )

    assert is_valid is True
    assert error_message == ''


def test_comissao_is_valid_data_rejects_nome_em_branco(recurso_legado):
    is_valid, error_message = Comissao.is_valid_data(
        nome='   ',
        recursos=[recurso_legado],
    )

    assert is_valid is False
    assert error_message == "O campo 'nome' é obrigatório."


def test_comissao_is_valid_data_rejects_recursos_vazios():
    is_valid, error_message = Comissao.is_valid_data(
        nome='Comissão Teste',
        recursos=[],
    )

    assert is_valid is False
    assert error_message == "O campo 'recursos' é obrigatório"


def test_comissao_is_valid_data_rejects_duplicidade_mesmo_nome_e_recurso(recurso_legado):
    ComissaoFactory(
        nome='Comissão Teste',
        recursos=[recurso_legado],
    )

    is_valid, error_message = Comissao.is_valid_data(
        nome='  Comissão  Teste  ',
        recursos=[recurso_legado],
    )

    assert is_valid is False
    assert error_message == 'Já existe uma comissão com o mesmo nome no recurso selecionado.'


def test_comissao_is_valid_data_rejects_recursos_em_outra_comissao_responsavel(recurso_legado):
    ComissaoFactory(
        nome='Comissão Responsável',
        recursos=[recurso_legado],
        responsavel_analise_pc=True,
    )

    is_valid, error_message = Comissao.is_valid_data(
        nome='Nova Comissão',
        recursos=[recurso_legado],
        responsavel_analise_pc=True,
    )

    assert is_valid is False
    assert error_message == (
        'Um ou mais recursos selecionados já estão associados a uma comissão de análise de prestação de contas.'
    )


def test_comissao_clean_normaliza_nome_e_usa_recursos_da_instancia_nao_salva(recurso_legado):
    comissao = Comissao(
        nome='  Comissão  Teste  ',
        responsavel_analise_pc=True,
    )
    comissao._recursos_validacao = [recurso_legado]

    comissao.clean()

    assert comissao.nome == 'Comissão Teste'


def test_comissao_clean_rejeita_instancia_nao_salva_sem_recursos():
    comissao = Comissao(nome='Comissão Teste')

    with pytest.raises(ValidationError, match="O campo 'recursos' é obrigatório"):
        comissao.clean()




