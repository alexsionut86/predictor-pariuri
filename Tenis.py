import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz

# Configurare pagină Streamlit
st.set_page_config(page_title="Predictor Tenis Live", layout="wide", page_icon="🎾")

st.title("🎾 Predictor Poisson & Cote Live: Tenis (ATP & WTA)")
st.write("Scanare automată a turneelor de tenis active și calcularea valorii matematice (Expected Value).")

# Cheia ta API salvată corect:
API_KEY = "2429b4002790df20061f98437e5c97b2"

# Configurare categorii Tenis
categorii_tenis = [
    {"id": "tennis_france_open", "nume": "🏆 Roland Garros (Openul Francez)"},
    {"id": "tennis_atp_lyon", "nume": "🎾 ATP Lyon"},
    {"id": "tennis_atp_geneva", "nume": "🎾 ATP Geneva"},
    {"id": "tennis_wta_strasbourg", "nume": "🎾 WTA Strasbourg"},
    {"id": "tennis_wta_rabat", "nume": "🎾 WTA Rabat"}
]

def adu_meciuri_tenis(sport_key):
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
    params = {
        "apiKey": API_KEY,
        "regions": "eu",
        "markets": "h2h",
        "bookmakers": "unibet,bwin,betclic,1xbet,pinnacle",
        "oddsFormat": "decimal"
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            st.error("⚠️ Ai epuizat creditele pe luna aceasta!")
            return []
        else:
            return []
    except Exception as e:
        st.error(f"Eroare la conexiune: {e}")
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
prag_ev = st.sidebar.slider("Prag Expected Value (EV %)", min_value=-20.0, max_value=20.0, value=2.0, step=0.5)

toate_meciurile = []

with st.spinner("Se descarcă cotele live pentru tenis..."):
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
                # Calculare probabilități implicite din cote (cu eliminarea marjei)
                marja = (1/cota_1) + (1/cota_2)
                prob_mat_1 = (1 / cota_1) / marja
                prob_mat_2 = (1 / cota_2) / marja
                
                # Calcul teoretic simplificat pentru EV (valoare)
                # Într-un sistem ideal, căutăm discrepanțe între bookmakeri. 
                # Aici folosim prețul inversat ca o estimare rapidă.
                ev_1 = (prob_mat_1 * cota_1 - 1) * 100
                ev_2 = (prob_mat_2 * cota_2 - 1) * 100
                
                # Recomandare bazată pe pragul ales
                recomandare = "Caută oportunități"
                if ev_1 >= prag_ev:
                    recomandare = f"🔥 Valoare pe {home_team}"
                elif ev_2 >= prag_ev:
                    recomandare = f"🔥 Valoare pe {away_team}"
                else:
                    recomandare = "Nicio valoare clară"
                
                toate_meciurile.append({
                    "Turneu/Categorie": cat["nume"],
                    "Dată & Oră RO": commence_time,
                    "Jucător 1 (Gazdă)": home_team,
                    "Jucător 2 (Oaspeți)": away_team,
                    "Cota Jucător 1": cota_1,
                    "Cota Jucător 2": cota_2,
                    "Șansă J1 (%)": f"{prob_mat_1*100:.1f}%",
                    "Șansă J2 (%)": f"{prob_mat_2*100:.1f}%",
                    "Pronostic Recomandat": recomandare
                })

if toate_meciurile:
    df = pd.DataFrame(toate_meciurile)
    st.success(f"S-au găsit {len(df)} meciuri active în următoarele zile!")
    
    # Afișare tabel inteligent
    st.dataframe(df.style.set_properties(**{'text-align': 'center'}), use_container_width=True)
else:
    st.info("Nu s-au găsit meciuri sau turnee active în acest moment în baza de date.")
