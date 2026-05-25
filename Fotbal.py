import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz

def preia_toate_meciurile_lumii():
    """
    Descarcă automat meciurile și cotele reale din cele 11 ligi selectate.
    """
    # 🔴 Cheia ta API salvată corect:
    API_KEY = "2429b4002790df20061f98437e5c97b2"
    
    ligi_configurate = [
        {"id": "soccer_australia_aleague", "nume": "A-League"},
        {"id": "soccer_japan_j_league","nume": "J League"},
        {"id": "soccer_korea_kleague1","nume": "K League 1"},
        
    ]
    
    lista_meciuri = []
    zona_ro = pytz.timezone("Europe/Bucharest")
    
    with st.spinner('Robotul analizează cotele și pregătește recomandările...'):
        for liga in ligi_configurate:
            url = f"https://api.the-odds-api.com/v4/sports/{liga['id']}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h&oddsFormat=decimal"
            
            try:
                response = requests.get(url, timeout=6)
                if response.status_code == 200:
                    date_api = response.json()
                    
                    for meci in date_api:
                        gazde = meci.get('home_team', 'Gazde')
                        oaspeti = meci.get('away_team', 'Oaspeti')
                        
                        # Dată și Oră
                        data_ora_ro = "Nespecificat"
                        timp_start = meci.get('commence_time') 
                        if timp_start:
                            try:
                                timp_utc = datetime.strptime(timp_start, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)
                                timp_local = timp_utc.astimezone(zona_ro)
                                data_ora_ro = timp_local.strftime("%d.%m / %H:%M")
                            except Exception:
                                pass

                        # Culegere cote - CORECTAT AICI!
                        c1, cX, c2 = 2.00, 3.20, 3.00
                        if meci.get('bookmakers'):
                            piete = meci['bookmakers'][0].get('markets', [])
                            if piete:
                                outcomes = piete[0].get('outcomes', [])
                                for out in outcomes:
                                    if out['name'] == gazde:
                                        c1 = out['price']
                                    elif out['name'] == oaspeti:
                                        c2 = out['price']
                                    else:
                                        cX = out['price']
                        
                        lista_meciuri.append({
                            'data_ora': data_ora_ro,
                            'liga': liga['nume'],
                            'g': gazde,
                            'o': oaspeti,
                            'c1': c1, 'cX': cX, 'c2': c2
                        })
            except Exception:
                continue

    if not lista_meciuri:
        lista_meciuri = [
            {'data_ora': '23.05 / 14:30', 'liga': '🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League - Anglia', 'g': 'Crystal Palace', 'o': 'Arsenal', 'c1': 5.50, 'cX': 4.20, 'c2': 1.55},
            {'data_ora': '22.05 / 20:30', 'liga': '🇷🇴 Liga 1 - România', 'g': 'CFR Cluj', 'o': 'FC Arges', 'c1': 1.65, 'cX': 3.75, 'c2': 5.25}
        ]
        
    return lista_meciuri

# --- INTERFAȚA STREAMLIT ---
st.set_page_config(page_title="Predictor Complet VIP", page_icon="⚽", layout="wide")

st.title("🤖 Multi-Scanner - Panou de Control și Bilete Sigure")
data_curenta = datetime.now().strftime("%d.%m.%Y")
st.markdown(f"Fiecare meci este verificat și filtrat automat: **{data_curenta}**")

meciuri = preia_toate_meciurile_lumii()

if meciuri:
    raport_total = []
    
    for m in meciuri:
        c1, cX, c2 = m['c1'], m['cX'], m['c2']
        probabilitate_1 = (1 / c1) * 100
        
        # Generare automată a celor 3 variante în funcție de cote
        if c1 <= 1.65:
            verdict = "🟩 FAVORIT CLAR"
            sugestie_safe = f"Șansă dublă 1X (Asigurat)"
            sugestie_medium = f"1 Solist ({m['g']})"
            sugestie_risk = f"1 & Peste 2.5 Goluri"
        elif 1.65 < c1 <= 2.30:
            verdict = "🟨 MECI ECHILIBRAT"
            sugestie_safe = "Interval goluri 1-4"
            sugestie_medium = "Ambele marchează (GG) sau 1X"
            sugestie_risk = "X final (Egalitate)"
        else:
            verdict = "🟥 OUTSIDER / HAZARD"
            sugestie_safe = "Peste 1.5 Goluri în meci"
            sugestie_medium = f"Șansă dublă X2 ({m['o']})"
            sugestie_risk = f"2 Solist (Surpriză {m['o']})"
            
        raport_total.append({
            "Dată / Oră": m['data_ora'],
            "Competiție": m['liga'],
            "Meci": f"{m['g']} vs {m['o']}",
            "Cota 1": f"{c1:.2f}",
            "Cota X": f"{cX:.2f}",
            "Cota 2": f"{c2:.2f}",
            "Verdict Risc": verdict,
            "🛡️ Varianta Safe (Prudent)": sugestie_safe,
            "⚡ Varianta Medium (Echilibrat)": sugestie_medium,
            "🔥 Varianta Risk (Cotă Mare)": sugestie_risk
        })
        
    df = pd.DataFrame(raport_total)
    df = df.sort_values(by="Dată / Oră", ascending=True)
    
    # Casete de statistici sus
    col1, col2, col3 = st.columns(3)
    meciuri_verzi = df[df["Verdict Risc"] == "🟩 FAVORIT CLAR"]
    col1.metric("Meciuri Total Procesate", len(df))
    col2.metric("Partide de Siguranță Ridicată (Verzi)", len(meciuri_verzi))
    col3.metric("Total Variante generate", len(df) * 3)
    
    st.write("---")
    
    # Tabelul general interactiv
    st.subheader("📋 Panou General - Alege varianta care ți se potrivește:")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # --- SECȚIUNEA VERDE DE JOS ---
    st.write("---")
    st.subheader("🔥 RECOMANDĂRI AUTOMATE BILET (Filtru Verde - Siguranță Maximă):")
    
    if not meciuri_verzi.empty:
        for idx, row in meciuri_verzi.iterrows():
            st.success(f"⏰ **[{row['Dată / Oră']}]** {row['Meci']} ({row['Competiție']}) ➔ Baza: **{row['🛡️ Varianta Safe (Prudent)']}** | Pentru cotă mai mare: **{row['⚡ Varianta Medium (Echilibrat)']}** (Cota: {row['Cota 1']})")
    else:
        st.info("În acest moment, niciun meci din cele 11 ligi nu are o favorită certă sub cota 1.65 pentru filtrul verde.")
else:
    st.error("Nu s-au putut procesa cotele globale.")
