import pytest
from model_bakery import baker

@pytest.fixture
def faq_01():
    return baker.make(
        'Faq',
        uuid='e7a6e5d7-49ee-45cf-86c7-55be1eadfc15',
        pergunta='Pergunta 01 - Cat Geral 01',
        resposta='Esta é a resposta da Pergunta 01',
    )


@pytest.fixture
def faq_02():
    return baker.make(
        'Faq',
        uuid='86b95b16-6d70-44c8-a3f8-f8ebcabc2b5f',
        pergunta='Pergunta 02 - Cat Associações 01',
        resposta='Esta é a resposta da Pergunta 02',
    )
