from __future__ import annotations

from django.db.models import Case, When, Value, CharField, Exists, OuterRef, Q
from django.db import models
from sme_ptrf_apps.paa.enums import PaaStatusEnum, PaaStatusAndamentoEnum


class PaaQuerySet(models.QuerySet):

    @staticmethod
    def _make_when(condition: dict | Q, value: str) -> When:
        """
            Método utilizado para reaproveitar os Cases de status_andamento para _debug_case
            Cria um When para uso em expressões Case a partir de dict de kwargs ou expressão Q.
        """
        if isinstance(condition, dict):
            return When(**condition, then=Value(value))
        return When(condition, then=Value(value))

    def annotate_status_geracao(self) -> PaaQuerySet:
        """
        Anota o queryset com campos calculados que representam o estado de geração do PAA.

        Anotações adicionadas:
            tem_documento_final_concluido (bool): True se há documento final concluído
                para a versão adequada ao status do PAA (original ou retificação).
            tem_ata_iniciada (bool): True se há ata com status NAO_GERADO para o
                tipo adequado ao status do PAA (apresentação ou retificação).
            tem_ata_concluida (bool): True se há ata com PDF concluído para o
                tipo adequado ao status do PAA.
            status_andamento (str): Status de andamento calculado (valor de PaaStatusAndamentoEnum).
            _debug_case (str): Descrição da condição satisfeita, útil para depuração.

        Returns:
            PaaQuerySet com os campos de status de geração anotados.
        """
        if 'status_andamento' in self.query.annotations:
            # Queryset já anotado evita reanotação desnecessária
            return self

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

        # Ata de Retificacao iniciada (considera fora de fluxo quando há Retificação sem uma ata iniciada)
        # Inclui EM_PROCESSAMENTO para não ignorar o PAA enquanto a ata estiver sendo gerada.
        ata_retificacao_iniciada = Exists(
            AtaPaa.objects.filter(
                paa=OuterRef('pk'),
                status_geracao_pdf__in=[AtaPaa.STATUS_NAO_GERADO, AtaPaa.STATUS_EM_PROCESSAMENTO],
                tipo_ata=AtaPaa.ATA_RETIFICACAO,
            )
        )

        # Ata de Apresentacao iniciada
        ata_apresentacao_iniciada = Exists(
            AtaPaa.objects.filter(
                paa=OuterRef('pk'),
                status_geracao_pdf=AtaPaa.STATUS_NAO_GERADO,
                tipo_ata=AtaPaa.ATA_APRESENTACAO,
            )
        )

        # Ata concluída PAA Retificacao
        ata_retificacao = Exists(
            AtaPaa.objects.filter(
                paa=OuterRef('pk'),
                status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
                tipo_ata=AtaPaa.ATA_RETIFICACAO,
                pdf_gerado_previamente=True  # Arquivo gerado
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

        # Anota a ata iniciada correta conforme o status do PAA
        tem_ata_iniciada = Case(
            When(status=PaaStatusEnum.EM_RETIFICACAO.name, then=ata_retificacao_iniciada),
            default=ata_apresentacao_iniciada,
            output_field=models.BooleanField(),
        )

        # Cada entrada: (condição, valor_status_andamento, label_debug)
        # Condição pode ser dict (kwargs) ou Q expression
        # Facilitar a identificação das condições que possam ocorrer fora de fluxo
        case_definitions: list[tuple[dict | Q, str, str]] = [
            # Fora do Fluxo - Réplica existente no PAA em Elaboração
            (
                {'status': PaaStatusEnum.EM_ELABORACAO.name, 'replica__isnull': False},
                PaaStatusAndamentoEnum.FORA_FLUXO.name,
                """
                    Em elaboração + com Réplica
                    - Necessário remover a réplica
                """,
            ),
            # Fora do Fluxo - Em Elaboração com ata gerada
            (
                {'status': PaaStatusEnum.EM_ELABORACAO.name, 'tem_ata_concluida': True},
                PaaStatusAndamentoEnum.FORA_FLUXO.name,
                """
                    Em elaboração + com Ata gerada
                    Necessário alterar os campos da ata:
                    - Status Pdf: [Não gerado]
                    - Documento gerado: [desmarcar]
                """,
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
                """
                    Gerado + Doc Final + Ata + Réplica
                    - Necessário remover a réplica
                    Obs: Verificar se a réplica foi registrada no log de réplicas
                """,
            ),
            # Fora de Fluxo: é gerado, não tem documento
            (
                {
                    'status': PaaStatusEnum.GERADO.name,
                    'tem_documento_final_concluido': False
                },
                PaaStatusAndamentoEnum.FORA_FLUXO.name,
                """
                    Gerado + sem Documento final
                    Necessário alterar o seguinte campo no PAA e gerar o documento final:
                    - status: [Em elaboração]
                """,
            ),
            # Fora de Fluxo: é gerado, não tem ata
            (
                {
                    'status': PaaStatusEnum.GERADO.name,
                    'tem_ata_concluida': False
                },
                PaaStatusAndamentoEnum.FORA_FLUXO.name,
                """
                    Gerado + sem Ata
                    Necessário regerar a ata, após alterar os seguinte campo no PAA:
                    - status: [Em elaboração]
                """,
            ),
            # Fora de Fluxo - Retificação sem Ata iniciada
            (
                {
                    'status': PaaStatusEnum.EM_RETIFICACAO.name,
                    'tem_ata_iniciada': False
                },
                PaaStatusAndamentoEnum.FORA_FLUXO.name,
                """
                    Em retificação + sem Ata iniciada
                    Recomendado cancelar a retificação e iniciá-la novamente
                    Ou, criar uma nova ata de retificação via admin, com os seguintes campos:
                    - Paa: [ referencia do PAA]
                    - Tipo Ata: [Ata de Retificação]
                    - justificativa da retificação: [informar a justificativa da retificação]
                """,
            ),
            # Fora de Fluxo - Retificação sem Réplica
            (
                {
                    'status': PaaStatusEnum.EM_RETIFICACAO.name,
                    'tem_ata_iniciada': True,
                    'replica__isnull': True
                },
                PaaStatusAndamentoEnum.FORA_FLUXO.name,
                """
                    Em retificação + sem Réplica
                    Recomendado cancelar a retificação e iniciá-la novamente
                    Obs: Sem réplica registrada não é possível registrar log ou realizar cancelamento seguro do
                    que foi alterado no PAA
                """,
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
                {
                    'status': PaaStatusEnum.EM_RETIFICACAO.name,
                    'replica__isnull': False,
                    'tem_documento_final_concluido': True,
                    'tem_ata_iniciada': True
                },
                PaaStatusAndamentoEnum.GERADO_PARCIALMENTE.name,
                'Em retificação + com Réplica + Doc Retificação gerado + Ata iniciada',
            ),
            # Retificação correta quando há uma Réplica
            (
                {
                    'status': PaaStatusEnum.EM_RETIFICACAO.name,
                    'replica__isnull': False,
                    'tem_ata_iniciada': True
                },
                PaaStatusAndamentoEnum.EM_RETIFICACAO.name,
                'Em retificação + com Réplica + Ata iniciada',
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

        return self.annotate(
            tem_documento_final_concluido=tem_documento_final_concluido,
            tem_ata_iniciada=tem_ata_iniciada,
            tem_ata_concluida=tem_ata_concluida,
            status_andamento=Case(
                *[self._make_when(cond, status) for cond, status, _ in case_definitions],
                default=Value(PaaStatusAndamentoEnum.EM_ELABORACAO.name),
                output_field=CharField(),
            ),
            _debug_case=Case(
                *[self._make_when(
                    cond,
                    f'Condição {index + 1}: {label}'
                ) for index, (cond, _, label) in enumerate(case_definitions)],
                default=Value('Condição padrão: Não mapeada'),
                output_field=CharField(),
            ),
        )

    def get_queryset(self) -> PaaQuerySet:
        """
        Retorna o queryset com as anotações de status de geração aplicadas.

        Returns:
            PaaQuerySet anotado via ``annotate_status_geracao``.
        """
        queryset = self.annotate_status_geracao()
        return queryset

    def filter_por_status_geracao(self, status_geracao: str) -> PaaQuerySet:
        """
        Filtra os PAAs pelo status de andamento calculado.

        Args:
            status_geracao: Nome do status a filtrar (valor de PaaStatusAndamentoEnum).

        Returns:
            PaaQuerySet filtrado pelo ``status_andamento`` informado.
        """
        return self.annotate_status_geracao().filter(
            status_andamento=status_geracao
        )

    def paas_gerados(self) -> PaaQuerySet:
        """
        Retorna apenas os PAAs com status de andamento GERADO.

        Returns:
            PaaQuerySet filtrado por ``status_andamento=GERADO``.
        """
        return self.annotate_status_geracao().filter(
            status_andamento=PaaStatusAndamentoEnum.GERADO.name
        )

    def paas_gerados_parcialmente(self) -> PaaQuerySet:
        """
        Retorna apenas os PAAs com status de andamento GERADO_PARCIALMENTE.

        Returns:
            PaaQuerySet filtrado por ``status_andamento=GERADO_PARCIALMENTE``.
        """
        return self.annotate_status_geracao().filter(
            status_andamento=PaaStatusAndamentoEnum.GERADO_PARCIALMENTE.name
        )

    def paas_gerados_e_parciais(self) -> PaaQuerySet:
        """
        Retorna apenas os PAAs com status de andamento GERADO ou GERADO_PARCIALMENTE.

        Returns:
            PaaQuerySet filtrado por ``status_andamento in [GERADO, GERADO_PARCIALMENTE]``.
        """
        return self.annotate_status_geracao().filter(
            status_andamento__in=[
                PaaStatusAndamentoEnum.GERADO.name,
                PaaStatusAndamentoEnum.GERADO_PARCIALMENTE.name,
            ]
        )

    def paas_em_elaboracao(self) -> PaaQuerySet:
        """
        Retorna apenas os PAAs com status de andamento EM_ELABORACAO.

        Returns:
            PaaQuerySet filtrado por ``status_andamento=EM_ELABORACAO``.
        """
        return self.annotate_status_geracao().filter(
            status_andamento=PaaStatusAndamentoEnum.EM_ELABORACAO.name
        )

    def paas_em_retificacao(self) -> PaaQuerySet:
        """
        Retorna apenas os PAAs com status do PAA EM_RETIFICACAO.
        Filtra pelo campo ``status`` do modelo diretamente

        Returns:
            PaaQuerySet filtrado por ``status=EM_RETIFICACAO``.
        """
        return self.annotate_status_geracao().filter(
            status=PaaStatusEnum.EM_RETIFICACAO.name
        )


class PaaManager(models.Manager):
    def get_queryset(self) -> PaaQuerySet:
        """
        Sobrescreve o queryset padrão para sempre incluir os campos anotados

        Returns:
            PaaQuerySet com anotações de status de geração aplicadas
        """
        return PaaQuerySet(self.model, using=self._db).annotate_status_geracao()
