import streamlit as st
import pandas as pd
import io
import re
from pypdf import PdfReader

# Configurare interfață
st.set_page_config(page_title="Scanner Probabilități Pro", layout="wide", page_icon="📊")

st.markdown("<h1 style='text-align: center;'>📊 Verificator Automat Bilet VIP</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #4CAF50;'>Incarcă biletul PDF (Superbet / eFortuna / altele) sau dă Paste la text</p>", unsafe_allow_html=True)
st.write("---")

if "bilet_automat" not in st.session_state:
    st.session_state.bilet_automat = []

def parseaza_text_superbet(text):
    """ Parser specializat pentru structura de text extrasă din PDF-urile Superbet """
    meciuri = []
    
    # Încercăm să extragem miza din textul PDF-ului
    miza_gasita = None
    miza_match = re.search(r"B\s*A\s*NI\s*RE\s*A\s*LI\s*([\d[.,]+)\s*RON", text, re.IGNORECASE)
    if not miza_match:
        miza_match = re.search(r"Miza[:\s]+([\d[.,]+)", text, re.IGNORECASE)
    if miza_match:
        try:
            miza_gasita = float(miza_match.group(1).replace(',', '.'))
        except ValueError:
            pass

    # Împărțim textul după blocurile de Bet Builder sau linii de demarcare
    linii = [l.strip() for l in text.split('\n') if l.strip()]
    
    # Căutăm secțiunile dintre meciuri
    i = 0
    while i < len(linii):
        # Un meci în Superbet începe de obicei după Status / Bet Builder
        # Căutăm tiparul de cota (ex: 1.45 sau 2.10) urmat de tipul de pariu sau echipe
        if i + 1 < len(linii) and ("U19" in linii[i] or " vs " in linii[i] or "-" in linii[i] or "BET BUILDER" in linii[i]):
            # Identificare nume meci (2 rânduri consecutive de echipe)
            if i + 1 < len(linii) and not re.search(r'^\d+(\.\d+)?$', linii[i]):
                echipe = f"{linii[i]} vs {linii[i+1]}" if "BET BUILDER" not in linii[i] else ""
        i += 1

    # Daca structura e complexa (Bet Builder), extras meciurile cu un Regex avansat pe tot textul:
    # Căutăm blocuri: Echipă 1 \n Echipă 2 \n ... Cotă
    pattern = r"([A-Za-z0-9\s]+U19|[A-Za-z0-9\s]{3,20})\n([A-Za-z0-9\s]+U19|[A-Za-z0-9\s]{3,20})\n(?:.*?\n)*?([\d]\.[\d]{2})"
    matches = re.findall(pattern, text)
    
    for match in matches:
        e1, e2, cota = match
        if "COT" not in e1 and "BAN" not in e1:
            meciuri.append({
                "nume": f"{e1.strip()} - {e2.strip()}",
                "prono": "Bet Builder / Combo",
                "cota": float(cota)
            })

    return meciuri, miza_gasita

# --- INTERFAȚĂ ---
uploaded_file = st.file_uploader("📄 Încarcă biletul în format PDF", type=["pdf"])

text_bilet = ""
miza_extrasa = 10.0

if uploaded_file is not None:
    try:
        reader = PdfReader(uploaded_file)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text() + "\n"
        text_bilet = pdf_text
        st.success("✅ PDF încărcat cu succes!")
    except Exception as e:
        st.error(f"Eroare la citirea PDF-ului: {e}")

text_bilet = st.text_area(
    "Text extras din bilet (poți edita manual dacă este nevoie):",
    value=text_bilet,
    height=200
)

col_miza, col_btn = st.columns([1, 2])
with col_miza:
    miza_simulata = st.number_input("💰 Miza biletului (RON):", min_value=1.0, value=miza_extrasa, step=1.0)

if st.button("⚡ SCANEAZĂ BILETUL ȘI CALCULEAZĂ PROCENTELE", use_container_width=True):
    lista_meciuri_temporara = []
    
    # 1. Încercăm parsatul automat pentru Superbet PDF
    meciuri_superbet, miza_pdf = parseaza_text_superbet(text_bilet)
    
    if meciuri_superbet:
        for m in meciuri_superbet:
            cota = m["cota"]
            prob_reala = max(1, min(99, int((1 / cota) * 100 * 0.95)))
            risc = "🟩 SAFE" if prob_reala >= 65 else ("🟨 MEDIUM" if prob_reala >= 40 else "🟥 RISK")
            
            lista_meciuri_temporara.append({
                "Meci / Eveniment": m["nume"],
                "Pronostic": m["prono"],
                "Cotă": cota,
                "Probabilitate": f"{prob_reala}%",
                "Nivel Risc": risc,
                "prob_num": prob_reala
            })
    else:
        # 2. Fallback la citirea linie cu linie
        linii = text_bilet.strip().split("\n")
        for linie in linii:
            parti = [p.strip() for p in re.split(r'[|,\t]', linie) if p.strip()]
            if len(parti) >= 2:
                try:
                    cota = float(parti[-1].replace(',', '.'))
                    nume = parti[0]
                    prono = parti[1] if len(parti) > 2 else "Eveniment"
                    
                    prob_reala = max(1, min(99, int((1 / cota) * 100 * 0.95)))
                    risc = "🟩 SAFE" if prob_reala >= 65 else ("🟨 MEDIUM" if prob_reala >= 40 else "🟥 RISK")
                    
                    lista_meciuri_temporara.append({
                        "Meci / Eveniment": nume,
                        "Pronostic": prono,
                        "Cotă": cota,
                        "Probabilitate": f"{prob_reala}%",
                        "Nivel Risc": risc,
                        "prob_num": prob_reala
                    })
                except ValueError:
                    continue

    st.session_state.bilet_automat = lista_meciuri_temporara
    st.success(f"✅ Am identificat {len(lista_meciuri_temporara)} meciuri pe bilet!")

# --- AFIȘARE REZULTATE ---
if st.session_state.bilet_automat:
    st.write("---")
    df_afisare = pd.DataFrame(st.session_state.bilet_automat)
    st.dataframe(df_afisare.drop(columns=["prob_num"]), use_container_width=True)
    
    cota_totala = 1.0
    prob_compusa = 1.0
    for m in st.session_state.bilet_automat:
        cota_totala *= m["Cotă"]
        prob_compusa *= (m["prob_num"] / 100)
        
    procent_final = round(prob_compusa * 100, 2)
    castig_potential = cota_totala * miza_simulata
    
    c1, c2, c3 = st.columns(3)
    with c1: st.metric(label="📈 COTĂ TOTALĂ", value=f"{cota_totala:.2f}")
    with c2: st.metric(label="🎯 PROBABILITATE REUȘITĂ", value=f"{procent_final}%")
    with c3: st.metric(label="💰 CÂȘTIG POTENȚIAL", value=f"{castig_potential:.2f} RON")
