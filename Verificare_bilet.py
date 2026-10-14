import streamlit as st
import pandas as pd
import io
import re
from pypdf import PdfReader

# Configurare interfață mobil premium
st.set_page_config(page_title="Scanner Probabilități Pro", layout="wide", page_icon="📊")

st.markdown("<h1 style='text-align: center;'>📊 Verificator Automat Bilet VIP</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #4CAF50;'>Incarcă biletul PDF sau introdu textul biletului</p>", unsafe_allow_html=True)
st.write("---")

if "bilet_automat" not in st.session_state:
    st.session_state.bilet_automat = []

def parseaza_pdf_superbet(text_raw):
    """
    Transformă textul brut și împrăștiat din PDF-ul Superbet în format curat:
    Echipa1 - Echipa2 | Pronostic | Cota
    """
    linii = [l.strip() for l in text_raw.split("\n") if l.strip()]
    linii_curate = []
    
    # Încercăm să grupăm blocurile de meciuri
    # Într-un PDF Superbet, un meci are: Echipa 1, Echipa 2, Cota, Opțiunile de pariu
    i = 0
    n = len(linii)
    
    while i < n:
        # Căutăm o cotă (ex: 1.45)
        cota_match = re.match(r"^(\d+\.\d{2})$", linii[i])
        
        # Dacă am găsit o cotă, analizăm rândurile din jur pentru meci și pronostic
        if cota_match:
            cota = cota_match.group(1)
            
            # Căutăm în sus echipele (de obicei sunt cu 2-5 rânduri mai sus)
            echipe = ""
            pronosticuri = []
            
            # Mergem înapoi pentru a găsi numele echipelor
            idx_sus = i - 1
            candidați_echipe = []
            while idx_sus >= 0 and len(candidați_echipe) < 2:
                txt = linii[idx_sus]
                # Excludem cuvinte cheie de sistem
                if not any(k in txt for k in ["COT", "BAN", "ST A TUS", "A ctiv", "BET BUILDER", "R1", "0", "1", "2"]):
                    if len(txt) > 2 and not txt.isdigit():
                        candidați_echipe.insert(0, txt)
                idx_sus -= 1
            
            if len(candidați_echipe) >= 2:
                echipe = f"{candidați_echipe[0]} - {candidați_echipe[1]}"
            
            # Mergem înainte pentru a colecta opțiunile de pariere (ex: "2-5", "GG sau Peste 2.5 goluri")
            idx_jos = i + 1
            while idx_jos < n and idx_jos < i + 6:
                txt = linii[idx_jos]
                if "BET BUILDER" in txt or "Repriza" in txt or "International" in txt or "UEF" in txt:
                    break
                if txt not in ["0", "Da", "Nu"] and not re.match(r"^\d+$", txt):
                    pronosticuri.append(txt)
                idx_jos += 1
            
            prono_str = " & ".join(pronosticuri) if pronosticuri else "Pariu Combo"
            
            if echipe:
                linii_curate.append(f"{echipe} | {prono_str} | {cota}")
                
        i += 1
        
    if linii_curate:
        # Eliminăm duplicatele păstrând ordinea
        rezultat_unic = []
        for l in linii_curate:
            if l not in rezultat_unic:
                rezultat_unic.append(l)
        return "\n".join(rezultat_unic)
    
    return ""

# --- PASUL 1: ÎNCĂRCARE PDF SAU INTRODUCERE TEXT ---
st.markdown("### 📋 Pasul 1: Incarcă biletul PDF sau lipeste textul")

uploaded_file = st.file_uploader("📄 Încarcă biletul în format PDF (Superbet)", type=["pdf"])

text_initial = ""

if uploaded_file is not None:
    try:
        reader = PdfReader(uploaded_file)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text() + "\n"
        
        # Încercăm conversia automată în format curat
        text_curatat = parseaza_pdf_superbet(pdf_text)
        
        if text_curatat:
            text_initial = text_curatat
            st.success("✅ Biletul din PDF a fost extras și formatat automat!")
        else:
            text_initial = pdf_text
            st.warning("⚠️ Am citit PDF-ul, dar te rugăm să verifici formatarea textului mai jos.")
            
    except Exception as e:
        st.error(f"Eroare la citirea PDF-ului: {e}")

text_bilet = st.text_area(
    "Text formatat automat (îl poți edita dacă dorești):",
    value=text_initial if text_initial else "Slovan Bratislava U19 - Stuttgart U19 | GG sau P2.5 & 2-5 goluri | 1.45\nAS Roma U19 - Real Madrid U19 | GG sau P2.5 & 2-5 goluri | 1.45",
    height=150
)

col_miza, col_btn = st.columns([1, 2])
with col_miza:
    miza_simulata = st.number_input("💰 Introdu miza biletului (RON):", min_value=1.0, value=8.50, step=0.5)

# Buton Procesare
if st.button("⚡ SCANEAZĂ BILETUL ȘI CALCULEAZĂ PROCENTELE", use_container_width=True):
    linii = text_bilet.strip().split("\n")
    lista_meciuri_temporara = []
    
    for linie in linii:
        if not linie.strip():
            continue
        
        parti = [p.strip() for p in re.split(r'[|]', linie) if p.strip()]
        
        if len(parti) >= 3:
            nume = parti[0]
            prono = parti[1]
            try:
                cota = float(parti[2].replace(',', '.'))
            except ValueError:
                cota = 1.50
        elif len(parti) == 2:
            nume = parti[0]
            prono = "Nespecificat"
            try:
                cota = float(parti[1].replace(',', '.'))
            except ValueError:
                cota = 1.50
        else:
            cota_match = re.search(r"[-+]?\d*[.,]\d+|\d+", linie)
            if cota_match:
                cota_str = cota_match.group().replace(',', '.')
                cota = float(cota_str)
                nume = linie.replace(cota_match.group(), "").strip()
                prono = "Eveniment"
            else:
                continue
                
        # Calcul probabilitate matematică ajustată
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

# --- AFIȘARE REZULTATE ---
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
