from rest_framework import serializers

from sme_ptrf_apps.core.models import Unidade
from sme_ptrf_apps.dre.services import MembroComissaoService
from sme_ptrf_apps.dre.api.serializers.comissao_serializer import ComissaoSerializer
from ...models import MembroComissao


class MembroComissaoListSerializer(serializers.ModelSerializer):
    dre = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Unidade.dres.all()
    )
    comissoes = ComissaoSerializer(many=True)

    class Meta:
        model = MembroComissao
        fields = (
            'uuid',
            'rf',
            'nome',
            'email',
            'eh_contador',
            'contador_crc',
            'qtd_comissoes',
            'dre',
            'comissoes'
        )


class MembroComissaoCreateSerializer(serializers.ModelSerializer):
    dre = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Unidade.dres.all()
    )

    def validate(self, attrs):
        eh_contador = attrs.get(
            'eh_contador',
            self.instance.eh_contador if self.instance else False
        )

        if not eh_contador:
            attrs['contador_crc'] = None
            return attrs

        crc = attrs.get(
            'contador_crc',
            self.instance.contador_crc if self.instance else None
        )

        crc = crc.strip().upper() if crc else ''

        if not crc:
            raise serializers.ValidationError({
                'contador_crc': 'Informe o CRC do contador.'
            })

        dre = attrs.get(
            'dre',
            self.instance.dre if self.instance else None
        )

        if dre:
            membros = MembroComissao.objects.filter(
                dre=dre,
                contador_crc__iexact=crc,
                eh_contador=True
            )

            if self.instance:
                membros = membros.exclude(pk=self.instance.pk)

            if membros.exists():
                raise serializers.ValidationError({
                    'contador_crc': 'Já existe um contador com este CRC nesta DRE.'
                })

        attrs['contador_crc'] = crc

        return attrs

    def create(self, validated_data):
        """
        Cria um novo membro da comissão e nas atas em elaboração.

        Recebe os dados validados e realiza a criação do membro da comissão
        por meio do serviço MembroComissaoService.
        """
        return MembroComissaoService.criar_membro(validated_data)

    def update(self, instance, validated_data):
        """
        Atualiza um membro da comissão e das atas em elaboração em que ele está presente.

        Existe o caso de exclusão da ata caso a atualização seja a retirada
        da comissão que é responsável pela análise pc.

        Recebe a instância do membro e os dados validados e realiza a
        atualização do membro da comissão por meio do serviço
        MembroComissaoService.
        """
        return MembroComissaoService.atualizar_membro(instance, validated_data)

    class Meta:
        model = MembroComissao
        fields = (
            'uuid',
            'rf',
            'nome',
            'email',
            'eh_contador',
            'contador_crc',
            'qtd_comissoes',
            'dre',
            'comissoes'
        )


class MembroComissaoRetrieveSerializer(serializers.ModelSerializer):
    from sme_ptrf_apps.core.api.serializers.unidade_serializer import UnidadeLookUpSerializer
    dre = UnidadeLookUpSerializer()
    comissoes = ComissaoSerializer(many=True)

    class Meta:
        model = MembroComissao
        fields = (
            'uuid',
            'rf',
            'nome',
            'email',
            'eh_contador',
            'contador_crc',
            'qtd_comissoes',
            'dre',
            'comissoes'
        )
