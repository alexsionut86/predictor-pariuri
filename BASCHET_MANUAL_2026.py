import streamlit as st
import pandas as pd
import io

# Configurare pagină optimizată pentru ecrane de mobil
st.set_page_config(page_title="Baschet VIP Manual", layout="wide", page_icon="🏀")

st.title("🏀 Algoritm Baschet VIP (Manual)")
st.write("Introdu cotele manual direct de pe telefon. Aplicația va seta Cota X la 0 și va genera instant fișierul Excel.")

st.write("---")

# Inițializăm lista în memoria aplicației dacă nu există deja
if "bilet_baschet_manual" not in st.session_state:
    st.session_state.bilet_baschet_manual = []

# --- FORMULAR INTRODUCERE DATE ---
st.subheader("➕ Introdu Meci Nou de Baschet:")

meci_nume = st.text_input("Nume Meci (ex: Real Madrid vs Barcelona):", "FCSB vs Rapid")
liga_nume = st.text_input("Competiție / Ligă (ex: Euroliga):", "Euroliga")

st.write("### 📉 Introduceți Cotele (Doar 1 și 2):")
col1, col2 = st.columns(2)
with col1:
    c1 = st.number_input("Cotă 1 (Gazde / Favorit)", min_value=1.01, value=1.50, step=0.01, format="%.2f")
with col2:
    c2 = st.number_input("Cotă 2 (Oaspeți / Outsider)", min_value=1.01, value=2.60, step=0.01, format="%.2f")

st.write("")

# Buton mare pe mobil pentru adăugare în bilet
if st.button("📥 ANALIZEAZĂ ȘI SALVEAZĂ ÎN EXCEL", use_container_width=True):
    # Algoritmul tău matematic personalizat pentru Baschet
    if c1 <= 1.65:
        verdict = "🟩 FAVORIT CLAR"
        safe = "Câștigător Meci"
        medium = "Victorie la Handicap"
        risk = "Peste prag puncte total meci"
    elif 1.65 < c1 <= 2.30:
        verdict = "🟨 MECI ECHILIBRAT"
        safe = "Total puncte mediu (Sigur)"
        medium = "Victorie în prelungiri (Oricine)"
        risk = "Scor strâns / Diferență sub 5 puncte"
    else:
        verdict = "🟥 OUTSIDER / HAZARD"
        safe = "Handicap Puncte în plus (+)"
        medium = "Victorie Directă Oaspeți"
        risk = "Surpriză mare (Victorie la handicap oaspeți)"

    # Separăm numele pentru a personaliza textele în tabel la fel ca în API
    if " vs " in meci_nume:
        gazde, oaspeti = meci_nume.split(" vs ", 1)
        safe = f"{safe}: {gazde}" if c1 <= 1.65 else (f"{safe}: {oaspeti}" if c1 > 2.30 else safe)
        if c1 <= 1.65: medium = f"{medium} ({gazde})"
        if c1 > 2.30: medium = f"{medium}: {oaspeti}"

    # Salvăm datele procesate cu Cota X forțată la 0
    st.session_state.bilet_baschet_manual.append({
        "Meci": meci_nume,
        "Cota 1": c1,
        "Cota X": 0,  # Regula ta de aur pentru baschet
        "Cota 2": c2,
        "Verdict Risc": verdict,
        "🛡️ Varianta Safe": safe,
        "⚡ Varianta Medium": medium,
        "🔥 Varianta Risk": risk
    })
    st.success(f"✅ Meciul '{meci_nume}' a fost salvat cu succes în listă!")

st.write("---")

# --- TABELUL ȘI DESCARCAREA EXCELULUI ---
if st.session_state.bilet_baschet_manual:
    st.subheader("📊 Tabelul tău curent:")
    
    df = pd.DataFrame(st.session_state.bilet_baschet_manual)
    st.dataframe(df, use_container_width=True)
    
    if st.button("🗑️ Golește tot tabelul", use_container_width=False):
        st.session_state.bilet_baschet_manual = []
        st.rerun()

    st.write("")
    
    # Generare Excel direct în memoria telefonului
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Baschet Manual')
    date_excel = buffer.getvalue()
    
    # Butonul mare verde de download
    st.download_button(
        label="🟢 DESCARCĂ FIȘIERUL EXCEL (.xlsx)",
        data=date_excel,
        file_name="Predictii_Baschet_Manual.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
else:
    st.info("Lista este goală. Introdu cotele de mai sus din agenție pentru a genera primul pronostic și fișierul Excel.")
