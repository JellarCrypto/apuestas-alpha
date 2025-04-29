# app_streamlit.py
"""
Streamlit App para análisis de apuestas deportivas en directo.
Pasa la API key directamente a las funciones de ingesta.
"""
import streamlit as st

# 1) Pedir la API Key en el sidebar
st.set_page_config(page_title="Apuestas Deportivas", layout="centered")
st.sidebar.header("🔑 Ajustes de API")
api_key = st.sidebar.text_input(
    "API-Football Key", type="password",
    help="Pega aquí tu API Key de RapidAPI (API-Football)."
)
if not api_key:
    st.sidebar.error("Necesitas introducir tu API Key para continuar")
    st.stop()

# 2) Importar **después** de pedir la clave
from data_ingest import fetch_live_fixtures, fetch_odds_for_fixture
from app import calcular_probabilidades_desde_cuotas

# 3) Obtener partidos en directo
st.title("⚡ Partidos en Directo")
try:
    live_fixtures = fetch_live_fixtures(api_key)
except Exception as e:
    st.error(f"Error al obtener fixtures en directo: {e}")
    st.stop()

if not live_fixtures:
    st.info("No hay partidos en directo en este momento.")
    st.stop()

# 4) Selector de partido
options = {
    f"{f['teams']['home']['name']} vs {f['teams']['away']['name']} ({f['fixture']['date']})":
    f["fixture"]["id"]
    for f in live_fixtures
}
choice = st.selectbox("Elige un partido en directo", list(options.keys()))
fixture_id = options[choice]
home, away = choice.split(" vs ")[0], choice.split(" vs ")[1].split(" (")[0]

# 5) Obtener cuotas y calcular Top 3 apuestas 1X2 con ≥80%
try:
    odds_data = fetch_odds_for_fixture(fixture_id, api_key)
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

