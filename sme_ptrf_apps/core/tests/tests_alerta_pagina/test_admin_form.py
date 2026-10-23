import pytest

from sme_ptrf_apps.core.forms import AlertaPaginaForm
from sme_ptrf_apps.users.fixtures.factories import GrupoAcessoFactory

pytestmark = pytest.mark.django_db


def _dados(recurso, **extra):
    return {
        'texto': '<p>x</p>',
        'categoria': 'AVISO_REMOCAO_PRESIDENTE',
        'data_disparo': '2026-11-15',
        'recurso': recurso.pk,
        'ativo': True, **extra
    }


def test_envia_email_exige_assunto_e_grupos(recurso_legado):
    form = AlertaPaginaForm(data=_dados(recurso_legado, enviar_email=True))

    assert not form.is_valid()
    assert set(form.errors) == {'assunto_email', 'grupos_email'}


def test_envia_email_completo_e_valido(recurso_legado):
    grupo = GrupoAcessoFactory()
    form = AlertaPaginaForm(
        data=_dados(recurso_legado, enviar_email=True, assunto_email='Aviso', grupos_email=[grupo.pk]))

    assert form.is_valid(), form.errors


def test_sem_envio_de_email_nao_exige_assunto_nem_grupos(recurso_legado):
    assert AlertaPaginaForm(data=_dados(recurso_legado)).is_valid()


def test_envia_email_exige_assunto(recurso_legado):
    grupo = GrupoAcessoFactory()
    form = AlertaPaginaForm(
        data=_dados(recurso_legado, enviar_email=True, assunto_email='', grupos_email=[grupo.pk]))

    assert not form.is_valid()
    assert set(form.errors) == {'assunto_email'}
