from datetime import date

from factory import SubFactory
from factory.django import DjangoModelFactory

from sme_ptrf_apps.core.models import RecebimentoEmailAlertaPagina
from sme_ptrf_apps.core.fixtures.factories.alerta_pagina_factory import (
    AlertaPaginaFactory,
)
from sme_ptrf_apps.users.fixtures.factories import UsuarioFactory


class RecebimentoEmailAlertaPaginaFactory(DjangoModelFactory):
    class Meta:
        model = RecebimentoEmailAlertaPagina

    alerta = SubFactory(AlertaPaginaFactory)
    usuario = SubFactory(UsuarioFactory)
    data_ocorrencia = date(2026, 11, 15)