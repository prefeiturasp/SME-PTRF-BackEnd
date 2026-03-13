import pytest
from django.test import RequestFactory
from sme_ptrf_apps.core.models.recurso import Recurso
from django.contrib.admin.sites import AdminSite
from sme_ptrf_apps.core.admin_filters.recurso_filters import RecursoListFilter


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def request_factory_admin():
    factory = RequestFactory()
    return factory.get("/admin/")


@pytest.fixture
def recursos(db):
    ptrf = Recurso.objects.create(nome="ptrf", ativo=True)
    premium = Recurso.objects.create(nome="premium", ativo=True)
    Recurso.objects.create(nome="inativo", ativo=False)

    return ptrf, premium


@pytest.fixture
def recurso_list_filter():
    return RecursoListFilter(
        request_factory_admin,
        {},
        Recurso,
        AdminSite()
    )
