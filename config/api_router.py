from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from django.urls import path
from sme_ptrf_apps.users.api.views import UserViewSet
from sme_ptrf_apps.despesas.api.views.despesas_viewset import DespesasViewSet
from sme_ptrf_apps import __version__


@api_view()
def versao(request):
    return Response({"versao": __version__})


if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("despesas", DespesasViewSet)


app_name = "api"
urlpatterns = router.urls
urlpatterns += [
    path("versao", versao)
]
