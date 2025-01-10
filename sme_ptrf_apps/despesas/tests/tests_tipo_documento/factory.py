import factory
from ...models import TipoDocumento


class TipoDocumentoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TipoDocumento

    nome = factory.Faker("nome")
    apenas_digitos = True
    numero_documento_digitado = False
    pode_reter_imposto = False
    eh_documento_de_retencao_de_imposto = False
    documento_comprobatorio_de_despesa = False
