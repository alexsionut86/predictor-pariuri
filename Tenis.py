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
prag_ev = st.sidebar.slider("Prag Expected Value pentru Alerte (EV %)", min_value=-5.0, max_value=15.0, value=1.0, step=0.5)

toate_meciurile = []

with st.spinner("Se scanează circuitele ATP și WTA..."):
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
                
                ev_1 = (prob_mat_1 * cota_1 - 1) * 100
                ev_2 = (prob_mat_2 * cota_2 - 1) * 100
                
                # --- NOUA LOGICĂ DIRECTĂ DE PRONOSTIC ---
                if ev_1 >= prag_ev:
                    recomandare = f"🚨 TOP VALOARE: Pune pe {home_team}!"
                elif ev_2 >= prag_ev:
                    recomandare = f"🚨 TOP VALOARE: Pune pe {away_team}!"
                else:
                    # Dacă meciul e echilibrat, robotul alege matematic cine are șanse mai mari
                    if prob_mat_1 > prob_mat_2:
                        recomandare = f"✅ De pus: {home_team} (Favorit)"
                    else:
                        recomandare = f"✅ De pus: {away_team} (Favorit)"
                
                toate_meciurile.append({
                    "Competiție": cat["nume"],
                    "Dată & Oră RO": commence_time,
                    "Jucător 1": home_team,
                    "Jucător 2": away_team,
                    "Cota J1": cota_1,
                    "Cota J2": cota_2,
                    "Șansă J1 (%)": f"{prob_mat_1*100:.1f}%",
                    "Șansă J2 (%)": f"{prob_mat_2*100:.1f}%",
                    "Ce punem? (Pronostic)": recomandare
                })

if toate_meciurile:
    df = pd.DataFrame(toate_meciurile)
    st.success(f"S-au găsit {len(df)} meciuri analizate!")
    st.dataframe(df.style.set_properties(**{'text-align': 'center'}), use_container_width=True)
else:
    st.info("Momentan nu sunt meciuri active deschise la pariuri în turneele din listă.")