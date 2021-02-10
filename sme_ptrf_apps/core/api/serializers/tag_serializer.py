from rest_framework import serializers

from sme_ptrf_apps.core.models import Tag


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class TagLookupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('uuid', 'nome', 'status')
