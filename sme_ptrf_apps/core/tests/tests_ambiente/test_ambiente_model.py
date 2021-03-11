import pytest
from django.contrib import admin
from sme_ptrf_apps.core.models import Ambiente

pytestmark = pytest.mark.django_db


def test_model_instance(ambiente_dev):
    model = ambiente_dev

    assert isinstance(model, Ambiente)


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Ambiente]
