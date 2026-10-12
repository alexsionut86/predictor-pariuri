import streamlit as st
import pandas as pd
import requests

# --- CONFIGURARE PAGINĂ ---
st.set_page_config(page_title="Fotbal VIP Pro - Anti-Risc Pro API", layout="wide", page_icon="⚽")

if "bilet_fotbal_premium" not in st.session_state:
    st.session_state["bilet_fotbal_premium"] = []

# --- TITLU ȘI STRATEGIE ---
st.markdown("<h1 style='text-align: center;'>⚽ Algoritm VIP Pro (API Pro Multi-Markets)</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Cote Reale direct de la Superbet, Betano, Bet365, Unibet, etc.</p>", unsafe_allow_html=True)

st.info("""
💡 **STRATEGIE ANTI-RISC PRO (2 MECIURI PER BILET):**
* Target Bilet: **Cota Finală ~2.00**
* Piețe Analizate Direct: **Șansă Dublă (1X / X2)** & **Peste 1.5 Goluri Marcate**.
""")
st.write("---")

# --- ALGORITM MATEMATIC DE PREDICTOR ---
def analizeaza_si_filtreaza_meci(meci_nume, liga_nume, status, c1, cX, c2, c_over15, c_1x, c_x2):
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
    ("Superbet", 29),
    ("Betano / Stoiximan", 23),
    ("Bet365", 8),
    ("Unibet", 3),
    ("1xBet", 1),
    ("Bwin", 6),
    ("Pinnacle", 4),
    ("888Sport", 18)
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
        if res.status_code ==
