import pytest
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from sme_ptrf_apps.core.admin_filters.recurso_filters import RecursoListFilter
from sme_ptrf_apps.core.models import Recurso


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def admin_request():
    return RequestFactory().get("/admin/")


# Mantido para compatibilidade com teste existente
@pytest.fixture
def request_factory_admin(admin_request):
    return admin_request


@pytest.fixture
def recursos(db):
    ptrf = Recurso.objects.create(nome="ptrf", ativo=True)
    premium = Recurso.objects.create(nome="premium", ativo=True)
    Recurso.objects.create(nome="inativo", ativo=False)
    return ptrf, premium


@pytest.fixture
def recurso_list_filter(admin_request):
    return RecursoListFilter(admin_request, {}, Recurso, AdminSite())


def make_filter(filter_class, admin_request, value=None):
    params = {"recurso": value} if value is not None else {}
    return filter_class(admin_request, params, Recurso, AdminSite())
