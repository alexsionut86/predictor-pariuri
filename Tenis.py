import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz

# Configurare pagină Streamlit
st.set_page_config(page_title="Predictor Tenis Pro", layout="wide", page_icon="🎾")

st.title("🎾 Predictor Tenis: Recomandări Directe pentru Bilet")
st.write("Algoritmul transformă cotele în pronosticuri clare (Semne, Game-uri sau Handicap).")

# Cheia ta API
API_KEY = "2429b4002790df20061f98437e5c97b2"

# Lista oficială de turnee
categorii_tenis = [
    {"id": "tennis_atp_aus_open_singles", "nume": "🏆 Australian Open (Masculin)"},
    {"id": "tennis_wta_aus_open_singles", "nume": "🏆 Australian Open (Feminin)"},
    {"id": "tennis_atp_french_open", "nume": "🏆 Roland Garros (Masculin)"},
    {"id": "tennis_wta_french_open", "nume": "🏆 Roland Garros (Feminin)"},
    {"id": "tennis_atp_wimbledon", "nume": "🏆 Wimbledon (Masculin)"},
    {"id": "tennis_wta_wimbledon", "nume": "🏆 Wimbledon (Feminin)"},
    {"id": "tennis_atp_us_open", "nume": "🏆 US Open (Masculin)"},
    {"id": "tennis_wta_us_open", "nume": "🏆 US Open (Feminin)"},
    {"id": "tennis_atp_barcelona_open", "nume": "🎾 ATP Barcelona"},
    {"id": "tennis_atp_canadian_open", "nume": "🎾 ATP Canadian Open"},
    {"id": "tennis_atp_china_open", "nume": "🎾 ATP China Open"},
    {"id": "tennis_atp_cincinnati_open", "nume": "🎾 ATP Cincinnati"},
    {"id": "tennis_atp_dubai", "nume": "🎾 ATP Dubai"},
    {"id": "tennis_atp_hamburg_open", "nume": "🎾 ATP Hamburg"},
    {"id": "tennis_atp_indian_wells", "nume": "🎾 ATP Indian Wells"},
    {"id": "tennis_atp_italian_open", "nume": "🎾 ATP Roma"},
    {"id": "tennis_atp_madrid_open", "nume": "🎾 ATP Madrid"},
    {"id": "tennis_atp_miami_open", "nume": "🎾 ATP Miami"},
    {"id": "tennis_atp_monte_carlo_masters", "nume": "🎾 ATP Monte-Carlo"},
    {"id": "tennis_atp_munich", "nume": "🎾 ATP Munchen"},
    {"id": "tennis_atp_paris_masters", "nume": "🎾 ATP Paris Masters"},
    {"id": "tennis_atp_qatar_open", "nume": "🎾 ATP Qatar"},
    {"id": "tennis_atp_shanghai_masters", "nume": "🎾 ATP Shanghai"},
    {"id": "tennis_wta_canadian_open", "nume": "🎾 WTA Canadian Open"},
    {"id": "tennis_wta_charleston_open", "nume": "🎾 WTA Charleston"},
    {"id": "tennis_wta_china_open", "nume": "🎾 WTA China Open"},
    {"id": "tennis_wta_cincinnati_open", "nume": "🎾 WTA Cincinnati"},
    {"id": "tennis_wta_dubai", "nume": "🎾 WTA Dubai"},
    {"id": "tennis_wta_indian_wells", "nume": "🎾 WTA Indian Wells"},
    {"id": "tennis_wta_italian_open", "nume": "🎾 WTA Roma"},
    {"id": "tennis_wta_madrid_open", "nume": "🎾 WTA Madrid"},
    {"id": "tennis_wta_miami_open", "nume": "🎾 WTA Miami"},
    {"id": "tennis_wta_qatar_open", "nume": "🎾 WTA Qatar"},
    {"id": "tennis_wta_strasbourg", "nume": "🎾 WTA Strasbourg"},
    {"id": "tennis_wta_stuttgart_open", "nume": "🎾 WTA Stuttgart"},
    {"id": "tennis_wta_wuhan_open", "nume": "🎾 WTA Wuhan"}
]

def adu_meciuri_tenis(sport_key):
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
    params = {
        "apiKey": API_KEY,
        "regions": "eu",
        "markets": "h2h",
        "bookmakers": "unibet,bwin,betclic,pinnacle",
        "oddsFormat": "decimal"
    }
    try:
        response = requests.get(url, params=params)
        return response.json() if response.status_code == 200 else []
    except:
        return []

def converteste_ora(ora_utc_str):
    try:
        ora_utc = datetime.strptime(ora_utc_str, "%Y-%m-%dT%H:%M:%SZ")
        tz_ro = pytz.timezone('Europe/Bucharest')
        ora_ro = ora_utc.replace(tzinfo=pytz.utc).astimezone(tz_ro)
        return ora_ro.strftime("%d-%m-%Y %H:%M")
    except:
        return ora_utc_str

# Sidebar - Strategie pariere
st.sidebar.header("🎯 Opțiuni Bilet")
mod_pariere = st.sidebar.selectbox("Ce tip de pronostic vrei pe bilet?", ["Doar Semne Clare (1 sau 2)", "Pariuri Variate (Game-uri / Handicap)"])

toate_meciurile = []

with st.spinner("Se generează pronosticurile..."):
    for cat in categorii_tenis:
        date_meciuri = adu_meciuri_tenis(cat["id"])
        
        for meci in date_meciuri:
            home_team = meci.get("home_team")
            away_team = meci.get("away_team")
            commence_time = converteste_ora(meci.get("commence_time"))
            
            cota_1, cota_2 = None, None
            bookmakers = meci.get("bookmakers", [])
            if bookmakers:
                markets = bookmakers[0].get("markets", [])
                if markets:
                    outcomes = markets[0].get("outcomes", [])
                    for out in outcomes:
                        if out["name"] == home_team: cota_1 = out["price"]
                        elif out["name"] == away_team: cota_2 = out["price"]
            
            if cota_1 and cota_2:
                marja = (1/cota_1) + (1/cota_2)
                prob_1 = ((1 / cota_1) / marja) * 100
                prob_2 = ((1 / cota_2) / marja) * 100
                
                # --- STRATEGIE DE GENERARE PRONOSTICURI ---
                if mod_pariere == "Doar Semne Clare (1 sau 2)":
                    pronostic = "👉 Semn: 1" if prob_1 > prob_2 else "👉 Semn: 2"
                else:
                    # Meci extrem de strâns (cote echilibrate) -> Recomandăm total game-uri ridicat
                    if 1.70 <= cota_1 <= 2.15 and 1.70 <= cota_2 <= 2.15:
                        pronostic = "📈 Peste 21.5 Game-uri"
                    # Favorit uriaș (cota foarte mică) -> Se cere handicap sau sub game-uri
                    elif cota_1 < 1.25:
                        pronostic = "🎾 Handicap: -4.5 Game-uri (1)"
                    elif cota_2 < 1.25:
                        pronostic = "🎾 Handicap: -4.5 Game-uri (2)"
                    # Meci normal -> Mergem direct pe semnul favoritului
                    else:
                        pronostic = "👉 Semn: 1" if prob_1 > prob_2 else "👉 Semn: 2"
                
                toate_meciurile.append({
                    "Competiție": cat["nume"],
                    "Dată & Oră RO": commence_time,
                    "Meci": f"{home_team} vs {away_team}",
                    "Cota 1": cota_1,
                    "Cota 2": cota_2,
                    "PRONOSTIC DIRECT": pronostic
                })

if toate_meciurile:
    df = pd.DataFrame(toate_meciurile)
    st.success(f"S-au analizat {len(df)} meciuri!")
    st.dataframe(df, use_container_width=True)
else:
    st.info("Nu sunt meciuri active în turneele selectate.")