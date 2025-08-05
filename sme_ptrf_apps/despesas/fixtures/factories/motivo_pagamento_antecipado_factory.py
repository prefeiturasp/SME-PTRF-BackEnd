from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.despesas.models.motivo_pagamento_antecipado import MotivoPagamentoAntecipado

fake = Faker("pt_BR")


class MotivoPagamentoAntecipadoFactory(DjangoModelFactory):
    class Meta:
        model = MotivoPagamentoAntecipado
