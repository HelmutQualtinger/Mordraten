"""Flask + Plotly Version der Europakarte.

Startet einen lokalen Webserver, der eine interaktive Plotly-Choroplethenkarte
Europas ausliefert. Metrik-Auswahl erfolgt über ein Dropdown-Menu (clientseitig
in Plotly.js, kein Reload noetig).
"""
import json
from pathlib import Path

from flask import Flask
import plotly.graph_objects as go

app = Flask(__name__)

DATA_PATH = Path(__file__).parent / "country_data.json"
with open(DATA_PATH, encoding="utf-8") as f:
    COUNTRY_DATA = json.load(f)

# Reihenfolge, Skala-Richtung (True = hoeher ist besser -> RdYlGn, False -> RdYlGn_r)
# und Formatierung je Metrik.
METRICS = {
    "income_ppp": {
        "label": "Medianeinkommen (kaufkraftbereinigt, PPP-$)",
        "higher_is_better": True,
        "suffix": " PPP-$",
    },
    "income_nominal_eur": {
        "label": "Medianeinkommen (nominal, EUR, nicht kaufkraftbereinigt)",
        "higher_is_better": True,
        "suffix": " EUR",
    },
    "wealth_ppp": {
        "label": "Medianvermögen (kaufkraftbereinigt, PPP-$)",
        "higher_is_better": True,
        "suffix": " PPP-$",
    },
    "lifeexp": {
        "label": "Lebenserwartung (Jahre)",
        "higher_is_better": True,
        "suffix": " Jahre",
    },
    "murder": {
        "label": "Mordrate (pro 100.000)",
        "higher_is_better": False,
        "suffix": " / 100k",
    },
    "suicide": {
        "label": "Selbstmordrate (pro 100.000)",
        "higher_is_better": False,
        "suffix": " / 100k",
    },
}

DEFAULT_METRIC = "income_ppp"


def build_figure() -> go.Figure:
    names = list(COUNTRY_DATA.keys())
    locations = [COUNTRY_DATA[n]["iso3"] for n in names]

    traces = []
    for key, cfg in METRICS.items():
        z = [COUNTRY_DATA[n].get(key) for n in names]
        # Plotly laesst None-Werte automatisch aus (kein Land eingefaerbt).
        text = [
            f"<b>{n}</b><br>{cfg['label']}<br>"
            + (f"{v:,.0f}{cfg['suffix']}".replace(",", ".") if v is not None else "keine Daten")
            for n, v in zip(names, z)
        ]
        colorscale = "RdYlGn" if cfg["higher_is_better"] else "RdYlGn_r"
        traces.append(
            go.Choropleth(
                locations=locations,
                z=z,
                locationmode="ISO-3",
                text=text,
                hoverinfo="text",
                colorscale=colorscale,
                colorbar=dict(title=cfg["label"], len=0.75),
                visible=(key == DEFAULT_METRIC),
                marker_line_color="white",
                marker_line_width=0.5,
            )
        )

    fig = go.Figure(data=traces)

    buttons = []
    keys = list(METRICS.keys())
    for i, key in enumerate(keys):
        visible = [j == i for j in range(len(keys))]
        buttons.append(
            dict(
                label=METRICS[key]["label"],
                method="update",
                args=[{"visible": visible}, {"title": METRICS[key]["label"]}],
            )
        )

    fig.update_layout(
        title=dict(text=METRICS[DEFAULT_METRIC]["label"], x=0.5),
        updatemenus=[
            dict(
                buttons=buttons,
                direction="down",
                x=0.02,
                y=1.08,
                xanchor="left",
                showactive=True,
            )
        ],
        geo=dict(
            scope="europe",
            resolution=50,
            showcoastlines=True,
            coastlinecolor="#94a3b8",
            showland=True,
            landcolor="#eaf3f8",
            showocean=True,
            oceancolor="#eaf3f8",
            projection_type="natural earth",
            lataxis_range=[33, 72],
            lonaxis_range=[-25, 45],
        ),
        margin=dict(l=10, r=10, t=60, b=10),
        height=800,
    )
    return fig


@app.route("/")
def index():
    fig = build_figure()
    return fig.to_html(include_plotlyjs=True, full_html=True)


if __name__ == "__main__":
    # Port 5000 vermeiden (macOS AirPlay belegt ihn haeufig).
    app.run(debug=True, port=8050)
