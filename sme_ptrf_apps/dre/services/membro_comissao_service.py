from django.db import transaction
from rest_framework import serializers
from sme_ptrf_apps.core.services import TerceirizadasService
from sme_ptrf_apps.dre.models import PresenteAtaDre, MembroComissao, Comissao, AtaParecerTecnico
from sme_ptrf_apps.utils.update_instance_from_dict import update_instance_from_dict


class MembroComissaoService:

    @classmethod
    def validar_duplicidade_rf(cls, rf, dre, instance_rf=None):
        """
        Valida se já existe um membro de comissão com o mesmo RF na DRE.

        Em atualizações, permite manter o mesmo RF da instância atual.
        """
        if not (rf and dre):
            return

        # Se for atualização e o RF não mudou, libera
        if instance_rf and instance_rf == rf:
            return

        if MembroComissao.objects.filter(rf=rf, dre=dre).exists():
            raise serializers.ValidationError(
                {"detail": "Já existe um membro de comissão com esse Registro Funcional."}
            )

    @classmethod
    def validar_e_extrair_comissoes(cls, validated_data):
        """
        Valida e extrai as comissões informadas nos dados validados.

        Remove as comissões de validated_data e garante que pelo menos
        uma comissão tenha sido informada para o membro.
        """
        comissoes = validated_data.pop("comissoes", [])
        if not comissoes:
            raise serializers.ValidationError({
                "detail": "Para salvar um membro de comissão, é necessário informar pelo menos uma comissão"
            })
        return comissoes

    @classmethod
    @transaction.atomic
    def criar_membro(cls, validated_data):
        """
        Cria um membro de comissão e processa suas comissões.

        Valida a duplicidade do RF, verifica as comissões informadas,
        cria o membro e realiza os vínculos necessários com as comissões
        e atas em elaboração.
        """
        rf = validated_data.get("rf")
        dre = validated_data.get("dre")

        cls.validar_duplicidade_rf(rf=rf, dre=dre)
        comissoes = cls.validar_e_extrair_comissoes(validated_data)

        membro = MembroComissao.objects.create(**validated_data)
        cls.processar_comissoes(instance=membro, comissoes=comissoes, dre=dre, rf=rf)

        return membro

    @classmethod
    @transaction.atomic
    def atualizar_membro(cls, instance, validated_data):
        """
        Atualiza um membro de comissão e suas comissões.

        Valida a duplicidade do RF e, caso novas comissões sejam informadas,
        processa os vínculos com as comissões e atas em elaboração antes
        de atualizar os demais dados do membro.
        """
        rf = validated_data.get("rf")
        dre = validated_data.get("dre")

        cls.validar_duplicidade_rf(rf=rf, dre=dre, instance_rf=instance.rf)

        comissoes = validated_data.pop("comissoes", None)
        if comissoes:
            cls.processar_comissoes(instance=instance, comissoes=comissoes, dre=dre, rf=rf)

        update_instance_from_dict(instance, validated_data, save=True)
        return instance

    @classmethod
    def processar_comissoes(cls, instance, comissoes, dre, rf):
        """
        Processa as comissões vinculadas ao membro.

        Adiciona as comissões ao membro e verifica se alguma delas possui
        responsável pela análise da prestação de contas. Quando houver,
        vincula o membro às atas em elaboração; caso contrário, remove
        seus vínculos das atas.
        """
        instance.adiciona_comissoes(comissoes)

        comissao_uuids = [str(c.uuid) for c in comissoes]
        tem_responsavel = Comissao.objects.filter(
            uuid__in=comissao_uuids
        ).exclude(responsavel_analise_pc=False).exists()

        atas = AtaParecerTecnico.objects.filter(
            dre=dre,
            status_geracao_pdf=AtaParecerTecnico.STATUS_NAO_GERADO,
        )

        if tem_responsavel:
            cls._vincular_membro_atas(atas, rf)
        else:
            cls._remover_membro_atas(atas, rf)

    @classmethod
    def _vincular_membro_atas(cls, atas, rf):
        """
        Vincula o membro às atas em elaboração quando ele ainda não está presente.

        Busca os dados do servidor pelo RF e cria o registro de presença
        na ata quando as informações do servidor estiverem disponíveis.
        """
        for ata in atas:
            if ata.presentes_na_ata.filter(rf=rf).exists():
                continue

            servidores = TerceirizadasService.get_informacao_servidor(rf)
            if not servidores:
                continue

            servidor = servidores[0]
            presente_ata = PresenteAtaDre.objects.create(
                ata=ata,
                rf=rf,
                nome=servidor.get("nm_pessoa"),
                cargo=servidor.get("cargo"),
            )
            ata.presentes_na_ata.add(presente_ata)

    @classmethod
    @transaction.atomic
    def deletar_membro(cls, instance):
        """
        Remove um membro de comissão e seus vínculos com atas em elaboração.

        Remove o membro das atas em elaboração da DRE e, em seguida,
        exclui o membro da comissão.
        """
        rf = instance.rf
        dre = instance.dre

        atas = AtaParecerTecnico.objects.filter(
            dre=dre,
            status_geracao_pdf=AtaParecerTecnico.STATUS_NAO_GERADO,
        )

        cls._remover_membro_atas(atas, rf)

        instance.delete()

    @classmethod
    def _remover_membro_atas(cls, atas, rf):
        """
        Remove o membro das atas em elaboração informadas.

        Exclui das atas os registros de presença que correspondem
        ao RF do membro.
        """
        for ata in atas:
            ata.presentes_na_ata.filter(rf=rf).delete()
