import streamlit as st
import pandas as pd
import io

# Configurare pagină optimizată pentru ecrane de mobil
st.set_page_config(page_title="Baschet VIP Manual", layout="wide", page_icon="🏀")

st.title("🏀 Algoritm Baschet VIP (Ghid Clar)")
st.write("Introdu cotele manual direct de pe telefon. Aplicația îți va spune direct ce pronostic exact să pui pe bilet.")

st.write("---")

# Inițializăm lista în memoria aplicației dacă nu există deja
if "bilet_baschet_manual" not in st.session_state:
    st.session_state.bilet_baschet_manual = []

# --- FORMULAR INTRODUCERE DATE ---
st.subheader("➕ Introdu Meci Nou de Baschet:")

meci_nume = st.text_input("Nume Meci (Trebuie scris cu 'vs', ex: Real Madrid vs Barcelona):", "Valencia vs Joventut Badalona")
liga_nume = st.text_input("Competiție / Ligă (ex: Euroliga):", "Euroliga")

st.write("### 📉 Introduceți Cotele (Doar 1 și 2):")
col1, col2 = st.columns(2)
with col1:
    c1 = st.number_input("Cotă 1 (Gazde)", min_value=1.01, value=1.31, step=0.01, format="%.2f")
with col2:
    c2 = st.number_input("Cotă 2 (Oaspeți)", min_value=1.01, value=3.30, step=0.01, format="%.2f")

st.write("")

# Buton mare pe mobil pentru adăugare în bilet
if st.button("📥 ANALIZEAZĂ ȘI ADAUGĂ ÎN BILET", use_container_width=True):
    # Algoritmul tău matematic personalizat pentru Baschet
    if c1 <= 1.65:
        verdict = "🟩 FAVORIT CLAR"
        safe = "Câștigător Meci"
        medium = "Victorie la Handicap"
        risk = "Peste prag puncte total meci"
        cota_alasa = c1
    elif 1.65 < c1 <= 2.30:
        verdict = "🟨 MECI ECHILIBRAT"
        safe = "Total puncte mediu (Sigur)"
        medium = "Victorie în prelungiri (Oricine)"
        risk = "Scor strâns / Diferență sub 5 puncte"
        cota_alasa = 1.40 # Estimare medie pentru total puncte safe
    else:
        verdict = "🟥 OUTSIDER / HAZARD"
        safe = "Handicap Puncte în plus (+)"
        medium = "Victorie Directă Oaspeți"
        risk = "Surpriză mare (Victorie la handicap oaspeți)"
        cota_alasa = c2

    # Separăm numele pentru a personaliza textele în tabel la fel ca în API
    if " vs " in meci_nume:
        gazde, oaspeti = meci_nume.split(" vs ", 1)
        # Recomandarea directă tradusă pe înțelesul oricui
        if c1 <= 1.65:
            recomandare_clara = f"Victorie directă {gazde} (Câștigător Meci)"
        elif c1 > 2.30:
            recomandare_clara = f"Victorie directă {oaspeti} (Câștigător Meci)"
        else:
            recomandare_clara = "Total Puncte - Sub/Peste limita standard de mijloc"
            
        safe = f"{safe}: {gazde}" if c1 <= 1.65 else (f"{safe}: {oaspeti}" if c1 > 2.30 else safe)
        if c1 <= 1.65: medium = f"{medium} ({gazde})"
        if c1 > 2.30: medium = f"{medium}: {oaspeti}"
    else:
        recomandare_clara = "Victorie Favorit (Verifică cotele)"

    # Salvăm datele procesate cu Cota X forțată la 0
    st.session_state.bilet_baschet_manual.append({
        "Meci": meci_nume,
        "Cota 1": c1,
        "Cota X": 0,  
        "Cota 2": c2,
        "Verdict Risc": verdict,
        "🛡️ Varianta Safe": safe,
        "⚡ Varianta Medium": medium,
        "🔥 Varianta Risk": risk,
        "Prono_Clar": recomandare_clara,
        "Cota_Jucata": cota_alasa
    })
    st.success(f"✅ Meciul '{meci_nume}' a fost salvat și adăugat la ghid!")

st.write("---")

# --- AFIȘARE GHID DIRECT ȘI COMANDE PENTRU PARIURI ---
if st.session_state.bilet_baschet_manual:
    
    # ==========================================
    # ZONA NOUĂ: TEXT CLAR PENTRU BILET
    # ==========================================
    st.markdown("## 📋 BILETUL VIP GENERAT AUTOMAT")
    st.info("Deschide aplicația de pariuri și pune exact ce scrie mai jos:")
    
    cota_totala = 1.0
    for idx, m in enumerate(st.session_state.bilet_baschet_manual):
        cota_totala *= m["Cota_Jucata"]
        st.markdown(f"**{idx + 1}. {m['Meci']}**")
        st.markdown(f"👉 În agenție selectezi: `{m['Prono_Clar']}` | Cotă: **{m['Cota_Jucata']:.2f}**")
        st.write("")
        
    st.markdown(f"### 📈 Cotă Totală Bilet: `{cota_totala:.2f}`")
    
    # Simulator de mize integrat direct în recomandare
    miza_ghid = st.number_input("💰 Introdu miza pe care vrei să o pui (RON):", min_value=5, value=50, step=5)
    st.markdown(f"💵 **Câștig Potențial estimat: `{(cota_totala * miza_ghid):.2f} RON`**")
    
    # Avertisment automat în funcție de lungimea biletului
    if len(st.session_state.bilet_baschet_manual) > 4:
        st.error("⚠️ ATENȚIE: Ai pus mai mult de 4 meciuri pe bilet! Matematic, riscul a crescut foarte mult. Recomandarea mea este să spargi biletul în două variante mai scurte, punând jumătate din miză pe fiecare.")
    else:
        st.success("🟩 Bilet stabil! Numărul de meciuri este optim pentru o investiție calculată.")
        
    st.write("---")
    
    # --- Zona tehnică de tabele și export (rămâne neschimbată) ---
    st.subheader("📊 Tabelul tehnic (pentru Excel):")
    df = pd.DataFrame(st.session_state.bilet_baschet_manual)
    # Ascundem coloanele ajutătoare din interfață să nu încurce ecranul de mobil
    df_afisare = df.drop(columns=["Prono_Clar", "Cota_Jucata"])
    st.dataframe(df_afisare, use_container_width=True)
    
    if st.button("🗑️ Golește tot biletul / Reset", use_container_width=False):
        st.session_state.bilet_baschet_manual = []
        st.rerun()

    # Generare Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_afisare.to_excel(writer, index=False, sheet_name='Baschet Manual')
    date_excel = buffer.getvalue()
    
    st.download_button(
        label="🟢 DESCARCĂ FIȘIERUL EXCEL (.xlsx)",
        data=date_excel,
        file_name="Predictii_Baschet_Manual.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
else:
    st.info("Biletul este gol. Introdu un meci și cotele de mai sus pentru ca algoritmul să îți scrie pronosticul clar.")
