from decimal import Decimal
from typing import Optional

from .context import DespesaDtoContext


class DespesaContextBuilder:
    """Constrói o DespesaDtoContext a partir dos dados validados pelo serializer.

    Para update, preenche automaticamente os campos ausentes a partir da instância
    existente (comportamento equivalente ao antigo `_validar_datas_update`).

    Parâmetros externos ao validated_data/instância:
    - recurso: vem de self.context.get("recurso") no serializer (apenas create)
    - initial_data: dados brutos do request, usado para rateios_raw (UUIDs como string)
    - uuid_solicitacao_acerto: presente nos fluxos 3 e 4 (criação/edição via acerto DRE);
      vem de self.context.get("uuid_solicitacao_acerto") no serializer
    """

    @staticmethod
    def build(
        validated_data: dict,
        instance=None,
        recurso=None,
        initial_data: dict = None,
        uuid_solicitacao_acerto: Optional[str] = None,
    ) -> DespesaDtoContext:

        def get(field):
            if field in validated_data:
                return validated_data[field]
            if instance:
                return getattr(instance, field, None)
            return None

        valor_original_raw = get("valor_original")
        valor_original = Decimal(str(valor_original_raw)) if valor_original_raw is not None else None

        reconhecida = get("eh_despesa_reconhecida_pela_associacao")
        if reconhecida is None:
            reconhecida = True

        return DespesaDtoContext(
            is_create=instance is None,
            valor_total=Decimal(str(get("valor_total") or 0)),
            valor_recursos_proprios=Decimal(str(get("valor_recursos_proprios") or 0)),
            data_transacao=get("data_transacao"),
            data_documento=get("data_documento"),
            retem_imposto=bool(get("retem_imposto") or False),
            eh_despesa_reconhecida_pela_associacao=bool(reconhecida),
            numero_boletim_de_ocorrencia=get("numero_boletim_de_ocorrencia") or "",
            rateios=get("rateios") or [],
            rateios_raw=(initial_data or {}).get("rateios", []),
            despesas_impostos=get("despesas_impostos") or [],
            motivos_pagamento_antecipado=get("motivos_pagamento_antecipado") or [],
            outros_motivos=get("outros_motivos_pagamento_antecipado"),
            associacao=get("associacao"),
            recurso=recurso,
            despesa_instance=instance,
            valor_original=valor_original,
            uuid_solicitacao_acerto=uuid_solicitacao_acerto,
        )
