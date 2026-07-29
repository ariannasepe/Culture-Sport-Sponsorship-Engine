"""
model/valuation.py

Livello finale: combina i valori base per componente con i moltiplicatori
qualitativi per produrre il valore economico di ciascun componente di output
e il Total Market Value complessivo, con relativa value share.
"""

from dataclasses import dataclass
from .variables import Component
from .scoring import ScoringResult, score_property
from .brand_equity import compute_brand_equity, BrandEquityResult

COMPONENT_LABELS = {
    Component.BRAND_EQUITY: "Brand Equity Value",
    Component.EXPOSURE: "Exposure Value",
    Component.DIGITAL_OWNED_MEDIA: "Digital Owned Media Value",
    Component.RELATIONSHIP: "Relationship Value",
    Component.ACTIVATION: "Activation Value",
}


@dataclass
class ComponentResult:
    key: str
    label: str
    base_value: float
    quality_multiplier: float
    final_value: float
    value_share: float  # % sul totale


@dataclass
class ValuationResult:
    property_name: str
    sector: str
    total_market_value: float
    components: list[ComponentResult]
    scoring: ScoringResult


def evaluate_property(property_name: str, sector: str, raw_data: dict,
                       multiplier_range: tuple[float, float] = (0.6, 1.4)) -> ValuationResult:
    scoring = score_property(raw_data, sector, multiplier_range)

    # Brand Equity Value: calcolato a parte con la logica "a fasce" (vedi model/brand_equity.py),
    # NON con la logica generica quantity x quality_multiplier usata dagli altri componenti,
    # perché Brand Equity non ha variabili di volume/quantity associate.
    brand_equity_result: BrandEquityResult = compute_brand_equity(raw_data, sector)

    component_final_values = {}
    for c in Component:
        if c == Component.BRAND_EQUITY:
            component_final_values[c] = brand_equity_result.final_value
        else:
            base = scoring.component_base_value.get(c, 0.0)
            mult = scoring.component_quality_multiplier.get(c, 1.0)
            component_final_values[c] = base * mult

    total = sum(component_final_values.values())

    components = []
    for c in Component:
        final_value = component_final_values[c]
        share = (final_value / total * 100) if total > 0 else 0.0
        if c == Component.BRAND_EQUITY:
            base_value = brand_equity_result.base_value
            quality_multiplier = brand_equity_result.adjustment_multiplier
        else:
            base_value = scoring.component_base_value.get(c, 0.0)
            quality_multiplier = scoring.component_quality_multiplier.get(c, 1.0)
        components.append(ComponentResult(
            key=c.value,
            label=COMPONENT_LABELS[c],
            base_value=base_value,
            quality_multiplier=quality_multiplier,
            final_value=final_value,
            value_share=share,
        ))

    # ordina per valore decrescente nel breakdown
    components.sort(key=lambda x: x.final_value, reverse=True)

    return ValuationResult(
        property_name=property_name,
        sector=sector,
        total_market_value=total,
        components=components,
        scoring=scoring,
    )
