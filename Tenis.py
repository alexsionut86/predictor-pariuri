import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz

# Configurare pagină Streamlit
st.set_page_config(page_title="Predictor Tenis VIP", layout="wide", page_icon="🎾")

st.title("🎾 Predictor Tenis PRO: Filtru Anti-Capcane (Roland Garros)")
st.write("Algoritmul elimină cotele periculoase și caută valoare (Value Bets) bazat pe tipul de turneu (ATP/WTA).")

# Cheia ta API
API_KEY = "2429b4002790df20061f98437e5c97b2"

# Lista de turnee active
categorii_tenis = [
    {"id": "tennis_atp_french_open", "nume": "ATP French Open (Roland Garros)"},
    {"id": "tennis_wta_french_open", "nume": "WTA French Open (Roland Garros)"},
]

def adu_meciuri_tenis(sport_key):
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
    params = {
        "apiKey": API_KEY,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
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
        return "N/A"

# Sidebar - Strategie de Filtrare
st.sidebar.header("🛡️ Managementul Riscului")
filtreaza_capcane = st.sidebar.checkbox("Ascunde meciurile extrem de riscante (Loterii)", value=True)

toate_meciurile = []

with st.spinner("Se analizează tablourile de joc și cotele din agenții..."):
    for cat in categorii_tenis:
        date_meciuri = adu_meciuri_tenis(cat["id"])
        
        if isinstance(date_meciuri, dict):
            continue
            
        is_wta = "WTA" in cat["nume"]
        
        for meci in date_meciuri:
            home_team = meci.get("home_team")
            away_team = meci.get("away_team")
            commence_time = converteste_ora(meci.get("commence_time"))
            
            cota_1, cota_2 = None, None
            bookmakers = meci.get("bookmakers", [])
            
            if bookmakers and len(bookmakers) > 0:
                markets = bookmakers[0].get("markets", [])
                if markets and len(markets) > 0:
                    outcomes = markets[0].get("outcomes", [])
                    for out in outcomes:
                        if out["name"] == home_team: cota_1 = float(out["price"])
                        elif out["name"] == away_team: cota_2 = float(out["price"])
            
            # Începe filtrarea și analiza inteligentă
            if cota_1 and cota_2:
                
                # Regula 1: Identificare echilibru total (Cote de tip capcană/loterie 1.70 - 2.10)
                if 1.65 <= cota_1 <= 2.15 and 1.65 <= cota_2 <= 2.15:
                    if filtreaza_capcane: 
                        continue  # Sare peste ele dacă utilizatorul vrea siguranță
                    verdict_risc = "⚠️ RISC RIDICAT (Loterie)"
                    pronostic = "📈 Peste 3.5 Seturi / Peste 22.5 Game-uri"
                
                # Regula 2: Favorit Uriaș ATP (Grand Slam - 3 din 5 seturi)
                elif cota_1 < 1.25 and not is_wta:
                    verdict_risc = "🟩 VIP SIGUR"
                    pronostic = f"🎾 Scor Corect: 3-0 sau 3-1 la seturi ({home_team})"
                elif cota_2 < 1.25 and not is_wta:
                    verdict_risc = "🟩 VIP SIGUR"
                    pronostic = f"🎾 Scor Corect: 3-0 sau 3-1 la seturi ({away_team})"
                    
                # Regula 3: Alerta la Tenis Feminin (WTA) - Favorită cu cotă mică, dar instabilă
                elif cota_1 < 1.30 and is_wta:
                    verdict_risc = "🟨 HIGHLIGHT WTA"
                    pronostic = f"👉 Handicap: -1.5 Seturi ({home_team}) SAU Sub 19.5 Game-uri"
                elif cota_2 < 1.30 and is_wta:
                    verdict_risc = "🟨 HIGHLIGHT WTA"
                    pronostic = f"👉 Handicap: -1.5 Seturi ({away_team}) SAU Sub 19.5 Game-uri"
                
                # Regula 4: Meciuri cu favorit mediu standard
                else:
                    verdict_risc = "🟦 VALUE BET"
                    if cota_1 < cota_2:
                        pronostic = f"👉 Câștigă direct: {home_team} (Cota: {cota_1:.2f})"
                    else:
                        pronostic = f"👉 Câștigă direct: {away_team} (Cota: {cota_2:.2f})"
                
                toate_meciurile.append({
                    "Circuit": "WTA 👩" if is_wta else "ATP 👨",
                    "Competiție": cat["nume"],
                    "Dată & Oră RO": commence_time,
                    "Meci": f"{home_team} vs {away_team}",
                    "Cota 1": f"{cota_1:.2f}",
                    "Cota 2": f"{cota_2:.2f}",
                    "VERDICT STRATEGIC": verdict_risc,
                    "RECOMANDARE PROFESIONISTĂ": pronostic
                })

if toate_meciurile:
    df = pd.DataFrame(toate_meciurile)
    df = df.drop_duplicates(subset=["Meci"])
    
    st.success(f"🔥 Filtrare completă! Din sute de meciuri, au rămas doar {len(df)} selecții inteligente.")
    
    # Sortăm ca să vedem meciurile cele mai sigure (VIP) primele în tabel
    df = df.sort_values(by=["VERDICT STRATEGIC"], ascending=True)
    
    st.dataframe(df, use_container_width=True)
else:
    st.info("Nu sunt meciuri care să îndeplinească criteriile stricte de siguranță în acest moment.")
