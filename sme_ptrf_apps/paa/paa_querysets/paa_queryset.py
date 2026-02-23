from django.db.models import Case, When, Value, CharField, Exists, OuterRef, Q
from django.db import models
from sme_ptrf_apps.paa.enums import PaaStatusEnum, PaaStatusAndamentoEnum


class PaaQuerySet(models.QuerySet):
    def annotate_status_geracao(self):
        from sme_ptrf_apps.paa.models.documento_paa import DocumentoPaa
        from sme_ptrf_apps.paa.models.ata_paa import AtaPaa

        tem_documento_final_concluido = Exists(
            DocumentoPaa.objects.filter(
                paa=OuterRef('pk'),
                versao=DocumentoPaa.VersaoChoices.FINAL,
                status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
            )
        )

        tem_ata_concluida = Exists(
            AtaPaa.objects.filter(
                paa=OuterRef('pk'),
                status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
            )
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

                # GERADO: status GERADO e ata gerado
                # Cenário fora de fluxo, mas possível(em manipulação admin)
                When(
                    status=PaaStatusEnum.GERADO.name,
                    tem_ata_concluida=False,
                    then=Value(PaaStatusAndamentoEnum.FORA_FLUXO.name),
                ),
                # RETIFICADO: status RETIFICACAO e sem documento ou ata gerado
                # Cenário fora de fluxo, mas possível(em manipulação admin)
                When(
                    Q(status=PaaStatusEnum.EM_RETIFICACAO.name) &
                    ~Q(tem_ata_concluida=True, tem_documento_final_concluido=True),
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

    # # Opcional: métodos de conveniência que delegam para o QuerySet
    # def paas_gerados(self):
    #     return self.get_queryset().paas_gerados()

    # def paas_gerados_parcialmente(self):
    #     return self.get_queryset().paas_gerados_parcialmente()

    # def paas_em_elaboracao(self):
    #     return self.get_queryset().paas_em_elaboracao()

    # def filter_por_status_geracao(self, status_geracao):
    #     return self.get_queryset().filter_por_status_geracao(status_geracao)
