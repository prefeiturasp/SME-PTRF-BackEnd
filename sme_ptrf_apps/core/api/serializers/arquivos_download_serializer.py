from rest_framework import serializers
from ...models import ArquivoDownload


class ArquivoDownloadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ArquivoDownload
        fields = "__all__"
