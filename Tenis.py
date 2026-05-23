import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz

# Configurare pagină Streamlit
st.set_page_config(page_title="Predictor Tenis Live", layout="wide", page_icon="🎾")

st.title("🎾 Predictor Poisson & Cote Live: Tenis Master PRO")
st.write("Scanare automată a tuturor turneelor mari ATP & WTA din circuit.")

# Cheia ta API salvată corect:
API_KEY = "2429b4002790df20061f98437e5c97b2"

# Toată lista ta oficială de turnee configurată corect
categorii_tenis = [
    # --- GRAND SLAMS ---
    {"id": "tennis_atp_aus_open_singles", "nume": "🏆 Australian Open (Masculin)"},
    {"id": "tennis_wta_aus_open_singles", "nume": "🏆 Australian Open (Feminin)"},
    {"id": "tennis_atp_french_open", "nume": "🏆 Roland Garros (Masculin)"},
    {"id": "tennis_wta_french_open", "nume": "🏆 Roland Garros (Feminin)"},
    {"id": "tennis_atp_wimbledon", "nume": "🏆 Wimbledon (Masculin)"},
    {"id": "tennis_wta_wimbledon", "nume": "🏆 Wimbledon (Feminin)"},
    {"id": "tennis_atp_us_open", "nume": "🏆 US Open (Masculin)"},
    {"id": "tennis_wta_us_open", "nume": "🏆 US Open (Feminin)"},
    
    # --- TURNEE ATP ---
    {"id": "tennis_atp_barcelona_open", "nume": "🎾 ATP Barcelona"},
    {"id": "tennis_atp_canadian_open", "nume": "🎾 ATP Canadian Open"},
    {"id": "tennis_atp_china_open", "nume": "🎾 ATP China Open"},
    {"id": "tennis_atp_cincinnati_open", "nume": "🎾 ATP Cincinnati"},
    {"id": "tennis_atp_dubai", "nume": "🎾 ATP Dubai"},
    {"id": "tennis_atp_hamburg_open", "nume": "🎾 ATP Hamburg"},
    {"id": "tennis_atp_indian_wells", "nume": "🎾 ATP Indian Wells"},
    {"id": "tennis_atp_italian_open", "nume": "🎾 ATP Roma (Italia)"},
    {"id": "tennis_atp_madrid_open", "nume": "🎾 ATP Madrid"},
    {"id": "tennis_atp_miami_open", "nume": "🎾 ATP Miami"},
    {"id": "tennis_atp_monte_carlo_masters", "nume": "🎾 ATP Monte-Carlo"},
    {"id": "tennis_atp_munich", "nume": "🎾 ATP Munchen"},
    {"id": "tennis_atp_paris_masters", "nume": "🎾 ATP Paris Masters"},
    {"id": "tennis_atp_qatar_open", "nume": "🎾 ATP Qatar"},
    {"id": "tennis_atp_shanghai_masters", "nume": "🎾 ATP Shanghai"},
    
    # --- TURNEE WTA ---
    {"id": "tennis_wta_canadian_open", "nume": "🎾 WTA Canadian Open"},
    {"id": "tennis_wta_charleston_open", "nume": "🎾 WTA Charleston"},
    {"id": "tennis_wta_china_open", "nume": "🎾 WTA China Open"},
    {"id": "tennis_wta_cincinnati_open", "nume": "🎾 WTA Cincinnati"},
    {"id": "tennis_wta_dubai", "nume": "🎾 WTA Dubai"},
    {"id": "tennis_wta_indian_wells", "nume": "🎾 WTA Indian Wells"},
    {"id": "tennis_wta_italian_open", "nume": "🎾 WTA Roma (Italia)"},
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
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except:
        return []

def converteste_ora(ora_utc_str):
    try:
        ora_utc = datetime.strptime(ora_utc_str, "%Y-%m-%dT%H:%M:%SZ")
        tz_utc = pytz.timezone('UTC')
        tz_ro = pytz.timezone('Europe/Bucharest')
        ora_utc = tz_utc.localize(ora_utc)
        ora_ro = ora_utc.astimezone(tz_ro)
        return ora_ro.strftime("%d-%m-%Y %H:%M")
    except:
        return ora_utc_str

# Interfața aplicației
st.sidebar.header("⚙️ Setări Filtrare")
mod_pariere = st.sidebar.selectbox("Ce tip de pronostic vrei să vezi?", ["Semn Final (1 sau 2)", "Game-uri & Handicap"])

toate_meciurile = []

with st.spinner("Se scanează meciurile..."):
    for cat in categorii_tenis:
        date_meciuri = adu_meciuri_tenis(cat["id"])
        
        for meci in date_meciuri:
            home_team = meci.get("home_team")
            away_team = meci.get("away_team")
            commence_time = converteste_ora(meci.get("commence_time"))
            
            cota_1 = None
            cota_2 = None
            
            bookmakers = meci.get("bookmakers", [])
            if bookmakers:
                markets = bookmakers[0].get("markets", [])
                if markets:
                    outcomes = markets[0].get("outcomes", [])
                    for out in outcomes:
                        if out["name"] == home_team:
                            cota_1 = out["price"]
                        elif out["name"] == away_team:
                            cota_2 = out["price"]
            
            if cota_1 and cota_2:
                marja = (1/cota_1) + (1/cota_2)
                prob_mat_1 = (1 / cota_1) / marja
                prob_mat_2 = (1 / cota_2) / marja
                
                # --- ALGORITM DE CALCUL PENTRU GAME-URI ȘI SEMNE ---
                if mod_pariere == "Semn Final (1 sau 2)":
                    if prob_mat_1 > prob_mat_2:
                        pronostic_final = f"👉 Pune: 1 (Victorie {home_team})"
                    else:
                        pronostic_final = f"👉 Pune: 2 (Victorie {away_team})"
                else:
                    # Dacă meciul e foarte dezechilibrat (ex: Sabalenka cota 1.05)
                    if cota_1 < 1.20 or cota_2 < 1.20:
                        pronostic_final = "📉 Sub 19.5 Game-uri (Meci rapid)"
                    # Dacă meciul e relativ echilibrat (cote între 1.50 și 2.50)
                    elif 1.50 <= cota_1 <= 2.50 and 1.50 <= cota_2 <= 2.50:
                        pronostic_final = "📈 Peste 21.5 Game-uri (Meci strâns)"
                    # Structură intermediară pentru handicap
                    elif cota_1 < cota_2:
                        pronostic_final = f"🎾 Handicap: -3.5 Game-uri {home_team}"
                    else:
                        pronostic_final = f"🎾 Handicap: -3.5 Game-uri {away_team}"
                
                toate_meciurile.append({
                    "Competiție": cat["nume"],
                    "Dată & Oră RO": commence_time,
                    "Jucător 1 (Gazde)": home_team,
                    "Jucător 2 (Oaspeți)": away_team,
                    "Cota 1": cota_1,
                    "Cota 2": cota_2,
                    "Șansă 1 (%)": f"{prob_mat_1*100:.1f}%",
                    "Șansă 2 (%)": f"{prob_mat_2*100:.1f}%",
                    "🔥 RECOMANDARE BILET": pronostic_final
                })

if toate_meciurile:
    df = pd.DataFrame(toate_meciurile)
    st.success(f"S-au găsit {len(df)} meciuri analizate!")
    st.dataframe(df.style.set_properties(**{'text-align': 'center'}), use_container_width=True)
else:
    st.info("Momentan nu sunt meciuri active deschise la pariuri.")