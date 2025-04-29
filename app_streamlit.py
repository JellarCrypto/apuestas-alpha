# app_streamlit.py
"""
Streamlit App para análisis de apuestas deportivas.
Detecta partidos en directo y calcula Top 3 apuestas 1X2 con ≥80% probabilidad.
"""
import os
import streamlit as st

# ── 1) Configuración de la página y petición de API Key ──────────────────────
st.set_page_config(page_title="Apuestas Deportivas", layout="centered")
st.sidebar.header("🔑 Ajustes de API")
api_key = st.sidebar.text_input(
    "API-Football Key", type="password",
    help="Pega aquí tu API Key de RapidAPI (API-Football)."
)
if not api_key:
    st.sidebar.error("🔑 Necesitas introducir tu API Key para continuar")
    st.stop()

# Inyectamos la clave en la variable de entorno antes de importar el módulo
os.environ["API_FOOTBALL_KEY"] = api_key

# ── 2) Ahora importamos tras asegurar que la clave existe ────────────────────
from data_ingest import fetch_live_fixtures, fetch_odds_for_fixture
from app import calcular_probabilidades_desde_cuotas

# ── 3) Obtener partidos en directo ──────────────────────────────────────────
st.title("⚡ Partidos en Directo")
live_fixtures = fetch_live_fixtures()
if not live_fixtures:
    st.info("No hay partidos en directo en este momento.")
    st.stop()

# ── 4) Selector de partido ───────────────────────────────────────────────────
options = {}
for f in live_fixtures:
    home = f["teams"]["home"]["name"]
    away = f["teams"]["away"]["name"]
    date = f["fixture"]["date"]
    fid = f["fixture"]["id"]
    label = f"{home} vs {away}  ({date})"
    options[label] = (fid, home, away)

choice = st.selectbox("Elige un partido en directo", list(options.keys()))
fixture_id, home, away = options[choice]

st.markdown(f"## {choice}")

# ── 5) Obtener cuotas y calcular Top 3 apuestas 1X2 con ≥80% ───────────────
try:
    odds_data = fetch_odds_for_fixture(fixture_id)
except Exception as e:
    st.error(f"Error al obtener cuotas: {e}")
    st.stop()

results = []
for offer in odds_data:
    for bet in offer.get("bets", []):
        if bet.get("name") in ["Match Winner", "1X2"]:
            mapping = {v["value"]: v["odd"] for v in bet.get("values", [])}
            if home in mapping and "Draw" in mapping and away in mapping:
                cL, cE, cV = mapping[home], mapping["Draw"], mapping[away]
                p1, p2, p3 = calcular_probabilidades_desde_cuotas(cL, cE, cV)
                for name, prob, quota in [
                    (home, p1, cL),
                    ("Empate", p2, cE),
                    (away, p3, cV)
                ]:
                    ve = prob * quota - 1
                    if prob >= 0.8:
                        results.append((name, prob, quota, ve))

if not results:
    st.info("No hay apuestas con probabilidad ≥80% para este partido.")
else:
    st.markdown("### Top 3 apuestas 1X2 (≥80% probabilidad)")
    for name, prob, quota, ve in sorted(results, key=lambda x: x[1], reverse=True)[:3]:
        st.write(f"**{name}**: {prob*100:.1f}% | Cuota={quota} | VE={ve:.2f}")
