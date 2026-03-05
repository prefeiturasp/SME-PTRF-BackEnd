from django.http import JsonResponse
from sme_ptrf_apps.core.models.recurso import Recurso


class TenantFromHeaderMiddleware:
    HEADER_NAME = "HTTP_X_RECURSO_SELECIONADO"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        recurso_uuid = request.META.get(self.HEADER_NAME)

        if not recurso_uuid:
            request.recurso = Recurso.objects.get(legado=True)
            return self.get_response(request)

        recurso = self.get_recurso(recurso_uuid)

        if not recurso:
            return JsonResponse(
                {"detail": "Recurso inválido ou inexistente"},
                status=400,
            )

        request.recurso = recurso
        return self.get_response(request)

    def get_recurso(self, recurso_uuid):
        return Recurso.by_uuid(recurso_uuid)
