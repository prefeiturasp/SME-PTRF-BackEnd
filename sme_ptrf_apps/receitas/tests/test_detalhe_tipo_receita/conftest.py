import pytest
from django.test import RequestFactory

from sme_ptrf_apps.receitas.models.detalhe_tipo_receita import DetalheTipoReceita
from sme_ptrf_apps.receitas.admin import DetalheTipoReceitaAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def detalhe_tipo_receita_admin():
    return DetalheTipoReceitaAdmin(model=DetalheTipoReceita, admin_site=site)


@pytest.fixture
def admin_request(db):
    from django.contrib.auth import get_user_model
    user_model = get_user_model()
    senha = 'Sgp0418'
    user = user_model.objects.create_superuser(username='admin_detalhe', password=senha, email='admin_detalhe@test.com')
    request = RequestFactory().get('/admin/')
    request.user = user
    return request


@pytest.fixture
def tipo_receita_sem_detalhamento(tipo_receita_factory):
    return tipo_receita_factory.create(nome='Tipo sem detalhamento', possui_detalhamento=False)


@pytest.fixture
def outro_tipo_receita_com_detalhamento(tipo_receita_factory):
    return tipo_receita_factory.create(nome='Outro Tipo com detalhamento', possui_detalhamento=True)
