import streamlit as st
import pandas as pd
import io
import re

# Configurare interfață mobil premium
st.set_page_config(page_title="Scanner Probabilități Pro", layout="wide", page_icon="📊")

st.markdown("<h1 style='text-align: center;'>📊 Verificator Automat Bilet VIP</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #4CAF50;'>Metoda Rapidă: Copiază biletul din agenție și dă Paste mai jos</p>", unsafe_allow_html=True)
st.write("---")

# Structură stocare meciuri
if "bilet_automat" not in st.session_state:
    st.session_state.bilet_automat = []

# --- CALCULATOR RAPID PRIN COPY-PASTE ---
st.markdown("### 📋 Pasul 1: Pune biletul copiat (sau scrie meciurile sub formă de text)")
text_bilet = st.text_area(
    "Exemplu format recunoscut: Nume Meci | Pronostic | Cotă (Fiecare meci pe un rând nou)",
    value="Olanda - Uzbekistan | Peste 1.5 | 1.17\nSri Lanka - Bhutan | PsF X | 1.37\nFranta - Irlanda de Nord | Peste 2.5 | 1.41",
    height=150
)

col_miza, col_btn = st.columns([1, 2])
with col_miza:
    miza_simulata = st.number_input("💰 Introdu miza biletului (RON):", min_value=1.0, value=10.0, step=1.0)

# Buton Procesare Text
if st.button("⚡ SCANEAZĂ BILETUL ȘI CALCULEAZĂ PROCENTELE", use_container_width=True):
    linii = text_bilet.strip().split("\n")
    lista_meciuri_temporara = []
    
    for linie in linii:
        if not linie.strip():
            continue
        
        # Încercăm să despărțim linia după caractere comune (|, camă, tab sau spații mari)
        parti = [p.strip() for p in re.split(r'[|,\t]', linie) if p.strip()]
        
        # Dacă linia are formatul standard: Meci | Pronostic | Cotă
        if len(parti) >= 3:
            nume = parti[0]
            prono = parti[1]
            try:
                # Extragem ultima parte ca fiind cota
                cota = float(parti[2])
            except ValueError:
                cota = 1.50
        # Dacă a pus doar Meci și Cotă (ex: FCSB - CFR 1.70)
        elif len(parti) == 2:
            nume = parti[0]
            prono = "Nespecificat"
            try:
                cota = float(parti[1])
            except ValueError:
                cota = 1.50
        else:
            # Încercăm să căutăm o cotă (număr zecimal) la finalul liniei prin regex
            cota_match = re.search(r"[-+]?\d*\.\d+|\d+", linie)
            if cota_match:
                cota = float(cota_match.group())
                nume = linie.replace(cota_match.group(), "").strip()
                prono = "Eveniment"
            else:
                continue
                
        # Calcul probabilitate matematică ajustată (fără marja casei)
        prob_reala = int((1 / cota) * 100 * 0.95)
        prob_reala = max(1, min(99, prob_reala))
        
        if prob_reala >= 65: risc = "🟩 SAFE"
        elif 40 <= prob_reala < 65: risc = "🟨 MEDIUM"
        else: risc = "🟥 RISK"
        
        lista_meciuri_temporara.append({
            "Meci / Eveniment": nume,
            "Pronostic": prono,
            "Cotă": cota,
            "Probabilitate": f"{prob_reala}%",
            "Nivel Risc": risc,
            "prob_num": prob_reala
        })
        
    st.session_state.bilet_automat = lista_meciuri_temporara
    st.success(f"✅ Am identificat și procesat {len(lista_meciuri_temporara)} meciuri de pe bilet!")

# --- AFIȘARE REZULTATE ȘI BILET FINAL ---
if st.session_state.bilet_automat:
    st.write("---")
    st.markdown("### 🔍 Anatomia Biletului Tău:")
    
    df_afisare = pd.DataFrame(st.session_state.bilet_automat)
    st.dataframe(df_afisare.drop(columns=["prob_num"]), use_container_width=True)
    
    # Calcul valori agregate
    cota_totala = 1.0
    prob_compusa = 1.0
    for m in st.session_state.bilet_automat:
        cota_totala *= m["Cotă"]
        prob_compusa *= (m["prob_num"] / 100)
        
    procent_final = round(prob_compusa * 100, 2)
    castig_potential = cota_totala * miza_simulata
    # Valoarea de investiție (EV - Expected Value)
    valoare_matematica = castig_potential * (procent_final / 100)

    # --- PANOU REZULTATE FINALE ---
    st.write("---")
    st.markdown("<h3 style='text-align: center;'>🏆 Rezultate Calcul Matematice</h3>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="📈 COTĂ TOTALĂ", value=f"{cota_totala:.2f}")
    with c2:
        st.metric(label="🎯 PROBABILITATE REUȘITĂ", value=f"{procent_final}%")
    with c3:
        st.metric(label="💰 CÂȘTIG POTENȚIAL", value=f"{castig_potential:.2f} RON")
        
    # Caseta de Verdict Inteligent bazată pe miza ta
    st.write("")
    if procent_final >= 50:
        st.success(f"🟩 **Verdict: Bilet Foarte Solid.** Din punct de vedere matematic, valoarea reală estimată a biletului tău este de **{valoare_matematica:.2f} RON**. Șanse mari de reușită.")
    elif 15 <= procent_final < 50:
        st.warning(f"🟨 **Verdict: Bilet Echilibrat (Combo).** Șanse moderate ({procent_final}%). Valoarea reală ponderată este de **{valoare_matematica:.2f} RON**. Nu urca miza prea sus!")
    else:
        st.error(f"🟥 **Verdict: Tip 'Bombă' (Risc Maxim).** Probabilitate mică de **{procent_final}%**. Valoarea matematică reală scade la doar **{valoare_matematica:.2f} RON**. Recomandat să lași miza la un nivel minim de distracție.")

    # Descărcare Raport Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_afisare.drop(columns=["prob_num"]).to_excel(writer, index=False, sheet_name='Analiza Procente')
    excel_data = buffer.getvalue()
    
    st.write("")
    st.download_button(
        label="🟢 EXPORTĂ BILETUL ÎN EXCEL",
        data=excel_data,
        file_name="Analiza_VIP_Bilet.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )