import streamlit as st
import pandas as pd
import requests

# --- CONFIGURARE PAGINĂ ---
st.set_page_config(page_title="Fotbal VIP Pro - Anti-Risc Pro API", layout="wide", page_icon="⚽")

if "bilet_fotbal_premium" not in st.session_state:
    st.session_state["bilet_fotbal_premium"] = []

# --- TITLU ȘI STRATEGIE ---
st.markdown("<h1 style='text-align: center;'>⚽ Algoritm VIP Pro (API Pro Multi-Markets)</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Cote Reale 1X2, Peste/Sub 1.5 Goluri și Șansă Dublă extrase direct din API.</p>", unsafe_allow_html=True)

st.info("""
💡 **STRATEGIE ANTI-RISC PRO (2 MECIURI PER BILET):**
* Target Bilet: **Cota Finală ~2.00**
* Piețe Analizate Direct: **Șansă Dublă (1X / X2)** & **Peste 1.5 Goluri Marcate**.
* Fără supoziții: Cotele reale pentru toate piețele sunt furnizate direct de casa de pariuri!
""")
st.write("---")

# --- ALGORITM MATEMATIC DE PREDICTOR PENTRU PIEȚE MULTIPLE ---
def analizeaza_si_filtreaza_meci(meci_nume, liga_nume, status, c1, cX, c2, c_over15, c_1x, c_x2):
    # Evaluare Favorit & Șansă Dublă
    if c1 > 0 and c1 <= 1.55:
        verdict = "🟩 FAVORIT CLAR (GAZDE)"
        predicție_principala = f"Șansă Dublă 1X (Cotă: {c_1x:.2f})" if c_1x > 0 else "Șansă Dublă 1X"
        p_principala = 92
        alternativa = f"Peste 1.5 Goluri (Cotă: {c_over15:.2f})" if c_over15 > 0 else "Peste 1.5 Goluri"
        p_alt = 88
    elif c2 > 0 and c2 <= 1.55:
        verdict = "🟩 FAVORIT CLAR (OASPEȚI)"
        predicție_principala = f"Șansă Dublă X2 (Cotă: {c_x2:.2f})" if c_x2 > 0 else "Șansă Dublă X2"
        p_principala = 92
        alternativa = f"Peste 1.5 Goluri (Cotă: {c_over15:.2f})" if c_over15 > 0 else "Peste 1.5 Goluri"
        p_alt = 88
    elif c_over15 > 0 and c_over15 <= 1.45:
        verdict = "🟨 TENDINȚĂ MARE GOLURI"
        predicție_principala = f"Peste 1.5 Goluri (Cotă: {c_over15:.2f})"
        p_principala = 86
        alternativa = f"Șansă Dublă 1X (Cotă: {c_1x:.2f})" if c_1x > 0 else "Șansă Dublă 1X"
        p_alt = 80
    else:
        verdict = "🟨 MECI ECHILIBRAT"
        predicție_principala = f"Peste 1.5 Goluri (Cotă: {c_over15:.2f})" if c_over15 > 0 else "Peste 1.5 Goluri"
        p_principala = 82
        alternativa = f"Șansă Dublă 1X (Cotă: {c_1x:.2f})" if c_1x > 0 else "Șansă Dublă 1X"
        p_alt = 78

    return {
        "Status": status,
        "Meci": meci_nume,
        "Ligă": liga_nume,
        "Cota 1": f"{c1:.2f}" if c1 > 0 else "N/A",
        "Cota X": f"{cX:.2f}" if cX > 0 else "N/A",
        "Cota 2": f"{c2:.2f}" if c2 > 0 else "N/A",
        "Cotă >1.5 Goluri": f"{c_over15:.2f}" if c_over15 > 0 else "N/A",
        "Cotă 1X": f"{c_1x:.2f}" if c_1x > 0 else "N/A",
        "Cotă X2": f"{c_x2:.2f}" if c_x2 > 0 else "N/A",
        "Verdict": verdict,
        "🎯 PREDICȚIE BAZĂ": f"{predicție_principala} ({p_principala}%)",
        "🛡️ ALTERNATIVĂ SAFE": f"{alternativa} ({p_alt}%)"
    }

# --- SIDEBAR CONFIG ---
st.sidebar.header("🔑 Configurare API Pro")
api_key_input = st.sidebar.text_input("API-Key (API-Sports):", type="password")
bookmaker_id = st.sidebar.selectbox("Casa de Pariuri Favorită:", [
    ("Toate / Prima Disponibilă", None),
    ("Bet365", 8),
    ("1xBet", 1),
    ("Unibet", 3),
    ("Bwin", 6),
    ("Pinnacle", 4)
], format_func=lambda x: x[0])[1]

# --- FUNCȚIE PRELUARE MULTIPLE PIEȚE DIN API ---
def extrage_toate_cotele_meci(fixture_id, headers, bookmaker_filter=None):
    c1, cX, c2 = 0.0, 0.0, 0.0
    c_over15 = 0.0
    c_1x, c_x2 = 0.0, 0.0

    try:
        url_odds = "https://v3.football.api-sports.io/odds"
        params = {"fixture": fixture_id}
        if bookmaker_filter:
            params["bookmaker"] = bookmaker_filter
            
        res = requests.get(url_odds, headers=headers, params=params, timeout=5)
        if res.status_code == 200:
            data = res.json().get("response", [])
            if data and data[0].get("bookmakers"):
                bookmakers = data[0]["bookmakers"]
                bm = bookmakers[0]
                for bet in bm.get("bets", []):
                    bet_id = bet.get("id")
                    
                    # Bet ID 1: Match Winner (1X2)
                    if bet_id == 1:
                        for val in bet.get("values", []):
                            if val["value"] == "Home":
                                c1 = float(val["odd"])
                            elif val["value"] == "Draw":
                                cX = float(val["odd"])
                            elif val["value"] == "Away":
                                c2 = float(val["odd"])
                                
                    # Bet ID 5: Goals Over/Under
                    elif bet_id == 5:
                        for val in bet.get("values", []):
                            if val["value"] == "Over 1.5":
                                c_over15 = float(val["odd"])
                                
                    # Bet ID 12: Double Chance (1X / X2)
                    elif bet_id == 12:
                        for val in bet.get("values", []):
                            if val["value"] == "Home/Draw":
                                c_1x = float(val["odd"])
                            elif val["value"] == "Draw/Away":
                                c_x2 = float(val["odd"])
    except Exception:
        pass

    return c1, cX, c2, c_over15, c_1x, c_x2

# --- INTERFAȚĂ PRINCIPALĂ ---
tab1, tab2 = st.tabs(["🚀 Căutare Automatizată Meciuri Zilei", "✍️ Introducere Manuală de Rezervă"])

with tab1:
    st.markdown("### 📅 Meciurile Programate")
    data_selectata = st.date_input("Alege Data:", pd.to_datetime("today"))
    data_str = data_selectata.strftime("%Y-%m-%d")
    
    limita_meciuri = st.slider("Număr de meciuri de analizat:", 5, 50, 15)
    
    if st.button("⚡ ÎNCARCĂ MECIURILE & TOATE COTELE LIVE", use_container_width=True):
        if not api_key_input:
            st.warning("⚠️ Introduceți cheia API în meniul din stânga!")
        else:
            headers = {
                'x-rapidapi-host': "v3.football.api-sports.io",
                'x-rapidapi-key': api_key_input
            }
            
            with st.spinner("⏳ Se extrag meciurile și cotele reale pentru 1X2, Over 1.5 și Șansă Dublă..."):
                try:
                    url_fix = "https://v3.football.api-sports.io/fixtures"
                    res_fix = requests.get(url_fix, headers=headers, params={"date": data_str}, timeout=10)
                    meciuri_raw = res_fix.json().get("response", [])
                    
                    if meciuri_raw:
                        st.session_state.bilet_fotbal_premium = []
                        total_de_procesat = min(len(meciuri_raw), limita_meciuri)
                        progres_bar = st.progress(0)
                        
                        for i, match in enumerate(meciuri_raw[:total_de_procesat]):
                            fix_id = match["fixture"]["id"]
                            home_team = match["teams"]["home"]["name"]
                            away_team = match["teams"]["away"]["name"]
                            league_name = match["league"]["name"]
                            status = match["fixture"]["status"]["short"]
                            
                            # Extragere cote reale pentru multiple piețe (1X2, Over 1.5, Double Chance)
                            c1, cX, c2, c_over15, c_1x, c_x2 = extrage_toate_cotele_meci(fix_id, headers, bookmaker_id)
                            
                            res = analizeaza_si_filtreaza_meci(
                                meci_nume=f"{home_team} vs {away_team}",
                                liga_nume=league_name,
                                status=status,
                                c1=c1, cX=cX, c2=c2,
                                c_over15=c_over15,
                                c_1x=c_1x, c_x2=c_x2
                            )
                            st.session_state.bilet_fotbal_premium.append(res)
                            progres_bar.progress((i + 1) / total_de_procesat)
                            
                        st.success(f"✅ Analiză completă finalizată pentru {total_de_procesat} meciuri!")
                        st.rerun()
                    else:
                        st.error("❌ Nu s-au găsit meciuri pentru data selectată sau cheia API este invalidă.")
                except Exception as e:
                    st.error(f"Eroare la conectare: {e}")

with tab2:
    st.markdown("### ✍️ Adaugă un meci manual cu cotele exacte")
    meci_i = st.text_input("Nume Meci:", "Atalanta vs Venezia")
    col1, col2, col3 = st.columns(3)
    with col1:
        c1_i = st.number_input("Cotă 1", min_value=1.00, value=1.54, step=0.01)
        c_1x_i = st.number_input("Cotă 1X", min_value=1.00, value=1.14, step=0.01)
    with col2:
        cX_i = st.number_input("Cotă X", min_value=1.00, value=4.65, step=0.01)
        c_over15_i = st.number_input("Cotă >1.5 Goluri", min_value=1.00, value=1.28, step=0.01)
    with col3:
        c2_i = st.number_input("Cotă 2", min_value=1.00, value=5.60, step=0.01)
        c_x2_i = st.number_input("Cotă X2", min_value=1.00, value=2.40, step=0.01)
    
    if st.button("➕ ADAUGĂ MECI ÎN TABEL"):
        res = analizeaza_si_filtreaza_meci(
            meci_i, "Serie A", "Azi",
            c1_i, cX_i, c2_i,
            c_over15_i, c_1x_i, c_x2_i
        )
        st.session_state.bilet_fotbal_premium.append(res)
        st.toast(f"✅ Adăugat: {meci_i}")

st.write("---")

# --- TABEL REZULTATE ---
if st.session_state.bilet_fotbal_premium:
    df = pd.DataFrame(st.session_state.bilet_fotbal_premium)
    st.markdown("### 📋 Meciuri Analizate (Cote Directe din API)")
    st.dataframe(df, use_container_width=True)
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            "📥 DESCARCĂ REZULTATELE (CSV)",
            data=df.to_csv(index=False).encode('utf-8-sig'),
            file_name="bilet_anti_risc_pro.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_d2:
        if st.button("🗑️ RESETEAZĂ TABELUL", use_container_width=True):
            st.session_state.bilet_fotbal_premium = []
            st.rerun()
