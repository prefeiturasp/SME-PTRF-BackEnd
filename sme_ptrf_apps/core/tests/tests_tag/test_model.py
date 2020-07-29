import pytest
from django.contrib import admin
from sme_ptrf_apps.core.models import Tag

pytestmark = pytest.mark.django_db


def test_model_instance(tag):
    model = tag

    assert isinstance(model, Tag)


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Tag]
