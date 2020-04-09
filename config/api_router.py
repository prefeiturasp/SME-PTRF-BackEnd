from django.conf import settings
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter, SimpleRouter

from sme_ptrf_apps import __version__
from sme_ptrf_apps.despesas.api.views.despesas_viewset import DespesasViewSet
from sme_ptrf_apps.despesas.api.views.especificacoes_viewset import EspecificacaoMaterialServicoViewSet
from sme_ptrf_apps.despesas.api.views.rateios_despesas_viewset import RateiosDespesasViewSet
from sme_ptrf_apps.users.api.views import LoginView, UserViewSet
from sme_ptrf_apps.receitas.api.views import ReceitaViewSet


@api_view()
def versao(request):
    return Response({"versao": __version__})


if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("despesas", DespesasViewSet)
router.register("especificacoes", EspecificacaoMaterialServicoViewSet)
router.register("rateios-despesas", RateiosDespesasViewSet)
router.register("receitas", ReceitaViewSet)

app_name = "api"
urlpatterns = router.urls
urlpatterns += [
    path("versao", versao),
    path("login", LoginView.as_view())
]
