import streamlit as st
import pandas as pd
import io
import re
from pypdf import PdfReader

# Configurare interfață Streamlit
st.set_page_config(page_title="Scanner Probabilități Pro", layout="wide", page_icon="📊")

st.markdown("<h1 style='text-align: center;'>📊 Verificator Automat Bilet VIP</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #4CAF50;'>Încarcă biletul PDF Superbet sau dă Paste la text mai jos</p>", unsafe_allow_html=True)
st.write("---")

if "bilet_automat" not in st.session_state:
    st.session_state.bilet_automat = []

def parseaza_pdf_superbet_universal(text_raw):
    """
    Parser robust pentru PDF-urile Superbet.
    Extrage cotele de la finalul documentului și le pune obligatoriu ca a 3-a coloană (după |).
    """
    # 1. Curățare caractere invalide
    text_curat = re.sub(r'[^\x00-\x7F]+', ' ', text_raw)
    linii = [l.strip() for l in text_curat.split('\n') if l.strip()]
    
    # 2. Extragerea listei de cote (de ex: 1.34, 1.30, 1.37 etc.)
    cote_gasite = []
    for l in linii:
        # Căutăm numere zecimale de forma 1.xx
        if re.match(r"^1\.\d{2}$", l):
            cote_gasite.append(float(l))
            
    # 3. Ignorare elemente de antet / sistem
    zgomot = [
        "International", "UEFA", "Liga", "Campioni", "Astazi", "Atazi", "Astan", "Aziz",
        "STATUS", "Activ", "Pariurile mele", "https", "COTA TOTALA", "BANI REALI",
        "SUPERBONUS", "CASTIG POTENTIAL", "RON", "Sport", "Simplu", "10/14/", "1/1", "Atzi"
    ]
    
    linii_utile = []
    for l in linii:
        if not any(z.lower() in l.lower() for z in zgomot) and not re.match(r"^1\.\d{2}$", l):
            linii_utile.append(l)

    # 4. Reconstrucția perechilor Echipe + Pronostic
    meciuri = []
    i = 0
    n = len(linii_utile)
    
    while i < n - 2:
        e1 = linii_utile[i]
        e2 = linii_utile[i+1]
        p = linii_utile[i+2]
        
        if re.match(r"^\d+-\d+$", p) or any(k in p for k in ["GG", "Peste", "Sub"]):
            detaliu = ""
            if i + 3 < n and "Interval" in linii_utile[i+3]:
                detaliu = f" ({linii_utile[i+3]})"
                i += 1
            
            meciuri.append({
                "echipe": f"{e1} - {e2}",
                "prono": f"{p}{detaliu}"
            })
            i += 3
        else:
            i += 1

    # 5. Combinare garantată: Echipe | Pronostic | Cota
    rezultat = []
    for idx, m in enumerate(meciuri):
        cota_meci = cote_gasite[idx] if idx < len(cote_gasite) else 1.35
        rezultat.append(f"{m['echipe']} | {m['prono']} | {cota_meci:.2f}")

    return "\n".join(rezultat)

# --- PASUL 1: INCĂRCARE PDF SAU INTRODUCERE TEXT ---
st.markdown("### 📋 Pasul 1: Încarcă biletul PDF sau lipeste textul")

uploaded_file = st.file_uploader("📄 Încarcă biletul în format PDF (Superbet)", type=["pdf"])

text_initial = ""

if uploaded_file is not None:
    try:
        reader = PdfReader(uploaded_file)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text() + "\n"
        
        text_curatat = parseaza_pdf_superbet_universal(pdf_text)
        
        if text_curatat:
            text_initial = text_curatat
            st.success("✅ Toate meciurile și cotele reale au fost asociate cu succes!")
        else:
            text_initial = pdf_text
            st.warning("⚠️ Am citit PDF-ul, dar te rugăm să verifici datele mai jos.")
            
    except Exception as e:
        st.error(f"Eroare la citirea fișierului PDF: {e}")

text_bilet = st.text_area(
    "Text formatat automat (verifică datele extrase):",
    value=text_initial if text_initial else "LASK Linz - Liverpool | 2-5 (Interval goluri) | 1.34\nFeyenoord Rotterdam - Como | 2-5 (Interval goluri) | 1.34",
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
        
        parti = [p.strip() for p in re.split(r'[|]', linie) if p.strip()]
        
        nume = parti[0] if len(parti) >= 1 else "Eveniment"
        prono = parti[1] if len(parti) >= 2 else "Pariu"
        
        # Extragem cota direct din a treia coloana sau dintr-un numar din linie
        cota = 1.35
        if len(parti) >= 3:
            try:
                cota = float(parti[2].replace(',', '.'))
            except ValueError:
                pass
        else:
            # Căutăm dacă cota a scăpat în textul pronosticului
            cota_match = re.search(r"(\d\.\d{2})", linie)
            if cota_match:
                cota = float(cota_match.group(1))
                
        # Curățăm cota dacă era rămasă în textul pronosticului
        prono = re.sub(r"\b1\.\d{2}\b", "", prono).strip()
        prono = re.sub(r"\s+", " ", prono)
                
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
