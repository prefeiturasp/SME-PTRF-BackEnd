from django.http import JsonResponse
from rest_framework.decorators import api_view
from waffle import get_waffle_flag_model


@api_view()
def feature_flags(request):
    Flag = get_waffle_flag_model()
    flags = Flag.get_all()
    return JsonResponse({flag.name: flag.is_active(request) for flag in flags})
