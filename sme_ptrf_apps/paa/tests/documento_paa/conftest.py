import pytest
import uuid
from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model

from sme_ptrf_apps.paa.models import DocumentoPaa
from sme_ptrf_apps.paa.admin import DocumentoPaaAdmin
from django.core.files.uploadedfile import SimpleUploadedFile


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


@pytest.fixture
def documento_paa_com_arquivo(db):
    arquivo = SimpleUploadedFile(
        "documento-paa.pdf",
        b"%PDF-1.4 fake pdf content",
        content_type="application/pdf"
    )

    return DocumentoPaa.objects.create(
        uuid=uuid.uuid4(),
        arquivo_pdf=arquivo,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
    )


@pytest.fixture
def documento_paa_sem_arquivo(db):
    return DocumentoPaa.objects.create(
        uuid=uuid.uuid4(),
        arquivo_pdf=None,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
    )
