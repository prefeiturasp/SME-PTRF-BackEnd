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

        # Cada entrada: (condição, valor_status_andamento, label_debug)
        # Condição pode ser dict (kwargs) ou Q expression
        # Facilitar a identificação das condições que possam ocorrer fora de fluxo
        case_definitions = [
            # Fora do Fluxo - Réplica existente no PAA em Elaboração
            (
                {'status': PaaStatusEnum.EM_ELABORACAO.name, 'replica__isnull': False},
                PaaStatusAndamentoEnum.FORA_FLUXO.name,
                'Em elaboração + com Réplica',
            ),
            # Fora do Fluxo - Em Elaboração com ata gerada
            (
                {'status': PaaStatusEnum.EM_ELABORACAO.name, 'tem_ata_concluida': True},
                PaaStatusAndamentoEnum.FORA_FLUXO.name,
                'Em elaboração + com Ata gerada',
            ),
            # Fora de Fluxo - Réplica existente quando gerado
            (
                {
                    'status': PaaStatusEnum.GERADO.name,
                    'tem_documento_final_concluido': True,
                    'tem_ata_concluida': True,
                    'replica__isnull': False
                },
                PaaStatusAndamentoEnum.FORA_FLUXO.name,
                'Gerado + Doc Final + Ata + Réplica',
            ),
            # Fora de Fluxo: é gerado, não tem ata
            (
                {'status': PaaStatusEnum.GERADO.name, 'tem_ata_concluida': False},
                PaaStatusAndamentoEnum.FORA_FLUXO.name,
                'Gerado + sem Ata',
            ),
            # Fora de Fluxo - Retificação sem Réplica
            (
                {'status': PaaStatusEnum.EM_RETIFICACAO.name, 'replica__isnull': True},
                PaaStatusAndamentoEnum.FORA_FLUXO.name,
                'Em retificação + sem Réplica',
            ),
            # Gerado completo - é gerado, tem documento e tem ata
            (
                {
                    'status': PaaStatusEnum.GERADO.name,
                    'tem_documento_final_concluido': True,
                    'tem_ata_concluida': True
                },
                PaaStatusAndamentoEnum.GERADO.name,
                'Gerado + Doc Final + Ata',
            ),
            # Retificação correta quando há uma Réplica
            (
                {'status': PaaStatusEnum.EM_RETIFICACAO.name, 'replica__isnull': False},
                PaaStatusAndamentoEnum.GERADO_PARCIALMENTE.name,
                'Em retificação + com Réplica',
            ),
            # Em Elaboração quando tem apenas documento final concluído
            (
                Q(status=PaaStatusEnum.EM_ELABORACAO.name) & tem_documento_final_concluido,
                PaaStatusAndamentoEnum.GERADO_PARCIALMENTE.name,
                'Em elaboração + Doc Final',
            ),
            # Em elaboração
            (
                {
                    'status': PaaStatusEnum.EM_ELABORACAO.name,
                    'tem_documento_final_concluido': False,
                    'tem_ata_concluida': False
                },
                PaaStatusAndamentoEnum.EM_ELABORACAO.name,
                'Em elaboração',
            ),
            # Fluxo não iniciado
            (
                {'status': PaaStatusEnum.NAO_INICIADO.name},
                PaaStatusAndamentoEnum.FORA_FLUXO.name,
                'PAA existente não pode ser \"Não iniciado\"',
            ),
        ]

        def make_when(condition, value):
            """
                Método utilizado para reaproveitar os Cases de status_andamento para _debug_case
            """
            if isinstance(condition, dict):
                return When(**condition, then=Value(value))
            return When(condition, then=Value(value))

        return self.annotate(
            tem_documento_final_concluido=tem_documento_final_concluido,
            tem_ata_concluida=tem_ata_concluida,
            status_andamento=Case(
                *[make_when(cond, status) for cond, status, _ in case_definitions],
                default=Value(PaaStatusAndamentoEnum.EM_ELABORACAO.name),
                output_field=CharField(),
            ),
            _debug_case=Case(
                *[make_when(
                    cond,
                    f'Condição {index + 1} - {label}'
                ) for index, (cond, _, label) in enumerate(case_definitions)],
                default=Value('Condição padrão: Não mapeada'),
                output_field=CharField(),
            ),
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

    def paas_em_retificacao(self):
        return self.annotate_status_geracao().filter(
            status=PaaStatusEnum.EM_RETIFICACAO.name
        )


class PaaManager(models.Manager):
    def get_queryset(self):
        """
        Sobrescreve o queryset padrão para sempre incluir os campos anotados
        """
        return PaaQuerySet(self.model, using=self._db).annotate_status_geracao()
