"""
report/generator.py

Genera il report HTML finale a partire da un ValuationResult (model/valuation.py).

Uso:
    from report.generator import generate_report
    generate_report(valuation_result, output_path="output/report.html")
"""

import json
from model.valuation import ValuationResult

# Stessa palette della dashboard World Index Data
COLOR_BG = "#4FC3F7"
COLOR_DARK = "#25465D"
COLOR_TOTAL = "#25465D"
COMPONENT_COLORS = {
    "brand_equity": "#00649C",
    "exposure": "#10a870",
    "digital_owned_media": "#E85933",
    "relationship": "#8E44AD",
    "activation": "#D4A017",
}

METHOD_NOTE_HTML = """
<h2>Nota metodologica</h2>
<p>Il modello valuta il valore di mercato indicativo degli asset sponsorizzativi di una
property (sportiva o culturale) attraverso un approccio <strong>asset-based</strong>,
scomposto in 5 componenti complementari.</p>
<p><strong>Come si calcola ogni componente:</strong></p>
<ul>
<li><strong>Exposure, Digital Owned Media, Relationship, Activation:</strong> valore base
(quantità x benchmark economico unitario) modulato da un moltiplicatore qualitativo
(0.6x - 1.4x) derivato dalle variabili di qualità associate.</li>
<li><strong>Brand Equity:</strong> calcolato diversamente, con una logica a fasce
(Elite/Alta/Media/Bassa) determinata dal blasone/prestigio della property, poi
aggiustata (+/-20%) da brand fit ed exclusivity.</li>
</ul>
<p><strong>Total Market Value</strong> = somma dei 5 componenti.
<strong>Value share</strong> = peso percentuale di ciascun componente sul totale.</p>
"""


def _kpi_cards_html(result: ValuationResult) -> str:
    cards = [f"""
        <div class="kpi-card kpi-totale active">
            <div class="kpi-label">Total Market Value</div>
            <div class="kpi-val">€ {result.total_market_value:,.0f}</div>
        </div>"""]
    for c in result.components:
        color = COMPONENT_COLORS.get(c.key, COLOR_DARK)
        cards.append(f"""
        <div class="kpi-card" style="border-top: 4px solid {color};">
            <div class="kpi-label">{c.label}</div>
            <div class="kpi-val" style="color:{color};">€ {c.final_value:,.0f}</div>
            <div class="kpi-sub">{c.value_share:.1f}% del totale</div>
        </div>""")
    return "".join(cards)


def _breakdown_table_html(result: ValuationResult) -> str:
    rows = []
    for c in result.components:
        color = COMPONENT_COLORS.get(c.key, COLOR_DARK)
        rows.append(f"""
        <tr>
            <td><span class="dot" style="background:{color};"></span>{c.label}</td>
            <td>€ {c.base_value:,.0f}</td>
            <td>x {c.quality_multiplier:.2f}</td>
            <td><strong>€ {c.final_value:,.0f}</strong></td>
            <td>{c.value_share:.1f}%</td>
        </tr>""")
    return "".join(rows)


def generate_report(result: ValuationResult, output_path: str = "output/report.html") -> str:
    labels = [c.label for c in result.components]
    values = [c.final_value for c in result.components]
    colors = [COMPONENT_COLORS.get(c.key, COLOR_DARK) for c in result.components]

    chart_data = json.dumps({"labels": labels, "values": values, "colors": colors})

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8" />
<title>Valutazione Sponsorizzativa — {result.property_name}</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    color: #222;
    padding: 20px 25px 40px 25px;
    background: {COLOR_BG};
    min-height: 100vh;
}}
.page {{ max-width: 1200px; margin: 0 auto; }}
.top-bar {{
    display: grid;
    grid-template-columns: 2fr 1fr;
    align-items: center;
    column-gap: 20px;
    margin-bottom: 22px;
}}
.title-box h1 {{
    font-weight: 800;
    font-size: 2.4rem;
    color: {COLOR_DARK};
    letter-spacing: -1px;
}}
.title-box p {{ color: #555; font-size: 1rem; margin-top: 4px; }}
.method-box {{
    background: #ffffff;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.15);
    max-height: 260px;
    overflow-y: auto;
    font-size: 0.85rem;
    color: #34465A;
}}
.method-box h2 {{ font-size: 1.05rem; font-weight: 700; margin-bottom: 10px; color: {COLOR_DARK}; }}
.method-box p {{ margin-bottom: 8px; line-height: 1.4; }}
.method-box ul {{ margin: 4px 0 8px 16px; }}
.method-box li {{ margin-bottom: 4px; }}
.kpi-bar {{
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 14px;
    margin-bottom: 20px;
}}
.kpi-card {{
    background: #ffffff;
    border-radius: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.12);
    padding: 16px 14px;
    text-align: center;
}}
.kpi-card.active {{ border-top: 4px solid {COLOR_TOTAL}; }}
.kpi-label {{
    font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.5px; color: #666; margin-bottom: 6px;
}}
.kpi-val {{ font-size: 1.4rem; font-weight: 800; color: {COLOR_DARK}; }}
.kpi-sub {{ font-size: 0.72rem; color: #888; margin-top: 4px; }}
.card {{
    background: #ffffff;
    border-radius: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.15);
    margin-top: 20px;
    padding: 18px;
}}
.card h2 {{
    font-size: 1.2rem; font-weight: 800; color: {COLOR_DARK};
    margin-bottom: 12px; letter-spacing: -0.5px;
}}
#chart {{ height: 420px; }}
table {{ width: 100%; border-collapse: collapse; font-size: 0.92rem; }}
th {{
    background: {COLOR_DARK}; color: white; text-align: left;
    padding: 10px 12px; font-weight: 700;
}}
td {{ padding: 10px 12px; border-bottom: 1px solid #eee; }}
tr:last-child td {{ border-bottom: none; }}
.dot {{
    display: inline-block; width: 10px; height: 10px;
    border-radius: 50%; margin-right: 8px;
}}
.total-row td {{ font-weight: 800; border-top: 2px solid {COLOR_DARK}; }}
.footer-note {{ margin-top: 18px; font-size: 0.78rem; color: #888; text-align: center; }}
</style>
</head>
<body>
<div class="page">

    <div class="top-bar">
        <div class="title-box">
            <h1>{result.property_name}</h1>
            <p>Valutazione asset-based — Settore: {result.sector.capitalize()}</p>
        </div>
        <div class="method-box">
            {METHOD_NOTE_HTML}
        </div>
    </div>

    <div class="kpi-bar">
        {_kpi_cards_html(result)}
    </div>

    <div class="card">
        <h2>Value share per componente</h2>
        <div id="chart"></div>
    </div>

    <div class="card">
        <h2>Breakdown dettagliato</h2>
        <table>
            <thead>
                <tr>
                    <th>Componente</th>
                    <th>Valore base</th>
                    <th>Moltiplicatore</th>
                    <th>Valore finale</th>
                    <th>Value share</th>
                </tr>
            </thead>
            <tbody>
                {_breakdown_table_html(result)}
                <tr class="total-row">
                    <td>Total Market Value</td>
                    <td>—</td>
                    <td>—</td>
                    <td>€ {result.total_market_value:,.0f}</td>
                    <td>100%</td>
                </tr>
            </tbody>
        </table>
    </div>

</div>

<script>
const chartData = {chart_data};
Plotly.newPlot("chart", [{{
    type: "pie",
    labels: chartData.labels,
    values: chartData.values,
    marker: {{ colors: chartData.colors }},
    textinfo: "label+percent",
    hovertemplate: "<b>%{{label}}</b><br>€ %{{value:,.0f}}<extra></extra>",
    hole: 0.35
}}], {{
    margin: {{ t: 10, b: 10, l: 10, r: 10 }},
    showlegend: true
}}, {{ responsive: true }});
</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Report generato: {output_path} ({len(html):,} caratteri)")
    return output_path
