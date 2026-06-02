import streamlit as st
import pandas as pd
import io

# Configurare pagină optimizată pentru ecrane de mobil
st.set_page_config(page_title="Tenis VIP Manual", layout="wide", page_icon="🎾")

st.title("🎾 Algoritm Tenis VIP (Manual)")
st.write("Introdu cotele meciurilor de tenis direct de pe telefon. Aplicația va seta Cota X la 0 și va genera fișierul Excel.")

st.write("---")

# Inițializăm lista în memoria aplicației dacă nu există deja
if "bilet_tenis_manual" not in st.session_state:
    st.session_state.bilet_tenis_manual = []

# --- FORMULAR INTRODUCERE DATE ---
st.subheader("➕ Introdu Meci Nou de Tenis:")

meci_nume = st.text_input("Nume Jucători (ex: Alcaraz vs Sinner):", "Alcaraz vs Sinner")
turneu_nume = st.text_input("Turneu / Competiție (ex: Roland Garros):", "Roland Garros")

st.write("### 📉 Introduceți Cotele Jucătorilor:")
col1, col2 = st.columns(2)
with col1:
    c1 = st.number_input("Cotă Jucător 1 (Favorit)", min_value=1.01, value=1.40, step=0.01, format="%.2f")
with col2:
    c2 = st.number_input("Cotă Jucător 2 (Outsider)", min_value=1.01, value=3.00, step=0.01, format="%.2f")

st.write("")

# Buton mare pe mobil pentru adăugare în bilet
if st.button("📥 ANALIZEAZĂ ȘI SALVEAZĂ ÎN EXCEL", use_container_width=True):
    # Algoritmul tău matematic adaptat pentru Tenis (bazat pe Cota 1)
    if c1 <= 1.45:
        verdict = "🟩 FAVORIT CLAR"
        safe = "Câștigător Meci"
        medium = "Câștigă Minim 1 Set (Favorit)"
        risk = "Scor Corect 2-0 / Handicap Game-uri (-)"
    elif 1.45 < c1 <= 2.20:
        verdict = "🟨 MECI ECHILIBRAT"
        safe = "Peste 19.5 Game-uri în meci"
        medium = "Jucătorul 2 câștigă minim un set"
        risk = "Meci cu Set decisiv (Peste 2.5/4.5 Seturi)"
    else:
        verdict = "🟥 OUTSIDER / HAZARD"
        safe = "Handicap Game-uri în plus (+)"
        medium = "Victorie Directă Outsider"
        risk = "Surpriză Mare (Scor corect în favoarea outsiderului)"

    # Personalizăm recomandările cu numele jucătorilor dacă ai scris textul cu " vs "
    if " vs " in meci_nume:
        jucator1, jucator2 = meci_nume.split(" vs ", 1)
        if c1 <= 1.45:
            safe = f"{safe}: {jucator1}"
            medium = f"Minim 1 Set: {jucator1}"
            risk = f"Scor Corect 2-0: {jucator1}"
        elif c1 > 2.20:
            safe = f"Handicap în plus (+): {jucator2}"
            medium = f"Victorie Directă: {jucator2}"

    # Salvăm datele procesate cu Cota X forțată la 0
    st.session_state.bilet_tenis_manual.append({
        "Meci": meci_nume,
        "Turneu/Competiție": turneu_nume,
        "Cota 1": c1,
        "Cota X": 0,  # Regula de structură pentru fișierele tale Excel (fără egal în tenis)
        "Cota 2": c2,
        "Verdict Risc": verdict,
        "🛡️ Varianta Safe": safe,
        "⚡ Varianta Medium": medium,
        "🔥 Varianta Risk": risk
    })
    st.success(f"✅ Meciul '{meci_nume}' a fost salvat cu succes în lista de tenis!")

st.write("---")

# --- TABELUL ȘI DESCARCAREA EXCELULUI ---
if st.session_state.bilet_tenis_manual:
    st.subheader("📊 Meciurile tale salvate (Tabel Tenis):")
    
    df = pd.DataFrame(st.session_state.bilet_tenis_manual)
    st.dataframe(df, use_container_width=True)
    
    if st.button("🗑️ Golește tot tabelul", use_container_width=False):
        st.session_state.bilet_tenis_manual = []
        st.rerun()

    st.write("")
    
    # Generare Excel direct în memoria telefonului
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Tenis Manual')
    date_excel = buffer.getvalue()
    
    # Butonul mare verde de download pe ecranul mobilului
    st.download_button(
        label="🟢 DESCARCĂ RECOMANDĂRILE TENIS ÎN EXCEL (.xlsx)",
        data=date_excel,
        file_name="Predictii_Tenis_Manual.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
else:
    st.info("Lista este goală. Introdu cotele de la turnee din agenție pentru a genera pronosticurile și fișierul Excel.")