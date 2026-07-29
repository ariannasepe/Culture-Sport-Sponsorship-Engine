# config/brand_equity_tiers.py
"""
Configurazione delle fasce (tier) usate per calcolare il Brand Equity Value.

QUESTO FILE E' PENSATO PER ESSERE MODIFICATO ANCHE DA CHI NON PROGRAMMA.
Non serve toccare la logica di calcolo per cambiare soglie, valori o pesi qui sotto:
basta modificare i numeri e le liste in questo file.

LOGICA:
1. Le "tier_driver_variables" di un settore vengono mediate (score 0-1) per
   determinare in quale fascia (tier) rientra la property (Elite/Alta/Media/Bassa).
2. Ogni fascia ha un "base_value" in euro: il valore di riferimento di mercato
   per il diritto di brand association in quella fascia.
3. Le "adjustment_variables" (brand_fit, exclusivity) applicano un piccolo
   correttivo (+/- rispetto a ADJUSTMENT_RANGE) sopra il base_value.

Brand Equity Value = base_value_fascia * moltiplicatore_aggiustamento

NOTA: i "base_value" qui sotto sono SEGNAPOSTO PLAUSIBILI, non benchmark
di mercato reali. Vanno sostituiti con dati reali quando disponibili.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Tier:
    name: str
    min_score: float
    base_value: float


ADJUSTMENT_VARIABLES: list[str] = ["brand_fit", "exclusivity"]
ADJUSTMENT_RANGE: tuple[float, float] = (0.8, 1.2)  # moltiplicatore min/max

SECTORS: dict[str, dict] = {
    "sport": {
        "tier_driver_variables": [
            "prestige",
            "sporting_competitiveness",
            "performance_continuity",
        ],
        "tiers": [
            Tier(name="Elite", min_score=0.85, base_value=400_000),
            Tier(name="Alta", min_score=0.65, base_value=150_000),
            Tier(name="Media", min_score=0.40, base_value=60_000),
            Tier(name="Bassa", min_score=0.00, base_value=20_000),
        ],
    },
    "cultura": {
        "tier_driver_variables": [
            "prestige",
            "audience_profile_score",
            "international_reach",
            "avg_dwell_time",
        ],
        "tiers": [
            Tier(name="Elite", min_score=0.85, base_value=200_000),
            Tier(name="Alta", min_score=0.65, base_value=80_000),
            Tier(name="Media", min_score=0.40, base_value=30_000),
            Tier(name="Bassa", min_score=0.00, base_value=10_000),
        ],
    },
}