"""
model/variables.py

Definisce lo schema delle variabili del modello di valutazione asset-based.

Ogni variabile è classificata in due tipi:

- "quantity": variabili di volume/quantità (reach, attendance, visitatori...).
  Vengono monetizzate direttamente tramite un benchmark economico unitario
  (unit_rate, espresso in €/unità) per generare un VALORE BASE.

- "quality": variabili qualitative normalizzate 0-1 (brand fit, prestige,
  exclusivity, engagement...). NON generano valore da sole, ma agiscono come
  MOLTIPLICATORI sul valore base del componente a cui sono associate.

Ogni variabile è inoltre mappata a UNO dei 5 componenti di output:
  brand_equity | exposure | digital_owned_media | relationship | activation

Questo schema è condiviso tra settore Sport e settore Cultura: cambiano le
variabili concrete, non la logica.
"""

from dataclasses import dataclass, field
from enum import Enum


class VarType(str, Enum):
    QUANTITY = "quantity"
    QUALITY = "quality"


class Component(str, Enum):
    BRAND_EQUITY = "brand_equity"
    EXPOSURE = "exposure"
    DIGITAL_OWNED_MEDIA = "digital_owned_media"
    RELATIONSHIP = "relationship"
    ACTIVATION = "activation"


@dataclass
class VariableDef:
    key: str                 
    label: str               
    var_type: VarType
    component: Component
    unit: str = ""             
    benchmark_min: float = 0.0   # usato per normalizzare le variabili "quality"
    benchmark_max: float = 1.0
    default_unit_rate: float = 0.0  # €/unità, solo per variabili "quantity"
    weight: float = 1.0          # peso relativo all'interno del proprio componente
    description: str = ""


# ---------------------------------------------------------------------------
# VARIABILI BASE COMUNI (sport + cultura)
# ---------------------------------------------------------------------------
COMMON_VARIABLES: list[VariableDef] = [
    VariableDef(
        key="audience_reach", label="Audience Reach", var_type=VarType.QUANTITY,
        component=Component.EXPOSURE, unit="contatti/anno",
        default_unit_rate=0.004, weight=0.35,
        description="Numero complessivo di persone raggiunte dalla property (somma canali).",
    ),
    VariableDef(
        key="audience_quality", label="Audience Quality", var_type=VarType.QUALITY,
        component=Component.EXPOSURE, unit="score 0-1",
        benchmark_min=0, benchmark_max=1, weight=0.25,
        description="Profilazione socio-demografica e affinità del pubblico raggiunto.",
    ),
    VariableDef(
        key="engagement", label="Engagement", var_type=VarType.QUALITY,
        component=Component.DIGITAL_OWNED_MEDIA, unit="score 0-1",
        benchmark_min=0, benchmark_max=0.15, weight=0.3,
        description="Tasso di interazione medio su contenuti/canali digitali (engagement rate).",
    ),
    VariableDef(
        key="visibility_exposure", label="Visibility / Exposure", var_type=VarType.QUANTITY,
        component=Component.EXPOSURE, unit="impression equiv./anno",
        default_unit_rate=0.0025, weight=0.4,
        description="Esposizione media stimata degli asset di visibilità (LED, naming, ecc.).",
    ),
    VariableDef(
        key="brand_fit", label="Brand Fit", var_type=VarType.QUALITY,
        component=Component.BRAND_EQUITY, unit="score 0-1",
        benchmark_min=0, benchmark_max=1, weight=0.3,
        description="Coerenza percepita tra i valori della property e dei possibili brand partner.",
    ),
    VariableDef(
        key="exclusivity", label="Exclusivity dell'asset", var_type=VarType.QUALITY,
        component=Component.BRAND_EQUITY, unit="score 0-1",
        benchmark_min=0, benchmark_max=1, weight=0.35,
        description="Grado di esclusività di categoria offerto agli sponsor/partner.",
    ),
    VariableDef(
        key="prestige", label="Prestige della property", var_type=VarType.QUALITY,
        component=Component.BRAND_EQUITY, unit="score 0-1",
        benchmark_min=0, benchmark_max=1, weight=0.35,
        description="Notorietà, storia e posizionamento percepito della property.",
    ),
    VariableDef(
        key="activation_potential", label="Activation Potential", var_type=VarType.QUALITY,
        component=Component.ACTIVATION, unit="score 0-1",
        benchmark_min=0, benchmark_max=1, weight=0.5,
        description="Capacità della property di ospitare attivazioni esperienziali per i partner.",
    ),
    VariableDef(
        key="relationship_hospitality", label="Relationship / Hospitality Value",
        var_type=VarType.QUANTITY, component=Component.RELATIONSHIP,
        unit="posti hospitality/anno", default_unit_rate=180.0, weight=0.5,
        description="Valore degli spazi/occasioni di relazione B2B offerti (hospitality, box, eventi VIP).",
    ),
    VariableDef(
        key="economic_benchmark_unitario", label="Benchmark economico unitario",
        var_type=VarType.QUANTITY, component=Component.EXPOSURE,
        unit="€/unità (riferimento)", default_unit_rate=1.0, weight=0.0,
        description="Parametro di calibrazione: valore di mercato unitario di riferimento del settore.",
    ),
]

# ---------------------------------------------------------------------------
# VARIABILI SETTORE SPORT
# ---------------------------------------------------------------------------
SPORT_VARIABLES: list[VariableDef] = [
    VariableDef("total_fanbase", "Fanbase totale", VarType.QUANTITY, Component.EXPOSURE,
                "tifosi", default_unit_rate=0.002, weight=0.2,
                description="Fanbase complessiva stimata (Italia + estero)."),
    VariableDef("tv_audience", "Audience TV", VarType.QUANTITY, Component.EXPOSURE,
                "spettatori/anno", default_unit_rate=0.003, weight=0.25,
                description="Audience televisiva cumulata annua."),
    VariableDef("stadium_attendance", "Audience stadio / attendance", VarType.QUANTITY,
                Component.EXPOSURE, "spettatori/anno", default_unit_rate=0.01, weight=0.15,
                description="Spettatori paganti cumulati su base stagionale."),
    VariableDef("digital_reach", "Digital reach", VarType.QUANTITY,
                Component.DIGITAL_OWNED_MEDIA, "follower/utenti", default_unit_rate=0.006, weight=0.4,
                description="Reach complessiva su canali digital owned (social + sito + app)."),
    VariableDef("social_engagement", "Social engagement", VarType.QUALITY,
                Component.DIGITAL_OWNED_MEDIA, "score 0-1", benchmark_min=0, benchmark_max=0.12, weight=0.3,
                description="Engagement rate medio sui canali social ufficiali."),
    VariableDef("sporting_competitiveness", "Competitività sportiva", VarType.QUALITY,
                Component.BRAND_EQUITY, "score 0-1", benchmark_min=0, benchmark_max=1, weight=0.15,
                description="Posizionamento competitivo (ranking, risultati recenti)."),
    VariableDef("performance_continuity", "Continuità di performance", VarType.QUALITY,
                Component.BRAND_EQUITY, "score 0-1", benchmark_min=0, benchmark_max=1, weight=0.15,
                description="Stabilità dei risultati nel tempo (riduce rischio percepito dallo sponsor)."),
    VariableDef("venue_utilization_rate", "Tasso di occupazione impianto", VarType.QUALITY,
                Component.RELATIONSHIP, "score 0-1", benchmark_min=0, benchmark_max=1, weight=0.2,
                description="Percentuale media di riempimento dell'impianto sulla capienza totale."),
    VariableDef("hospitality_capacity", "Hospitality disponibile", VarType.QUANTITY,
                Component.RELATIONSHIP, "posti/anno", default_unit_rate=180.0, weight=0.3,
                description="Numero di posti hospitality/premium disponibili su base annua."),
    VariableDef("sponsorable_assets_count", "Numero asset sponsorizzabili", VarType.QUANTITY,
                Component.ACTIVATION, "asset", default_unit_rate=25000.0, weight=0.5,
                description="Numero di asset di sponsorizzazione attivabili (naming, jersey, LED, ecc.)."),
]

# ---------------------------------------------------------------------------
# VARIABILI SETTORE CULTURA
# ---------------------------------------------------------------------------
CULTURE_VARIABLES: list[VariableDef] = [
    VariableDef("total_visitors", "Visitatori totali", VarType.QUANTITY, Component.EXPOSURE,
                "visitatori/anno", default_unit_rate=0.02, weight=0.3,
                description="Visitatori complessivi annui (fisici, tutte le sedi/eventi)."),
    VariableDef("unique_visitors", "Visitatori unici", VarType.QUANTITY, Component.EXPOSURE,
                "visitatori unici/anno", default_unit_rate=0.03, weight=0.2,
                description="Visitatori unici stimati al netto delle visite ripetute."),
    VariableDef("avg_dwell_time", "Tempo medio di permanenza", VarType.QUALITY,
                Component.BRAND_EQUITY, "minuti", benchmark_min=15, benchmark_max=180, weight=0.15,
                description="Tempo medio di permanenza on-site: proxy di qualità dell'esperienza."),
    VariableDef("num_events_exhibitions", "Numero eventi/mostre", VarType.QUANTITY,
                Component.ACTIVATION, "eventi/anno", default_unit_rate=8000.0, weight=0.3,
                description="Numero di eventi/mostre/produzioni annue attivabili come asset."),
    VariableDef("audience_profile_score", "Profilo del pubblico", VarType.QUALITY,
                Component.BRAND_EQUITY, "score 0-1", benchmark_min=0, benchmark_max=1, weight=0.2,
                description="Profilazione socio-culturale ed economica del pubblico (affluenza, istruzione)."),
    VariableDef("tourist_audience_pct", "% pubblico turistico", VarType.QUALITY,
                Component.EXPOSURE, "score 0-1", benchmark_min=0, benchmark_max=1, weight=0.2,
                description="Quota di pubblico non residente/internazionale sul totale visitatori."),
    VariableDef("international_reach", "Portata internazionale", VarType.QUALITY,
                Component.BRAND_EQUITY, "score 0-1", benchmark_min=0, benchmark_max=1, weight=0.15,
                description="Rilevanza e notorietà della property a livello internazionale."),
    VariableDef("digital_engagement", "Engagement digitale", VarType.QUALITY,
                Component.DIGITAL_OWNED_MEDIA, "score 0-1", benchmark_min=0, benchmark_max=0.12, weight=0.35,
                description="Engagement rate medio sui canali digital owned della property culturale."),
    VariableDef("newsletter_crm_reach", "Newsletter / CRM reach", VarType.QUANTITY,
                Component.DIGITAL_OWNED_MEDIA, "contatti CRM", default_unit_rate=0.15, weight=0.35,
                description="Contatti attivi in newsletter/CRM raggiungibili direttamente."),
    VariableDef("experiential_activations", "Attivazioni educational/experiential", VarType.QUANTITY,
                Component.ACTIVATION, "attivazioni/anno", default_unit_rate=6000.0, weight=0.2,
                description="Numero di percorsi/attivazioni educational o esperienziali proponibili a partner."),
]


def get_variable_set(sector: str) -> list[VariableDef]:
    """Ritorna l'elenco completo delle variabili (comuni + settoriali) per un settore."""
    sector = sector.lower().strip()
    if sector == "sport":
        return COMMON_VARIABLES + SPORT_VARIABLES
    elif sector == "cultura":
        return COMMON_VARIABLES + CULTURE_VARIABLES
    raise ValueError(f"Settore non riconosciuto: {sector!r}. Usa 'sport' o 'cultura'.")
