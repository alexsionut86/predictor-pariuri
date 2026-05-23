import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz

# Configurare pagină Streamlit
st.set_page_config(page_title="Predictor Fotbal Pro", layout="wide", page_icon="⚽")

st.title("⚽ Predictor Automat Fotbal: Toate Ligile din Lume")
st.write("Scanare automată a tuturor campionatelor oficiale stabilite din ofertă.")

# Cheia ta API salvată corect:
API_KEY = "2429b4002790df20061f98437e5c97b2"

# Toată lista ta oficială de ligi de fotbal, configurată exact cum ai cerut
categorii_fotbal = [
    {"id": "soccer_epl", "nume": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League - Anglia"},
    {"id": "soccer_efl_champ", "nume": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Championship - Anglia"},
    {"id": "soccer_england_league1", "nume": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 League One - Anglia"},
    {"id": "soccer_england_league2", "nume": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 League Two - Anglia"},
    {"id": "soccer_fa_cup", "nume": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 FA Cup - Anglia"},
    {"id": "soccer_england_efl_cup", "nume": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 EFL Cup - Anglia"},
    {"id": "soccer_spain_la_liga", "nume": "🇪🇸 La Liga - Spania"},
    {"id": "soccer_spain_segunda_division", "nume": "🇪🇸 La Liga 2 - Spania"},
    {"id": "soccer_spain_copa_del_rey", "nume": "🇪🇸 Copa del Rey - Spania"},
    {"id": "soccer_italy_serie_a", "nume": "🇮🇹 Serie A - Italia"},
    {"id": "soccer_italy_serie_b", "nume": "🇮🇹 Serie B - Italia"},
    {"id": "soccer_italy_coppa_italia", "nume": "🇮🇹 Coppa Italia - Italia"},
    {"id": "soccer_germany_bundesliga", "nume": "🇩🇪 Bundesliga - Germania"},
    {"id": "soccer_germany_bundesliga2", "nume": "🇩🇪 Bundesliga 2 - Germania"},
    {"id": "soccer_germany_liga3", "nume": "🇩🇪 3. Liga - Germania"},
    {"id": "soccer_germany_dfb_pokal", "nume": "🇩🇪 DFB-Pokal - Germania"},
    {"id": "soccer_germany_bundesliga_women", "nume": "🇩🇪 Frauen-Bundesliga - Germania"},
    {"id": "soccer_france_ligue_one", "nume": "🇫🇷 Ligue 1 - Franța"},
    {"id": "soccer_france_ligue_two", "nume": "🇫🇷 Ligue 2 - Franța"},
    {"id": "soccer_france_coupe_de_france", "nume": "🇫🇷 Coupe de France - Franța"},
    {"id": "soccer_netherlands_eredivisie", "nume": "🇳🇱 Eredivisie - Olanda"},
    {"id": "soccer_portugal_primeira_liga", "nume": "🇵🇹 Primeira Liga - Portugalia"},
    {"id": "soccer_belgium_first_div", "nume": "🇧🇪 First Division A - Belgia"},
    {"id": "soccer_austria_bundesliga", "nume": "🇦🇹 Bundesliga - Austria"},
    {"id": "soccer_turkey_super_league", "nume": "🇹🇷 Super Lig - Turcia"},
    {"id": "soccer_greece_super_league", "nume": "🇬🇷 Super League - Grecia"},
    {"id": "soccer_poland_ekstraklasa", "nume": "🇵🇱 Ekstraklasa - Polonia"},
    {"id": "soccer_russia_premier_league", "nume": "🇷🇺 Premier League - Rusia"},
    {"id": "soccer_sweden_allsvenskan", "nume": "🇸🇪 Allsvenskan - Suedia"},
    {"id": "soccer_sweden_superettan", "nume": "🇸🇪 Superettan - Suedia"},
    {"id": "soccer_norway_eliteserien", "nume": "🇳🇴 Eliteserien - Norvegia"},
    {"id": "soccer_denmark_superliga", "nume": "🇩🇰 Superliga - Danemarca"},
    {"id": "soccer_finland_veikkausliiga", "nume": "🇫🇮 Veikkausliiga - Finlanda"},
    {"id": "soccer_league_of_ireland", "nume": "🇮🇪 Premier Division - Irlanda"},
    {"id": "soccer_switzerland_superleague", "nume": "🇨🇭 Super League - Elveția"},
    {"id": "soccer_saudi_arabia_pro_league", "nume": "🇸🇦 Saudi Pro League - Arabia Saudită"},
    {"id": "soccer_japan_j_league", "nume": "🇯🇵 J1 League - Japonia"},
    {"id": "soccer_korea_kleague1", "nume": "🇰🇷 K League 1 - Coreea de Sud"},
    {"id": "soccer_china_superleague", "nume": "🇨🇳 Super League - China"},
    {"id": "soccer_australia_aleague", "nume": "🇦🇺 A-League - Australia"},
    {"id": "soccer_usa_mls", "nume": "🇺🇸 MLS - SUA"},
    {"id": "soccer_brazil_campeonato", "nume": "🇧🇷 Série A - Brazilia"},
    {"id": "soccer_brazil_serie_b", "nume": "🇧🇷 Série B - Brazilia"},
    {"id": "soccer_argentina_primera_division", "nume": "🇦🇷 Primera División - Argentina"},
    {"id": "soccer_chile_campeonato", "nume": "🇨🇱 Primera División - Chile"},
    {"id": "soccer_mexico_ligamx", "nume": "🇲🇽 Liga MX - Mexic"},
    {"id": "soccer_uefa_champs_league", "nume": "🇪🇺 UEFA Champions League"},
    {"id": "soccer_uefa_champs_league_qualification", "nume": "🇪🇺 UEFA Champions League - Calificări"},
    {"id": "soccer_uefa_champs_league_women", "nume": "🇪🇺 UEFA Champions League - Feminin"},
    {"id": "soccer_uefa_europa_league", "nume": "🇪🇺 UEFA Europa League"},
    {"id": "soccer_uefa_europa_conference_league", "nume": "🇪🇺 UEFA Europa Conference League"},
    {"id": "soccer_uefa_european_championship", "nume": "🇪🇺 UEFA Euro 2024"},
    {"id": "soccer_uefa_euro_qualification", "nume": "🇪🇺 UEFA Euro - Calificări"},
    {"id": "soccer_uefa_nations_league", "nume": "🇪🇺 UEFA Nations League"},
    {"id": "soccer_conmebol_copa_america", "nume": "🌎 Copa América"},
    {"id": "soccer_conmebol_copa_libertadores", "nume": "🌎 Copa Libertadores"},
    {"id": "soccer_conmebol_copa_sudamericana", "nume": "🌎 Copa Sudamericana"},
    {"id": "soccer_concacaf_leagues_cup", "nume": "🌎 CONCACAF Leagues Cup"},
    {"id": "soccer_concacaf_gold_cup", "nume": "🌎 CONCACAF Gold Cup"},
    {"id": "soccer_africa_cup_of_nations", "nume": "🌍 Cupa Africii pe Națiuni"},
    {"id": "soccer_fifa_world_cup", "nume": "🏆 Cupa Mondială FIFA"},
    {"id": "soccer_fifa_world_cup_winner", "nume": "🏆 Cupa Mondială FIFA - Câștigător Final"},
    {"id": "soccer_fifa_world_cup_womens", "nume": "🏆 Cupa Mondială FIFA - Feminin"},
    {"id": "soccer_fifa_world_cup_qualifiers_europe", "nume": "🏆 Calificări Cupa Mondială - Europa"},
    {"id": "soccer_fifa_world_cup_qualifiers_south_america", "nume": "🏆 Calificări Cupa Mondială - America de Sud"},
    {"id": "soccer_fifa_club_world_cup", "nume": "🏆 Cupa Mondială a Cluburilor FIFA"}
]

def adu_meciuri_fotbal(sport_key, market_type):
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
    params = {
        "apiKey": API_KEY,
        "regions": "eu",
        "markets": market_type,
        "bookmakers": "unibet,betclic,bwin,pinnacle",
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

# --- INTERFAȚA SIDEBAR (STANGA) ---
st.sidebar.header("🎛️ Opțiuni Bilet Fotbal")
tip_pariu_ales = st.sidebar.selectbox("Ce tip de pronostic vrei?", ["Rezultat Final (1, X, 2)", "Total Goluri (Peste/Sub)"])

toate_meciurile = []

# Stabilim ce piață cerem de la server în funcție de selecție
market_solicitat = "h2h" if tip_pariu_ales == "Rezultat Final (1, X, 2)" else "totals"

with st.spinner("Se scanează campionatele oficiale și se calculează pronosticurile..."):
    for liga in categorii_fotbal:
        meciuri_liga = adu_meciuri_fotbal(liga["id"], market_solicitat)
        
        for meci in meciuri_liga:
            home = meci.get("home_team")
            away = meci.get("away_team")
            ora = converteste_ora(meci.get("commence_time"))
            
            bookmakers = meci.get("bookmakers", [])
            if not bookmakers:
                continue
                
            markets = bookmakers[0].get("markets", [])
            if not markets:
                continue
                
            outcomes = markets[0].get("outcomes", [])
            
            # 1. GENERARE PRONOSTICURI PENTRU REZULTAT FINAL
            if market_solicitat == "h2h":
                cota_1, cota_x, cota_2 = None, None, None
                for o in outcomes:
                    if o["name"] == home: cota_1 = o["price"]
                    elif o["name"] == "Draw": cota_x = o["price"]
                    elif o["name"] == away: cota_2 = o["price"]
                    
                if cota_1 and cota_2:
                    if cota_1 < cota_2 and cota_1 < 1.85:
                        pronostic = "👉 Semn: 1"
                    elif cota_2 < cota_1 and cota_2 < 1.85:
                        pronostic = "👉 Semn: 2"
                    else:
                        pronostic = "👉 Șansă Dublă: 1X" if cota_1 < cota_2 else "👉 Șansă Dublă: X2"
                    
                    toate_meciurile.append({
                        "Campionat": liga["nume"],
                        "Dată & Oră RO": ora,
                        "Meci": f"{home} vs {away}",
                        "Cota 1": cota_1,
                        "Cota X": cota_x,
                        "Cota 2": cota_2,
                        "PRONOSTIC DIRECT": pronostic
                    })
            
            # 2. GENERARE PRONOSTICURI PENTRU TOTAL GOLURI
            else:
                if outcomes:
                    linie = outcomes[0].get("point")
                    pronostic = f"👉 Pune: Peste {linie} Goluri" if outcomes[0]["price"] < 2.10 else f"👉 Pune: Sub {linie} Goluri"
                    
                    toate_meciurile.append({
                        "Campionat": liga["nume"],
                        "Dată & Oră RO": ora,
                        "Meci": f"{home} vs {away}",
                        "Linie Goluri": linie,
                        "PRONOSTIC DIRECT": pronostic
                    })

if toate_meciurile:
    df = pd.DataFrame(toate_meciurile)
    st.success(f"S-au găsit și analizat {len(df)} meciuri de fotbal deschise la pariuri!")
    st.dataframe(df, use_container_width=True)
else:
    st.info("Momentan nu sunt meciuri active deschise la pariuri pentru campionatele selectate.")
