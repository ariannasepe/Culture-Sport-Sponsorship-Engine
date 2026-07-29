"""
model/scoring.py

Motore di normalizzazione e scoring.

Per le variabili "quality": normalizza il valore grezzo in un punteggio 0-1
rispetto al benchmark_min/max definito in variables.py, poi calcola per
ciascun componente un MOLTIPLICATORE QUALITATIVO come media pesata dei punteggi
delle variabili quality mappate su quel componente.

Il moltiplicatore è ricentrato attorno a 1.0 (range configurabile, default 0.6-1.4)
in modo che una qualità "media" (score 0.5) non annulli il valore base, ma lo
modifichi in modo proporzionato.
"""

from dataclasses import dataclass
from .variables import VariableDef, VarType, Component, get_variable_set


def normalize(raw_value: float, vmin: float, vmax: float) -> float:
    """Normalizza un valore grezzo in un punteggio 0-1, clampato ai bordi."""
    if vmax == vmin:
        return 0.5
    score = (raw_value - vmin) / (vmax - vmin)
    return max(0.0, min(1.0, score))


@dataclass
class ScoringResult:
    variable_scores: dict            # key -> normalized score (solo quality)
    component_quality_multiplier: dict  # Component -> moltiplicatore (0.6 - 1.4 default)
    component_base_value: dict       # Component -> valore base in € (solo da quantity)
    variable_base_values: dict       # key -> valore base € (solo quantity, per breakdown)


def score_property(raw_data: dict, sector: str,
                    multiplier_range: tuple[float, float] = (0.6, 1.4)) -> ScoringResult:
    """
    raw_data: dict {variable_key: valore_grezzo}
        Per variabili quantity: valore_grezzo è espresso nell'unità della variabile
        (es. persone, contatti...). Il unit_rate di default può essere sovrascritto
        passando raw_data[f"{key}__unit_rate"].
    sector: "sport" | "cultura"
    """
    variables = get_variable_set(sector)
    var_by_key = {v.key: v for v in variables}

    variable_scores: dict[str, float] = {}
    variable_base_values: dict[str, float] = {}

    # accumulatori per componente
    quality_weighted_sum = {c: 0.0 for c in Component}
    quality_weight_total = {c: 0.0 for c in Component}
    base_value_sum = {c: 0.0 for c in Component}

    for var in variables:
        if var.component == Component.BRAND_EQUITY:
            continue  # Brand Equity ha una logica dedicata: vedi model/brand_equity.py

        raw = raw_data.get(var.key)
        if raw is None:
            continue  # variabile non fornita: ignorata (modello resta parametrico/incompleto ok)

        if var.var_type == VarType.QUALITY:
            score = normalize(raw, var.benchmark_min, var.benchmark_max)
            variable_scores[var.key] = score
            quality_weighted_sum[var.component] += score * var.weight
            quality_weight_total[var.component] += var.weight

        elif var.var_type == VarType.QUANTITY:
            unit_rate = raw_data.get(f"{var.key}__unit_rate", var.default_unit_rate)
            base_value = raw * unit_rate
            variable_base_values[var.key] = base_value
            base_value_sum[var.component] += base_value

    # calcolo moltiplicatore qualitativo per componente
    lo, hi = multiplier_range
    component_quality_multiplier = {}
    for c in Component:
        if quality_weight_total[c] > 0:
            avg_score = quality_weighted_sum[c] / quality_weight_total[c]
        else:
            avg_score = 0.5  # nessuna variabile quality fornita per questo componente: neutro
        # rimappa 0-1 -> [lo, hi]
        component_quality_multiplier[c] = lo + avg_score * (hi - lo)

    return ScoringResult(
        variable_scores=variable_scores,
        component_quality_multiplier=component_quality_multiplier,
        component_base_value=base_value_sum,
        variable_base_values=variable_base_values,
    )
