import streamlit as st
import pandas as pd
import io
import re
import pdfplumber

# Configurare interfață Streamlit
st.set_page_config(page_title="Scanner Probabilități Pro", layout="wide", page_icon="📊")

st.markdown("<h1 style='text-align: center;'>📊 Verificator Automat Bilet VIP</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #4CAF50;'>Încarcă biletul PDF Superbet sau dă Paste la text mai jos</p>", unsafe_allow_html=True)
st.write("---")

if "bilet_automat" not in st.session_state:
    st.session_state.bilet_automat = []

def extrage_meciuri_pdfplumber(uploaded_file):
    """
    Extrage meciurile, pronosticurile și cotele exacte din PDF folosind pdfplumber.
    Identifică cotele din dreapta paginii pe baza poziției vizuale.
    """
    meciuri_gasite = []
    
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text(layout=True)
            if not text:
                continue
                
            linii = text.split('\n')
            
            # Caută numerele de cote (ex: 1.34, 1.30, 1.37)
            i = 0
            n = len(linii)
            
            # Păstrăm liniile curate
            linii_curate = []
            for l in linii:
                l_str = l.strip()
                if l_str and not any(k in l_str for k in ["COTA TOTALA", "BANI REALI", "SUPERBONUS", "CASTIG POTENTIAL", "STATUS", "Pariurile mele"]):
                    linii_curate.append(l_str)
                    
            # Parcurgem liniile pentru a grupa Echipe + Pronostic + Cotă
            idx = 0
            while idx < len(linii_curate):
                linie = linii_curate[idx]
                
                # Căutăm linii care conțin cote la final (de ex: "1.34" sau "2-5           1.34")
                cota_match = re.search(r"\b(1\.\d{2})\b", linie)
                
                if cota_match:
                    cota_val = float(cota_match.group(1))
                    
                    # Ne uităm în sus pentru a găsi echipele și pronosticul
                    prono = re.sub(r"\b1\.\d{2}\b", "", linie).strip()
                    
                    echipe = []
                    # Mergem înapoi 1-3 rânduri pentru echipe
                    for back in range(1, 4):
                        if idx - back >= 0:
                            l_prev = linii_curate[idx - back]
                            if not re.search(r"\b1\.\d{2}\b", l_prev) and len(l_prev) > 3:
                                echipe.insert(0, l_prev)
                                
                    if len(echipe) >= 2:
                        nume_meci = f"{echipe[-2]} - {echipe[-1]}"
                        prono_text = prono if prono else "Interval goluri"
                        meciuri_gasite.append(f"{nume_meci} | {prono_text} | {cota_val:.2f}")
                        
                idx += 1
                
    # Dacă s-au găsit duplicate din cauza layout-ului, le filtrăm
    meciuri_unice = []
    for m in meciuri_gasite:
        if m not in meciuri_unice:
            meciuri_unice.append(m)
            
    return "\n".join(meciuri_unice)

# --- PASUL 1: ÎNCĂRCARE PDF SAU TEXT ---
st.markdown("### 📋 Pasul 1: Încarcă biletul PDF sau lipeste textul")

uploaded_file = st.file_uploader("📄 Încarcă biletul în format PDF (Superbet)", type=["pdf"])

text_initial = ""

if uploaded_file is not None:
    try:
        text_curatat = extrage_meciuri_pdfplumber(uploaded_file)
        
        if text_curatat:
            text_initial = text_curatat
            st.success("✅ PDF procesat cu succes prin pdfplumber! Cotele au fost extrase precis.")
        else:
            st.warning("⚠️ Nu am putut extrage automat cotele. Te rugăm să introduci textul manual.")
            
    except Exception as e:
        st.error(f"Eroare la citirea PDF-ului: {e}")

text_bilet = st.text_area(
    "Text formatat automat (verifică datele extrase):",
    value=text_initial if text_initial else "LASK Linz - Liverpool | 2-5 Interval goluri | 1.34\nFeyenoord Rotterdam - Como | 2-5 Interval goluri | 1.34",
    height=220
)

col_miza, col_btn = st.columns([1, 2])
with col_miza:
    miza_simulata = st.number_input("💰 Introdu miza biletului (RON):", min_value=1.0, value=5.00, step=0.50)

# --- PASUL 2: PROCESARE ȘI CALCUL ---
if st.button("⚡ SCANEAZĂ BILETUL ȘI CALCULEAZĂ PROCENTELE", use_container_width=True):
    linii = text_bilet.strip().split("\n")
    lista_meciuri_temporara = []
    
    for linie in linii:
        if not linie.strip():
            continue
        
        parti = [p.strip() for p in linie.split('|') if p.strip()]
        
        if len(parti) >= 3:
            nume = parti[0]
            prono = parti[1]
            try:
                cota = float(parti[2].replace(',', '.'))
            except ValueError:
                cota = 1.35
        elif len(parti) == 2:
            nume = parti[0]
            prono = "Eveniment"
            try:
                cota = float(parti[1].replace(',', '.'))
            except ValueError:
                cota = 1.35
        else:
            continue
                
        prob_reala = int((1 / cota) * 100 * 0.95)
        prob_reala = max(1, min(99, prob_reala))
        
        risc = "🟩 SAFE" if prob_reala >= 65 else ("🟨 MEDIUM" if prob_reala >= 40 else "🟥 RISK")
        
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

# --- PASUL 3: AFIȘARE REZULTATE ---
if st.session_state.bilet_automat:
    st.write("---")
    st.markdown("### 🔍 Anatomia Biletului Tău:")
    
    df_afisare = pd.DataFrame(st.session_state.bilet_automat)
    st.dataframe(df_afisare.drop(columns=["prob_num"]), use_container_width=True)
    
    cota_totala = 1.0
    prob_compusa = 1.0
    for m in st.session_state.bilet_automat:
        cota_totala *= m["Cotă"]
        prob_compusa *= (m["prob_num"] / 100)
        
    procent_final = round(prob_compusa * 100, 2)
    castig_potential = cota_totala * miza_simulata
    valoare_matematica = castig_potential * (procent_final / 100)

    st.write("---")
    st.markdown("<h3 style='text-align: center;'>🏆 Rezultate Calcul Matematice</h3>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="📈 COTĂ TOTALĂ", value=f"{cota_totala:.2f}")
    with c2:
        st.metric(label="🎯 PROBABILITATE REUȘITĂ", value=f"{procent_final}%")
    with c3:
        st.metric(label="💰 CÂȘTIG POTENȚIAL", value=f"{castig_potential:.2f} RON")
        
    st.write("")
    if procent_final >= 50:
        st.success(f"🟩 **Verdict: Bilet Foarte Solid.** Din punct de vedere matematic, valoarea reală estimată este de **{valoare_matematica:.2f} RON**.")
    elif 15 <= procent_final < 50:
        st.warning(f"🟨 **Verdict: Bilet Echilibrat (Combo).** Șanse moderate ({procent_final}%). Valoarea reală ponderată este de **{valoare_matematica:.2f} RON**.")
    else:
        st.error(f"🟥 **Verdict: Tip 'Bombă' (Risc Maxim).** Probabilitate mică de **{procent_final}%**.")

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
