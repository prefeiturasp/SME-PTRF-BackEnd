from django.conf import settings
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter, SimpleRouter

from sme_ptrf_apps import __version__
from sme_ptrf_apps.core.api.views import (
    AssociacoesViewSet,
    AtasViewSet,
    DemonstrativoFinanceiroViewSet,
    MembroAssociacaoViewSet,
    PeriodosViewSet,
    PrestacoesContasViewSet,
    RelacaoBensViewSet,
    ProcessosAssociacaoViewSet,
    UnidadesViewSet

)
from sme_ptrf_apps.despesas.api.views.despesas_viewset import DespesasViewSet
from sme_ptrf_apps.despesas.api.views.especificacoes_viewset import EspecificacaoMaterialServicoViewSet
from sme_ptrf_apps.despesas.api.views.fornecedores_viewset import FornecedoresViewSet
from sme_ptrf_apps.despesas.api.views.rateios_despesas_viewset import RateiosDespesasViewSet
from sme_ptrf_apps.dre.api.views import TecnicosDreViewSet
from sme_ptrf_apps.receitas.api.views import ReceitaViewSet, RepasseViewSet
from sme_ptrf_apps.users.api.views import EsqueciMinhaSenhaViewSet, LoginView, RedefinirSenhaViewSet, UserViewSet
from sme_ptrf_apps.dre.api.views import FaqCategoriasViewSet, FaqsViewSet


@api_view()
def versao(request):
    return Response({"versao": __version__})


if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("usuarios", UserViewSet)
router.register("despesas", DespesasViewSet)
router.register("especificacoes", EspecificacaoMaterialServicoViewSet)
router.register("rateios-despesas", RateiosDespesasViewSet)
router.register("receitas", ReceitaViewSet)
router.register("fornecedores", FornecedoresViewSet)
router.register("associacoes", AssociacoesViewSet)
router.register("repasses", RepasseViewSet, basename='repasses-pendentes')
router.register("periodos", PeriodosViewSet)
router.register("prestacoes-contas", PrestacoesContasViewSet)
router.register("demonstrativo-financeiro", DemonstrativoFinanceiroViewSet)
router.register("relacao-bens", RelacaoBensViewSet)
router.register("atas-associacao", AtasViewSet)
router.register("membros-associacao", MembroAssociacaoViewSet)
router.register("esqueci-minha-senha", EsqueciMinhaSenhaViewSet)
router.register("redefinir-senha", RedefinirSenhaViewSet)
router.register("processos-associacao", ProcessosAssociacaoViewSet)
router.register("unidades", UnidadesViewSet)
router.register("tecnicos-dre", TecnicosDreViewSet)
router.register("faq-categorias", FaqCategoriasViewSet)
router.register("faqs", FaqsViewSet)

app_name = "api"
urlpatterns = router.urls
urlpatterns += [
    path("versao", versao),
    path("login", LoginView.as_view()),
]
