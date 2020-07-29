from rest_framework import serializers

from sme_ptrf_apps.core.models import Tag


class TagLookupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('uuid', 'nome', 'status')
