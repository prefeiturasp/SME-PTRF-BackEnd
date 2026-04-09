from django.db.models import Case, When, Value, CharField, Exists, OuterRef, Q
from django.db import models
from sme_ptrf_apps.paa.enums import PaaStatusEnum, PaaStatusAndamentoEnum


class PaaQuerySet(models.QuerySet):
    def annotate_status_geracao(self):
        from sme_ptrf_apps.paa.models.documento_paa import DocumentoPaa
        from sme_ptrf_apps.paa.models.ata_paa import AtaPaa

        # Documento final concluído PAA Original
        doc_final_original = Exists(
            DocumentoPaa.objects.filter(
                paa=OuterRef('pk'),
                versao=DocumentoPaa.VersaoChoices.FINAL,
                retificacao=False,
                status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
            )
        )
        # Documento final concluído PAA Retificação
        doc_final_retificacao = Exists(
            DocumentoPaa.objects.filter(
                paa=OuterRef('pk'),
                versao=DocumentoPaa.VersaoChoices.FINAL,
                retificacao=True,
                status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
            )
        )

        # Ata concluída PAA Original
        ata_apresentacao = Exists(
            AtaPaa.objects.filter(
                paa=OuterRef('pk'),
                status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
                tipo_ata=AtaPaa.ATA_APRESENTACAO,
            )
        )

        # Ata concluída PAA Retificacao
        ata_retificacao = Exists(
            AtaPaa.objects.filter(
                paa=OuterRef('pk'),
                status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
                tipo_ata=AtaPaa.ATA_RETIFICACAO,
            )
        )

        # Anota o documento correto conforme o status do PAA
        tem_documento_final_concluido = Case(
            When(status=PaaStatusEnum.EM_RETIFICACAO.name, then=doc_final_retificacao),
            default=doc_final_original,
            output_field=models.BooleanField(),
        )

        # Anota a ata correta conforme o status do PAA
        tem_ata_concluida = Case(
            When(status=PaaStatusEnum.EM_RETIFICACAO.name, then=ata_retificacao),
            default=ata_apresentacao,
            output_field=models.BooleanField(),
        )

        return self.annotate(
            tem_documento_final_concluido=tem_documento_final_concluido,
            tem_ata_concluida=tem_ata_concluida,
            status_andamento=Case(

                # GERADO: status GERADO + documento final concluído + ata concluída
                When(
                    status=PaaStatusEnum.GERADO.name,
                    tem_documento_final_concluido=True,
                    tem_ata_concluida=True,
                    then=Value(PaaStatusAndamentoEnum.GERADO.name),
                ),

                # RETIFICACAO: status EM_RETIFICACAO + com replica
                # Enquanto Status está em retificação, deve haver uma réplica
                When(
                    status=PaaStatusEnum.EM_RETIFICACAO.name,
                    replica__isnull=False,
                    then=Value(PaaStatusAndamentoEnum.GERADO_PARCIALMENTE.name),
                ),

                # GERADO: status GERADO e sem ata gerada
                # Cenário fora de fluxo, mas possível(em manipulação admin)
                When(
                    status=PaaStatusEnum.GERADO.name,
                    tem_ata_concluida=False,
                    then=Value(PaaStatusAndamentoEnum.FORA_FLUXO.name),
                ),

                # GERADO_PARCIALMENTE: status EM_RETIFICACAO
                When(
                    status=PaaStatusEnum.EM_RETIFICACAO.name,
                    then=Value(PaaStatusAndamentoEnum.GERADO_PARCIALMENTE.name),
                ),

                # GERADO_PARCIALMENTE: status EM_ELABORACAO + documento final concluído
                When(
                    Q(status=PaaStatusEnum.EM_ELABORACAO.name) & tem_documento_final_concluido,
                    then=Value(PaaStatusAndamentoEnum.GERADO_PARCIALMENTE.name),
                ),

                # NAO_INICIADO: status padrão NAO_INICIADO
                When(
                    status=PaaStatusEnum.NAO_INICIADO.name,
                    then=Value(PaaStatusAndamentoEnum.NAO_INICIADO.name)
                ),
                default=Value(PaaStatusAndamentoEnum.EM_ELABORACAO.name),
                output_field=CharField(),
            )
        )

    def get_queryset(self):
        queryset = self.annotate_status_geracao()
        return queryset

    def filter_por_status_geracao(self, status_geracao):
        return self.annotate_status_geracao().filter(
            status_andamento=status_geracao
        )

    def paas_gerados(self):
        return self.annotate_status_geracao().filter(
            status_andamento=PaaStatusAndamentoEnum.GERADO.name
        )

    def paas_gerados_parcialmente(self):
        return self.annotate_status_geracao().filter(
            status_andamento=PaaStatusAndamentoEnum.GERADO_PARCIALMENTE.name
        )

    def paas_gerados_e_parciais(self):
        return self.annotate_status_geracao().filter(
            status_andamento__in=[
                PaaStatusAndamentoEnum.GERADO.name,
                PaaStatusAndamentoEnum.GERADO_PARCIALMENTE.name,
            ]
        )

    def paas_em_elaboracao(self):
        return self.annotate_status_geracao().filter(
            status_andamento=PaaStatusAndamentoEnum.EM_ELABORACAO.name
        )


class PaaManager(models.Manager):
    def get_queryset(self):
        """
        Sobrescreve o queryset padrão para sempre incluir os campos anotados
        """
        return PaaQuerySet(self.model, using=self._db).annotate_status_geracao()
