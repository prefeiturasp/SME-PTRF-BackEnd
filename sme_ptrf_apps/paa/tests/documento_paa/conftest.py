import pytest
from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model

from sme_ptrf_apps.paa.models import DocumentoPaa
from sme_ptrf_apps.paa.admin import DocumentoPaaAdmin


@pytest.fixture
def documento_paa_admin():
    return DocumentoPaaAdmin(model=DocumentoPaa, admin_site=site)


@pytest.fixture
def documento_paa(documento_paa_factory):
    return documento_paa_factory.create()


@pytest.fixture
def usuario_task():
    User = get_user_model()
    return User.objects.create_user(
        username='usuario_task_test',
        password='senha123',
        email='task@teste.com'
    )
