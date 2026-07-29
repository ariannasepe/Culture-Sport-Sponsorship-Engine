"""
model/brand_equity.py

Calcolo dedicato del Brand Equity Value, con la logica "a fasce" concordata:

  Brand Equity Value = base_value_della_fascia  x  moltiplicatore_di_aggiustamento

- La fascia (tier) si determina mediando (0-1) le variabili di "blasone/prestigio"
  per il settore in questione.
- Il moltiplicatore di aggiustamento deriva da brand_fit ed exclusivity, ricentrato
  nel range configurato (default 0.8 - 1.2).

Tutti i numeri (soglie, valori-base, range di aggiustamento) sono in
config/brand_equity_tiers.yaml e possono essere modificati senza toccare questo file.
"""

from dataclasses import dataclass
from .variables import get_variable_set
from .scoring import normalize
from config.brand_equity_tiers import SECTORS, ADJUSTMENT_VARIABLES, ADJUSTMENT_RANGE


@dataclass
class BrandEquityResult:
    tier_name: str
    tier_score: float          # 0-1, media delle tier_driver_variables
    base_value: float          # euro, valore della fascia
    adjustment_multiplier: float
    final_value: float


def compute_brand_equity(raw_data: dict, sector: str) -> BrandEquityResult:
    sector = sector.lower().strip()
    sector_config = SECTORS[sector]

    var_defs = {v.key: v for v in get_variable_set(sector)}

    # --- 1. calcolo tier_score: media (semplice) delle tier_driver_variables normalizzate
    driver_scores = []
    for key in sector_config["tier_driver_variables"]:
        raw = raw_data.get(key)
        if raw is None:
            continue
        vdef = var_defs.get(key)
        if vdef is None:
            continue
        score = normalize(raw, vdef.benchmark_min, vdef.benchmark_max)
        driver_scores.append(score)

    tier_score = sum(driver_scores) / len(driver_scores) if driver_scores else 0.5

    # --- 2. selezione della fascia (la prima il cui min_score è <= tier_score, tiers ordinati desc)
    tiers = sorted(sector_config["tiers"], key=lambda t: t.min_score, reverse=True)
    selected_tier = tiers[-1]  # fallback: fascia più bassa
    for tier in tiers:
        if tier_score >= tier.min_score:
            selected_tier = tier
            break

    base_value = float(selected_tier.base_value)

    # --- 3. moltiplicatore di aggiustamento da brand_fit / exclusivity
    lo, hi = ADJUSTMENT_RANGE
    adj_scores = []
    for key in ADJUSTMENT_VARIABLES:
        raw = raw_data.get(key)
        if raw is None:
            continue
        vdef = var_defs.get(key)
        if vdef is None:
            continue
        score = normalize(raw, vdef.benchmark_min, vdef.benchmark_max)
        adj_scores.append(score)

    adj_avg = sum(adj_scores) / len(adj_scores) if adj_scores else 0.5
    adjustment_multiplier = lo + adj_avg * (hi - lo)

    final_value = base_value * adjustment_multiplier

    return BrandEquityResult(
        tier_name=selected_tier.name,
        tier_score=tier_score,
        base_value=base_value,
        adjustment_multiplier=adjustment_multiplier,
        final_value=final_value,
    )
