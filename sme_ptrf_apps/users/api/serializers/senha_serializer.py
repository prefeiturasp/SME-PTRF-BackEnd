
from django.contrib.auth import get_user_model
from rest_framework import serializers

from sme_ptrf_apps.users.tasks import enviar_email_redifinicao_senha

User = get_user_model()


class EsqueciMinhaSenhaSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        instance.hash_redefinicao = instance.create_hash
        instance.save()

        enviar_email_redifinicao_senha.delay(email=instance.email, username=instance.username,
                                             nome=instance.name, hash_definicao=instance.hash_redefinicao)

        return instance

    class Meta:
        model = User
        fields = ('username', 'email',)
